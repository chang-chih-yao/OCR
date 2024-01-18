# setup.py
from setuptools import find_packages, setup
from setuptools.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext

setup(
    #name="app",
    #version='1.0',
    ext_modules = cythonize(
        [
            Extension("scripts.my_func", ["scripts/my_func.py"]),
        ],
        build_dir="build_cythonize",
        compiler_directives={
            'language_level' : "3",
            'always_allow_keywords': True,
        }
    ),
    cmdclass={'build_ext': build_ext},
)
