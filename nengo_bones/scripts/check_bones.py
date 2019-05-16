"""Applies validation to auto-generated files."""

import os
import sys

import click

import nengo_bones


@click.command()
@click.option("--root-dir", default=".",
              help="Directory containing files to be checked")
def main(root_dir):
    """
    Validates auto-generated project files.

    Note: This does not check the ci scripts, because those are generated
    on-the-fly in TravisCI (so any ci files we do find are likely local
    artifacts).
    """

    click.echo("*" * 50)
    click.echo("Checking version of nengo-bones generated files:")
    click.echo("root dir: %s\n" % root_dir)

    passed = True

    for filename in nengo_bones.all_templated_files:
        click.echo(filename + ":")

        # TODO: Ensure that the file is there <=> it is the config
        if not os.path.exists(os.path.join(root_dir, filename)):
            click.echo("  File not found")
            continue

        with open(os.path.join(root_dir, filename)) as f:
            version = None
            for line in f.readlines()[:50]:
                if (line.startswith("# Version:")
                        or line.startswith(".. Version:")):
                    version = line.split(":")[1].strip()
                    break

        if version is None:
            click.echo("  This file was not generated with nengo-bones")
        if version != nengo_bones.__version__:
            click.secho(
                "  Version (%s) does not match nengo-bones version (%s);\n"
                "  please update by running `bones-generate` from\n"
                "  the root directory." % (version, nengo_bones.__version__),
                fg="red")
            passed = False
        else:
            click.secho("  Up to date", fg="green")

    click.echo("*" * 50)

    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()  # pragma: no cover pylint: disable=no-value-for-parameter
