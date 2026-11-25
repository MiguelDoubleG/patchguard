"""Load YAML content files and check them against the schemas and game rules."""

import yaml
from jsonschema import Draft202012Validator

from patchguard.rules import check_champion, check_items
from patchguard.schemas import CHAMPION_SCHEMA, ITEMS_FILE_SCHEMA


def load_yaml(path):
    """Read a YAML file and return it as plain Python data."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def yaml_error_message(error):
    """Turn PyYAML's long error into one line with the position."""
    mark = getattr(error, "problem_mark", None)
    problem = getattr(error, "problem", None) or str(error)
    if mark is None:
        return f"YAML syntax error: {problem}"
    return f"YAML syntax error at line {mark.line + 1}, column {mark.column + 1}: {problem}"


def schema_errors(data, schema):
    """Return a list of readable error messages. An empty list means valid."""
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.json_path)
    return [f"{e.json_path}: {e.message}" for e in errors]


def validate_champion_file(path):
    try:
        champ = load_yaml(path)
    except yaml.YAMLError as error:
        return [yaml_error_message(error)]

    errors = schema_errors(champ, CHAMPION_SCHEMA)
    if errors:
        return errors  # don't run game rules on badly shaped data
    errors = check_champion(champ)
    if champ["id"] != path.stem:
        errors.append(f"file name '{path.name}' doesn't match id '{champ['id']}'")
    return errors


def validate_items_file(path):
    try:
        items = load_yaml(path)
    except yaml.YAMLError as error:
        return [yaml_error_message(error)]

    errors = schema_errors(items, ITEMS_FILE_SCHEMA)
    if errors:
        return errors
    return check_items(items)