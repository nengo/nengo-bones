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

install_requires = ["click>=7.0", "jinja2>=2.10", "pyyaml>=5.1"]
tests_require = [
    "codespell>=1.12.0",
    "gitlint>=0.1.2",
    "jupyter>=1.0.0",
    "nbval>=0.6.0",
    "pylint>=1.9.2",
    "pytest>=3.6.0",
    "pytest-cov>=2.6.0",
    "pytest-xdist>=1.16.0",
]
docs_require = [
    "nbsphinx>=0.2.13",
    "nengo-sphinx-theme>=0.7.0",
    "numpydoc>=0.6.0",
    "sphinx>=1.8.0",
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
    install_requires=install_requires,
    extras_require={
        "all": docs_require + tests_require,
        "docs": docs_require,
        "tests": tests_require,
    },
    classifiers=[],  # TODO
    entry_points="""
        [console_scripts]
        generate-bones=nengo_bones.scripts.generate_bones:main
        check-bones=nengo_bones.scripts.check_bones:main
    """,
    include_package_data=True,
)
