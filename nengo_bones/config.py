"""Handles the processing of nengo-bones configuration settings."""

from collections import OrderedDict
import os

import yaml


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
    if "travis_yml" in config:
        config["travis_yml"].setdefault("python", "3.6")
        config["travis_yml"].setdefault("global_vars", {})
        config["travis_yml"].setdefault("pypi_user", None)
        config["travis_yml"].setdefault("deploy_dists", ["sdist"])
        config["travis_yml"].setdefault("bones_install", "nengo-bones")

        for job in config["travis_yml"]["jobs"]:
            if job.get("script", "").startswith("docs"):
                job.setdefault("apt_install", ["pandoc"])

    if "codecov_yml" in config:
        config["codecov_yml"].setdefault("skip_appveyor", True)
        config["codecov_yml"].setdefault("abs_target", "auto")
        config["codecov_yml"].setdefault("diff_target", "100%")


def validate_config(config):
    """
    Validates a populated config dict.

    Parameters
    ----------
    config : dict
        Dictionary containing configuration values.
    """
    mandatory = ["pkg_name", "repo_name"]
    if "travis_yml" in config:
        mandatory.append("travis_yml.jobs")

    for entry in mandatory:
        tmp = config
        for key in entry.split("."):
            try:
                tmp = tmp[key]
            except KeyError:
                raise KeyError("Config file must define %s" % entry)

    if "ci_scripts" in config:
        for ci_config in config["ci_scripts"]:
            validate_ci_config(ci_config)

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
        raise KeyError("Script config must define 'template' "
                       "(for entry %s)" % ci_config)

    try:
        # make sure that people don't accidentally do
        # pip_install: dependency (which gives a string), rather than
        # pip_install:
        #   - dependency
        for key in ("pip_install", "pre_commands", "post_commands"):
            if not isinstance(ci_config[key], list):
                raise TypeError(
                    "%s should be a list, found '%s'; did you forget "
                    "to add '-' before each entry?" % (
                        key, ci_config[key]))
    except KeyError:
        pass


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
        raise RuntimeError("Could not find conf_file: %s\n\nPerhaps you are "
                           "not in the project's root directory?" % conf_file)

    def ordered_load(stream):
        """Use OrderedDict instead of dict for loading mappings."""

        class OrderedLoader(yaml.SafeLoader):  # pylint: disable=too-many-ancestors
            """Custom loader containing OrderedDict mapping."""

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))

        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
        return yaml.load(stream, OrderedLoader)

    with open(str(conf_file)) as f:
        config = ordered_load(f)

    validate_config(config)

    fill_defaults(config)

    return config
