"""End-to-end tests: run the whole tool on a copy of the data folder."""

import shutil
from pathlib import Path

import pytest

from patchguard.cli import main

DATA = Path(__file__).parent.parent / "data"


@pytest.fixture
def data_dir(tmp_path):
    # tmp_path is a fresh empty folder pytest gives each test, so we can
    # break files freely without touching the real data.
    copy = tmp_path / "data"
    shutil.copytree(DATA, copy)
    return copy


def test_valid_data_exits_0(data_dir, capsys):
    assert main([str(data_dir)]) == 0
    assert "3 files checked, 0 failed, 0 errors" in capsys.readouterr().out


def test_bad_data_exits_1(data_dir, capsys):
    path = data_dir / "champions" / "korrim.yaml"
    path.write_text(path.read_text().replace("[140, 120, 100]", "[140, 150, 100]"))
    assert main([str(data_dir)]) == 1
    assert "cooldown goes up at rank 2" in capsys.readouterr().out


def test_broken_yaml_is_reported_not_crashed(data_dir, capsys):
    path = data_dir / "champions" / "korrim.yaml"
    path.write_text(path.read_text().replace("role: tank", "role tank"))
    assert main([str(data_dir)]) == 1
    assert "YAML syntax error at line 5" in capsys.readouterr().out


def test_missing_folder_exits_2(tmp_path):
    assert main([str(tmp_path / "nope")]) == 2


def test_preview_is_written(data_dir, tmp_path):
    out = tmp_path / "preview.html"
    main([str(data_dir), "--preview", str(out)])
    html = out.read_text(encoding="utf-8")
    assert "Vessa" in html and "Ironbark Shield" in html