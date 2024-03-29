"""Scripts for auto-generating nengo-bones files."""

import sys
from pathlib import Path

import click

from nengo_bones import __version__, all_sections
from nengo_bones.config import find_config, load_config
from nengo_bones.scripts.base import bones
from nengo_bones.scripts.check_notice import check_notice
from nengo_bones.templates import BonesTemplate, load_env


def render_template(ctx, output_file):
    """
    Render a template to file.

    Parameters
    ----------
    ctx : `click.Context`
        CLI context, containing information specified upstream.
    output_file : str
        Filename for the rendered output file.
    """
    template = BonesTemplate(output_file, ctx.obj["env"])
    template.render_to_file(
        ctx.obj["output_dir"],
        version=__version__,
        **template.get_render_data(ctx.obj["config"]),
    )


@bones.group(name="generate", invoke_without_command=True)
@click.option("--conf-file", default=None, help="Filepath for config file")
@click.option("--output-dir", default=".", help="Output directory for scripts")
@click.pass_context
def main(ctx, conf_file, output_dir):
    """
    Loads config file and sets up template environment.

    By default, this updates all templated files that are
    to be committed to the repository.

    We look in the current directory for a ``.templates`` folder. If it
    exists, any templates defined in that folder will be loaded first.
    Otherwise, built-in templates will be loaded from the
    ``nengo_bones/templates`` directory.

    If you are overriding a template in the ``.templates`` folder, the
    original built-in version of that template can be accessed with
    the ``templates/`` prefix. This is useful in ``include`` and
    ``extends`` tags. For example, to add text to the default
    ``LICENSE.rst`` template, put the following in
    ``.templates/LICENSE.rst.template``:

    .. code-block:: rst

       {% include "templates/LICENSE.rst.template %}

       Additional license info
       =======================
       ...
    """

    ctx.ensure_object(dict)

    config = load_config(conf_file)

    Path(output_dir).mkdir(exist_ok=True)

    ctx.obj["config"] = config
    ctx.obj["output_dir"] = output_dir
    ctx.obj["env"] = load_env()

    def check_cfg(name):
        name = name.replace("-", "_")
        if name not in config:
            click.echo(f"No config entry detected for {name}, skipping")
            return False
        return True

    if ctx.invoked_subcommand is None:
        for cfg_name in all_sections:
            if check_cfg(cfg_name):
                ctx.invoke(globals()[cfg_name])
    elif not check_cfg(ctx.invoked_subcommand):
        sys.exit(1)


@main.command()
@click.pass_context
def ci_scripts(ctx):
    """Generate CI shell scripts."""

    config = ctx.obj["config"]
    for params in config["ci_scripts"]:
        script_name = params.pop("template")
        output_file = params.pop("output_name", script_name)
        BonesTemplate(f"{script_name}.sh", ctx.obj["env"]).render_to_file(
            ctx.obj["output_dir"],
            output_name=f"{output_file}.sh",
            # pass top-level config and script-specific params
            **{**config, **params},
        )


@main.command()
@click.pass_context
def license_rst(ctx):
    """Generate LICENSE.rst file."""

    render_template(ctx, "LICENSE.rst")

    if ctx.obj["config"]["license_rst"]["add_to_files"]:
        check_notice(
            find_config().parent, ctx.obj["config"]["license_rst"]["text"], fix=True
        )


@main.command()
@click.pass_context
def contributing_rst(ctx):
    """Generate CONTRIBUTING.rst file."""

    render_template(ctx, "CONTRIBUTING.rst")


@main.command()
@click.pass_context
def contributors_rst(ctx):
    """Generate CONTRIBUTORS.rst file."""

    render_template(ctx, "CONTRIBUTORS.rst")


@main.command()
@click.pass_context
def manifest_in(ctx):
    """Generate MANIFEST.in file."""

    render_template(ctx, "MANIFEST.in")


@main.command()
@click.pass_context
def setup_py(ctx):
    """Generate setup.py file."""

    render_template(ctx, "setup.py")


@main.command()
@click.pass_context
def setup_cfg(ctx):
    """Generate setup.cfg file."""

    render_template(ctx, "setup.cfg")


@main.command()
@click.pass_context
def docs_conf_py(ctx):
    """Generate docs/conf.py file."""

    render_template(ctx, "docs/conf.py")


@main.command()
@click.pass_context
def pyproject_toml(ctx):
    """Generate pyproject.toml file."""

    render_template(ctx, "pyproject.toml")


@main.command()
@click.pass_context
def py_typed(ctx):
    """Generate {{ pkg_name }}/py.typed file."""

    render_template(ctx, "pkg/py.typed")


@main.command()
@click.pass_context
def version_py(ctx):
    """Generate {{ pkg_name }}/version.py file."""

    render_template(ctx, "pkg/version.py")
