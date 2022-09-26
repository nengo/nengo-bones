# pylint: disable=missing-docstring

from click.testing import CliRunner

from nengo_bones.scripts import check_bones, generate_bones
from nengo_bones.tests.utils import assert_exit, write_file


def _write_nengo_yml(tmp_path, nengo_yml=None):
    if nengo_yml is None:
        nengo_yml = """
            project_name: Dumdum
            pkg_name: dummy
            repo_name: dummy_org/dummy
            contributors_rst: {}
            """

    write_file(tmp_path=tmp_path, filename=".nengobones.yml", contents=nengo_yml)


def _generate_valid_file(tmp_path):
    """Generate a valid contributors.rst with bones-generate."""
    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "contributors-rst",
        ],
    )
    assert_exit(result, 0)


def _run_check_bones(tmp_path):
    cmdline_args = [
        "--root-dir",
        str(tmp_path),
        "--conf-file",
        str(tmp_path / ".nengobones.yml"),
        "--verbose",
    ]
    return CliRunner().invoke(check_bones.main, cmdline_args)


def test_success(tmp_path):
    _write_nengo_yml(tmp_path)
    _generate_valid_file(tmp_path)
    result = _run_check_bones(tmp_path)
    assert_exit(result, 0)
    assert "CONTRIBUTORS.rst:\n  Up to date" in result.output


def test_no_file(tmp_path):
    _write_nengo_yml(tmp_path)
    result = _run_check_bones(tmp_path)
    assert_exit(result, 0)
    assert ".travis.yml:\n  File not found" in result.output


def test_modified_file(tmp_path):
    _write_nengo_yml(tmp_path)
    _generate_valid_file(tmp_path)
    with (tmp_path / "CONTRIBUTORS.rst").open("a") as f:
        f.write("x")
    result = _run_check_bones(tmp_path)
    assert_exit(result, 1)
    assert "CONTRIBUTORS.rst:\n  Content does not match" in result.output
    assert "  Full diff" in result.output


def test_file_not_generated_by_bones(tmp_path):
    _write_nengo_yml(tmp_path)
    (tmp_path / "CONTRIBUTORS.rst").write_text("a contributor")
    result = _run_check_bones(tmp_path)
    assert_exit(result, 0)
    assert (
        "CONTRIBUTORS.rst:\n  This file was not generated with nengo-bones"
        in result.output
    )


def test_file_pretending_to_be_bones_generated(tmp_path):
    _write_nengo_yml(
        tmp_path,
        nengo_yml="""
            project_name: Dumdum
            pkg_name: dummy
            repo_name: dummy_org/dummy
        """,
    )
    (tmp_path / "CONTRIBUTORS.rst").write_text("Automatically generated by nengo-bones")
    result = _run_check_bones(tmp_path)
    assert_exit(result, 1)
    assert (
        "CONTRIBUTORS.rst:\n"
        "  This file contains 'Automatically generated by nengo-bones'" in result.output
    )
