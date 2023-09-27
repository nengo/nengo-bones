# pylint: disable=missing-docstring

from nengo_bones.scripts.check_notice import check_notice
from nengo_bones.tests.utils import write_file


def test_check_notice(tmp_path, capsys):
    write_file(
        tmp_path=tmp_path,
        filename="dummy.py",
        contents="# license text",
    )
    checked, missing = check_notice(tmp_path, "license text", verbose=True)
    assert checked == 1
    assert missing == 0
    assert f"Present: {tmp_path / 'dummy.py'}" in capsys.readouterr().out


def test_check_missing_notice(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename="dummy.py",
        contents="",
    )
    checked, missing = check_notice(tmp_path, "license text")
    assert checked == 1
    assert missing == 1


def test_add_missing_notice(tmp_path):
    write_file(
        tmp_path=tmp_path,
        filename="dummy.py",
        contents="",
    )
    checked, missing = check_notice(tmp_path, "license text", fix=True)
    assert checked == 1
    assert missing == 1

    checked, missing = check_notice(tmp_path, "license text")
    assert checked == 1
    assert missing == 0
