"""nengo-bones version information.

We use calendar versioning (see https://calver.org/)
and conform to PEP440 (see https://www.python.org/dev/peps/pep-0440/).
'.devN' will be added to the version unless the code base represents
a release version. Release versions are git tagged with the version.
"""

from datetime import date

name = "nengo-bones"
today = date.today()
version_info = (today.year % 1000, today.month)
dev = 0

version = "{v}{dev}".format(
    v=".".join(str(v) for v in version_info),
    dev=(".dev%d" % dev) if dev is not None else "",
)
