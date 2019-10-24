"""Scripts for auto-generating nengo-bones files."""

import os
import sys

import click

from nengo_bones import __version__, all_sections
from nengo_bones.config import load_config
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


@click.group(invoke_without_command=True)
@click.option("--conf-file", default=None, help="Filepath for config file")
@click.option("--output-dir", default=".", help="Output directory for scripts")
@click.pass_context
def main(ctx, conf_file, output_dir):
    """Loads config file and sets up template environment.

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

    if not os.path.exists(output_dir):
        os.makedirs(os.path.normpath(output_dir))

    ctx.obj["config"] = config
    ctx.obj["output_dir"] = output_dir
    ctx.obj["env"] = load_env()

    def check_cfg(name):
        name = name.replace("-", "_")
        if name not in config:
            print("No config entry detected for %s, skipping" % name)
            return False
        return True

    if ctx.invoked_subcommand is None:
        for cfg_name in all_sections:
            if check_cfg(cfg_name):
                ctx.invoke(globals()[cfg_name])
    elif not check_cfg(ctx.invoked_subcommand):
        sys.exit()


@main.command()
@click.pass_context
def ci_scripts(ctx):
    """Generate TravisCI shell scripts."""

    config = ctx.obj["config"]
    for params in config["ci_scripts"]:
        script_name = params.pop("template")
        output_file = params.pop("output_name", script_name)
        BonesTemplate(script_name + ".sh", ctx.obj["env"]).render_to_file(
            ctx.obj["output_dir"],
            output_name=output_file + ".sh",
            pkg_name=config["pkg_name"],
            repo_name=config["repo_name"],
            **params,
        )


@main.command()
@click.pass_context
def travis_yml(ctx):
    """Generate TravisCI config file."""

    render_template(ctx, ".travis.yml")


@main.command()
@click.pass_context
def codecov_yml(ctx):
    """Generate codecov config file."""

    render_template(ctx, ".codecov.yml")


@main.command()
@click.pass_context
def license_rst(ctx):
    """Generate LICENSE.rst file."""

    render_template(ctx, "LICENSE.rst")


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
def pre_commit_config_yaml(ctx):
    """Generate .pre-commit-config.yaml file."""

    render_template(ctx, ".pre-commit-config.yaml")


@main.command()
@click.pass_context
def pyproject_toml(ctx):
    """Generate pyproject.toml file."""

    render_template(ctx, "pyproject.toml")


if __name__ == "__main__":
    main(obj={})  # pragma: no cover pylint: disable=no-value-for-parameter
