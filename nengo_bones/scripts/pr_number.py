"""Retrieves the next PR number for a specific repository."""

import click
import requests

import nengo_bones


def get_issue_count(repo):
    """Count the number of issues and PRs in a repository."""

    response = requests.get(
        "https://api.github.com/repos/%s/issues?state=all&sort=created"
        % (repo,),
    )
    return int(response.json()[0]["number"])


@click.command()
@click.argument("repo", required=False, default=None)
@click.option("--conf-file", default=None, help="Filepath for config file")
def main(repo, conf_file):
    """Get the next available PR number for a repository.

    When writing a CHANGELOG entry, it helpful to predict the PR number for the
    branch before the PR has actually been made. This script counts the issues
    in the repository and returns the next available number.

    This command will read --conf-file to determine the current repository.
    To check for another repository, pass it as an argument.
    """

    if repo is None:
        config = nengo_bones.load_config(conf_file)
        repo = config["repo_name"]

    click.echo("Asking GitHub for information about %s..." % (repo,))
    current_num = get_issue_count(repo)
    next_num = current_num + 1
    click.echo("If you open a PR now it will be assigned #%d" % (next_num,))
    click.echo("Use this link for the changelog entry:")
    click.echo("https://github.com/%s/pull/%d" % (repo, next_num))


if __name__ == "__main__":
    main()  # pragma: no cover pylint: disable=no-value-for-parameter
