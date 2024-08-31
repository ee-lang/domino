from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "game_state_cy",
        ["game_state_cy.pyx"],
        language="c++"
    ),
]

setup(
    ext_modules = cythonize(extensions)
)