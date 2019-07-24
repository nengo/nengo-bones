"""Handles the processing of nengo-bones templates using jinja2."""

from collections import OrderedDict
import os
import stat
import warnings

try:
    from black import FileMode, format_str, TargetVersion

    HAS_BLACK = True
except ImportError:
    HAS_BLACK = False
import jinja2


class BonesTemplate:
    """
    A templated file known to Nengo Bones.

    The only necessary information is the output filename, relative to the
    ``templates`` directory, which means that the output filename for the
    Sphinx configuration is ``docs/conf.py``. Other attributes are determined
    from the output filename.

    Parameters
    ----------
    output_file : str
        Filename for the rendered output file.
    env : ``jinja2.Environment``
        Initialized jinja environment for loading/rendering templates.

    Attributes
    ----------
    env : ``jinja2.Environment``
        Initialized jinja environment for loading/rendering templates.
    output_file : str
        Filename for the rendered output file.
    section : str
        The heading for the section in the config file containing config
        options specific to the template being rendered.
    template_file : str
        Filename for the input template file.
    """

    __slots__ = ("env", "output_file", "section", "template_file")

    def __init__(self, output_file, env):

        self.output_file = output_file
        self.env = env

        section = output_file.lstrip(".")
        section = section.replace(".", "_")
        section = section.replace("/", "_")
        section = section.replace("-", "_")
        section = section.lower()
        self.section = section

        self.template_file = "%s.template" % (output_file,)

    def get_render_data(self, config):
        """
        Construct the ``data`` that will be used to render this template.

        This method creates a new dictionary so the original ``config``
        is not modified. Additionally, certain sections have
        processing done to them in addition to flattening out
        the section to the top-level of the config.

        Parameters
        ----------
        config : dict
            Dictionary containing configuration values.

        Returns
        -------
        data : dict
            A dictionary that can be passed to `.render` and `.render_to_file`.
        """
        data = {}
        # TODO: separate "top-level" config into its own section?
        data.update(config)
        data.update(config[self.section])

        # Add special options for specific sections
        if self.section == "travis_yml":
            jobs = data["travis_yml"]["jobs"]
            for job in jobs:
                # shortcuts for setting environment variables
                if "env" not in job:
                    job["env"] = OrderedDict()
                for var in ("script", "test_args"):
                    if var in job:
                        job["env"][var] = job.pop(var)

        elif self.section == "manifest_in":
            data["custom"] = data["manifest_in"]

        elif self.section == "setup_py":
            setup_config = data["setup_py"]

            extras = OrderedDict()
            extra_types = {
                "classifiers": "list",
                "entry_points": "dict",
                "package_data": "dict",
            }
            # We iterate over setup_config (rather than extra_types) so that
            # the order in setup_config is preserved
            for key in list(setup_config):
                if key in extra_types:
                    extras[key] = (extra_types[key], setup_config.pop(key))
            data["extras"] = extras

        return data

    def render(self, **data):
        """
        Render this template to a string.

        Parameters
        ----------
        data : dict
            Will be passed on to the ``template.render`` function.
        """
        rendered = self.env.get_template(self.template_file).render(**data)

        # Format Python templates with black
        if HAS_BLACK:
            if self.output_file.endswith(".py"):
                black_mode = FileMode(
                    target_versions={
                        TargetVersion.PY35,
                        TargetVersion.PY36,
                        TargetVersion.PY37,
                    }
                )
                rendered = format_str(rendered, mode=black_mode)
        else:
            warnings.warn(
                "Black not installed, rendered template may not be formatted correctly"
            )

        return rendered

    def render_to_file(self, output_dir, output_name=None, **data):
        """
        Render a template to file.

        .. note:: Rendered shell scripts (files with the ``.sh extension``)
                  are automatically marked as executable.

        Parameters
        ----------
        output_dir : str
            Directory in which the rendered file should be placed.
        output_name : str, optional
            An alternative filename for the rendered file.
            This overrides the class's internal ``output_file`` attribute.
        data : dict
            Will be passed on to the ``render`` function.
        """
        if output_name is None:
            output_name = self.output_file
        output_path = os.path.join(output_dir, output_name)

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        with open(output_path, "w") as f:
            f.write(self.render(**data))

        # We mark all `.sh` files as executable
        if output_name.endswith(".sh"):
            st = os.stat(output_path)
            os.chmod(output_path, st.st_mode | stat.S_IEXEC)


def load_env():
    """Creates a jinja environment for loading/rendering templates."""

    bones_toplevel = os.path.normpath(os.path.dirname(__file__))

    # Load overridden templates first.
    # Builtins are referenced with templates/*.template
    override_dirs = []
    override_dirs.append(".templates")
    override_dirs.append(bones_toplevel)
    override_loader = jinja2.FileSystemLoader(override_dirs)
    # If those fail, use the builtins
    builtin_loader = jinja2.FileSystemLoader(os.path.join(bones_toplevel, "templates"))

    env = jinja2.Environment(
        loader=jinja2.ChoiceLoader([override_loader, builtin_loader]),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["rstrip"] = lambda s, chars: s.rstrip(chars)

    return env
