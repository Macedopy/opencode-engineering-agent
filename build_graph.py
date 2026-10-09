import re, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VAULT = ROOT / "vault"
OUT = VAULT / "graph.json"

nodes, edges = [], []

for md in sorted(VAULT.rglob("*.md")):
    text = md.read_text(encoding="utf-8")
    nodes.append(md.stem)
    for link in re.findall(r"\[\[([^\]|]+)", text):
        edges.append({"from": md.stem, "to": link})

OUT.write_text(json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK: {len(nodes)} nodes, {len(edges)} edges -> {OUT}")
