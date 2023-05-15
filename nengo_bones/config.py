"""Handles the processing of nengo-bones configuration settings."""

import datetime
import pathlib

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
            f"{key} should be a list, found '{cfg[key]}'; did you forget "
            "to add '-' before each entry?"
        )


def find_config():
    """
    Finds the default nengo-bones config file.

    Returns
    -------
    conf_file : `pathlib.Path`
        Path to the default config file.
    """
    # for now, assume that config file is in cwd
    conf_file = pathlib.Path.cwd() / ".nengobones.yml"

    return conf_file


def fill_defaults(config):  # noqa: C901
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
    config.setdefault("min_python", "3.8")
    config.setdefault("main_branch", "master")
    config.setdefault("license", "proprietary")

    if "setup_py" in config:
        cfg = config["setup_py"]
        cfg.setdefault("python_requires", f">={config['min_python']}")
        cfg.setdefault("include_package_data", False)

        license_string = {
            "abr-free": "Free for non-commercial use",
            "abr-nonfree": "Proprietary",
            "apache": "Apache 2.0 license",
            "mit": "MIT license",
            "proprietary": "Proprietary",
        }[config["license"]]
        cfg.setdefault("license_string", license_string)

        org_name, repo_name = config["repo_name"].split("/")
        domain = {
            "nengo": "https://www.nengo.ai",
            "nengo-labs": "https://labs.nengo.ai",
            "abr": "https://www.appliedbrainresearch.com",
        }.get(org_name, "https://www.nengo.ai")
        cfg.setdefault("url", f"{domain}/{repo_name}")

        classifiers = cfg.get("classifiers", [])
        license_classifier = {
            "abr-free": "License :: Free for non-commercial use",
            "abr-nonfree": "License :: Other/Proprietary License",
            "apache": "License :: OSI Approved :: Apache Software License",
            "mit": "License :: OSI Approved :: MIT License",
            "proprietary": "License :: Other/Proprietary License",
        }[config["license"]]
        classifiers.append(license_classifier)
        cfg["classifiers"] = list(sorted(classifiers))

    if "setup_cfg" in config:
        cfg = config["setup_cfg"]
        cfg.setdefault("pytest", {})
        cfg.setdefault("pylint", {})
        cfg.setdefault("flake8", {})
        cfg.setdefault("coverage", {})
        cfg.setdefault("codespell", {})
        cfg.setdefault("mypy", {})
        cfg["pytest"].setdefault("xfail_strict", False)

    if "docs_conf_py" in config:
        cfg = config["docs_conf_py"]
        cfg.setdefault("nengo_logo", "general-full-light.svg")
        cfg.setdefault("nengo_logo_color", "#a8acaf")

    if "version_py" in config:
        cfg = config["version_py"]
        cfg.setdefault("type", "semver")


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
        if "pylint" in config["setup_cfg"]:
            pylint = config["setup_cfg"]["pylint"]
            check_list(pylint, "disable")
            check_list(pylint, "ignore")
            check_list(pylint, "known_third_party")
        if "mypy" in config["setup_cfg"]:
            mypy = config["setup_cfg"]["mypy"]
            check_list(mypy, "ignore_missing_imports")


def validate_setup_py_config(config):
    """
    Validates the ``setup_py`` section of the config.

    Parameters
    ----------
    config : dict
        Dictionary containing configuration values.
    """
    if "setup_py" in config:
        classifiers = config["setup_py"].get("classifiers", [])
        if any(c.startswith("License") for c in classifiers):
            raise ValueError(
                "License classifier is set automatically, remove manual entry"
            )


# Defined at top-level so they can be used in tests
license_types = ["abr-free", "abr-nonfree", "proprietary", "mit", "apache"]
mandatory_entries = [
    "project_name",
    "pkg_name",
    "repo_name",
    "version_py.release",
]


def validate_config(config):  # noqa: C901
    """
    Validates a populated config dict.

    Parameters
    ----------
    config : dict
        Dictionary containing configuration values.
    """
    for entry in mandatory_entries:
        tmp = config
        for i, key in enumerate(entry.split(".")):
            try:
                tmp = tmp[key]
            except KeyError as e:
                if "." in entry and i == 0:
                    # if the toplevel isn't defined, ignore this
                    break

                raise KeyError(f"Config file must define {entry}") from e

    if config.get("license", "proprietary") not in license_types:
        license_types_str = ", ".join(f'"{ltype}"' for ltype in license_types)
        raise ValueError(f"license must be one of {license_types_str}")

    if "ci_scripts" in config:
        for ci_config in config["ci_scripts"]:
            validate_ci_config(ci_config)

    validate_black_config(config)
    validate_setup_cfg_config(config)
    validate_setup_py_config(config)

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
        raise KeyError(f"Script config must define 'template' (for entry {ci_config})")

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

    if not pathlib.Path(conf_file).exists():
        raise RuntimeError(
            f"Could not find conf_file: {conf_file}\n\nPerhaps you are "
            "not in the project's root directory?"
        )

    with open(conf_file, encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    validate_config(config)

    fill_defaults(config)

    return config
