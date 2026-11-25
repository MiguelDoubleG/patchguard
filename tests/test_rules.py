"""Tests for the game rules in patchguard/rules.py."""

from pathlib import Path

import pytest

from patchguard.rules import check_champion, check_items
from patchguard.validate import load_yaml

DATA = Path(__file__).parent.parent / "data"


@pytest.fixture
def vessa():
    # A fixture runs fresh for every test, so each test can change its own copy.
    return load_yaml(DATA / "champions" / "vessa.yaml")


@pytest.fixture
def korrim():
    return load_yaml(DATA / "champions" / "korrim.yaml")


@pytest.fixture
def items():
    return load_yaml(DATA / "items.yaml")


def test_sample_champions_pass(vessa, korrim):
    assert check_champion(vessa) == []
    assert check_champion(korrim) == []


@pytest.mark.parametrize(
    "cooldowns, should_pass",
    [
        ([8, 7, 6, 5, 4], True),   # goes down every rank
        ([8, 8, 8, 8, 8], True),   # flat is fine
        ([8, 9, 6, 5, 4], False),  # goes up at rank 2
        ([8, 7, 6, 5, 6], False),  # goes up at the last rank
    ],
)
def test_cooldowns_must_not_go_up(vessa, cooldowns, should_pass):
    vessa["abilities"][1]["cooldowns"] = cooldowns  # Q
    errors = check_champion(vessa)
    assert (errors == []) == should_pass


def test_wrong_number_of_ranks(vessa):
    vessa["abilities"][4]["cooldowns"] = [120, 100]  # R needs 3
    vessa["abilities"][4]["costs"] = [100, 100]
    errors = check_champion(vessa)
    assert any("expected 3 cooldown values, got 2" in e for e in errors)


def test_abilities_out_of_order(vessa):
    vessa["abilities"][1], vessa["abilities"][2] = vessa["abilities"][2], vessa["abilities"][1]
    errors = check_champion(vessa)
    assert any("must be in order" in e for e in errors)


def test_champion_without_resource_cannot_have_costs(korrim):
    korrim["abilities"][1]["costs"] = [50, 50, 50, 50, 50]
    errors = check_champion(korrim)
    assert any("can't have costs" in e for e in errors)


def test_mana_champion_needs_costs(vessa):
    del vessa["abilities"][1]["costs"]
    errors = check_champion(vessa)
    assert any("needs costs" in e for e in errors)


def test_sample_items_pass(items):
    assert check_items(items) == []


def test_unknown_component(items):
    items[3]["builds_from"] = ["oak_buckler", "ruby_shrad"]
    assert check_items(items) == ["ironbark_shield: builds from unknown item 'ruby_shrad'"]


def test_item_cheaper_than_components(items):
    items[4]["cost"] = 300
    assert check_items(items) == ["ember_tome: costs 300 but its components cost 350"]


def test_duplicate_item_id(items):
    items.append(dict(items[0]))
    assert check_items(items) == ["oak_buckler: duplicate item id"]