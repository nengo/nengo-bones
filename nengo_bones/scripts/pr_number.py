"""Retrieves the next PR number for a specific repository."""

import click
import requests

from nengo_bones.config import load_config
from nengo_bones.scripts.base import bones


def get_issue_count(repo):
    """Count the number of issues and PRs in a repository."""

    response = requests.get(
        f"https://api.github.com/repos/{repo}/issues?state=all&sort=created", timeout=60
    )
    return int(response.json()[0]["number"])


@bones.command(name="pr-number")
@click.argument("repo", required=False, default=None)
@click.option("--conf-file", default=None, help="Filepath for config file")
def main(repo, conf_file):
    """
    Get the next available PR number for a repository.

    When writing a CHANGELOG entry, it helpful to predict the PR number for the
    branch before the PR has actually been made. This script counts the issues
    in the repository and returns the next available number.

    This command will read --conf-file to determine the current repository.
    To check for another repository, pass it as an argument.
    """

    if repo is None:
        config = load_config(conf_file)
        repo = config["repo_name"]

    click.echo(f"Asking GitHub for information about {repo}...")
    current_num = get_issue_count(repo)
    next_num = current_num + 1
    click.echo(f"If you open a PR now it will be assigned #{next_num}")
    click.echo("Use this link for the changelog entry:")
    click.echo(f"https://github.com/{repo}/pull/{next_num}")
