"""Game rules that a schema can't express.

Each check returns a list of error messages. An empty list means it passed.
These run only after the schema check passes, so the data has the right shape.
"""

ABILITY_ORDER = ["P", "Q", "W", "E", "R"]
RANKS = {"P": 0, "Q": 5, "W": 5, "E": 5, "R": 3}


def check_champion(champ):
    errors = []
    keys = [ability["key"] for ability in champ["abilities"]]
    if keys != ABILITY_ORDER:
        errors.append(f"abilities must be in order {ABILITY_ORDER}, got {keys}")

    for ability in champ["abilities"]:
        errors += check_ability(ability, champ["resource"])
    return errors


def check_ability(ability, resource):
    errors = []
    key = ability["key"]
    label = f"{key} ({ability['name']})"
    cooldowns = ability.get("cooldowns", [])
    costs = ability.get("costs")

    expected = RANKS[key]
    if len(cooldowns) != expected:
        errors.append(f"{label}: expected {expected} cooldown values, got {len(cooldowns)}")

    for rank, (before, after) in enumerate(zip(cooldowns, cooldowns[1:]), start=2):
        if after > before:
            errors.append(f"{label}: cooldown goes up at rank {rank} ({before} -> {after})")

    if resource == "none" and costs is not None:
        errors.append(f"{label}: champion has no resource, so this ability can't have costs")
    if resource != "none" and key != "P" and costs is None:
        errors.append(f"{label}: {resource} champion needs costs for this ability")
    if costs is not None and len(costs) != len(cooldowns):
        errors.append(f"{label}: has {len(costs)} costs but {len(cooldowns)} cooldowns")
    return errors


def check_items(items):
    errors = []
    by_id = {}
    for item in items:
        if item["id"] in by_id:
            errors.append(f"{item['id']}: duplicate item id")
        by_id[item["id"]] = item

    for item in items:
        components = item.get("builds_from", [])
        missing = [c for c in components if c not in by_id]
        for component in missing:
            errors.append(f"{item['id']}: builds from unknown item '{component}'")
        if missing or not components:
            continue

        component_total = sum(by_id[c]["cost"] for c in components)
        if item["cost"] < component_total:
            errors.append(
                f"{item['id']}: costs {item['cost']} but its components cost {component_total}"
            )
    return errors