"""Applies standard formatting to Jupyter Notebook (.ipynb) files."""

import os
import re
import subprocess

import black
import click
import nbformat


def format_notebook(nb):
    """Formats an opened Jupyter notebook."""

    # --- Remove bad metadata
    # Should pass `nengo/tests/test_examples.py:test_minimal_metadata`
    if "kernelspec" in nb.metadata:
        del nb.metadata["kernelspec"]

    language_info = getattr(nb.metadata, "language_info", {})
    badinfo = (
        "codemirror_mode",
        "file_extension",
        "mimetype",
        "nbconvert_exporter",
        "version",
    )
    for badkey in badinfo:
        if badkey in language_info:
            del language_info[badkey]

    # --- Clean up cells
    worksheets = nb.worksheets if hasattr(nb, "worksheets") else [nb]
    for ws in worksheets:
        empty = []  # empty cells

        for cell in ws.cells:
            source = getattr(cell, "source", None)

            if source is not None and len(source.strip()) == 0:
                empty.append(cell)
                continue

            if cell.cell_type == "code":
                format_code(cell)
            elif cell.cell_type == "markdown":
                format_markdown(cell)

        # remove empty cells
        for cell in empty:
            ws.cells.remove(cell)


def format_code(cell):
    """Format a code cell."""

    # format with black
    cell["source"] = apply_black(cell["source"])

    # remove any output (print statements, plots, etc.)
    cell.outputs = []

    # reset cell execution number
    cell["execution_count"] = None

    # clear useless metadata
    clear_cell_metadata_entry(cell, "collapsed")
    clear_cell_metadata_entry(cell, "deletable", value=True)
    clear_cell_metadata_entry(cell, "editable", value=True)

    # check with codespell
    apply_codespell(cell["source"])


def format_markdown(cell):
    """Format a markdown cell."""

    # clear useless metadata
    clear_cell_metadata_entry(cell, "deletable", value=True)
    clear_cell_metadata_entry(cell, "editable", value=True)

    # remove empty lines from the end
    cell["source"] = cell["source"].rstrip()

    # clear whitespace at ends of lines
    source = getattr(cell, "source", None)
    if source is not None and len(source) > 0:
        assert isinstance(source, str)
        cell["source"] = "\n".join(line.rstrip(" ") for line in source.split("\n"))

    # check with codespell
    apply_codespell(cell["source"])


def apply_black(source):
    """
    Apply black formatting to a cell.

    Parameters
    ----------
    source : str
        Content of cell.

    Returns
    -------
    source : str
        Formatted cell contents.
    """
    # if we have any IPython magic functions (starting with % or !),
    # replace them temporarily (black can't handle them)
    magic_re = re.compile(r"^(\s*)([%!][A-Za-z]+.*)$", flags=re.MULTILINE)

    # go through matches backwards so that subbing doesn't change inds
    magic_pairs = []
    matches = list(magic_re.finditer(source))
    assert len(matches) < 10000, "Too many magic matches"

    for i, match in enumerate(matches[::-1]):
        space, magic = match.groups("")

        replacement = "# MaGiC%04d" % i
        magic_pairs.append((magic, replacement))
        source = source[: match.start(1)] + space + replacement + source[match.end(2) :]

    # run black
    source = black.format_str(source, mode=black.FileMode())

    # put magic functions back
    for magic, replacement in magic_pairs:
        assert replacement in source, "Magic identifier disappeared"
        source = source.replace(replacement, magic)

    return source


def apply_codespell(source):
    """Use codespell to check spelling in a cell.

    Note: this simply prints any potential spelling mistakes to stdout for the user
    to manually verify (since trying to automatically correct them seems too unsafe).

    Parameters
    ----------
    source : str
        Content of cell.
    """
    result = subprocess.run(
        "codespell -",
        input=source,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        check=False,
    )
    if result.returncode != 0:
        print("Potential spelling mistakes detected:")
        print(result.stdout)


def clear_cell_metadata_entry(cell, key, value="_ANY_"):
    """Remove metadata entry from a cell

    Parameters
    ----------
    cell : cell
        Cell to remove the entry from.
    key : string
        The metadata entry to remove.
    value : object (optional)
        If set, only remove the entry if its value equals ``value``. Defaults
        to removing the entry no matter its value.
    """
    metadata = cell["metadata"]
    if key in metadata and value in ("_ANY_", metadata[key]):
        del metadata[key]


def clear_file(fname, target_version=4, verbose=False):
    """Clear outputs and metadata from an unopened Jupyter notebook."""

    with open(fname, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    format_notebook(nb)

    with open(fname, "w", encoding="utf-8") as f:
        nbformat.write(nb, f, version=target_version)

    if verbose:
        print("wrote %s" % fname)


def clear_dir(dname, **kwargs):
    """Clear all notebooks in a directory."""

    assert os.path.isdir(dname)
    fnames = os.listdir(dname)
    fpaths = [
        os.path.join(dname, fname) for fname in fnames if not fname.startswith(".")
    ]
    clear_paths(
        [fpath for fpath in fpaths if os.path.isdir(fpath) or fpath.endswith(".ipynb")],
        **kwargs,
    )


def clear_paths(fnames, **kwargs):
    """Clear all notebooks in list of notebook files and directories."""

    for fname in fnames:
        if os.path.isdir(fname):
            clear_dir(fname, **kwargs)
        else:
            clear_file(fname, **kwargs)


@click.command()
@click.argument("files", required=True, nargs=-1)
@click.option("--target-version", default=4, help="Version of notebook format to save.")
@click.option(
    "--verbose/--no-verbose", default=False, help="Enable/disable verbose output."
)
def main(files, **kwargs):
    """
    Clears the output and extra metadata of Jupyter Notebook (.ipynb) files.
    """
    clear_paths(files, **kwargs)
