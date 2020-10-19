# pylint: disable=missing-docstring

"""
Note: in these tests we're just checking that the templates get rendered
correctly. The test that the scripts work functionally is implicit in
the ci scripts of this repository itself, which are generated by this code.
"""

import os

import pytest
from click.testing import CliRunner

from nengo_bones import all_files, all_sections
from nengo_bones.scripts import generate_bones
from nengo_bones.tests.utils import assert_exit, make_has_line, write_file


def test_ci_scripts(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dummy
        pkg_name: dummy
        repo_name: dummy/dummy_repo

        ci_scripts:
          - template: base_script
            pip_install:
              - pip0
              - pip1
          - template: static
            codespell_ignore_words:
              - onne
              - ttwo
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
          - template: remote-script
            remote_script: test
            output_name: remote-test
            azure_name: azure-name
            azure_group: azure-group
            coverage: true
          - template: remote-script
            remote_script: docs
            output_name: remote-docs
            remote_vars:
              remote_var: remote_val
    """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path / ".ci"),
            "ci-scripts",
        ],
    )

    assert_exit(result, 0)

    def has_line(filename, target, startswith=True):
        with (tmp_path / filename).open() as f:
            for line in f.readlines():
                line = line.strip()
                found = line.startswith(target) if startswith else line.endswith(target)
                if found:
                    return True
        return False

    assert has_line(".ci/base_script.sh", 'exe pip install "pip0" "pip1"')
    assert has_line(".ci/base_script.sh", "# Automatically generated by nengo-bones")

    assert has_line(".ci/static.sh", "exe pylint dummy")
    assert has_line(".ci/static.sh", '--ignore-words-list="onne,ttwo"')

    assert has_line(".ci/test.sh", "--durations 20 $TEST_ARGS", startswith=False)
    assert not has_line(
        ".ci/test.sh",
        "--cov=dummy --cov-report=term-missing $TEST_ARGS",
        startswith=False,
    )

    assert has_line(
        ".ci/test-coverage.sh",
        "--cov=dummy --cov-report=term-missing $TEST_ARGS",
        startswith=False,
    )

    assert has_line(".ci/examples.sh", "exe pre command 0")
    assert has_line(".ci/examples.sh", "exe pre command 1")
    assert has_line(".ci/examples.sh", "exe post command 0")
    assert has_line(".ci/examples.sh", "exe post command 1")

    assert has_line(
        ".ci/docs.sh",
        "exe git clone -b gh-pages-release "
        "https://github.com/dummy/dummy_repo.git ../dummy_repo-docs",
    )

    assert has_line(".ci/deploy.sh", 'exe python -c "from dummy import version')

    assert has_line(
        ".ci/remote-test.sh",
        "exe az vm start --resource-group azure-group --name azure-name",
    )
    assert has_line(".ci/remote-test.sh", "bash .ci/test.sh install")
    assert has_line(".ci/remote-test.sh", 'COVERAGE_FILE="tmp/dummy')

    assert has_line(".ci/remote-docs.sh", 'export remote_var="remote_val"')
    assert has_line(".ci/remote-docs.sh", "bash .ci/docs.sh install")
    assert has_line(".ci/remote-docs.sh", 'REMOTE_FAILED_FILE="tmp/dummy')


def test_travis_yml(tmp_path):
    # minimal config, testing defaults
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
            project_name: Dummy
            pkg_name: dummy
            repo_name: dummy/dummy_repo
            travis_yml:
              jobs:
                - thing: val
            """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "travis-yml",
        ],
    )

    assert_exit(result, 0)

    with (tmp_path / ".travis.yml").open() as f:
        data = f.read()

    assert "# Automatically generated by nengo-bones" in data
    assert "jobs:\n  include:\n  -\n    thing: val\n\nbefore_install" in data
    assert "stage: deploy" not in data

    # full config, testing all options
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dummy
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
        """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "travis-yml",
        ],
    )

    assert_exit(result, 0)

    with (tmp_path / ".travis.yml").open() as f:
        lines = f.readlines()

    has_line = make_has_line(lines, strip=True)

    assert has_line("# Automatically generated by nengo-bones")

    assert has_line("python: 5.0")

    assert has_line('- GLOBAL0="globval0"')
    assert has_line('- GLOBAL1="globval1"')

    assert has_line('SCRIPT="job0"')
    assert has_line("python: 6.0")

    assert has_line('SCRIPT="job1"')

    assert has_line("- stage: deploy")
    assert has_line("user: myuser")
    assert has_line('distributions: "dist0 dist1 "')


def test_codecov_yml(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dummy
        pkg_name: dummy
        repo_name: dummy/dummy_repo
        codecov_yml: {}
        """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "codecov-yml",
        ],
    )
    assert_exit(result, 0)

    with (tmp_path / ".codecov.yml").open() as f:
        data = f.read()

    assert "!ci.appveyor.com" in data
    assert "target: auto" in data
    assert "target: 100%" in data

    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
            project_name: Dummy
            pkg_name: dummy
            repo_name: dummy/dummy_repo
            codecov_yml:
              skip_appveyor: false
              abs_target: abs
              diff_target: diff
            """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "codecov-yml",
        ],
    )
    assert_exit(result, 0)

    with (tmp_path / ".codecov.yml").open() as f:
        data = f.read()

    assert "!ci.appveyor.com" not in data
    assert "target: abs" in data
    assert "target: diff" in data


def test_ci_script_custom_template(tmp_path):
    (tmp_path / ".templates").mkdir()
    write_file(
        tmp_path=tmp_path / ".templates",
        filename="custom.sh.template",
        contents="""
        {% extends "templates/test.sh.template" %}

        {% block script %}
            {{ custom_msg }}
        {% endblock %}
        """,
    )

    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dummy
        pkg_name: dummy
        repo_name: dummy/dummy_repo

        ci_scripts:
          - template: custom
            custom_msg: this is a custom message
        """,
    )

    try:
        saved = os.getcwd()
        os.chdir(tmp_path)
        result = CliRunner().invoke(generate_bones.main, ["ci-scripts"])
    finally:
        os.chdir(saved)

    assert_exit(result, 0)

    with (tmp_path / "custom.sh").open() as f:
        data = f.read()

    assert "; then\n\n    this is a custom message\n\nelif" in data


@pytest.mark.parametrize("license_type", ["nengo", "mit"])
def test_license(tmp_path, license_type):
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dumdum
        pkg_name: dummy
        repo_name: dummy_org/dummy
        copyright_start: 2014
        copyright_end: 2017
        license_rst:
          type: %(license_type)s
    """
        % dict(license_type=license_type, tmp_path=tmp_path),
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "license-rst",
        ],
    )
    assert_exit(result, 0)

    with (tmp_path / "LICENSE.rst").open() as f:
        lines = f.readlines()

    has_line = make_has_line(lines)

    assert has_line(".. Automatically generated by nengo-bones")

    assert has_line("Dumdum license")
    if license_type == "mit":
        assert has_line("MIT License")

    assert has_line("Copyright (c) 2014-2017")
    if license_type == "nengo":
        assert has_line("Dumdum is made available under a proprietary license")


def test_contributing(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dumdum
        pkg_name: dummy
        repo_name: dummy_org/dummy
        contributing_rst: {}
    """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "contributing-rst",
        ],
    )
    assert_exit(result, 0)

    lines = (tmp_path / "CONTRIBUTING.rst").read_text().split("\n")

    has_line = make_has_line(lines)

    assert has_line(".. Automatically generated by nengo-bones")
    assert has_line("Contributing to Dumdum")
    assert has_line("`filing an issue <https://github.com/dummy_org/dummy/issues>`_!")


def test_contributors(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dumdum
        pkg_name: dummy
        repo_name: dummy_org/dummy
        contributors_rst: {}
    """,
    )

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

    with (tmp_path / "CONTRIBUTORS.rst").open() as f:
        lines = f.readlines()

    has_line = make_has_line(lines)
    assert has_line(".. Automatically generated by nengo-bones")
    assert has_line("Dumdum contributors")


def test_manifest(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dummy
        pkg_name: dummy
        repo_name: dummy_org/dummy
        manifest_in:
            graft:
              - this-folder
              - that-folder
            recursive-exclude:
              - "*.bak"
    """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "manifest-in",
        ],
    )
    assert_exit(result, 0)

    with (tmp_path / "MANIFEST.in").open() as f:
        lines = f.readlines()

    has_line = make_has_line(lines)
    assert has_line("# Automatically generated by nengo-bones")
    assert has_line("graft this-folder")
    assert has_line("graft that-folder")
    assert has_line("recursive-exclude *.bak")


def test_setup_py(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dummy
        pkg_name: dummy
        repo_name: dummy_org/dummy
        setup_py:
          description: My project description
          python_require: ">=3.6"
          install_req:
            - numpy>=1.11
            - pkg2<8
          docs_req:
            - pkg1>=3
          package_data:
            dummy:
              - dummy-data/file1
            other:
              - other-data/file2
              - other-data/file3
          entry_points:
            point.a:
              - "a = b"
              - "c = d"
          classifiers:
            - "Classifier :: 1"
            - "ClassifierTwo :: B"
    """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "setup-py",
        ],
    )
    assert_exit(result, 0)

    with (tmp_path / "setup.py").open() as f:
        lines = f.readlines()

    has_line = make_has_line(lines)
    assert has_line("# Automatically generated by nengo-bones")
    assert has_line("install_req = [")
    assert has_line('    "numpy>=1.11",')
    assert has_line("docs_req = [")
    assert has_line('    "pkg1>=3"')
    assert has_line("setup(")
    assert has_line("    package_data={")
    assert has_line('        "dummy": [')
    assert has_line('            "dummy-data/file1",')
    assert has_line('        "other": [')
    assert has_line('            "other-data/file2",')
    assert has_line('            "other-data/file3",')
    assert has_line("    entry_points={")
    assert has_line('        "point.a": [')
    assert has_line('            "a = b",')
    assert has_line('            "c = d",')
    assert has_line("    classifiers=[")
    assert has_line('        "Classifier :: 1",')
    assert has_line('        "ClassifierTwo :: B",')


def test_setup_cfg(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dummy
        pkg_name: dummy
        repo_name: dummy_org/dummy
        setup_cfg:
          coverage:
            exclude_lines:
              - "extra-exclude-pattern*"
            omit_files:
              - "dummy/tests/*"
              - "dummy/other/*"
          flake8:
            ignore:
              - E123
              - E226
              - E133
          pytest:
            norecursedirs:
              - dummy/_vendor
            markers:
              mymarker:
                  foobar
            filterwarnings:
              - "ignore:hello:DeprecationWarning"
            allclose_tolerances:
              - "test_something.py::test_something atol=0.01  # comment"
          pylint:
            ignore:
              - zz-some-file.py
            disable:
              - zz-some-thing
            known_third_party:
              - zz-my-third-party
    """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "setup-cfg",
        ],
    )
    assert_exit(result, 0)

    with (tmp_path / "setup.cfg").open() as f:
        lines = f.readlines()

    has_line = make_has_line(lines)
    assert has_line("# Automatically generated by nengo-bones")
    assert has_line("[coverage:report]")
    assert has_line("exclude_lines =")
    assert has_line("    extra-exclude-pattern*")
    assert has_line("omit =")
    assert has_line("    dummy/tests/*")
    assert has_line("    dummy/other/*")
    assert has_line("[flake8]")
    assert has_line("ignore =")
    assert has_line("    E123")
    assert has_line("    E226")
    assert has_line("    E133")
    assert has_line("[tool:pytest]")
    assert has_line("norecursedirs =")
    assert has_line("    dummy/_vendor")
    assert has_line("markers =")
    assert has_line("    mymarker: foobar")
    assert has_line("filterwarnings =")
    assert has_line("    ignore:hello:DeprecationWarning")
    assert has_line("allclose_tolerances =")
    assert has_line("    test_something.py::test_something atol=0.01  # comment")
    assert has_line("[pylint]")
    assert has_line("ignore =")
    assert has_line("    zz-some-file.py")
    assert has_line("disable =")
    assert has_line("    zz-some-thing")
    assert has_line("known-third-party =")
    assert has_line("    zz-my-third-party")


def test_setup_cfg_valueerror(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        pkg_name: dummy
        repo_name: dummy_org/dummy
        setup_cfg:
          pylint_ignore: compat.py
    """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "setup-cfg",
        ],
    )
    assert_exit(result, 1)


def test_setup_cfg_custom_marker(pytestconfig):
    # this marker is added in the setup.cfg file
    assert "test-marker: Not a real marker" in pytestconfig.getini("markers")


def test_docs_conf_py(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dummy
        pkg_name: dummy
        repo_name: dummy_org/dummy
        docs_conf_py:
            intersphinx_mapping: {}
    """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "docs-conf-py",
        ],
    )
    assert_exit(result, 0)

    with (tmp_path / "docs" / "conf.py").open() as f:
        lines = f.readlines()

    has_line = make_has_line(lines)
    assert has_line("# Automatically generated by nengo-bones")


def test_docs_conf_py_tagmanager_id_warn(tmp_path):
    def test_nengobones_file(tagmanager_id):
        write_file(
            tmp_path=tmp_path,
            filename=".nengobones.yml",
            contents="""
            project_name: Dummy
            pkg_name: dummy
            repo_name: dummy_org/dummy
            docs_conf_py:
                tagmanager_id: %s
        """
            % (tagmanager_id,),
        )

        result = CliRunner().invoke(
            generate_bones.main,
            [
                "--conf-file",
                str(tmp_path / ".nengobones.yml"),
                "--output-dir",
                str(tmp_path),
                "docs-conf-py",
            ],
        )
        assert_exit(result, 0)

    with pytest.warns(None) as recwarns:
        test_nengobones_file("GTM-ABCDEFG")
    assert not any("tagmanager_id" in str(w.message) for w in recwarns)

    with pytest.warns(UserWarning, match="'tagmanager_id' looks strange"):
        test_nengobones_file("GTM-ABCDEFGH")

    with pytest.warns(UserWarning, match="'tagmanager_id' looks strange"):
        test_nengobones_file("GTK-ABCDEFG")


def test_empty_travis_yml(tmp_path):
    # minimal config, testing missing travis_yml
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
            project_name: Dummy
            pkg_name: dummy
            repo_name: dummy/dummy_repo
            """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
            "travis-yml",
        ],
    )
    assert_exit(result, 0)

    assert "No config entry detected for travis_yml" in result.output

    assert not (tmp_path / ".travis.yml").exists()


def test_generate_all(tmp_path):
    nengo_yml = "project_name: Dummy\npkg_name: dummy\nrepo_name: dummy/dummy_repo\n"

    for configname in all_sections:
        nengo_yml += f"{configname}:"
        nengo_yml += "\n  jobs: []" if configname == "travis_yml" else " {}"
        nengo_yml += "\n"

    write_file(tmp_path=tmp_path, filename=".nengobones.yml", contents=nengo_yml)

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert_exit(result, 0)

    for file_path in all_files:
        assert (tmp_path / file_path).exists()


def test_generate_none(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename=".nengobones.yml",
        contents="""
        project_name: Dummy
        pkg_name: dummy
        repo_name: dummy_org/dummy
    """,
    )

    result = CliRunner().invoke(
        generate_bones.main,
        [
            "--conf-file",
            str(tmp_path / ".nengobones.yml"),
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert_exit(result, 0)

    for file_path in all_files:
        assert not (tmp_path / file_path).exists()
