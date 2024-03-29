# pylint: disable=missing-docstring

import os
from functools import partial

import pytest
from click.testing import CliRunner

from nengo_bones.scripts import pr_number
from nengo_bones.scripts.base import bones
from nengo_bones.tests.utils import assert_exit, make_has_line, write_file


def mocked_requests_get(url, repo=None, number=None, **_):
    """Used to mock out github requests so that we don't get timed out."""

    class MockResponse:
        def __init__(self, json_data):
            self.json_data = json_data

        def json(self):
            return self.json_data

    assert url == (f"https://api.github.com/repos/{repo}/issues?state=all&sort=created")

    return MockResponse([{"number": number}])


@pytest.mark.parametrize("mode", ("repo", "conf-default", "conf-arg"))
def test_pr_number(monkeypatch, tmp_path, mode):
    repo = f"a-repo/{mode}"

    monkeypatch.setattr(
        pr_number.requests,
        "get",
        partial(mocked_requests_get, repo=repo, number=len(mode)),
    )

    if mode != "repo":
        write_file(
            tmp_path=tmp_path,
            filename=".nengobones.yml",
            contents=f"""
            project_name: NengoBones
            pkg_name: nengo-bones
            repo_name: {repo}
            """,
        )

    if mode == "repo":
        result = CliRunner().invoke(bones, ["pr-number", repo])
    elif mode == "conf-arg":
        result = CliRunner().invoke(
            bones, ["pr-number", "--conf-file", str(tmp_path / ".nengobones.yml")]
        )
    else:
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = CliRunner().invoke(bones, ["pr-number"])
        finally:
            os.chdir(original_dir)

    assert_exit(result, 0)

    lines = result.output.split("\n")
    has_line = make_has_line(lines, regex=True)
    assert has_line(f"about {repo}\\.\\.\\.")
    assert has_line(f"assigned #{len(mode) + 1}")
