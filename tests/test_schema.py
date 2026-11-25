"""Tests for the schema check in patchguard/validate.py."""

from pathlib import Path

from patchguard.schemas import CHAMPION_SCHEMA
from patchguard.validate import load_yaml, schema_errors

DATA = Path(__file__).parent.parent / "data"


def load_vessa():
    return load_yaml(DATA / "champions" / "vessa.yaml")


def test_valid_champion_has_no_schema_errors():
    assert schema_errors(load_vessa(), CHAMPION_SCHEMA) == []


def test_missing_field():
    champ = load_vessa()
    del champ["role"]
    assert schema_errors(champ, CHAMPION_SCHEMA) == ["$: 'role' is a required property"]


def test_wrong_type():
    champ = load_vessa()
    champ["base_stats"]["armor"] = "twenty-one"
    errors = schema_errors(champ, CHAMPION_SCHEMA)
    assert errors == ["$.base_stats.armor: 'twenty-one' is not of type 'number'"]


def test_misspelled_field_is_caught():
    champ = load_vessa()
    champ["abilities"][1]["cooldwons"] = champ["abilities"][1].pop("cooldowns")
    errors = schema_errors(champ, CHAMPION_SCHEMA)
    assert any("'cooldwons' was unexpected" in e for e in errors)