from cython.view cimport array as cvarray
from libc.stdlib cimport atof
cimport numpy as np
import numpy as np

cpdef parse(np.ndarray[dtype=np.uint8_t] input,
            np.ndarray[dtype=np.float32_t, ndim=2] output):
    """Parse simple ITK point output

    :param input: the ASCII contents of the file
    :param output: an Nx3 array of the appropriate size to receive it
    """
    cdef:
        int iidx=0
        int oidx=0
        char *search_string=b"OutputPoint"
        char *pinput=<char *>input.data
        int sidx
        int begin_idx
    while oidx < output.shape[0]:
        sidx = 0
        while iidx < input.shape[0]:
            if sidx == 11:
                break
            if search_string[sidx] == input[iidx]:
               iidx += 1
               sidx += 1
            else:
               iidx += 1
               sidx = 0
        # ascii 45 is "-"
        # ascii 46 and 47  are "." and "/" which should not be encountered
        # ascii 48 through 57 are 0 through 9
        while iidx < input.shape[0] and (input[iidx] < 45 or input[iidx] >= 58):
            iidx += 1
        if iidx == input.shape[0]:
            break
        begin_idx = iidx
        while iidx < input.shape[0] and input[iidx] >=45 and input[iidx] < 58:
            iidx += 1
        if iidx == input.shape[0]:
            break
        output[oidx, 0] = atof(pinput + begin_idx)
        while iidx < input.shape[0] and (input[iidx] < 45 or input[iidx] >= 58):
            iidx += 1
        if iidx == input.shape[0]:
            break
        begin_idx = iidx
        while iidx < input.shape[0] and input[iidx] >=45 and input[iidx] < 58:
            iidx += 1
        if iidx == input.shape[0]:
            break
        output[oidx, 1] = atof(pinput + begin_idx)
        while iidx < input.shape[0] and (input[iidx] < 45 or input[iidx] >= 58):
            iidx += 1
        if iidx == input.shape[0]:
            break
        begin_idx = iidx
        while iidx < input.shape[0] and input[iidx] >= 45 and input[iidx] < 58:
            iidx += 1
        if iidx == input.shape[0]:
            break
        output[oidx, 2] = atof(pinput + begin_idx)
        oidx += 1