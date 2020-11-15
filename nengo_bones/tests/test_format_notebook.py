# pylint: disable=missing-docstring

import os
import re
import sys

import nbformat
import pytest
from click.testing import CliRunner
from nbconvert.preprocessors import ExecutePreprocessor

from nengo_bones.scripts import format_notebook
from nengo_bones.tests.utils import assert_exit


def check_notebook(nb_path, correct):
    """Check that the notebook is perfectly clear and contains the expected content."""

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # check no outputs
    no_output = True
    for cell in nb.cells:
        no_output &= getattr(cell, "outputs", []) == []
        no_output &= getattr(cell, "execution_count", None) is None
        no_output &= "collapsed" not in cell

    # check minimal metadata
    no_metadata = True
    no_metadata &= "kernelspec" not in nb.metadata
    no_metadata &= "signature" not in nb.metadata

    badinfo = (
        "codemirror_mode",
        "file_extension",
        "mimetype",
        "nbconvert_exporter",
        "version",
    )
    for info in badinfo:
        no_metadata &= info not in nb.metadata.language_info

    # check that content matches expected content
    content_match = [cell["source"] for cell in nb.cells] == correct

    return no_output, no_metadata, content_match


def test_format_notebook(tmpdir):
    nb = nbformat.v4.new_notebook()
    nb["cells"] = [
        nbformat.v4.new_markdown_cell("Title   \n\nserach\n\n"),
        nbformat.v4.new_code_cell("%dirs\nprint('foo')   \n# coment\n\n"),
        nbformat.v4.new_code_cell("  "),
        nbformat.v4.new_markdown_cell(
            "this is a long line that should wrap aaaaaaaaaaaaaaaaaaaaaaa "
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        ),
    ]

    # this should be the content of the cells after formatting
    correct = [
        "Title\n\nserach",
        "%dirs\n"
        + ('print("foo")' if format_notebook.HAS_BLACK else "print('foo')   ")
        + "\n# coment",
        "this is a long line that should wrap aaaaaaaaaaaaaaaaaaaaaaa\n"
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    ]

    # run notebook to generate output
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    ep.preprocess(nb, {"metadata": {"path": str(tmpdir)}})

    # write these manually to make sure they get cleared
    nb["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb["cells"][1]["execution_count"] = 3
    nb["cells"][1]["metadata"]["collapsed"] = True

    # write notebooks (put one in subdir to check we clear dirs properly)
    os.mkdir(str(tmpdir.join("subdir")))
    paths = [
        str(tmpdir.join("test1.ipynb")),
        str(tmpdir.join("subdir").join("test2.ipynb")),
    ]
    for path in paths:
        with open(path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)

    # check that the notebooks are not formatted
    for path in paths:
        assert not any(check_notebook(path, correct))

    # verify that --check correctly detects that notebooks are not formatted
    with pytest.warns(None) as recwarns:
        result = CliRunner().invoke(
            format_notebook.main, [str(tmpdir), "--check", "--verbose"]
        )

    if sys.version_info < (3, 6, 0):
        assert any(
            "bones-format-notebook requires Python>=3.6" in str(w.message)
            for w in recwarns
        )
        return

    assert_exit(result, 1)
    assert '-    "Title   \\n",\n+    "Title\\n",' in result.output

    # run the clear-notebook script on the whole directory
    result = CliRunner().invoke(format_notebook.main, [str(tmpdir), "--verbose"])
    assert_exit(result, 0)

    # check that all files were found
    for path in paths:
        assert path in result.output

    # check that spelling errors were detected/corrected
    assert "search" in result.output
    assert "comment" in result.output

    # check that the notebooks are now formatted
    for path in paths:
        assert all(check_notebook(path, correct))

    # verify that --check correctly detects that notebooks are now formatted
    result = CliRunner().invoke(format_notebook.main, [str(tmpdir), "--check"])
    assert_exit(result, 0)


@pytest.mark.xfail(
    not format_notebook.HAS_PRETTIER,
    reason="prettier not installed",
)
@pytest.mark.skipif(
    sys.version_info < (3, 6, 0), reason="format-notebook requires Python>=3.6"
)
def test_format_notebook_prettier(tmpdir):
    nb = nbformat.v4.new_notebook()
    nb["cells"] = [
        nbformat.v4.new_markdown_cell("prettier\nwill\nunwrap\nthese\nlines"),
    ]

    nb_path = str(tmpdir.join("test.ipynb"))
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    result = CliRunner().invoke(
        format_notebook.main, [str(tmpdir), "--verbose", "--prettier"]
    )
    assert_exit(result, 0)

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    assert nb.cells[0]["source"] == "prettier will unwrap these lines"


def test_format_notebook_noprettier_error(tmpdir, monkeypatch):
    monkeypatch.setattr(format_notebook, "HAS_PRETTIER", False)

    result = CliRunner().invoke(format_notebook.main, [str(tmpdir), "--prettier"])
    assert_exit(result, 1)
    assert isinstance(result.exception, ValueError) and (
        re.match("Cannot format.*Prettier.*not installed", str(result.exception))
    )


@pytest.mark.skipif(
    sys.version_info < (3, 6, 0), reason="format-notebook requires Python>=3.6"
)
def test_format_notebook_static(tmpdir):
    nb = nbformat.v4.new_notebook()
    nb["cells"] = [
        nbformat.v4.new_code_cell("def test(): a = b"),
    ]

    with open(str(tmpdir.join("test.ipynb")), "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    result = CliRunner().invoke(format_notebook.main, [str(tmpdir), "--verbose"])
    assert_exit(result, 1)

    # check that pylint/flake8 errors were detected
    assert "undefined-variable" in result.output  # pylint
    assert "F821" in result.output  # flake8


def test_format_dir_ignore(tmpdir):
    rootdir = tmpdir.mkdir("rootdir")
    rootdir.mkdir("_build")
    rootdir.mkdir("my.ipynb_checkpoints")
    rootdir.mkdir("format_this_dir")
    result = CliRunner().invoke(format_notebook.main, [str(rootdir)])
    assert re.search("Ignoring directory '[^']*_build'", result.output)
    assert re.search(r"Ignoring directory '[^']*my\.ipynb_checkpoints'", result.output)
    assert not re.search(r"Ignoring directory '[^']*format_this_dir'", result.output)
