# pylint: disable=missing-docstring
import subprocess
from pathlib import Path

from click.testing import CliRunner

from nengo_bones import version
from nengo_bones.scripts import check_deploy
from nengo_bones.scripts.base import bones
from nengo_bones.tests.utils import assert_exit, write_file


def _write_repo_and_check(tmp_path, version_py=None, pypirc=True):
    if version_py is None:
        version_py = """
            major: 1
            minor: 2
            patch: 3
            release: true
        """

    nengo_yml = f"""\
    project_name: Fake NengoBones
    pkg_name: nengo_bones
    repo_name: nengo/nengo-bones
    version_py:
    {version_py}
    """
    write_file(tmp_path=tmp_path, filename=".nengobones.yml", contents=nengo_yml)

    pypirc_text = """\
    [pypi]
    username = __token__
    password = token
    [testpypi]
    username = __token__
    password = token
    """
    if pypirc:
        write_file(tmp_path=tmp_path, filename=".pypirc", contents=pypirc_text)

    result = CliRunner().invoke(
        bones,
        [
            "generate",
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert_exit(result, 0)
    return CliRunner().invoke(
        bones,
        [
            "check-deploy",
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
        ],
    )


def _monkeypatch(
    tmp_path,
    monkeypatch,
    tag="v1.2.3",
    branch="release-candidate-1.2.3",
    subject="Release v1.2.3",
    dev=None,
    version_str="1.2.3",
    fail_check_manifest=False,
):
    def ask_git(*args):
        if "tag" in args:
            return tag
        if "branch" in args:
            return branch
        if "show-branch" in args:
            return subject
        return ""

    monkeypatch.setattr(check_deploy, "_ask_git", ask_git)
    monkeypatch.setattr(check_deploy, "pypirc", tmp_path / ".pypirc")
    monkeypatch.setattr(version, "dev", dev)
    monkeypatch.setattr(version, "version", version_str)

    original_run = subprocess.run

    def mock_run(args, **kwargs):
        if args[0] == "check-manifest":
            return subprocess.CompletedProcess(
                args,
                returncode=1 if fail_check_manifest else 0,
                stdout=f"{'fail' if fail_check_manifest else 'pass'} check-manifest",
            )
        else:
            return original_run(args, **kwargs)  # pylint: disable=subprocess-run-check

    monkeypatch.setattr(subprocess, "run", mock_run)


def test_mock_success(tmp_path, monkeypatch):
    _monkeypatch(tmp_path, monkeypatch)
    result = _write_repo_and_check(tmp_path)
    assert_exit(result, 0)
    assert "All checks passed" in result.output


def _test_failure(tmp_path, monkeypatch, **patch_args):
    _monkeypatch(tmp_path, monkeypatch, **patch_args)
    result = _write_repo_and_check(tmp_path)
    assert_exit(result, 1)
    return result


def test_tag_branch_no_match(tmp_path, monkeypatch):
    result = _test_failure(tmp_path, monkeypatch, tag="", branch="main")
    assert "not on a release tag or release candidate branch" in result.output


def test_dev_flag(tmp_path, monkeypatch):
    result = _test_failure(tmp_path, monkeypatch, dev="0")
    assert "This is a dev version. Should be a release version." in result.output


def test_subject(tmp_path, monkeypatch):
    result = _test_failure(tmp_path, monkeypatch, subject="Starting next version")
    assert "Commit subject should be 'Release v1.2.3'" in result.output


def test_pypirc(tmp_path, monkeypatch):
    _monkeypatch(tmp_path, monkeypatch)
    result = _write_repo_and_check(tmp_path, pypirc=False)
    assert_exit(result, 1)
    assert "Cannot find ~/.pypirc. Make one" in result.output
    assert "[pypi] section not found in ~/.pypirc" in result.output
    assert "[testpypi] section not found in ~/.pypirc" in result.output


def test_changes(tmp_path, monkeypatch):
    write_file(tmp_path=tmp_path, filename="CHANGES.rst", contents="1.2.3 (unreleased)")
    result = _test_failure(tmp_path, monkeypatch)
    assert "Changelog has not been updated for release" in result.output


def test_rc_version(tmp_path, monkeypatch):
    result = _test_failure(tmp_path, monkeypatch, branch="release-candidate-1.2.2")
    assert (
        "Version '1.2.3' does not match git branch 'release-candidate-1.2.2'"
        in result.output
    )


def test_tag_version(tmp_path, monkeypatch):
    result = _test_failure(tmp_path, monkeypatch, tag="v1.2.2")
    assert "Version '1.2.3' does not match git tag 'v1.2.2'" in result.output


def test_check_manifest(tmp_path, monkeypatch):
    result = _test_failure(tmp_path, monkeypatch, fail_check_manifest=True)
    assert "fail check-manifest" in result.output


def test_non_mock(tmp_path, monkeypatch):
    # still going to mock out the pypirc part, since we don't want to force devs
    # who are never going to be deploying to pypi to set up a pypirc file
    pypirc_text = """\
        [pypi]
        username = __token__
        password = token
        [testpypi]
        username = __token__
        password = token
        """
    write_file(tmp_path=tmp_path, filename=".pypirc", contents=pypirc_text)
    monkeypatch.setattr(check_deploy, "pypirc", tmp_path / ".pypirc")

    result = CliRunner().invoke(
        bones,
        [
            "check-deploy",
            "--conf-file",
            str(Path(__file__).parents[2] / ".nengobones.yml"),
        ],
    )

    if version.dev is not None:
        # we expect this check to fail if this isn't a release commit
        assert_exit(result, 1)
        assert (
            # this is the error we expect most of the time
            "not on a release tag or release candidate" in result.output
            # this is the error we get when on a release candidate branch but not
            # the release commit
            or "This is a dev version" in result.output
        )
    else:
        assert_exit(result, 0)
