"""nengo-bones version information.

We use semantic versioning (see http://semver.org/).
and conform to PEP440 (see https://www.python.org/dev/peps/pep-0440/).
'.devN' will be added to the version unless the code base represents
a release version. Release versions are git tagged with the version.

The API of nengo-bones is different from other libraries, so we increment
version numbers as follows:

1. Major version when command line scripts change significantly.
2. Minor version when changes require patches to downstream projects.
3. Patch version when changes do not require downstream patches.
"""

name = "nengo-bones"
version_info = (0, 2, 0)  # (major, minor, patch)
dev = None

version = "{v}{dev}".format(v='.'.join(str(v) for v in version_info),
                            dev=('.dev%d' % dev) if dev is not None else '')
