from precomputed_tif.client import ArrayReader
import pathlib
import tifffile
import math
from functools import partial
import argparse
import multiprocessing
import tqdm
import numpy as np
import itertools
from precomputed_tif.blockfs_stack import BlockfsStack
from blockfs.directory import Directory
import sys

    
def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file-path', help='path of input file', required= True)
    parser.add_argument("--x-index",
                        help="The index of the x-coordinate in the alignment"
                             " points matrix, e.g. \"0\" if the x and z "
                        "axes were transposed. Defaults to 2.",
                        type=int,
                        default=2)
    parser.add_argument("--y-index",
                        help="The index of the y-coordinate in the alignment"
                             " points matrix, e.g. \"0\" if the y and z "
                        "axes were transposed. Defaults to 1.",
                        type=int,
                        default=1)
    parser.add_argument("--z-index",
                        help="The index of the z-coordinate in the alignment"
                             " points matrix, e.g. \"2\" if the x and z "
                        "axes were transposed. Defaults to 0.",
                        type=int,
                        default=0)
    parser.add_argument("--flip-x",
                        help="Indicates that the image should be flipped "
                        "in the X direction after transposing and resizing.",
                        action="store_true",
                        default=False)
    parser.add_argument("--flip-y",
                        help="Indicates that the image should be flipped "
                        "in the y direction after transposing and resizing.",
                        action="store_true",
                        default=False)
    parser.add_argument("--flip-z",
                        help="Indicates that the image should be flipped "
                        "in the z direction after transposing and resizing.",
                        action="store_true",
                        default=False)

    parser.add_argument("--dest",
                            help="Destination directory for precomputed stack.", 
                        required= True)

    parser.add_argument("--levels",
                        type=int,
                        help="# of mipmap levels",
                        default=4)

    parser.add_argument("--input-levels",
                        type=int,
                        help="mipmap level on disk",
                        default=1)

    parser.add_argument("--n-cores",
                        type=int,
                        default=multiprocessing.cpu_count(),
                        help="The number of cores to use for multiprocessing.")

    parser.add_argument("--voxel-size",
                        default="1.8,1.8,2.0",
                        help="The voxel size in microns, default is for 4x "
                             "SPIM. This should be three comma-separated "
                             "values, e.g. \"1.8,1.8,2.0\".")
    return parser.parse_args(args)

def flip_transpose_function(input_file_path, z0, y0, x0, index_x=2, index_y=1, index_z=0,flip_x=False, flip_y=False, flip_z=False):

    z0_y0_x0=[z0,y0,x0]
    x0_out =x0
    x1_out =min(ar.shape[2], x0+64)
    y0_out =y0
    y1_out =min(ar.shape[1], y0+64)
    z0_out =z0
    z1_out =min(ar.shape[0], z0+64)
    
    if flip_x:
        x0_in = max(0, ar.shape[2]-z0_y0_x0[index_x]-64)
        x1_in =ar.shape[2]-z0_y0_x0[index_x]
        x_inc =-1
    else:
        x0_in= z0_y0_x0[index_x]
        x1_in= min(ar.shape[2], z0_y0_x0[index_x]+64)
        x_inc =1
        
    if flip_y:
        y0_in = max(0, ar.shape[1]-z0_y0_x0[index_y]-64)
        y1_in =ar.shape[1]-z0_y0_x0[index_y]
        y_inc =-1
    else:
        y0_in= z0_y0_x0[index_y]
        y1_in = min(ar.shape[1],z0_y0_x0[index_y]+64)
        y_inc =1
        
    if flip_z:
        z0_in = max(0, ar.shape[0]-z0_y0_x0[index_z]-64)
        z1_in =ar.shape[0]-z0_y0_x0[index_z]
        z_inc =-1
    else:
        z0_in= z0_y0_x0[index_z]
        z1_in =min(ar.shape[0], z0_y0_x0[index_z]+64)
        z_inc =1
    
    index_x = index_x
    index_y = index_y
    index_z = index_z
    block_in = ar[z0_in:z1_in,y0_in:y1_in,x0_in:x1_in]
    block_out=block_in[::z_inc, ::y_inc, ::x_inc].transpose(index_z, index_y, index_x)
    
    expected_block_size = DIRECTORY.get_block_size( x0_out, y0_out, z0_out)
   
    assert(tuple(block_out.shape) == expected_block_size)
    
    DIRECTORY.write_block(np.ascontiguousarray(block_out), x0_out, y0_out, z0_out)

def write_level_1(args, stack:BlockfsStack):
    global DIRECTORY
    DIRECTORY = stack.make_l1_directory(args.n_cores)
    DIRECTORY.create()
    DIRECTORY.start_writer_processes()

    x0 = np.arange(0, ar.shape[args.x_index], 64)
    y0 = np.arange(0, ar.shape[args.y_index], 64)
    z0 = np.arange(0, ar.shape[args.z_index], 64)

    with multiprocessing.Pool() as pool:
        futures = []
        output = []
        for za0, ya0, xa0 in list(itertools.product(z0, y0, x0)):
            futures.append(pool.apply_async(flip_transpose_function, (args.input_file_path, 
                                                            za0, ya0, xa0), dict(index_x=args.x_index, index_y=args.y_index, 
                                                                                 index_z=args.z_index,flip_x=args.flip_x, flip_y=args.flip_y ,
                                                                                 flip_z=args.flip_z)))
        for future in tqdm.tqdm(futures):
            output.append(future.get())
        DIRECTORY.close()
             
def main():
    global ar
    args = parse_args(sys.argv[1:])
    path = pathlib.Path(args.input_file_path)
    ar = ArrayReader(path.as_uri(), format="blockfs", level=args.input_levels)
    shape=ar.shape
    shape_t=[shape[args.z_index],shape[args.y_index],shape[args.x_index]]
    stack = BlockfsStack(shape_t, args.dest)
    voxel_size = [int(float(_) * 1000) for _ in args.voxel_size.split(",")]
    voxel_size=[voxel_size[args.z_index],voxel_size[args.y_index],voxel_size[args.x_index]]
    stack.write_info_file(args.levels, voxel_size)
    write_level_1(args, stack)
    for level in range(2, args.levels+1):
        stack.write_level_n(level, n_cores=args.n_cores)

if __name__ == "__main__":
    main()
