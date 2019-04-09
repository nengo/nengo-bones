#!/usr/bin/env python
import io
import os
import runpy

try:
    from setuptools import find_packages, setup
except ImportError:
    raise ImportError(
        "'setuptools' is required but not installed. To install it, "
        "follow the instructions at "
        "https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py")


def read(*filenames, **kwargs):
    encoding = kwargs.get("encoding", "utf-8")
    sep = kwargs.get("sep", "\n")
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


root = os.path.dirname(os.path.realpath(__file__))
version = runpy.run_path(os.path.join(
    root, 'nengo_bones', 'version.py'))['version']

install_requires = [
]
docs_require = [
    "sphinx",
    "nengo_sphinx_theme",
]
optional_requires = [
]
tests_require = [
    "pytest>=3.6",
]


setup(
    name="nengo-bones",
    version=version,
    author="Applied Brain Research",
    author_email="info@appliedbrainresearch.com",
    packages=find_packages(),
    url="https://github.com/nengo/nengo-bones",
    license="Free for non-commercial use",
    description="Tools for managing Nengo projects",
    long_description=read("README.rst", "CHANGES.rst"),
    setup_requires=["pytest-runner"] if testing else [] + install_requires,
    install_requires=install_requires,
    extras_require={
        "all": docs_require + optional_requires + tests_require,
        "docs": docs_require,
        "optional": optional_requires,
        "tests": tests_require,
    },
    tests_require=tests_require,
    classifiers=[
        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
)
