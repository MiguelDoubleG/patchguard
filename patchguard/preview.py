"""Build an HTML page with a card for each champion and item."""
 
from html import escape
 
from patchguard.validate import load_yaml
 
STYLE = """
body { font-family: system-ui, sans-serif; background: #10141c; color: #e6e6e6; margin: 24px; }
h1 { margin-top: 0; }
h2 { margin-top: 32px; color: #c8aa6e; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; align-items: start; }
.card { background: #1b2230; border: 1px solid #2f3a4f; border-radius: 10px; padding: 16px; }
.card.error { border-color: #e05252; }
.card h3 { margin: 0; }
.subtitle { color: #9aa4b5; margin: 2px 0 12px; }
.tag { display: inline-block; background: #2f3a4f; border-radius: 4px; padding: 2px 8px; margin-right: 4px; font-size: 12px; }
table { width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 12px; }
td { padding: 2px 0; }
td:last-child { text-align: right; }
.ability { border-top: 1px solid #2f3a4f; padding: 8px 0; font-size: 14px; }
.key { display: inline-block; width: 22px; text-align: center; background: #c8aa6e; color: #10141c; border-radius: 4px; font-weight: bold; margin-right: 6px; }
.numbers { color: #9aa4b5; font-size: 13px; }
.gold { color: #c8aa6e; font-weight: bold; }
.error li { color: #ff8a8a; }
"""
 
 
def fmt(numbers):
    """[8, 7.5, 7] -> '8 / 7.5 / 7'"""
    return " / ".join(f"{n:g}" for n in numbers)
 
 
def ability_html(ability, resource):
    lines = [f'<span class="key">{escape(ability["key"])}</span><b>{escape(ability["name"])}</b>']
    lines.append(f"<div>{escape(ability['description'])}</div>")
    if "cooldowns" in ability:
        lines.append(f'<div class="numbers">Cooldown: {fmt(ability["cooldowns"])} s</div>')
    if "costs" in ability:
        lines.append(f'<div class="numbers">Cost: {fmt(ability["costs"])} {escape(resource)}</div>')
    return f'<div class="ability">{"".join(lines)}</div>'
 
 
def champion_card(champ):
    stats = "".join(
        f"<tr><td>{escape(stat.replace('_', ' '))}</td><td>{value:g}</td></tr>"
        for stat, value in champ["base_stats"].items()
    )
    abilities = "".join(ability_html(a, champ["resource"]) for a in champ["abilities"])
    return f"""
<article class="card">
  <h3>{escape(champ["name"])}</h3>
  <div class="subtitle">{escape(champ["title"])}</div>
  <span class="tag">{escape(champ["role"])}</span><span class="tag">{escape(champ["resource"])}</span>
  <table>{stats}</table>
  {abilities}
</article>"""
 
 
def item_card(item, names):
    stats = "".join(
        f"<tr><td>{escape(stat.replace('_', ' '))}</td><td>+{value:g}</td></tr>"
        for stat, value in item["stats"].items()
    )
    recipe = ""
    if item.get("builds_from"):
        parts = " + ".join(escape(names[c]) for c in item["builds_from"])
        recipe = f'<div class="numbers">Builds from: {parts}</div>'
    return f"""
<article class="card">
  <h3>{escape(item["name"])}</h3>
  <div class="subtitle"><span class="gold">{item["cost"]} gold</span></div>
  <table>{stats}</table>
  {recipe}
</article>"""
 
 
def error_card(path, errors):
    items = "".join(f"<li>{escape(message)}</li>" for message in errors)
    return f"""
<article class="card error">
  <h3>{escape(path.name)}</h3>
  <div class="subtitle">Not previewed: fix these errors first</div>
  <ul>{items}</ul>
</article>"""
 
 
def build_preview(results):
    """results is the list of (path, errors) pairs that the CLI already built."""
    champion_cards, item_cards = [], []
    for path, errors in results:
        if errors:
            target = item_cards if path.name == "items.yaml" else champion_cards
            target.append(error_card(path, errors))
        elif path.name == "items.yaml":
            items = load_yaml(path)
            names = {item["id"]: item["name"] for item in items}
            item_cards += [item_card(item, names) for item in items]
        else:
            champion_cards.append(champion_card(load_yaml(path)))
 
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>patchguard preview</title>
<style>{STYLE}</style>
</head>
<body>
<h1>patchguard preview</h1>
<h2>Champions</h2>
<div class="grid">{"".join(champion_cards)}</div>
<h2>Items</h2>
<div class="grid">{"".join(item_cards)}</div>
</body>
</html>"""
 