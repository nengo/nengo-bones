"""Applies standard formatting to Jupyter Notebook (.ipynb) files."""

import difflib
import pathlib
import re
import subprocess
import sys
import textwrap

import black
import click
import nbformat

from nengo_bones.scripts.base import bones

HAS_PRETTIER = (
    subprocess.run(
        "npx --no-install --quiet prettier --version ",
        shell=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).returncode
    == 0
)


def format_notebook(nb, fname, verbose=False, prettier=None):  # noqa: C901
    """Formats an opened Jupyter notebook."""

    if verbose:
        click.echo(f"Formatting '{fname}'")

    passed = True

    # --- Remove bad metadata
    # Should pass `nengo/tests/test_examples.py:test_minimal_metadata`
    badmeta = ["kernelspec", "widgets"]
    for badkey in badmeta:
        if badkey in nb.metadata:
            del nb.metadata[badkey]

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
    empty = []  # empty cells
    all_code = []  # code cells
    all_markdown = []  # markdown cells

    for cell in nb.cells:
        source = getattr(cell, "source", None)

        if source is not None and len(source.strip()) == 0:
            empty.append(cell)
            continue

        if cell.cell_type == "code":
            format_code(cell)
            all_code.append(cell)
        elif cell.cell_type == "markdown":
            format_markdown(cell, prettier=prettier)
            all_markdown.append(cell)

        # remove empty lines from the end
        cell["source"] = cell["source"].rstrip()

    # remove empty cells
    for cell in empty:
        nb.cells.remove(cell)

    # static checks needs to see the whole file, so we call them on all the code cells
    # together at the end
    passed &= apply_static_checker(
        "pylint --from-stdin "
        "--disable=missing-docstring,trailing-whitespace,wrong-import-position,"
        f"unnecessary-semicolon,missing-final-newline {fname}",
        all_code,
    )
    passed &= apply_static_checker(
        "flake8 --extend-ignore=E402,E703,W291,W292,W293,W391 "
        f"--stdin-display-name={fname} --show-source -",
        all_code,
    )
    passed &= apply_static_checker(
        "codespell -",
        all_markdown + all_code,
    )

    return passed


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
    clear_cell_metadata_entry(cell, "scrolled")
    clear_cell_metadata_entry(cell, "deletable", value=True)
    clear_cell_metadata_entry(cell, "editable", value=True)
    clear_cell_metadata_entry(cell, "pycharm")


def format_markdown(cell, prettier=None):
    """Format a markdown cell."""

    # clear useless metadata
    clear_cell_metadata_entry(cell, "deletable", value=True)
    clear_cell_metadata_entry(cell, "editable", value=True)
    clear_cell_metadata_entry(cell, "pycharm")

    # clear whitespace at ends of lines
    source = getattr(cell, "source", None)
    if source is not None and len(source) > 0:
        assert isinstance(source, str)
        cell["source"] = "\n".join(line.rstrip(" ") for line in source.split("\n"))

    # apply prettier
    if prettier:
        cell["source"] = run_command(
            "npx prettier --parser markdown --print-width 88 --prose-wrap always",
            cell["source"],
        ).stdout

    # apply text wrapping
    wrapper = textwrap.TextWrapper(
        width=88,
        tabsize=4,
        break_long_words=False,
        break_on_hyphens=False,
        replace_whitespace=False,
        drop_whitespace=True,
    )
    cell["source"] = "\n".join(
        wrapper.fill(line) for line in cell["source"].splitlines()
    )


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

        replacement = f"# MaGiC{i:04d}"
        magic_pairs.append((magic, replacement))
        source = source[: match.start(1)] + space + replacement + source[match.end(2) :]

    # run black
    source = black.format_str(source, mode=black.FileMode())

    # put magic functions back
    for magic, replacement in magic_pairs:
        assert replacement in source, "Magic identifier disappeared"
        source = source.replace(replacement, magic)

    return source


def run_command(command, inputs):
    """
    Run a command in external shell with input piped from string.

    Parameters
    ----------
    command : str
        Shell command to be executed.
    inputs : str
        Input that will be piped to command through stdin.

    Returns
    -------
    result : `subprocess.CompletedProcess`
        Object containing results of executing shell command.
    """

    return subprocess.run(
        command,
        input=inputs,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        check=False,
    )


def apply_static_checker(command, cells):
    """
    Apply static checks to code in cells.

    Parameters
    ----------
    command : str
        Command line code to be executed on content of cells.
    cells : list
        List of notebook code cells.

    Returns
    -------
    passed : bool
        True if static checks passed, else False
    """

    def sanitize(source):
        return "\n".join(
            line
            for line in source.splitlines()
            if not line.startswith("%") and not line.startswith("!")
        )

    # note: we put two blank lines between each cell so that cells that
    # begin/end with a function/class definition will have the right whitespace
    # when concatenated
    all_source = "\n\n\n".join(sanitize(c["source"]) for c in cells)

    result = run_command(command, all_source)

    if result.returncode != 0:
        click.echo(f"{command.split()[0]} errors detected:")
        click.echo(result.stdout)

    return result.returncode == 0


def clear_cell_metadata_entry(cell, key, value="_ANY_"):
    """
    Remove metadata entry from a cell.

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


def format_file(fname, target_version=4, verbose=False, check=False, prettier=None):
    """Formats a file containing a Jupyter notebook."""

    with open(fname, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    if check:
        current = nbformat.writes(nb).splitlines()

    passed = format_notebook(nb, fname, verbose=verbose, prettier=prettier)

    if check:
        diff = list(
            difflib.unified_diff(
                current,
                nbformat.writes(nb).splitlines(),
                fromfile=f"current {fname}",
                tofile=f"new {fname}",
            )
        )

        if len(diff) > 0:
            click.secho(
                f"{fname} has not been formatted; please run `bones format-notebook`",
                fg="red",
            )
            if verbose:
                click.echo("\nFull diff")
                click.echo("=========")
                for line in diff:
                    click.echo(line.strip("\n"))
            passed = False
    else:
        with open(fname, "w", encoding="utf-8") as f:
            nbformat.write(nb, f, version=target_version)

    return passed


def format_dir(dname, **kwargs):
    """Format all notebooks in a directory."""

    assert dname.is_dir()
    str_dname = str(dname)
    if str_dname.endswith(".ipynb_checkpoints") or str_dname.endswith("_build"):
        click.echo(f"Ignoring directory '{dname}'")
        return True

    return format_paths(
        [
            fpath
            for fpath in dname.glob("[!.]*")
            if fpath.is_dir() or fpath.suffix == ".ipynb"
        ],
        **kwargs,
    )


def format_paths(fnames, **kwargs):
    """Format all notebooks in list of notebook files and directories."""

    passed = True

    for fname in fnames:
        fname = pathlib.Path(fname)
        if fname.is_dir():
            passed &= format_dir(fname, **kwargs)
        else:
            passed &= format_file(fname, **kwargs)

    return passed


@bones.command(name="format-notebook")
@click.argument("files", required=True, nargs=-1)
@click.option("--target-version", default=4, help="Version of notebook format to save.")
@click.option(
    "--verbose/--no-verbose", default=False, help="Enable/disable verbose output."
)
@click.option(
    "--check/--no-check",
    default=False,
    help="Check that notebook is already formatted instead of modifying content.",
)
@click.option(
    "--prettier/--no-prettier",
    default=False,
    help="Enable/disable markdown cell formatting with Prettier.",
)
def main(files, **kwargs):
    """Apply standardized formatting to Jupyter notebooks."""

    if kwargs["prettier"] and not HAS_PRETTIER:
        # user explicitly asked for prettier, but it is not installed, so fail
        raise ValueError("Cannot format markdown with Prettier; it is not installed.")

    passed = format_paths(files, **kwargs)

    if not passed:
        sys.exit(1)
