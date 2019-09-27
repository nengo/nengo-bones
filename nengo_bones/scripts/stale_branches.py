"""Retrieves a list of stale branches in a specific repository."""

from collections import OrderedDict
from datetime import datetime
import os
import random
import time

import click
import requests
from requests.exceptions import HTTPError, RequestException

import nengo_bones

import pdb


class _backoff:
    MAX_COUNTER = 5  # corresponds to a minute of waiting

    def __init__(self):
        self.counter = 0

    def __call__(self):
        fudge_ms = random.randint(0, 1000) / 1000
        time.sleep(2 ** self.counter + fudge_ms)
        self.counter = min(self.MAX_COUNTER, self.counter + 1)


backoff = _backoff()


class GitHubRequester:
    def __init__(self):
        username = os.getenv("BONES_GH_USER")
        if username is None:
            raise RuntimeError("Please export BONES_GH_USER")
        token = os.getenv("BONES_GH_TOKEN")
        if token is None:
            raise RuntimeError("Please export BONES_GH_TOKEN")
        self.session = requests.Session()
        self.session.auth = (username, token)
        self.session.headers = {
            "User-Agent": "Nengo Bones v%s" % nengo_bones.__version__
        }

    def __call__(self, repo, endpoint):
        resp = None
        while resp is None:
            try:
                resp = self.session.get(
                    "https://api.github.com/repos/%s/%s" % (repo, endpoint)
                )
                resp.raise_for_status()
            except (HTTPError, RequestException) as e:
                click.echo("%s" % e)
                click.echo("Taking a short break and retrying...")
                resp = None
                backoff()
        return resp.json()


def get_stale_branches(repo, age_years=2):
    """Get a list of branches older than ``age_years``."""

    now = datetime.now()
    req = GitHubRequester()

    # Get list of branches
    branches_json = req(repo, "branches")
    branches = OrderedDict(
        [
            (branch["name"], {"age": None, "open_pr": None, "is_pr_base": False})
            for branch in branches_json
        ]
    )

    # Attach last modified date to branch
    for branch in list(branches):
        info = req(repo, "branches/%s" % branch)
        if "name" not in info:
            print(info)
        assert info["name"] == branch
        last_modified = datetime.strptime(
            info["commit"]["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ"
        )
        age = now - last_modified
        if age.days >= age_years * 365:
            branches[branch]["age"] = age
        else:
            del branches[branch]

    # Attach PRs to branches
    for pr in req(repo, "pulls?state=open"):
        head_repo = "{}/{}".format(
            pr["head"]["user"]["login"], pr["head"]["repo"]["name"]
        )
        head_branch = pr["head"]["ref"]
        if head_repo == repo and head_branch in branches:
            branches[head_branch]["open_pr"] = pr["html_url"]
        base_ref = pr["base"]["ref"]
        if base_ref in branches:
            branches[base_ref]["is_pr_base"] = True

    return branches


@click.command()
@click.argument("repo", required=False, default=None)
@click.option("--conf-file", default=None, help="Filepath for config file")
def main(repo, conf_file):
    """Get a list of stale branches for a repository.

    This is used for regular maintenance tasks.
    """

    if repo is None:
        config = nengo_bones.config.load_config(conf_file)
        repo = config["repo_name"]

    click.echo("Asking GitHub for information about %s..." % (repo,))
    stale_branches = get_stale_branches(repo)
    for branch, info in stale_branches.items():
        click.echo(
            "Branch {} is {:.1f} months old.".format(branch, info["age"].days / 30)
        )
        if info["open_pr"] is not None:
            click.echo("└─PR: {}".format(info["open_pr"]))


if __name__ == "__main__":
    main()  # pragma: no cover pylint: disable=no-value-for-parameter
