# pylint: disable=missing-docstring

__copyright__ = "2018-2019, Applied Brain Research"
__license__ = "Free for non-commercial use; see LICENSE.rst"

from nengo_bones.version import version as __version__

from nengo_bones.config import load_config

all_templated_files = {
    ".travis.yml": "travis_yml",
    ".codecov.yml": "codecov_yml",
    "docs/conf.py": "docs_conf_py",
    "setup.cfg": "setup_cfg",
    "setup.py": "setup_py",
    "CONTRIBUTING.rst": "contributing_rst",
    "CONTRIBUTORS.rst": "contributors_rst",
    "LICENSE.rst": "license_rst",
    "MANIFEST.in": "manifest_in",
}
