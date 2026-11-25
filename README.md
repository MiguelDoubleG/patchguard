patchguard

A command-line tool that catches mistakes in game content files before they ship. It checks champion and item configs written in YAML, explains every problem in plain language, and builds an HTML preview of the content so designers can see what they changed.

The champions and items in data/ are made up for this demo.

Why
In a live game, much of every patch is data rather than code: champion stats, ability cooldowns, item costs and recipes. That data is edited by hand, and small mistakes slip through easily. A misspelled key like cooldwons is silently ignored, a cooldown goes up at rank 2, or an item ends up cheaper than the parts it's built from. patchguard checks for these automatically on every change, so they're caught in review instead of by players.

What it checks
Validation runs in two layers.

1. Schema (JSON Schema). This layer checks the shape of each file:

Required fields are present and have the right type.
Values come from allowed sets, such as role and resource.
Ids are lowercase and use underscores.
Unknown or misspelled keys are rejected.
2. Game rules (Python). This layer checks relationships the schema can't express:

Cooldowns never increase from one rank to the next.
Basic abilities have 5 ranks, the ultimate has 3 and the passive has none.
Abilities appear in P, Q, W, E, R order.
Only champions with a resource bar have ability costs, and their costs line up with their cooldowns.
Each champion's file name matches its id.
Every component an item builds from exists.
An item costs at least as much as its components combined.
No two items share an id.
The game rules only run once a file passes the schema check, so they can trust the data's shape.

Example output
$ python -m patchguard
FAIL data/champions/korrim.yaml
     R (Mountain's Wrath): cooldown goes up at rank 2 (140 -> 150)
OK   data/champions/vessa.yaml
FAIL data/items.yaml
     ironbark_shield: builds from unknown item 'ruby_shrad'
     ember_tome: costs 300 but its components cost 350

3 files checked, 2 failed, 3 errors
Broken YAML is reported as one line instead of crashing the tool:

FAIL data/champions/korrim.yaml
     YAML syntax error at line 5, column 1: could not find expected ':'
Preview
--preview writes an HTML page with a card for each champion and item. Files that fail validation get a red card listing their errors.

patchguard preview

Usage
python -m venv .venv
.venv\Scripts\activate          # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

python -m patchguard                          # check ./data
python -m patchguard path/to/data -q          # only show files that fail
python -m patchguard --preview preview.html   # also build the HTML preview
python -m pytest                              # run the tests
Exit codes:

0: everything is valid.
1: the content has errors.
2: the tool was used incorrectly, for example a folder that doesn't exist.
Continuous integration
GitHub Actions runs on every push and pull request (.github/workflows/tests.yml). It does three things:

Runs the test suite.
Validates the real data with patchguard.
Uploads the HTML preview as a downloadable artifact.
A content change that breaks a rule turns the run red before it can be merged.

Design decisions
Two layers. Declarative JSON Schema handles shape, and plain Python handles relationships between values and across files. Each layer does what it's good at.
Report every error, not just the first. A designer fixing a file sees the full list at once instead of fixing and re-running repeatedly.
Safe parsing. YAML is loaded with yaml.safe_load, which can't create arbitrary Python objects from a file.
Escaped output. All content is HTML-escaped in the preview, so text in a config can't inject markup or scripts.
Testable entry point. main(argv) returns an exit code instead of exiting, so tests call it directly with fake arguments.
Tests
There are 22 pytest tests:

Unit tests for each game rule, including edge cases such as flat cooldowns.
Schema tests for missing fields, wrong types and misspelled keys.
End-to-end tests that run the whole tool on a temporary copy of the data and check exit codes, broken YAML and the preview output.
Project layout
patchguard/
  schemas.py     JSON Schemas for champions and items
  rules.py       game rules a schema can't express
  validate.py    loading YAML and running both layers
  preview.py     HTML preview
  cli.py         command-line interface
data/            sample champions and items
tests/           pytest suite
Possible next steps
Detect circular item recipes, where A builds from B and B builds from A.
Compare two versions of the data and print a balance-change report for patch notes.
Move rule thresholds into a config file so designers can tune them without editing code.
Run as a pre-commit hook so errors are caught before a commit is made.
