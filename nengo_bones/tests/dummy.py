"""Tools for creating dummy objects for testing."""

from traceback import print_tb


def write_file(tmpdir, filename, contents):
    """Writes a (multiline) string to file."""

    with open(str(tmpdir.join(filename)), "w") as f:
        contents = contents.splitlines()

        # skip first entry if it's a blank newline
        if contents[0] == "":
            contents = contents[1:]

        # assume that all lines indented by some constant that we want
        # to strip out
        indent = len(contents[0]) - len(contents[0].lstrip(" "))
        contents = "\n".join(s[indent:] for s in contents)
        f.write(contents)


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
