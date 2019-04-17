# pylint: disable=missing-docstring

"""
Note: in these tests we're just checking that the templates get rendered
correctly. The test that the scripts work functionally is implicit in
the ci scripts of this repository itself, which are generated by this code.
"""

import os
import sys

from click.testing import CliRunner
import pytest

from nengo_bones.version import version as bones_version
from nengo_bones.scripts import generate_bones
from nengo_bones.tests.utils import write_file, assert_exit


def test_ci_scripts(tmpdir):
    write_file(tmpdir, ".nengobones.yml", """
        pkg_name: dummy
        repo_name: dummy/dummy_repo

        ci_scripts:
          - template: base_script
            pip_install:
              - pip0
              - pip1
          - template: static
          - template: test
            nengo_tests: true
          - template: test
            coverage: true
            output_name: test-coverage
          - template: examples
            pre_commands:
              - pre command 0
              - pre command 1
            post_commands:
              - post command 0
              - post command 1
          - template: docs
          - template: deploy
    """)

    result = CliRunner().invoke(
        generate_bones.main,
        ["--conf-file", str(tmpdir.join(".nengobones.yml")),
         "--output-dir", str(tmpdir.join(".ci")),
         "ci-scripts"])

    assert_exit(result, 0)

    def has_line(filename, target, startswith=True):
        with open(str(tmpdir.join(filename))) as f:
            for line in f.readlines():
                line = line.strip()
                found = (line.startswith(target) if startswith
                         else line.endswith(target))
                if found:
                    return True
        return False

    assert has_line(".ci/base_script.sh", 'exe pip install "pip0" "pip1"')
    assert has_line(".ci/base_script.sh", "# Version: %s" % bones_version)

    assert has_line(".ci/static.sh", "exe pylint dummy --rcfile")

    assert has_line(".ci/test.sh", '--durations 20 $TEST_ARGS',
                    startswith=False)
    assert not has_line(
        ".ci/test.sh",
        '--cov=dummy --cov-append --cov-report=term-missing $TEST_ARGS',
        startswith=False)

    assert has_line(
        ".ci/test-coverage.sh",
        '--cov=dummy --cov-append --cov-report=term-missing $TEST_ARGS',
        startswith=False)

    assert has_line(".ci/examples.sh", "exe pre command 0")
    assert has_line(".ci/examples.sh", "exe pre command 1")
    assert has_line(".ci/examples.sh", "exe post command 0")
    assert has_line(".ci/examples.sh", "exe post command 1")

    assert has_line(
        ".ci/docs.sh",
        "exe git clone -b gh-pages-release "
        "https://github.com/dummy/dummy_repo.git ../dummy_repo-docs")

    assert has_line(
        ".ci/deploy.sh", 'exe python -c "from dummy import version')


@pytest.mark.xfail(sys.version_info < (3, 6, 0),
                   reason="Dictionary order non-deterministic pre 3.6")
def test_travis_yml(tmpdir):
    # minimal config, testing defaults
    write_file(tmpdir, ".nengobones.yml", """
            pkg_name: dummy
            repo_name: dummy/dummy_repo
            travis_yml:
              jobs:
                - thing: val
            """)

    result = CliRunner().invoke(
        generate_bones.main,
        ["--conf-file", str(tmpdir.join(".nengobones.yml")),
         "--output-dir", str(tmpdir),
         "travis-yml"])

    assert_exit(result, 0)

    with open(str(tmpdir.join(".travis.yml"))) as f:
        data = f.read()

    assert "# Version: %s" % bones_version in data
    assert "jobs:\n  include:\n  -\n    thing: val\n\nbefore_install" in data
    assert "stage: deploy" not in data

    # full config, testing all options
    write_file(tmpdir, ".nengobones.yml", """
        pkg_name: dummy
        repo_name: dummy/dummy_repo
        travis_yml:
          jobs:
            - script: job0
              test_args:
                arg0: val0
                arg1: val1
              python: 6.0
              coverage: true
            - script: job1
              coverage: false
          python: 5.0
          global_vars:
            global0: globval0
            global1: globval1
          pypi_user: myuser
          deploy_dists:
            - dist0
            - dist1
        """)

    result = CliRunner().invoke(
        generate_bones.main,
        ["--conf-file", str(tmpdir.join(".nengobones.yml")),
         "--output-dir", str(tmpdir),
         "travis-yml"])

    assert_exit(result, 0)

    with open(str(tmpdir.join(".travis.yml"))) as f:
        lines = [x.strip() for x in f.readlines()]

    def has_line(target):
        nonlocal lines

        while len(lines) > 0:
            line = lines.pop(0)

            if line.startswith(target):
                return True

        return False

    assert has_line("# Version: %s" % bones_version)

    assert has_line('python: 5.0')

    assert has_line('- GLOBAL0="globval0"')
    assert has_line('- GLOBAL1="globval1"')

    assert has_line('SCRIPT="job0"')
    assert has_line('python: 6.0')

    assert has_line('SCRIPT="job1"')

    assert has_line("- stage: deploy")
    assert has_line("user: myuser")
    assert has_line('distributions: "dist0 dist1 "')


def test_codecov_yml(tmpdir):
    write_file(tmpdir, ".nengobones.yml", """
        pkg_name: dummy
        repo_name: dummy/dummy_repo
        codecov_yml: {}
        """)

    result = CliRunner().invoke(
        generate_bones.main,
        ["--conf-file", str(tmpdir.join(".nengobones.yml")),
         "--output-dir", str(tmpdir),
         "codecov-yml"])
    assert_exit(result, 0)

    with open(str(tmpdir.join(".codecov.yml"))) as f:
        data = f.read()

    assert "!ci.appveyor.com" in data
    assert "target: auto" in data
    assert "target: 100%" in data

    write_file(tmpdir, ".nengobones.yml", """
            pkg_name: dummy
            repo_name: dummy/dummy_repo
            codecov_yml:
              skip_appveyor: false
              abs_target: abs
              diff_target: diff
            """)

    result = CliRunner().invoke(
        generate_bones.main,
        ["--conf-file", str(tmpdir.join(".nengobones.yml")),
         "--output-dir", str(tmpdir),
         "codecov-yml"])
    assert_exit(result, 0)

    with open(str(tmpdir.join(".codecov.yml"))) as f:
        data = f.read()

    assert "!ci.appveyor.com" not in data
    assert "target: abs" in data
    assert "target: diff" in data


def test_custom_template(tmpdir):
    write_file(tmpdir, "custom.sh.template", """
        {% extends "test.sh.template" %}

        {% block script %}
            {{ custom_msg }}
        {% endblock %}
        """)

    write_file(tmpdir, ".nengobones.yml", """
        pkg_name: dummy
        repo_name: dummy/dummy_repo

        ci_scripts:
          - template: custom
            custom_msg: this is a custom message
        """)

    result = CliRunner().invoke(
        generate_bones.main,
        ["--conf-file", str(tmpdir.join(".nengobones.yml")),
         "--output-dir", str(tmpdir), "--template-dir", str(tmpdir),
         "ci-scripts"])

    assert_exit(result, 0)

    with open(str(tmpdir.join("custom.sh"))) as f:
        data = f.read()

    assert "; then\n\n    this is a custom message\n\nelif" in data


def test_empty_codecov_yml(tmpdir):
    # minimal config, testing missing codecov_yml
    write_file(tmpdir, ".nengobones.yml", """
            pkg_name: dummy
            repo_name: dummy/dummy_repo
            travis_yml:
              jobs:
                - thing: val
            """)

    result = CliRunner().invoke(
        generate_bones.main,
        ["--conf-file", str(tmpdir.join(".nengobones.yml")),
         "--output-dir", str(tmpdir),
         "codecov-yml"])
    assert_exit(result, 1)

    assert str(result.exception) == "'codecov_yml'"


def test_empty_travis_yml(tmpdir):
    # minimal config, testing missing travis_yml
    write_file(tmpdir, ".nengobones.yml", """
            pkg_name: dummy
            repo_name: dummy/dummy_repo
            codecov_yml: {}
            """)

    result = CliRunner().invoke(
        generate_bones.main,
        ["--conf-file", str(tmpdir.join(".nengobones.yml")),
         "--output-dir", str(tmpdir),
         "travis-yml"])
    assert_exit(result, 1)

    assert str(result.exception) == "'travis_yml'"


def test_generate_all(tmpdir):
    file_configs = {".travis.yml": ("travis_yml", "\n  jobs: []"),
                    ".codecov.yml": ("codecov_yml", "{}")}

    nengo_yml = "pkg_name: dummy\nrepo_name: dummy/dummy_repo\n"

    for file_config in file_configs.values():
        nengo_yml += "%s: %s\n" % file_config

    write_file(tmpdir, ".nengobones.yml", nengo_yml)

    result = CliRunner().invoke(
        generate_bones.main,
        ["--conf-file", str(tmpdir.join(".nengobones.yml")),
         "--output-dir", str(tmpdir)])

    assert_exit(result, 0)

    for file_path in file_configs:
        assert os.path.exists(str(tmpdir.join(file_path)))
