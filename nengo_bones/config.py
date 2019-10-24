"""Handles the processing of nengo-bones configuration settings."""

from collections import OrderedDict
import datetime
import os

import yaml


def check_list(cfg, key):
    """
    Verify that config value is a list.

    This is designed to catch the common error of specifying

    .. code-block:: yaml

        option:
            value

    instead of

    .. code-block:: yaml

        option:
            - value

    Parameters
    ----------
    cfg : dict
        Configuration options being checked.
    key: str
        Name of configuration value to be checked.

    Raises
    ------
    TypeError
        If ``key`` is in ``cfg`` and its value is not a list.
    """
    if key in cfg and not isinstance(cfg[key], list):
        raise TypeError(
            "%s should be a list, found '%s'; did you forget "
            "to add '-' before each entry?" % (key, cfg[key])
        )


def find_config():
    """
    Finds the default nengo-bones config file.

    Returns
    -------
    conf_file : str
        Path to the default config file.
    """
    # for now, assume that config file is in cwd
    conf_file = os.path.join(os.getcwd(), ".nengobones.yml")

    return conf_file


def fill_defaults(config):
    """
    Fills in default values in a loaded config (in-place).

    Parameters
    ----------
    config : dict
        Dictionary containing configuration values.
    """

    config.setdefault("author", "Applied Brain Research")
    config.setdefault("author_email", "info@appliedbrainresearch.com")
    config.setdefault("copyright_start", datetime.datetime.now().year)
    config.setdefault("copyright_end", datetime.datetime.now().year)

    if "travis_yml" in config:
        cfg = config["travis_yml"]
        cfg.setdefault("python", "3.6")
        cfg.setdefault("global_vars", OrderedDict())
        cfg.setdefault("pypi_user", None)
        cfg.setdefault("deploy_dists", ["sdist"])
        cfg.setdefault("bones_install", "nengo-bones")

        for job in cfg["jobs"]:
            if job.get("script", "").startswith("docs"):
                job.setdefault("apt_install", ["pandoc"])

    if "codecov_yml" in config:
        cfg = config["codecov_yml"]
        cfg.setdefault("skip_appveyor", True)
        cfg.setdefault("abs_target", "auto")
        cfg.setdefault("diff_target", "100%")

    if "license_rst" in config:
        cfg = config["license_rst"]
        cfg.setdefault("type", "nengo")

    if "setup_py" in config:
        cfg = config["setup_py"]
        cfg.setdefault("license", "Free for non-commercial use")
        cfg.setdefault("python_requires", ">=3.5")
        cfg.setdefault("include_package_data", False)
        cfg.setdefault(
            "url", "https://www.nengo.ai/%s" % config["pkg_name"].replace("_", "-")
        )

    if "setup_cfg" in config:
        cfg = config["setup_cfg"]
        cfg.setdefault("pytest", OrderedDict())
        cfg.setdefault("pylint", OrderedDict())
        cfg.setdefault("flake8", OrderedDict())
        cfg.setdefault("coverage", OrderedDict())
        cfg["pytest"].setdefault("xfail_strict", False)

    if "docs_conf_py" in config:
        cfg = config["docs_conf_py"]
        cfg.setdefault("nengo_logo", "general-full-light.svg")
        cfg.setdefault("nengo_logo_color", "#a8acaf")

    if "contributors_rst" in config:
        cfg = config["contributors_rst"]
        cfg.setdefault(
            "nengo_list", config.get("license_rst", {}).get("type", "") == "nengo"
        )


def validate_black_config(config):
    """
    Validates aspects of the config related to Black.

    Parameters
    ----------
    config : dict
        Dictionary containing configuration values.
    """

    has_precommit = "pre_commit_config_yaml" in config
    has_pyproject = "pyproject_toml" in config
    if not (has_precommit or has_pyproject):
        return
    if not (has_pyproject and has_precommit):
        raise KeyError(
            "Config file must define both 'pyproject_toml' "
            "and 'pre_commit_config_yaml' or neither"
        )
    precommit = config["pre_commit_config_yaml"]
    pyproject = config["pyproject_toml"]
    check_list(precommit, "exclude")
    check_list(pyproject, "exclude")
    if precommit.get("exclude", []) != pyproject.get("exclude", []):
        raise ValueError(
            "'pyproject_toml' and 'pre_commit_config_yaml' "
            "must have the same 'exclude' list."
        )


def validate_setup_cfg_config(config):
    """
    Validates the ``setup_cfg`` section of the config.

    Parameters
    ----------
    config : dict
        Dictionary containing configuration values.
    """
    if "setup_cfg" in config:
        if "pytest" in config["setup_cfg"]:
            pytest = config["setup_cfg"]["pytest"]
            check_list(pytest, "addopts")
            check_list(pytest, "allclose_tolerances")
            check_list(pytest, "filterwarnings")
            check_list(pytest, "nengo_neurons")
            check_list(pytest, "norecursedirs")
            check_list(pytest, "plt_filename_drop")


def validate_config(config):  # noqa: C901
    """
    Validates a populated config dict.

    Parameters
    ----------
    config : dict
        Dictionary containing configuration values.
    """
    mandatory = ["project_name", "pkg_name", "repo_name", "travis_yml.jobs"]

    for entry in mandatory:
        tmp = config
        for i, key in enumerate(entry.split(".")):
            try:
                tmp = tmp[key]
            except KeyError:
                if "." in entry and i == 0:
                    # if the toplevel isn't defined, ignore this
                    break

                raise KeyError("Config file must define %s" % entry)

    if "ci_scripts" in config:
        for ci_config in config["ci_scripts"]:
            validate_ci_config(ci_config)

    validate_black_config(config)
    validate_setup_cfg_config(config)

    # TODO: check that there aren't unused config options in yml


def validate_ci_config(ci_config):
    """
    Validates an entry in the ci_scripts list of a config dict.

    Parameters
    ----------
    ci_config : dict
        Dictionary containing ci_scripts configuration values.
    """
    if "template" not in ci_config:
        raise KeyError(
            "Script config must define 'template' " "(for entry %s)" % ci_config
        )

    # make sure that people don't accidentally do things like
    # pip_install: dependency (which gives a string), rather than
    # pip_install:
    #   - dependency
    list_opts = (
        "pip_install",
        "pre_commands",
        "post_commands",
        "codespell_ignore_words",
    )
    for opt in list_opts:
        check_list(ci_config, opt)


def load_config(conf_file=None):
    """
    Loads config values from a file and applies defaults/validation.

    Parameters
    ----------
    conf_file : str
        Filepath for config file (if None, will load the default returned by
        `.find_config`).

    Returns
    -------
    config : dict
        Dictionary containing configuration values.
    """

    if conf_file is None:
        conf_file = find_config()

    if not os.path.exists(str(conf_file)):
        raise RuntimeError(
            "Could not find conf_file: %s\n\nPerhaps you are "
            "not in the project's root directory?" % conf_file
        )

    def ordered_load(stream):
        """Use OrderedDict instead of dict for loading mappings."""

        class OrderedLoader(yaml.SafeLoader):  # pylint: disable=too-many-ancestors
            """Custom loader containing OrderedDict mapping."""

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))

        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
        )
        return yaml.load(stream, OrderedLoader)

    with open(str(conf_file)) as f:
        config = ordered_load(f)

    validate_config(config)

    fill_defaults(config)

    return config
