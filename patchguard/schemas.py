"""JSON Schemas describing what valid game content looks like."""

ROLES = ["assassin", "fighter", "mage", "marksman", "support", "tank"]
RESOURCES = ["mana", "energy", "none"]
ABILITY_KEYS = ["P", "Q", "W", "E", "R"]
BASE_STATS = [
    "health",
    "health_per_level",
    "attack_damage",
    "armor",
    "move_speed",
    "attack_range",
]

ABILITY_SCHEMA = {
    "type": "object",
    "required": ["key", "name", "description"],
    "properties": {
        "key": {"enum": ABILITY_KEYS},
        "name": {"type": "string", "minLength": 1},
        "description": {"type": "string", "minLength": 1},
        "cooldowns": {
            "type": "array",
            "items" : {"type": "number", "exclusiveMinimum": 0},
            "minItems": 1,
        },
        "costs": {
            "type": "array",
            "items" : {"type": "number", "minimum": 0},
            "minItems": 1,
        },
    },
    "additionalProperties": False,
}

CHAMPION_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "title", "role", "resource", "base_stats", "abilities"],
    "properties": {
        "id": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
        "name": {"type": "string", "minLength": 1},
        "title": {"type": "string"},
        "role": {"enum": ROLES},
        "resource": {"enum": RESOURCES},
        "base_stats": {
            "type": "object",
            "required": BASE_STATS,
            "properties": {stat: {"type": "number", "minimum": 0} for stat in BASE_STATS},
            "additionalProperties": False,
        },
        "abilities": {
            "type": "array",
            "items": ABILITY_SCHEMA,
            "minItems": 5,
            "maxItems": 5,
        },
    },
    "additionalProperties": False,
}

ITEM_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "cost", "stats"],
    "properties": {
        "id": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
        "name": {"type": "string", "minLength": 1},
        "cost": {"type": "integer", "minimum": 0},
        "builds_from": {
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": True,
        },
        "stats": {
            "type": "object",
            "additionalProperties": {"type": "number"},
            "minProperties": 1,
        },
    },
    "additionalProperties": False,
}

ITEMS_FILE_SCHEMA = {"type": "array", "items": ITEM_SCHEMA}