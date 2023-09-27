# pylint: disable=missing-docstring

import os
import pathlib

import pytest

from nengo_bones import config
from nengo_bones.tests import utils


def test_find_config():
    assert config.find_config() == pathlib.Path.cwd() / ".nengobones.yml"


def test_fill_defaults():
    init_cfg = {
        "repo_name": "test_org/test_repo",
        "setup_py": {},
    }
    config.fill_defaults(init_cfg)

    assert init_cfg["setup_py"]["license_string"] == "Proprietary"
    assert init_cfg["setup_py"]["classifiers"] == [
        "License :: Other/Proprietary License"
    ]


def test_validate_config():
    init_cfg = {"version_py": {}}
    for entry in config.mandatory_entries:
        with pytest.raises(KeyError, match=f"must define {entry}"):
            config.validate_config(init_cfg)

        keys = entry.split(".")
        tmp = init_cfg
        for key in keys[:-1]:
            tmp = tmp[key]
        tmp[keys[-1]] = {}

    config.validate_config(init_cfg)

    init_cfg["ci_scripts"] = {}

    # error when license type is not recognized
    init_cfg["license"] = "bsd"
    with pytest.raises(ValueError, match='must be one of "abr-free", "abr-nonfree"'):
        config.validate_config(init_cfg)
    del init_cfg["license"]

    # error when license classifier manually specified
    test_cfg = {"classifiers": ["License :: Cool license"]}
    init_cfg["setup_py"] = test_cfg
    with pytest.raises(ValueError, match="remove manual entry"):
        config.validate_config(init_cfg)
    del init_cfg["setup_py"]

    # error when template not defined
    test_cfg = {}
    init_cfg["ci_scripts"] = [test_cfg]
    with pytest.raises(KeyError, match="must define 'template'"):
        config.validate_config(init_cfg)
    test_cfg["template"] = "test"

    # error when pip_install is a string instead of list
    test_cfg["pip_install"] = "pip_req"
    with pytest.raises(TypeError, match="pip_install should be a list"):
        config.validate_config(init_cfg)
    test_cfg["pip_install"] = ["pip_req"]

    # error when pre_commands is a string instead of list
    test_cfg["pre_commands"] = "command"
    with pytest.raises(TypeError, match="pre_commands should be a list"):
        config.validate_config(init_cfg)
    test_cfg["pre_commands"] = ["command"]

    # error when only one of pre_commit_config_yaml or pyproject_toml exists
    init_cfg["pyproject_toml"] = {}
    with pytest.raises(KeyError, match="must define both"):
        config.validate_config(init_cfg)
    init_cfg["pre_commit_config_yaml"] = {}

    # error when Black exclude lists don't match
    init_cfg["pre_commit_config_yaml"]["exclude"] = ["file2.py"]
    init_cfg["pyproject_toml"]["exclude"] = ["file1.py"]
    with pytest.raises(ValueError, match="must have the same 'exclude' list"):
        config.validate_config(init_cfg)
    del init_cfg["pre_commit_config_yaml"]["exclude"]
    del init_cfg["pyproject_toml"]["exclude"]


def test_missing_config(tmp_path):
    with pytest.raises(RuntimeError, match="Could not find conf_file"):
        config.load_config(tmp_path / ".does-not-exist.yml")


def test_load_config(tmp_path):
    truth = {
        "project_name": "Dummy",
        "pkg_name": "dummy",
        "repo_name": "abr/dummy",
        "min_python": "3.8",
        "main_branch": "master",
        "author": "A Dummy",
        "author_email": "dummy@dummy.com",
        "copyright_start": 0,
        "copyright_end": 1,
        "notice": "dummy notice",
        "license": "proprietary",
        "ci_scripts": [
            {"template": "static", "pip_install": ["static_pip0", "static_pip1"]}
        ],
        "setup_py": {
            "license_string": "Proprietary",
            "python_requires": ">=3.8",
            "include_package_data": False,
            "url": "https://www.appliedbrainresearch.com/dummy",
            "classifiers": ["License :: Other/Proprietary License"],
        },
    }

    utils.write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dummy
        pkg_name: dummy
        repo_name: abr/dummy
        author: A Dummy
        author_email: dummy@dummy.com
        copyright_start: 0
        copyright_end: 1
        notice: dummy notice

        ci_scripts:
          - template: static
            pip_install:
              - static_pip0
              - static_pip1

        setup_py: {}
        """,
    )

    loaded = config.load_config(tmp_path / ".nengobones.yml")

    try:
        assert loaded == truth
    except AssertionError:  # pragma: no cover
        print("loaded")
        print("\n".join(f"{k}: {v}" for k, v in loaded.items()))
        print("truth")
        print("\n".join(f"{k}: {v}" for k, v in truth.items()))
        raise

    # check loading from cwd
    cwd = pathlib.Path.cwd()
    os.chdir(tmp_path)
    try:
        loaded = config.load_config()
    finally:
        os.chdir(cwd)

    assert loaded == truth
