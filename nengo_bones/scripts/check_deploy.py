"""Checks that the current project is ready to be deployed."""

import importlib
import subprocess
import sys
from pathlib import Path

import click

from nengo_bones.config import find_config, load_config
from nengo_bones.scripts.base import bones


def _ask_git(*args):
    return subprocess.check_output(("git",) + args, encoding="utf-8").strip()


pypirc = Path.home() / ".pypirc"


@bones.command(name="check-deploy")
@click.option("--conf-file", default=None, help="Filepath for config file")
def main(conf_file):
    """Validates that the project is ready to be deployed."""

    conf_file = find_config() if conf_file is None else conf_file
    config = load_config(conf_file)
    root_dir = Path(conf_file).parent

    version = importlib.import_module(config["pkg_name"]).version

    git_tag = _ask_git("-C", str(root_dir), "tag", "--points-at", "HEAD")
    git_branch = _ask_git("-C", str(root_dir), "branch", "--show-current")
    rc = git_branch.startswith("release-candidate-")
    release = git_tag.startswith("v")

    if not rc and not release:
        click.echo("Repository is not on a release tag or release candidate branch")
        sys.exit(1)

    passed = True

    def check(condition, msg):
        if not condition:
            nonlocal passed
            click.echo(msg)
            passed = False

    pypirc_text = pypirc.read_text() if pypirc.exists() else ""

    check(version.dev is None, "This is a dev version. Should be a release version.")

    commit_subject = _ask_git("-C", str(root_dir), "show-branch", "--no-name", "HEAD")
    check(
        commit_subject == f"Release v{version.version}",
        f"Commit subject should be 'Release v{version.version}'",
    )

    if not pypirc.exists():
        click.echo("Cannot find ~/.pypirc. Make one to store PyPI credentials.")

    changelog = Path(root_dir) / "CHANGES.rst"
    if changelog.exists():
        check(
            "unreleased" not in changelog.read_text(),
            "Changelog has not been updated for release",
        )

    if rc:
        check(
            version.version == git_branch[len("release-candidate-") :],
            f"Version '{version.version}' does not match git branch '{git_branch}'",
        )
        check(
            not pypirc.exists() or "[testpypi]\n" in pypirc_text,
            "[testpypi] section not found in ~/.pypirc",
        )

    if release:
        check(
            f"v{version.version}" == git_tag,
            f"Version '{version.version}' does not match git tag '{git_tag}'",
        )
        check(
            not pypirc.exists() or "[pypi]\n" in pypirc_text,
            "[pypi] section not found in ~/.pypirc",
        )

    output = subprocess.run(
        ["check-manifest", root_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        check=False,
    )
    check(output.returncode == 0, f"Error in manifest:\n{output.stdout}")

    if passed:
        click.echo("All checks passed")
    else:
        sys.exit(1)
