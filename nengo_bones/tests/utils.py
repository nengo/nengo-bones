"""Tools for writing tests in nengo-bones."""

import re
from textwrap import dedent
from traceback import print_tb


def write_file(tmpdir, filename, contents):
    """Writes a (multiline) string to file."""

    contents = contents.lstrip("\n")

    tmpdir.join(filename).write(dedent(contents))


def assert_exit(result, status):
    """Check click.CliRunner exit code and display errors if any."""

    try:
        assert result.exit_code == status
    except AssertionError:
        print("cli failed with:")
        print(result.output)
        print(result.exc_info)
        print(result.exception)
        print_tb(result.exc_info[2])
        raise


def make_has_line(lines, strip=False, regex=False):
    """Create a function to check file or output lines in order"""

    idx = 0

    def has_line(target, strip=strip, regex=regex, print_on_fail=True):
        nonlocal lines
        nonlocal idx

        while idx < len(lines):
            line = lines[idx]
            idx += 1

            if strip:
                line = line.strip()

            match = re.search(target, line) if regex else line.startswith(target)
            if match:
                return True

        if print_on_fail:
            print("Failed to find '%s' in\n" % target)
            print("".join(lines))

        return False

    return has_line
