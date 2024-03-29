"""Handles the processing of nengo-bones templates using jinja2."""

import datetime
import stat
import subprocess
from collections import defaultdict
from pathlib import Path

import jinja2

from nengo_bones.config import find_config


class BonesTemplate:
    """
    A templated file known to NengoBones.

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
    extra_render_data = defaultdict(list)

    def __init__(self, output_file, env):
        self.output_file = output_file
        self.env = env

        section = output_file.lstrip(".")
        section = section.replace("pkg/", "")  # Don't require `pkg_` prefix
        section = section.replace(".", "_")
        section = section.replace("/", "_")
        section = section.replace("-", "_")
        section = section.lower()
        self.section = section

        self.template_file = f"{output_file}.template"

    @classmethod
    def add_render_data(cls, filename):
        """
        Register functions that add template-specific render data.

        For example:

        .. testcode::

           @nengo_bones.templates.BonesTemplate.add_render_data("my_new_template")
           def add_my_new_template_data(data):
               data["attr"] = "val"
               ...
        """

        def _add_render_data(func):
            cls.extra_render_data[filename].append(func)
            return func

        return _add_render_data

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
        for adder in self.extra_render_data[self.section]:
            adder(data)
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

        # Apply additional formatting to python files
        if self.output_file.endswith(".py"):
            # Add license notice
            if "license_rst" in data and data["license_rst"]["add_to_files"]:
                rendered = add_notice(data["license_rst"]["text"], rendered)

            for tool in ["black -q -", "docformatter -", "isort -"]:
                rendered = subprocess.run(
                    tool.split(),
                    input=rendered,
                    stdout=subprocess.PIPE,
                    encoding="utf-8",
                    check=True,
                    cwd=find_config().parent,
                ).stdout

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

        # Special case: templates in `templates/pkg` directory have `pkg` replaced
        # with the actual name of the package
        if output_name.startswith("pkg/"):
            assert "pkg_name" in data
            output_name = output_name.replace("pkg/", f"{data['pkg_name']}/")
        output_path = Path(output_dir, output_name)
        output_path.parent.mkdir(exist_ok=True, parents=True)
        output_path.write_text(self.render(**data), encoding="utf-8")

        # We mark all `.sh` files as executable
        if output_path.suffix == ".sh":
            st = output_path.stat()
            output_path.chmod(st.st_mode | stat.S_IEXEC)


@BonesTemplate.add_render_data("manifest_in")
def add_manifest_data(data):
    """Add MANIFEST.in-specific entries to the 'data' dict."""
    data["custom"] = data["manifest_in"]


def _get_extras(sect_data, extra_types):
    extras = {}
    # We iterate over sect_data (rather than extra_types) so that order is preserved
    for key in list(sect_data):
        if key in extra_types:
            extras[key] = (extra_types[key], sect_data.pop(key))
    return extras


@BonesTemplate.add_render_data("setup_py")
def add_setup_py_data(data):
    """Add setup.py-specific entries to the 'data' dict."""
    data["extras"] = _get_extras(
        data["setup_py"],
        extra_types={
            "classifiers": "list",
            "py_modules": "list",
            "entry_points": "dict",
            "package_data": "dict",
        },
    )


@BonesTemplate.add_render_data("setup_cfg")
def add_setup_cfg_data(data):
    """Add setup.cfg-specific entries to the 'data' dict."""
    pytest_data = data["setup_cfg"]["pytest"]
    pytest_data["extras"] = _get_extras(
        pytest_data,
        extra_types={
            "allclose_tolerances": "list",
            "filterwarnings": "list",
            "nengo_neurons": "list",
            "nengo_simulator": "str",
            "nengo_simloader": "str",
            "nengo_test_unsupported": "dict",
            "plt_dirname": "str",
            "plt_filename_drop": "list",
            "rng_salt": "str",
            "xfail_strict": "str",
        },
    )


@BonesTemplate.add_render_data("version_py")
def add_version_py_data(data):
    """Add version.py-specific entries to the 'data' dict."""
    data["today"] = datetime.datetime.now(
        tz=datetime.timezone(datetime.timedelta(hours=-5))
    )


def load_env():
    """Creates a jinja environment for loading/rendering templates."""

    bones_toplevel = Path(__file__).parent

    # Load overridden templates first.
    # Builtins are referenced with templates/*.template
    override_dirs = []
    override_dirs.append(".templates")
    override_dirs.append(bones_toplevel)
    override_loader = jinja2.FileSystemLoader(override_dirs)
    # If those fail, use the builtins
    builtin_loader = jinja2.FileSystemLoader(bones_toplevel / "templates")

    env = jinja2.Environment(
        loader=jinja2.ChoiceLoader([override_loader, builtin_loader]),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["rstrip"] = lambda s, chars: s.rstrip(chars)

    return env


def add_notice(license_text, current_text):
    """Add license text to file contents."""

    license_text = "\n".join(f"# {line}".strip() for line in license_text.splitlines())
    return f"{license_text}\n\n{current_text}"
