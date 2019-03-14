"""Scripts for auto-generating nengo-bones files."""

import os

import click
import jinja2

import nengo_bones


@click.group()
@click.option("--conf-file", default=None, help="Filepath for config file")
@click.option("--output-dir", default=".", help="Output directory for scripts")
@click.option("--template-dir", default=None,
              help="Directory containing additional templates")
@click.pass_context
def main(ctx, conf_file, output_dir, template_dir):
    """Loads config file and sets up template environment."""

    ctx.ensure_object(dict)

    config = nengo_bones.load_config(conf_file)

    template_dirs = [] if template_dir is None else [template_dir]
    template_dirs.append(
        os.path.join(os.path.dirname(__file__), "..", "templates"))
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dirs),
        trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)

    if not os.path.exists(output_dir):
        os.makedirs(os.path.normpath(output_dir))

    ctx.obj["env"] = env
    ctx.obj["config"] = config
    ctx.obj["output_dir"] = output_dir


@main.command()
@click.pass_context
def ci_scripts(ctx):
    """Generate TravisCI shell scripts."""

    config = ctx.obj["config"]
    for params in config["ci_scripts"]:
        script_name = params.pop("template")
        template = ctx.obj["env"].get_template(script_name + ".sh.template")
        output_name = params.pop("output_name", script_name)

        with open(os.path.join(
                ctx.obj["output_dir"], output_name + ".sh"), "w") as f:
            f.write(template.render(
                pkg_name=config["pkg_name"], repo_name=config["repo_name"],
                version=nengo_bones.__version__, **params))


@main.command()
@click.pass_context
def travis_yml(ctx):
    """Generate TravisCI config file."""

    config = ctx.obj["config"]

    jobs = config["travis_yml"]["jobs"]
    for job in jobs:
        # shortcuts for setting environment variables
        if "env" not in job:
            job["env"] = {}
        for var in ("script", "test_args", "python_version"):
            if var in job:
                job["env"][var] = job.pop(var)

    template = ctx.obj["env"].get_template(".travis.yml.template")
    with open(os.path.join(ctx.obj["output_dir"], ".travis.yml"), "w") as f:
        f.write(template.render(version=nengo_bones.__version__,
                                **config["travis_yml"]))


@main.command()
@click.pass_context
def codecov_yml(ctx):
    """Generate codecov config file."""

    config = ctx.obj["config"]

    template = ctx.obj["env"].get_template(".codecov.yml.template")
    with open(os.path.join(ctx.obj["output_dir"], ".codecov.yml"), "w") as f:
        f.write(template.render(
            version=nengo_bones.__version__,
            **config["codecov_yml"]))


if __name__ == "__main__":
    main(obj={})  # pragma: no cover pylint: disable=no-value-for-parameter
