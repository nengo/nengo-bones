#!/usr/bin/env python
import imp
import io
import os
import sys

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
version_module = imp.load_source(
    "version", os.path.join(root, "{{ PACKAGE }}", "version.py"))
testing = "test" in sys.argv or "pytest" in sys.argv

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
    name="{{ REPO NAME }}",
    version=version_module.version,
    author="Applied Brain Research",
    author_email="info@appliedbrainresearch.com",
    packages=find_packages(),
    scripts=[],
    data_files=[],
    url="https://github.com/nengo/{{ REPO NAME }}",
    license="Free for non-commercial use",
    description="{{ DESCRIPTION }}",
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
