"""Handles the processing of nengo-bones configuration settings."""

import datetime
import pathlib
from textwrap import dedent

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

    if "license_rst" in config:
        cfg = config["license_rst"]
        cfg.setdefault("add_to_files", False)
        cfg.setdefault("text", license_text(config["license"], config["project_name"]))


def license_text(license, project_name):
    """Return license text for given license type."""

    if license.startswith("abr"):
        text = f"""\
            **ABR License**

            {project_name} is made available under a proprietary license, the
            "ABR TECHNOLOGY LICENSE AND USE AGREEMENT" (the "ABR License").
            The main ABR License file is available for download at
            `<https://www.appliedbrainresearch.com/license>`_.
            The entire contents of this ``LICENSE.rst`` file, including any
            terms and conditions herein, form part of the ABR License.

            Commercial Use Licenses are available to purchase for a yearly fee.
            Academic and Personal Use Licenses for {project_name} are available at
            {'no' if license == 'abr-free' else 'a reduced'} cost.
            Both types of licences can be obtained from the
            ABR store at `<https://www.appliedbrainresearch.com/store>`_.

            If you have any sales questions,
            please contact `<sales@appliedbrainresearch.com>`_.
            If you have any technical support questions, please post them on the ABR
            community forums at `<https://forum.nengo.ai/>`_ or contact
            `<support@appliedbrainresearch.com>`_.
            """
    elif license == "proprietary":
        text = """\
            All information contained herein is and remains the property of
            Applied Brain Research. The intellectual and technical concepts contained
            herein are proprietary to Applied Brain Research and may be covered by U.S.
            and Foreign Patents, patents in process, and are protected by trade secret
            or copyright law. Dissemination of this information or reproduction of this
            material is strictly forbidden unless prior written permission is obtained
            from Applied Brain Research. Access to the source code contained herein is
            hereby forbidden to anyone except current Applied Brain Research employees,
            contractors or other outside parties that have executed Confidentiality
            and/or Non-disclosure agreements explicitly covering such access.

            The copyright notice above does not evidence any actual or intended
            publication or disclosure of this source code, which includes information
            that is confidential and/or proprietary, and is a trade secret, of
            Applied Brain Research. ANY REPRODUCTION, MODIFICATION, DISTRIBUTION,
            PUBLIC PERFORMANCE, OR PUBLIC DISPLAY OF OR THROUGH USE OF THIS
            SOURCE CODE WITHOUT THE EXPRESS WRITTEN CONSENT OF APPLIED BRAIN RESEARCH
            IS STRICTLY PROHIBITED, AND IN VIOLATION OF APPLICABLE LAWS AND
            INTERNATIONAL TREATIES. THE RECEIPT OR POSSESSION OF THIS SOURCE
            CODE AND/OR RELATED INFORMATION DOES NOT CONVEY OR IMPLY ANY RIGHTS
            TO REPRODUCE, DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO MANUFACTURE,
            USE, OR SELL ANYTHING THAT IT MAY DESCRIBE, IN WHOLE OR IN PART.
        """
    elif license == "mit":
        text = """\
            **MIT License**

            Permission is hereby granted, free of charge,
            to any person obtaining a copy of this software
            and associated documentation files (the "Software"),
            to deal in the Software without restriction,
            including without limitation the rights to use, copy, modify, merge,
            publish, distribute, sublicense, and/or sell copies of the Software,
            and to permit persons to whom the Software is furnished to do so,
            subject to the following conditions:

            The above copyright notice and this permission notice shall be included
            in all copies or substantial portions of the Software.

            THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
            IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
            FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
            AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
            LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
            OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
            SOFTWARE.
        """
    elif license == "apache":
        text = """\
            **Apache License**

            Licensed under the Apache License, Version 2.0 (the "License");
            you may not use this file except in compliance with the License.
            You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

            Unless required by applicable law or agreed to in writing, software
            distributed under the License is distributed on an "AS IS" BASIS,
            WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
            See the License for the specific language governing permissions and
            limitations under the License.

            ::

                                             Apache License
                                       Version 2.0, January 2004
                                    http://www.apache.org/licenses/

               TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

               1. Definitions.

                  "License" shall mean the terms and conditions for use, reproduction,
                  and distribution as defined by Sections 1 through 9 of this document.

                  "Licensor" shall mean the copyright owner or entity authorized by
                  the copyright owner that is granting the License.

                  "Legal Entity" shall mean the union of the acting entity and all
                  other entities that control, are controlled by, or are under common
                  control with that entity. For the purposes of this definition,
                  "control" means (i) the power, direct or indirect, to cause the
                  direction or management of such entity, whether by contract or
                  otherwise, or (ii) ownership of fifty percent (50%) or more of the
                  outstanding shares, or (iii) beneficial ownership of such entity.

                  "You" (or "Your") shall mean an individual or Legal Entity
                  exercising permissions granted by this License.

                  "Source" form shall mean the preferred form for making modifications,
                  including but not limited to software source code, documentation
                  source, and configuration files.

                  "Object" form shall mean any form resulting from mechanical
                  transformation or translation of a Source form, including but
                  not limited to compiled object code, generated documentation,
                  and conversions to other media types.

                  "Work" shall mean the work of authorship, whether in Source or
                  Object form, made available under the License, as indicated by a
                  copyright notice that is included in or attached to the work
                  (an example is provided in the Appendix below).

                  "Derivative Works" shall mean any work, whether in Source or Object
                  form, that is based on (or derived from) the Work and for which the
                  editorial revisions, annotations, elaborations, or other modifications
                  represent, as a whole, an original work of authorship. For the purposes
                  of this License, Derivative Works shall not include works that remain
                  separable from, or merely link (or bind by name) to the interfaces of,
                  the Work and Derivative Works thereof.

                  "Contribution" shall mean any work of authorship, including
                  the original version of the Work and any modifications or additions
                  to that Work or Derivative Works thereof, that is intentionally
                  submitted to Licensor for inclusion in the Work by the copyright owner
                  or by an individual or Legal Entity authorized to submit on behalf of
                  the copyright owner. For the purposes of this definition, "submitted"
                  means any form of electronic, verbal, or written communication sent
                  to the Licensor or its representatives, including but not limited to
                  communication on electronic mailing lists, source code control systems,
                  and issue tracking systems that are managed by, or on behalf of, the
                  Licensor for the purpose of discussing and improving the Work, but
                  excluding communication that is conspicuously marked or otherwise
                  designated in writing by the copyright owner as "Not a Contribution."

                  "Contributor" shall mean Licensor and any individual or Legal Entity
                  on behalf of whom a Contribution has been received by Licensor and
                  subsequently incorporated within the Work.

               2. Grant of Copyright License. Subject to the terms and conditions of
                  this License, each Contributor hereby grants to You a perpetual,
                  worldwide, non-exclusive, no-charge, royalty-free, irrevocable
                  copyright license to reproduce, prepare Derivative Works of,
                  publicly display, publicly perform, sublicense, and distribute the
                  Work and such Derivative Works in Source or Object form.

               3. Grant of Patent License. Subject to the terms and conditions of
                  this License, each Contributor hereby grants to You a perpetual,
                  worldwide, non-exclusive, no-charge, royalty-free, irrevocable
                  (except as stated in this section) patent license to make, have made,
                  use, offer to sell, sell, import, and otherwise transfer the Work,
                  where such license applies only to those patent claims licensable
                  by such Contributor that are necessarily infringed by their
                  Contribution(s) alone or by combination of their Contribution(s)
                  with the Work to which such Contribution(s) was submitted. If You
                  institute patent litigation against any entity (including a
                  cross-claim or counterclaim in a lawsuit) alleging that the Work
                  or a Contribution incorporated within the Work constitutes direct
                  or contributory patent infringement, then any patent licenses
                  granted to You under this License for that Work shall terminate
                  as of the date such litigation is filed.

               4. Redistribution. You may reproduce and distribute copies of the
                  Work or Derivative Works thereof in any medium, with or without
                  modifications, and in Source or Object form, provided that You
                  meet the following conditions:

                  (a) You must give any other recipients of the Work or
                      Derivative Works a copy of this License; and

                  (b) You must cause any modified files to carry prominent notices
                      stating that You changed the files; and

                  (c) You must retain, in the Source form of any Derivative Works
                      that You distribute, all copyright, patent, trademark, and
                      attribution notices from the Source form of the Work,
                      excluding those notices that do not pertain to any part of
                      the Derivative Works; and

                  (d) If the Work includes a "NOTICE" text file as part of its
                      distribution, then any Derivative Works that You distribute must
                      include a readable copy of the attribution notices contained
                      within such NOTICE file, excluding those notices that do not
                      pertain to any part of the Derivative Works, in at least one
                      of the following places: within a NOTICE text file distributed
                      as part of the Derivative Works; within the Source form or
                      documentation, if provided along with the Derivative Works; or,
                      within a display generated by the Derivative Works, if and
                      wherever such third-party notices normally appear. The contents
                      of the NOTICE file are for informational purposes only and
                      do not modify the License. You may add Your own attribution
                      notices within Derivative Works that You distribute, alongside
                      or as an addendum to the NOTICE text from the Work, provided
                      that such additional attribution notices cannot be construed
                      as modifying the License.

                  You may add Your own copyright statement to Your modifications and
                  may provide additional or different license terms and conditions
                  for use, reproduction, or distribution of Your modifications, or
                  for any such Derivative Works as a whole, provided Your use,
                  reproduction, and distribution of the Work otherwise complies with
                  the conditions stated in this License.

               5. Submission of Contributions. Unless You explicitly state otherwise,
                  any Contribution intentionally submitted for inclusion in the Work
                  by You to the Licensor shall be under the terms and conditions of
                  this License, without any additional terms or conditions.
                  Notwithstanding the above, nothing herein shall supersede or modify
                  the terms of any separate license agreement you may have executed
                  with Licensor regarding such Contributions.

               6. Trademarks. This License does not grant permission to use the trade
                  names, trademarks, service marks, or product names of the Licensor,
                  except as required for reasonable and customary use in describing the
                  origin of the Work and reproducing the content of the NOTICE file.

               7. Disclaimer of Warranty. Unless required by applicable law or
                  agreed to in writing, Licensor provides the Work (and each
                  Contributor provides its Contributions) on an "AS IS" BASIS,
                  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
                  implied, including, without limitation, any warranties or conditions
                  of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
                  PARTICULAR PURPOSE. You are solely responsible for determining the
                  appropriateness of using or redistributing the Work and assume any
                  risks associated with Your exercise of permissions under this License.

               8. Limitation of Liability. In no event and under no legal theory,
                  whether in tort (including negligence), contract, or otherwise,
                  unless required by applicable law (such as deliberate and grossly
                  negligent acts) or agreed to in writing, shall any Contributor be
                  liable to You for damages, including any direct, indirect, special,
                  incidental, or consequential damages of any character arising as a
                  result of this License or out of the use or inability to use the
                  Work (including but not limited to damages for loss of goodwill,
                  work stoppage, computer failure or malfunction, or any and all
                  other commercial damages or losses), even if such Contributor
                  has been advised of the possibility of such damages.

               9. Accepting Warranty or Additional Liability. While redistributing
                  the Work or Derivative Works thereof, You may choose to offer,
                  and charge a fee for, acceptance of support, warranty, indemnity,
                  or other liability obligations and/or rights consistent with this
                  License. However, in accepting such obligations, You may act only
                  on Your own behalf and on Your sole responsibility, not on behalf
                  of any other Contributor, and only if You agree to indemnify,
                  defend, and hold each Contributor harmless for any liability
                  incurred by, or claims asserted against, such Contributor by reason
                  of your accepting any such warranty or additional liability.

               END OF TERMS AND CONDITIONS

               APPENDIX: How to apply the Apache License to your work.

                  To apply the Apache License to your work, attach the following
                  boilerplate notice, with the fields enclosed by brackets "[]"
                  replaced with your own identifying information. (Don't include
                  the brackets!)  The text should be enclosed in the appropriate
                  comment syntax for the file format. We also recommend that a
                  file or class name and description of purpose be included on the
                  same "printed page" as the copyright notice for easier
                  identification within third-party archives.

               Copyright [yyyy] [name of copyright owner]

               Licensed under the Apache License, Version 2.0 (the "License");
               you may not use this file except in compliance with the License.
               You may obtain a copy of the License at

                   http://www.apache.org/licenses/LICENSE-2.0

               Unless required by applicable law or agreed to in writing, software
               distributed under the License is distributed on an "AS IS" BASIS,
               WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
               See the License for the specific language governing permissions and
               limitations under the License.
        """

    return dedent(text)


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
