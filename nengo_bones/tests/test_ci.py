# pylint: disable=missing-docstring

"""
These tests are designed to be executed during CI, to test that the ci scripts
are working correctly.

They will not pass when run locally.
"""

import os
import sys

import pytest


@pytest.mark.xfail("TRAVIS" not in os.environ,
                   reason="Not running on TravisCI")
def test_extra_commands():
    # pre_commands will be used to set an environment variable, which
    # we check for here
    assert "TEST_PRE_COMMANDS" in os.environ

    # post_commands shouldn't have been executed yet, so no env variable
    # (we verify that post_commands does actually insert commands in
    # test_generate_bones)
    assert "TEST_POST_COMMANDS" not in os.environ


@pytest.mark.xfail("TRAVIS" not in os.environ,
                   reason="Not running on TravisCI")
def test_env_vars():
    # global variable created in travis config
    assert os.environ["TEST_GLOBAL_VAR"] == "test global var val"

    # var whose value is overridden on a per-job basis
    assert os.environ["TEST_LOCAL_VAR"] == "test local var val"


@pytest.mark.xfail("TRAVIS" not in os.environ,
                   reason="Not running on TravisCI")
def test_coverage(pytestconfig):
    cov_flag = pytestconfig.getoption("--cov", None)

    # check conditional coverage behaviour
    if os.environ["SCRIPT"] == "test-coverage":
        assert cov_flag is not None
    else:
        assert cov_flag is None


@pytest.mark.xfail("TRAVIS" not in os.environ,
                   reason="Not running on TravisCI")
def test_custom_args(pytestconfig):
    assert pytestconfig.getoption("--test-arg")


@pytest.mark.xfail("TRAVIS" not in os.environ,
                   reason="Not running on TravisCI")
def test_python_version():
    assert ".".join(str(x) for x in sys.version_info[:2]) == os.environ[
        "TRAVIS_PYTHON_VERSION"]
