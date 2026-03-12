from pathlib import Path
from setuptools import setup

import os

try:
    import torch
    from torch.utils.cpp_extension import BuildExtension, CppExtension, CUDA_HOME
except ImportError:
    torch = None
    BuildExtension = None
    CppExtension = None
    CUDA_HOME = None

ROOT = os.path.dirname(os.path.abspath(__file__))
has_cuda = torch is not None and torch.cuda.is_available() and CUDA_HOME is not None

include_dirs = [
    os.path.join(ROOT, "mast3r_fusion/backend/include"),
    os.path.join(ROOT, "thirdparty/eigen"),
]

sources = [
    "mast3r_fusion/backend/src/gn.cpp",
]
ext_modules = []
extra_compile_args = {
    "cores": ["j8"],
    "cxx": ["-O3"],
}

if has_cuda:
    from torch.utils.cpp_extension import CUDAExtension

    sources.append("mast3r_fusion/backend/src/gn_kernels.cu")
    sources.append("mast3r_fusion/backend/src/matching_kernels.cu")
    extra_compile_args["nvcc"] = [
        "-O3",
        "-gencode=arch=compute_60,code=sm_60",
        "-gencode=arch=compute_61,code=sm_61",
        "-gencode=arch=compute_70,code=sm_70",
        "-gencode=arch=compute_75,code=sm_75",
        "-gencode=arch=compute_80,code=sm_80",
        "-gencode=arch=compute_86,code=sm_86",
    ]
    ext_modules = [
        CUDAExtension(
            "mast3r_fusion_backends",
            include_dirs=include_dirs,
            sources=sources,
            extra_compile_args=extra_compile_args,
        )
    ]
elif torch is None:
    print("Torch not found, skipping backend build.")
elif CUDA_HOME is None:
    print("CUDA_HOME is not set, skipping CUDA backend build.")
else:
    print("CUDA not found, cannot compile backend!")

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExtension} if BuildExtension is not None else {},
)
