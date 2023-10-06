# Automatically generated by nengo-bones, do not edit this file directly

# pylint: disable=consider-using-f-string,bad-string-format-type

"""
NengoBones version information.

We use calendar versioning (see https://calver.org/) and conform to PEP440 (see
https://www.python.org/dev/peps/pep-0440/). '.dev0' will be added to the version
unless the code base represents a release version. Release versions are git
tagged with the version.
"""

version_info = (23, 10, 6)  # bones: ignore

name = "nengo-bones"
dev = 0

# use old string formatting, so that this can still run in Python <= 3.5
# (since this file is parsed in setup.py, before python_requires is applied)
version = ".".join(str(v) for v in version_info)
if dev is not None:
    version += ".dev%d" % dev  # pragma: no cover

copyright = "Copyright (c) 2018-2023 Applied Brain Research"
