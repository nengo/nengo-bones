# pylint: disable=missing-docstring

from click.testing import CliRunner

from nengo_bones.scripts import check_bones
from nengo_bones.tests.utils import write_file, assert_exit
from nengo_bones.version import version


def test_files(tmpdir):
    # file not found
    result = CliRunner().invoke(
        check_bones.main, ["--root-dir", str(tmpdir)])

    assert_exit(result, 0)
    assert ".travis.yml:\n  File not found" in result.output

    # successful version read
    write_file(tmpdir, ".travis.yml", """
        this is some text
        that comes before
        the title
        # this is a comment with Version: 0.0.0 in it
        # Version: %s

        some text
        that comes after
        """ % version)
    result = CliRunner().invoke(
        check_bones.main, ["--root-dir", str(tmpdir)])

    assert_exit(result, 0)
    assert ".travis.yml:\n  Up to date" in result.output

    # old version
    write_file(tmpdir, ".travis.yml", "# Version: 0.0.0")
    result = CliRunner().invoke(
        check_bones.main, ["--root-dir", str(tmpdir)])
    assert_exit(result, 1)
    assert ".travis.yml:\n  Version (0.0.0) does not match" in result.output

    # no version info
    write_file(tmpdir, ".travis.yml", "this file has no version data")
    result = CliRunner().invoke(
        check_bones.main, ["--root-dir", str(tmpdir)])
    assert_exit(result, 1)
    assert ".travis.yml:\n  This file was not generated with nengo-bones"
