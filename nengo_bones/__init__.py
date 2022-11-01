# pylint: disable=missing-docstring

__license__ = "Free for non-commercial use; see LICENSE.rst"

from . import config, templates
from .version import copyright as __copyright__
from .version import version as __version__

all_sections = [
    "codecov_yml",
    "docs_conf_py",
    "setup_cfg",
    "setup_py",
    "contributing_rst",
    "contributors_rst",
    "license_rst",
    "manifest_in",
    "pre_commit_config_yaml",
    "pyproject_toml",
    "py_typed",
    "version_py",
]

all_files = [
    ".codecov.yml",
    "docs/conf.py",
    "setup.cfg",
    "setup.py",
    "CONTRIBUTING.rst",
    "CONTRIBUTORS.rst",
    "LICENSE.rst",
    "MANIFEST.in",
    ".pre-commit-config.yaml",
    "pyproject.toml",
    "pkg/py.typed",
    "pkg/version.py",
]
