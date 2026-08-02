#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2,<7"]
# ///
"""Generate a deterministic self-contained HTML viewer for the repository OKF wiki."""

from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

GENERATOR_VERSION = "1.0.0"
RESERVED = {"index.md", "log.md", "viz.html", "viz-manifest.json"}


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def display_metadata(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return str(value)


def parse_concept(
    path: Path, wiki: Path, as_of: date, committed_text: str | None = None
) -> dict[str, Any]:
    text = (
        committed_text
        if committed_text is not None
        else path.read_text(encoding="utf-8")
    ).replace("\r\n", "\n")
    metadata: dict[str, Any] = {}
    body = text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end >= 0:
            parsed = yaml.safe_load(text[4:end])
            if isinstance(parsed, dict):
                metadata = parsed
            body = text[end + 5 :]
    relative = path.relative_to(wiki)
    concept_id = "/" + relative.as_posix()
    links = sorted(
        {
            target.split("#", 1)[0]
            for target in re.findall(r"\[[^\]]+\]\((/[^)\s]+)", body)
            if target.split("#", 1)[0].endswith(".md")
        }
    )
    generated_value = metadata.get("generated", "")
    verified_value = metadata.get("verified", "")
    generated = display_metadata(generated_value)
    verified = display_metadata(verified_value)
    stale_after = str(metadata.get("stale_after", ""))
    is_stale = bool(stale_after and stale_after < as_of.isoformat())
    verifier = (
        str(verified_value.get("by", ""))
        if isinstance(verified_value, dict)
        else verified
    )
    trust = (
        "human-reviewed"
        if verifier.startswith("human:")
        else "machine-confirmed"
        if verified
        else "unverified"
    )
    sources = []
    source_values = metadata.get("sources", [])
    if not isinstance(source_values, list):
        source_values = []
    for source in source_values:
        if isinstance(source, dict):
            sources.append(
                {
                    "id": str(source.get("id", "")),
                    "resource": str(source.get("resource", "")),
                    "title": str(source.get("title", "")),
                    "lastModified": str(source.get("last_modified", "")),
                }
            )
    return {
        "id": concept_id,
        "title": str(metadata.get("title") or path.stem.replace("-", " ").title()),
        "description": str(metadata.get("description", "")),
        "type": str(metadata.get("type", "Unknown")),
        "tags": metadata.get("tags", [])
        if isinstance(metadata.get("tags", []), list)
        else [],
        "status": str(metadata.get("status", "unknown")),
        "trust": trust,
        "staleAfter": stale_after,
        "stale": is_stale,
        "generated": generated,
        "verified": verified,
        "sources": sources,
        "hierarchy": list(relative.parent.parts),
        "links": links,
    }


def render(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).replace(
        "<", "\\u003c"
    )
    title = html.escape("Repository knowledge relationships")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
body {{ margin: 0; padding: 1rem; }}
.controls {{ display: flex; flex-wrap: wrap; gap: .75rem; margin-block: 1rem; }}
input, select {{ padding: .5rem; }}
#graph {{ width: 100%; min-height: 36rem; border: 1px solid #7776; }}
.node {{ cursor: pointer; }} .node circle {{ fill: #0f766e; stroke: currentColor; }}
.node text {{ font-size: 11px; }} line {{ stroke: #64748b; stroke-width: 1; }}
table {{ border-collapse: collapse; width: 100%; }} th, td {{ border: 1px solid #7776; padding: .4rem; text-align: left; }}
.hierarchy-list {{ columns: 2 20rem; }} .hierarchy-list button {{ border: 0; background: transparent; color: inherit; text-decoration: underline; cursor: pointer; }}
.sr-heading {{ margin-top: 2rem; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p id="summary"></p>
<div class="controls" aria-label="Knowledge filters">
<label>Search <input id="search" type="search"></label>
<label>Type <select id="type"><option value="">All</option></select></label>
<label>Status <select id="status"><option value="">All</option></select></label>
<label>Trust <select id="trust"><option value="">All</option></select></label>
<label><input id="stale" type="checkbox"> Stale only</label>
</div>
<svg id="graph" role="img" aria-labelledby="graph-title"><title id="graph-title">Directed wiki relationship graph</title></svg>
<aside id="detail" aria-live="polite"><h2>Concept details</h2><p>Select a node or table row.</p></aside>
<section aria-labelledby="hierarchy-title"><h2 id="hierarchy-title">Hierarchy</h2><p>Taxonomy is shown separately from semantic cross-links.</p><div id="hierarchy" class="hierarchy-list"></div></section>
<h2 class="sr-heading">Accessible concept list</h2>
<table><thead><tr><th>Concept</th><th>Type</th><th>Status</th><th>Trust</th><th>Stale after</th><th>References</th><th>Backlinks</th></tr></thead><tbody id="rows"></tbody></table>
<script type="application/json" id="wiki-data">{encoded}</script>
<script>
const data=JSON.parse(document.getElementById('wiki-data').textContent);
const byId=new Map(data.nodes.map(n=>[n.id,n]));
const backlinks=new Map(data.nodes.map(n=>[n.id,[]])); data.edges.forEach(e=>backlinks.get(e.target)?.push(e.source));
const controls=['type','status','trust'];
for(const key of controls){{const s=document.getElementById(key);[...new Set(data.nodes.map(n=>n[key]))].sort().forEach(v=>{{const o=document.createElement('option');o.value=v;o.textContent=v;s.append(o)}})}}
function escapeHtml(v){{const d=document.createElement('div');d.textContent=String(v);return d.innerHTML}}
function list(values){{return values.length?`<ul>${{values.map(v=>`<li>${{escapeHtml(v)}}</li>`).join('')}}</ul>`:'<p>none</p>'}}
function show(n){{const sources=n.sources.map(s=>`${{s.id||'source'}} — ${{s.title||'untitled'}} — ${{s.resource||'no resource'}}${{s.lastModified?` (modified ${{s.lastModified}})`:''}}`);document.getElementById('detail').innerHTML=`<h2>${{escapeHtml(n.title)}}</h2><p><code>${{escapeHtml(n.id)}}</code></p><p>${{escapeHtml(n.description||'No description provided.')}}</p><p>Type: ${{escapeHtml(n.type)}}; status: ${{escapeHtml(n.status)}}; trust: ${{escapeHtml(n.trust)}}; stale after: ${{escapeHtml(n.staleAfter||'not declared')}}</p><p>Tags: ${{n.tags.map(escapeHtml).join(', ')||'none'}}</p><p>Generated: ${{escapeHtml(n.generated||'not declared')}}; verified: ${{escapeHtml(n.verified||'not declared')}}</p><h3>Sources</h3>${{list(sources)}}<h3>References</h3>${{list(n.links)}}<h3>Backlinks</h3>${{list(backlinks.get(n.id)||[])}}`}}
function drawHierarchy(){{const target=document.getElementById('hierarchy');target.replaceChildren();data.hierarchy.forEach(group=>{{const section=document.createElement('section'),heading=document.createElement('h3'),items=document.createElement('ul');heading.textContent=group.path;group.concepts.forEach(id=>{{const node=byId.get(id),item=document.createElement('li'),button=document.createElement('button');button.type='button';button.textContent=node?.title||id;button.addEventListener('click',()=>node&&show(node));item.append(button);items.append(item)}});section.append(heading,items);target.append(section)}})}}
function filtered(){{const q=document.getElementById('search').value.toLowerCase();return data.nodes.filter(n=>(!q||`${{n.title}} ${{n.id}} ${{n.tags.join(' ')}}`.toLowerCase().includes(q))&&controls.every(k=>!document.getElementById(k).value||n[k]===document.getElementById(k).value)&&(!document.getElementById('stale').checked||n.stale))}}
function draw(){{const nodes=filtered(),ids=new Set(nodes.map(n=>n.id)),svg=document.getElementById('graph');svg.replaceChildren();const w=Math.max(svg.clientWidth,700),h=560,r=Math.min(w,h)*.38,cx=w/2,cy=h/2;svg.setAttribute('viewBox',`0 0 ${{w}} ${{h}}`);const pos=new Map(nodes.map((n,i)=>[n.id,[cx+r*Math.cos(2*Math.PI*i/Math.max(nodes.length,1)),cy+r*Math.sin(2*Math.PI*i/Math.max(nodes.length,1))]]));data.edges.filter(e=>ids.has(e.source)&&ids.has(e.target)).forEach(e=>{{const [x1,y1]=pos.get(e.source),[x2,y2]=pos.get(e.target),l=document.createElementNS('http://www.w3.org/2000/svg','line');for(const [k,v] of Object.entries({{x1,y1,x2,y2}}))l.setAttribute(k,v);svg.append(l)}});nodes.forEach(n=>{{const [x,y]=pos.get(n.id),g=document.createElementNS('http://www.w3.org/2000/svg','g');g.setAttribute('class','node');g.setAttribute('tabindex','0');g.setAttribute('transform',`translate(${{x}},${{y}})`);const c=document.createElementNS(g.namespaceURI,'circle');c.setAttribute('r','8');const t=document.createElementNS(g.namespaceURI,'text');t.setAttribute('x','12');t.setAttribute('y','4');t.textContent=n.title;g.append(c,t);g.addEventListener('click',()=>show(n));g.addEventListener('keydown',e=>{{if(e.key==='Enter'||e.key===' ')show(n)}});svg.append(g)}});const rows=document.getElementById('rows');rows.replaceChildren();nodes.forEach(n=>{{const tr=document.createElement('tr');tr.tabIndex=0;tr.innerHTML=`<td>${{escapeHtml(n.title)}}<br><code>${{escapeHtml(n.id)}}</code></td><td>${{escapeHtml(n.type)}}</td><td>${{escapeHtml(n.status)}}</td><td>${{escapeHtml(n.trust)}}</td><td>${{escapeHtml(n.staleAfter||'')}}</td><td>${{n.links.map(escapeHtml).join('<br>')}}</td><td>${{(backlinks.get(n.id)||[]).map(escapeHtml).join('<br>')}}</td>`;tr.addEventListener('click',()=>show(n));tr.addEventListener('keydown',e=>{{if(e.key==='Enter')show(n)}});rows.append(tr)}});document.getElementById('summary').textContent=`${{nodes.length}} of ${{data.nodes.length}} concepts; ${{data.edges.length}} directed references. Source ${{data.manifest.sourceRevision}}.`}}
document.querySelectorAll('input,select').forEach(e=>e.addEventListener('input',draw));drawHierarchy();draw();
</script>
</body>
</html>
"""


def uncommitted_generation_inputs(root: Path) -> list[str]:
    status = git(
        root,
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        "wiki",
        ".agents.config/skills/dev/wiki-visualize",
    )
    generated_outputs = {"wiki/viz.html", "wiki/viz-manifest.json"}
    dirty = []
    for line in status.splitlines():
        path = line[3:].strip('"').replace("\\", "/")
        candidates = {part.strip() for part in path.split(" -> ")}
        if not candidates.issubset(generated_outputs):
            dirty.append(line)
    return dirty


def committed_markdown_paths(root: Path, wiki: Path) -> list[Path]:
    tracked = git(root, "ls-tree", "-r", "--name-only", "HEAD", "--", "wiki")
    paths = []
    for relative_name in tracked.splitlines():
        relative = Path(relative_name)
        candidate = (root / relative).resolve()
        if (
            relative.suffix == ".md"
            and relative.name not in RESERVED
            and candidate.is_relative_to(wiki.resolve())
        ):
            paths.append(candidate)
    return sorted(paths, key=lambda path: path.relative_to(wiki).as_posix())


def committed_text(root: Path, path: Path) -> str:
    relative = path.relative_to(root).as_posix()
    result = subprocess.run(
        ["git", "show", f"HEAD:{relative}"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return result.stdout.decode("utf-8")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: uv run generate_wiki_viz.py <repository-root>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    wiki = root / "wiki"
    dirty_inputs = uncommitted_generation_inputs(root)
    if dirty_inputs:
        print(
            "Refusing to attribute uncommitted wiki/skill content to HEAD:\n"
            + "\n".join(dirty_inputs),
            file=sys.stderr,
        )
        return 1
    source_revision = git(root, "rev-parse", "HEAD")
    generation_time = git(root, "show", "-s", "--format=%cI", "HEAD")
    source_date = date.fromisoformat(git(root, "show", "-s", "--format=%cs", "HEAD"))
    concepts = committed_markdown_paths(root, wiki)
    nodes = [
        parse_concept(path, wiki, source_date, committed_text(root, path))
        for path in concepts
    ]
    known = {node["id"] for node in nodes}
    edges = sorted(
        [
            {"source": node["id"], "target": target, "type": "references"}
            for node in nodes
            for target in node["links"]
            if target in known
        ],
        key=lambda edge: (edge["source"], edge["target"]),
    )
    hierarchy_by_path: dict[str, list[str]] = {}
    for node in nodes:
        hierarchy_path = "/".join(node["hierarchy"]) or "(root)"
        hierarchy_by_path.setdefault(hierarchy_path, []).append(node["id"])
    hierarchy = [
        {"path": path, "concepts": sorted(concepts)}
        for path, concepts in sorted(hierarchy_by_path.items())
    ]
    graph_digest = hashlib.sha256(
        json.dumps(
            {"nodes": nodes, "edges": edges, "hierarchy": hierarchy},
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    manifest = {
        "sourceRevision": source_revision,
        "skillVersion": f"{source_revision}:.agents.config/skills/dev/wiki-visualize",
        "generationTime": generation_time,
        "generatorVersion": GENERATOR_VERSION,
        "conceptCount": len(nodes),
        "edgeCount": len(edges),
        "contentDigest": f"sha256:{graph_digest}",
    }
    payload = {
        "manifest": manifest,
        "nodes": nodes,
        "edges": edges,
        "hierarchy": hierarchy,
    }
    (wiki / "viz.html").write_text(render(payload), encoding="utf-8", newline="\n")
    (wiki / "viz-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
