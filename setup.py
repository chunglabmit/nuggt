from setuptools import setup, find_packages, Extension
import numpy as np
import os

version = "0.1.0"

with open("./README.md") as fd:
    long_description = fd.read()

sitk_align_extension = Extension(
    name="nuggt._sitk_align",
    sources=[os.path.join("nuggt", "_sitk_align.pyx")],
    include_dirs=[np.get_include()]
)
setup(
    name="nuggt",
    version=version,
    description=
    "NeUroproof Ground Truth: cell center annotator using Neuroproof",
    long_description=long_description,
    install_requires=[
        "numpy",
        "neuroglancer",
        "scipy",
        "tifffile",
        "tqdm"
    ],
    setup_requires=[
        "Cython"
    ],
    author="Kwanghun Chung Lab",
    packages=["nuggt", "nuggt.utils"],
    entry_points={ 'console_scripts': [
        'calculate-intensity-in-regions=nuggt.calculate_intensity_in_regions:main',
        'count-points-in-region=nuggt.count_points_in_region:main',
        'crop-coordinates=nuggt.crop_coordinates:main',
        'nuggt=nuggt.main:main',
        'nuggt-align=nuggt.align:main',
        'nuggt-display=nuggt.display_image:main',
        'make-alignment-file=nuggt.make_alignment_file:main',
        'rescale-alignment-file=nuggt.rescale_alignment_file:main',
        'rescale-image-for-alignment=nuggt.rescale_image_for_alignment:main',
        'sitk-align=nuggt.sitk_align:main',
        'yea-nay=nuggt.yea_nay:main'
    ]},
    url="https://github.com/chunglabmit/nuggt",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 3.5',
    ],
    ext_modules=[sitk_align_extension],
    zip_safe=False
)