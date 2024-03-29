"""Applies validation to auto-generated files."""

import difflib
import sys
from pathlib import Path

import click

from nengo_bones import __version__, all_files
from nengo_bones.config import load_config
from nengo_bones.scripts import check_notice
from nengo_bones.scripts.base import bones
from nengo_bones.templates import BonesTemplate, load_env


def _check_file(filename, *, config, env, path, verbose):
    full_filename = filename.replace("pkg", config["pkg_name"])
    click.echo(full_filename + ":")

    # TODO: Ensure that the file is there <=> it is in the config
    if not (path / full_filename).exists():
        click.echo("  File not found")
        return True

    with (path / full_filename).open(encoding="utf-8") as f:
        current_lines = f.readlines()

    for line in current_lines[:50]:
        if "Automatically generated by nengo-bones" in line:
            break
    else:
        click.echo("  This file was not generated with nengo-bones")
        return True

    template = BonesTemplate(filename, env)
    if template.section not in config:
        click.secho(
            "  This file contains 'Automatically generated by nengo-bones',\n"
            "  but there is no corresponding configuration in .nengobones.yml.\n"
            "  Please remove this text or configure it in .nengobones.yml.",
            fg="red",
        )
        return False

    new_lines = template.render(**template.get_render_data(config)).splitlines(
        keepends=True
    )

    # Strip out ignored lines
    current_lines = [line for line in current_lines if "# bones: ignore" not in line]
    new_lines = [line for line in new_lines if "# bones: ignore" not in line]

    diff = list(
        difflib.unified_diff(
            current_lines,
            new_lines,
            fromfile=f"current {filename}",
            tofile=f"new {filename}",
        )
    )

    if len(diff) > 0:
        click.secho(
            f"  Content does not match nengo-bones (version {__version__});\n"
            "  please update by running `bones generate` from\n"
            "  the root directory.",
            fg="red",
        )
        if verbose:
            click.echo("\n  Full diff")
            click.echo("  =========")
            for line in diff:
                click.echo(f"  {line.rstrip()}")
        return False
    else:
        click.secho("  Up to date", fg="green")
    return True


@bones.command(name="check")
@click.option(
    "--root-dir", default=".", help="Directory containing files to be checked"
)
@click.option("--conf-file", default=None, help="Filepath for config file")
@click.option(
    "--verbose", is_flag=True, help="Show more information about failed checks."
)
def main(root_dir, conf_file, verbose):
    """
    Validates auto-generated project files.

    Note: This does not check the ci scripts, because those are generated
    on-the-fly during CI (so any ci files we do find are likely local artifacts).
    """

    config = load_config(conf_file)
    env = load_env()
    path = Path(root_dir)

    click.echo("*" * 50)
    click.echo("Checking content of nengo-bones generated files:")
    click.echo(f"root dir: {root_dir}\n")
    passed = [
        _check_file(filename, config=config, env=env, path=path, verbose=verbose)
        for filename in all_files
    ]

    if "license_rst" in config and config["license_rst"]["add_to_files"]:
        _, missing = check_notice.check_notice(path, config["license_rst"]["text"])
        passed.append(missing == 0)

    click.echo("*" * 50)

    if not all(passed):
        sys.exit(1)
