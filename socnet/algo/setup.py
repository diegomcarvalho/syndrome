from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [
    Extension("bestfit",  ["bestfit.pyx"])
]
setup(
    name="opt",
    ext_modules=cythonize(extensions),
)
