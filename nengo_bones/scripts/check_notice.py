"""Checks that license text is added to all .py files."""

import re

import click

from nengo_bones.templates import add_notice


def check_notice(root, text, fix=False, verbose=False, exclude=None):
    """
    Check for license notices in all .py files.

    Parameters
    ----------
    root : Path
        Root directory to search within.
    text : str
        License text that should be in files.
    fix : bool
        Add the notice to any file that is missing one.
    verbose : bool
        Print the name of all files checked.
    exclude : list of str
        Regex patterns for files to exclude from checking.

    Returns
    -------
    checked : int
        Number of files checked.
    missing: int
        Number of files missing a notice.
    """

    click.echo("Checking for license text in python files:")

    checked = 0
    missing = 0
    for path in root.rglob("*.py"):
        if exclude is not None and any(
            re.search(p, str(path)) is not None for p in exclude
        ):
            continue

        checked += 1
        current_text = path.read_text()

        modified = add_notice(text, current_text)

        if modified[: len(text)] != current_text[: len(text)]:
            missing += 1
            if fix:
                path.write_text(modified)
                click.secho(f"Fixed: {path}", fg="yellow")
            else:
                click.secho(f"Missing: {path}", fg="red")
        elif verbose:
            click.secho(f"Present: {path}", fg="green")

    if missing == 0:
        click.secho("  Up to date", fg="green")

    return checked, missing
