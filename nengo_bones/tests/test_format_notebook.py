# pylint: disable=missing-docstring

import os

from click.testing import CliRunner
import pytest

from nengo_bones.tests.utils import assert_exit


def check_notebook(nb_path):
    """Check that the notebook is perfectly clear"""
    # pylint: disable=import-outside-toplevel
    import nbformat

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

    # check whitespace at end of line
    no_whitespace = not any(
        line.endswith(" ") for cell in nb.cells for line in cell["source"].split("\n")
    )
    # newlines at end of cell (we eliminate all terminal newlines for markdown cells,
    # but code cells are expected to end with one newline)
    no_whitespace &= not any(
        cell["source"].endswith("\n" if cell.cell_type == "markdown" else "\n\n")
        for cell in nb.cells
    )

    # check empty cells are deleted
    not_empty = not any(cell["source"].strip() == "" for cell in nb.cells)

    return no_output, no_metadata, no_whitespace, not_empty


def test_format_notebook(tmpdir):
    # pylint: disable=import-outside-toplevel
    pytest.importorskip("IPython", minversion="3.0")
    pytest.importorskip("black")
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor
    from nengo_bones.scripts import format_notebook

    nb = nbformat.v4.new_notebook()
    nb["cells"] = [
        nbformat.v4.new_markdown_cell("""Title   \n\n"""),
        nbformat.v4.new_code_cell("""%dirs\nprint("foo")   \n\n"""),
        nbformat.v4.new_code_cell("  "),
    ]

    # run notebook to generate output
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    ep.preprocess(nb, {"metadata": {"path": str(tmpdir)}})

    # write these manually to make sure they get cleared
    nb["metadata"]["kernelspec"] = "dummy"
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

    # check that the notebooks are un-clear
    for path in paths:
        assert not any(check_notebook(path))

    # run the clear-notebook script on the whole directory
    result = CliRunner().invoke(format_notebook.main, [str(tmpdir), "--verbose"])
    assert_exit(result, 0)

    # check that all files were found
    for path in paths:
        assert path in result.output

    # check that the notebooks are now clear
    for path in paths:
        assert all(check_notebook(path))
