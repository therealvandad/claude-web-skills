#!/usr/bin/env python3
"""
skill-brain: draw every installed Claude Code skill as a node in an interactive
graph, with the "Related skills" links between SKILL.md files as the wires.

Usage
  python build_skill_brain.py                          # scan ~/.claude/skills, write skill-brain.html
  python build_skill_brain.py --open                   # same, then open it in the browser
  python build_skill_brain.py --dir D:/more/skills     # also scan extra skill folders (repeatable)
  python build_skill_brain.py --project .              # also scan <project>/.claude/skills
  python build_skill_brain.py --json                   # print nodes/edges as JSON instead of HTML
  python build_skill_brain.py --out graph.html

What counts as a link
  * every `backticked-name` inside a "## Related skills" section (kind: related)
  * any other `backticked-token` anywhere in the body that equals an existing skill name (kind: mention)
A related-section name that matches no installed skill becomes a dashed "dangling" node.
Skills nobody links to and that link to nobody are drawn with a warning ring (isolated).

Groups: the segment after "web-" (web-layout-hero -> layout); everything else is "other".
Node size grows with in-degree (how many skills point at it).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import webbrowser
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.S)
FENCE_RE = re.compile(r"```.*?```", re.S)
TICK_RE = re.compile(r"`([^`\n]+)`")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*[a-z0-9]$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.M)
PREVIEW_LINES = 40


# --------------------------------------------------------------------------- scanning

def default_roots() -> list[Path]:
    return [Path.home() / ".claude" / "skills"]


def find_skill_files(roots: list[Path]) -> list[tuple[Path, str]]:
    """Return (SKILL.md path, source label) for every <root>/<skill>/SKILL.md, de-duplicated."""
    out: list[tuple[Path, str]] = []
    seen: set[str] = set()
    for root in roots:
        if not root.is_dir():
            print(f"warning: not a directory: {root}", file=sys.stderr)
            continue
        for d in sorted(root.iterdir()):
            f = d / "SKILL.md"
            if d.is_dir() and f.is_file():
                key = str(f.resolve()).lower()
                if key not in seen:
                    seen.add(key)
                    out.append((f, source_label(root)))
    return out


def source_label(root: Path) -> str:
    home = Path.home()
    try:
        rel = root.resolve().relative_to(home.resolve())
        return "~/" + rel.as_posix()
    except ValueError:
        return str(root)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Tiny YAML-ish parser: enough for name / description (quoted, plain or folded over lines)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta: dict[str, str] = {}
    key = None
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        if indent == 0 and ":" in raw:
            key, _, val = raw.partition(":")
            key = key.strip()
            val = val.strip()
            if val in (">", "|", ">-", "|-"):
                val = ""
            meta[key] = val.strip('"').strip("'")
        elif key and indent > 0:
            meta[key] = (meta[key] + " " + raw.strip()).strip()
    return meta, text[m.end():]


def group_of(name: str) -> str:
    if name.startswith("web-"):
        rest = name[4:]
        return rest.split("-", 1)[0] or "other"
    return "other"


def related_section(body: str) -> str:
    """Text of the first heading whose title starts with 'Related', up to the next heading of equal or higher level."""
    heads = list(HEADING_RE.finditer(body))
    for i, h in enumerate(heads):
        if h.group(2).lower().startswith("related"):
            level = len(h.group(1))
            end = len(body)
            for nxt in heads[i + 1:]:
                if len(nxt.group(1)) <= level:
                    end = nxt.start()
                    break
            return body[h.end():end]
    return ""


def related_names(section: str) -> list[str]:
    """Skill names referenced in a Related section.

    Bullets look like "- `web-perf-images` for lazy loading, `fetchpriority` and CLS": only the
    first backticked token of each bullet names a skill; later ones are prose. A section with no
    bullets falls back to every backticked slug in it.
    """
    section = FENCE_RE.sub("", section)
    names: list[str] = []
    bullets = [ln for ln in section.splitlines() if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", ln)]
    if bullets:
        for ln in bullets:
            m = TICK_RE.search(ln)
            if m:
                names.append(m.group(1).strip())
    else:
        names = [t.strip() for t in TICK_RE.findall(section)]
    return [t for t in names if SLUG_RE.match(t)]


def scan(files: list[tuple[Path, str]]) -> dict:
    nodes: list[dict] = []
    by_name: dict[str, dict] = {}
    for f, source in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"warning: cannot read {f}: {e}", file=sys.stderr)
            continue
        meta, body = parse_frontmatter(text)
        folder = f.parent.name
        name = (meta.get("name") or folder).strip()
        rel_names = related_names(related_section(body))
        mention_pool = [t.strip() for t in TICK_RE.findall(FENCE_RE.sub("", body))]
        node = {
            "id": name,
            "name": name,
            "folder": folder,
            "nameMismatch": name != folder,
            "description": meta.get("description", "").strip(),
            "group": group_of(name),
            "source": source,
            "file": str(f),
            "lines": sum(1 for _ in text.splitlines()),
            "preview": "\n".join(text.splitlines()[:PREVIEW_LINES]),
            "_related": list(dict.fromkeys(rel_names)),
            "_mentions": list(dict.fromkeys(mention_pool)),
            "ghost": False,
        }
        if name in by_name:
            print(f"warning: duplicate skill name {name!r}: {by_name[name]['file']} and {f}", file=sys.stderr)
            node["id"] = f"{name}@{source}"
            node["duplicate"] = True
        nodes.append(node)
        by_name.setdefault(name, node)

    edges: list[dict] = []
    ghosts: dict[str, dict] = {}
    seen_pairs: set[tuple[str, str]] = set()

    def add_edge(src: dict, tgt_id: str, kind: str) -> None:
        if tgt_id == src["id"] or (src["id"], tgt_id) in seen_pairs:
            return
        seen_pairs.add((src["id"], tgt_id))
        edges.append({"source": src["id"], "target": tgt_id, "kind": kind})

    for n in nodes:
        for target in n["_related"]:
            if target == n["name"]:
                continue
            if target in by_name:
                add_edge(n, by_name[target]["id"], "related")
            else:
                if target not in ghosts:
                    ghosts[target] = {
                        "id": "dangling:" + target, "name": target, "folder": "", "nameMismatch": False,
                        "description": "(referenced in a Related skills section but not installed)",
                        "group": group_of(target), "source": "", "file": "", "lines": 0, "preview": "",
                        "ghost": True,
                    }
                add_edge(n, ghosts[target]["id"], "dangling")
        for token in n["_mentions"]:
            if token in by_name and token != n["name"] and token not in n["_related"]:
                add_edge(n, by_name[token]["id"], "mention")

    for n in nodes:
        n.pop("_related", None)
        n.pop("_mentions", None)

    all_nodes = nodes + list(ghosts.values())
    indeg = {n["id"]: 0 for n in all_nodes}
    outdeg = {n["id"]: 0 for n in all_nodes}
    for e in edges:
        indeg[e["target"]] += 1
        outdeg[e["source"]] += 1
    for n in all_nodes:
        n["inDegree"] = indeg[n["id"]]
        n["outDegree"] = outdeg[n["id"]]
        n["isolated"] = (not n["ghost"]) and indeg[n["id"]] == 0 and outdeg[n["id"]] == 0

    groups: dict[str, int] = {}
    for n in all_nodes:
        groups[n["group"]] = groups.get(n["group"], 0) + 1
    group_list = [{"id": g, "count": c} for g, c in sorted(groups.items(), key=lambda kv: (-kv[1], kv[0]))]
    return {"nodes": all_nodes, "edges": edges, "groups": group_list}


# --------------------------------------------------------------------------- html

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skill Brain</title>
<style>
  :root{--bg:#07080f;--panel:#0f1120;--line:#1f2338;--text:#e6e8f2;--muted:#8b90a8;--warn:#ff6b6b;--ghost:#5a5f7a}
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:var(--bg);color:var(--text);font:14px/1.45 system-ui,Segoe UI,Roboto,sans-serif;overflow:hidden}
  #canvas{position:absolute;inset:0;display:block;cursor:grab}
  #top{position:absolute;top:0;left:0;right:0;display:flex;gap:10px;align-items:center;padding:10px 14px;
       background:linear-gradient(to bottom,rgba(7,8,15,.95),rgba(7,8,15,0));pointer-events:none;flex-wrap:wrap}
  #top>*{pointer-events:auto}
  h1{font-size:15px;margin:0;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
  h1 b{color:var(--text)}
  input,select,button{background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:8px;padding:6px 10px;font:inherit}
  input{min-width:220px}
  button{cursor:pointer}
  button:hover{border-color:#3a4060}
  button.on{background:#2a2f52;border-color:#5a63a6}
  .legend{display:flex;gap:8px 10px;flex-wrap:wrap;color:var(--muted);font-size:12px;max-width:60vw}
  .legend span{cursor:pointer;white-space:nowrap}
  .legend span::before{content:"";display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;background:var(--c);box-shadow:0 0 8px var(--c)}
  .legend span.off{opacity:.35}
  #side{position:absolute;top:0;right:0;bottom:0;width:min(460px,100%);background:rgba(15,17,32,.96);border-left:1px solid var(--line);
        transform:translateX(100%);transition:transform .2s;padding:18px;overflow:auto;backdrop-filter:blur(6px)}
  #side.open{transform:none}
  #side h2{margin:0 0 4px;font-size:18px;word-break:break-word;padding-right:28px}
  #side .meta{color:var(--muted);font-size:12px;margin-bottom:12px;word-break:break-all}
  #side .tag{display:inline-block;padding:1px 8px;border-radius:999px;font-size:11px;color:#000;background:var(--c);margin-right:6px}
  #side .flag{display:inline-block;padding:1px 8px;border-radius:999px;font-size:11px;color:#fff;background:#7a2a2a;margin-right:6px}
  #side pre{white-space:pre-wrap;word-break:break-word;background:#0a0b16;border:1px solid var(--line);border-radius:8px;padding:12px;font:12px/1.5 ui-monospace,Consolas,monospace;max-height:45vh;overflow:auto}
  #side .links a{color:#5ad1ff;cursor:pointer;text-decoration:none}
  #side .links a:hover{text-decoration:underline}
  #side .links small{color:var(--muted)}
  #side ul{margin:4px 0 10px;padding-left:18px}
  #side .row{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
  #close{position:absolute;top:10px;right:12px;border:none;background:none;color:var(--muted);font-size:20px;cursor:pointer}
  #status{position:absolute;left:14px;bottom:12px;color:var(--muted);font-size:12px;max-width:60%}
  @media (max-width:700px){input{min-width:140px}.legend{max-width:100%}}
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div id="top">
  <h1>Skill <b>Brain</b></h1>
  <input id="q" placeholder="search skills…">
  <select id="grp"><option value="">all groups</option></select>
  <button id="isoBtn" title="Show only skills with no links in or out">Isolated only</button>
  <button id="mentionBtn" class="on" title="Toggle the fainter 'mentioned in the body' links">Mentions</button>
  <button id="relayout">↻ Shake</button>
  <div class="legend" id="legend"></div>
</div>
<div id="side"><button id="close">×</button><div id="sideBody"></div></div>
<div id="status"></div>
<script>
const DATA = __DATA__;
const PALETTE = ['#5ad1ff','#ff7ab6','#ffb347','#9cff8f','#c3b5ff','#ffe066','#4dd4c0','#ff8c69','#8fd3ff','#f49ac2','#b8e986','#ffd1a1','#a0a8ff','#7ee8fa'];
const COLORS = {};
DATA.groups.forEach((g,i)=>{COLORS[g.id] = g.id==='other' ? '#aab2c8' : PALETTE[i % PALETTE.length]});
const GHOST='#5a5f7a', WARN='#ff6b6b';
const cv=document.getElementById('canvas'), ctx=cv.getContext('2d');
let W=0,H=0,DPR=1, nodes=[], edges=[], byId={};
let view={x:0,y:0,k:1}, drag=null, pan=null, hover=null, selected=null, alpha=1, mouse=null;
let filterGroup='', query='', isoOnly=false, showMentions=true, hiddenGroups=new Set();
const status=m=>{document.getElementById('status').textContent=m};

function resize(){const ow=W,oh=H; DPR=window.devicePixelRatio||1; W=innerWidth; H=innerHeight; cv.width=W*DPR; cv.height=H*DPR; cv.style.width=W+'px'; cv.style.height=H+'px'; ctx.setTransform(DPR,0,0,DPR,0,0);
  if(ow>0&&oh>0){view.x+=(W-ow)/2; view.y+=(H-oh)/2} else {view.x=W/2; view.y=H/2}}
addEventListener('resize',resize); resize();

function load(data){
  const gIdx=Object.fromEntries(data.groups.map((g,i)=>[g.id,i])), G=Math.max(1,data.groups.length);
  const R = G>1 ? Math.min(W,H)*0.32 : 0;
  nodes=data.nodes.map(n=>{const a=(gIdx[n.group]/G)*Math.PI*2, cx=Math.cos(a)*R, cy=Math.sin(a)*R;
    return Object.assign({},n,{x:cx+(Math.random()-.5)*200,y:cy+(Math.random()-.5)*200,vx:0,vy:0,lobeX:cx,lobeY:cy,
      r:(n.ghost?5:7)+Math.min(10,n.inDegree*1.1)})});
  byId=Object.fromEntries(nodes.map(n=>[n.id,n]));
  edges=data.edges.map(e=>({s:byId[e.source],t:byId[e.target],kind:e.kind})).filter(e=>e.s&&e.t);
  const sel=document.getElementById('grp'); sel.innerHTML='<option value="">all groups ('+nodes.filter(n=>!n.ghost).length+' skills)</option>';
  for(const g of data.groups){const o=document.createElement('option');o.value=g.id;o.textContent=g.id+' ('+g.count+')';sel.appendChild(o)}
  const lg=document.getElementById('legend'); lg.innerHTML='';
  for(const g of data.groups){const s=document.createElement('span');s.style.setProperty('--c',COLORS[g.id]);s.textContent=g.id;s.title='click to hide/show this group';
    s.onclick=()=>{if(hiddenGroups.has(g.id))hiddenGroups.delete(g.id);else hiddenGroups.add(g.id);s.classList.toggle('off');alpha=1};lg.appendChild(s)}
  const gh=document.createElement('span');gh.style.setProperty('--c',GHOST);gh.textContent='not installed';lg.appendChild(gh);
  const iso=document.createElement('span');iso.style.setProperty('--c',WARN);iso.textContent='isolated';lg.appendChild(iso);
  const real=nodes.filter(n=>!n.ghost), isoN=real.filter(n=>n.isolated).length, ghostN=nodes.length-real.length;
  status(real.length+' skills · '+edges.length+' links · '+isoN+' isolated · '+ghostN+' dangling · drag, scroll to zoom, click a node to read it');
}

function edgeVisible(e){return (showMentions||e.kind!=='mention') && visible(e.s) && visible(e.t)}
function visible(n){
  if(filterGroup && n.group!==filterGroup) return false;
  if(hiddenGroups.has(n.group)) return false;
  if(isoOnly && !n.isolated) return false;
  if(query){const q=query.toLowerCase(); return (n.name+' '+n.description+' '+n.group).toLowerCase().includes(q)}
  return true;
}

function step(){
  if(alpha<0.003) return;
  const vis=nodes.filter(visible);
  for(let i=0;i<vis.length;i++){const a=vis[i];
    for(let j=i+1;j<vis.length;j++){const b=vis[j];
      let dx=b.x-a.x,dy=b.y-a.y,d2=dx*dx+dy*dy+0.01,d=Math.sqrt(d2); if(d>420) continue;
      const f=3000/d2; dx/=d; dy/=d; a.vx-=dx*f;a.vy-=dy*f;b.vx+=dx*f;b.vy+=dy*f}}
  for(const e of edges){ if(!edgeVisible(e)) continue;
    let dx=e.t.x-e.s.x,dy=e.t.y-e.s.y,d=Math.sqrt(dx*dx+dy*dy)+0.01;
    const f=(d-(e.kind==='mention'?150:100))*(e.kind==='mention'?0.004:0.012); dx/=d;dy/=d;
    e.s.vx+=dx*f;e.s.vy+=dy*f;e.t.vx-=dx*f;e.t.vy-=dy*f}
  for(const n of vis){
    n.vx+=(n.lobeX-n.x)*0.005; n.vy+=(n.lobeY-n.y)*0.005;
    n.vx-=n.x*0.0006; n.vy-=n.y*0.0006;
    if(drag===n){n.vx=n.vy=0;continue}
    n.vx*=0.82;n.vy*=0.82; n.x+=n.vx*alpha; n.y+=n.vy*alpha}
  alpha*=0.99;
}
function toScreen(n){return [view.x+n.x*view.k,view.y+n.y*view.k]}
function fromScreen(sx,sy){return [(sx-view.x)/view.k,(sy-view.y)/view.k]}

let t0=performance.now();
function draw(now){
  const t=(now-t0)/1000; ctx.clearRect(0,0,W,H);
  const g=ctx.createRadialGradient(W/2,H/2,20,W/2,H/2,Math.max(W,H)*0.7);
  g.addColorStop(0,'#141733');g.addColorStop(1,'#07080f');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  const connected=new Set(); const focus=hover||selected;
  if(focus) for(const e of edges){if(e.s===focus)connected.add(e.t); if(e.t===focus)connected.add(e.s)}
  for(const e of edges){ if(!edgeVisible(e)) continue;
    const [x1,y1]=toScreen(e.s),[x2,y2]=toScreen(e.t);
    const mx=(x1+x2)/2+(y2-y1)*0.15,my=(y1+y2)/2-(x2-x1)*0.15;
    const hot=focus&&(e.s===focus||e.t===focus);
    ctx.beginPath();ctx.moveTo(x1,y1);ctx.quadraticCurveTo(mx,my,x2,y2);
    ctx.strokeStyle= hot?'rgba(255,255,255,.75)' : e.kind==='dangling'?'rgba(255,107,107,.45)' : e.kind==='mention'?'rgba(120,140,255,.12)' : 'rgba(120,140,255,.3)';
    ctx.lineWidth=hot?2:(e.kind==='mention'?0.8:1.2); ctx.setLineDash(e.kind==='dangling'?[4,5]:[]); ctx.stroke(); ctx.setLineDash([]);
    if(e.kind!=='mention'||hot){const p=((t*0.35)+(e.s.x*0.001))%1,u=1-p;
      const px=u*u*x1+2*u*p*mx+p*p*x2,py=u*u*y1+2*u*p*my+p*p*y2;
      ctx.beginPath();ctx.arc(px,py,hot?2.6:1.6,0,7);ctx.fillStyle=hot?'#fff':'rgba(160,180,255,.8)';ctx.fill()}
  }
  for(const n of nodes){ if(!visible(n)) continue;
    const [x,y]=toScreen(n); const c=n.ghost?GHOST:(COLORS[n.group]||'#aab2c8');
    const dim=focus&&n!==focus&&!connected.has(n);
    const r=n.r*Math.min(1.6,Math.max(.6,view.k))*(n===focus?1.25:1);
    ctx.globalAlpha=dim?0.22:1;
    const glow=ctx.createRadialGradient(x,y,r*0.3,x,y,r*3.2); glow.addColorStop(0,c+'66'); glow.addColorStop(1,c+'00');
    ctx.fillStyle=glow;ctx.beginPath();ctx.arc(x,y,r*3.2,0,7);ctx.fill();
    ctx.beginPath();ctx.arc(x,y,r,0,7);
    if(n.ghost){ctx.strokeStyle=c;ctx.setLineDash([3,3]);ctx.lineWidth=1.5;ctx.stroke();ctx.setLineDash([]);ctx.fillStyle='#0b0c18';ctx.fill()}
    else{ctx.fillStyle=c;ctx.fill();ctx.strokeStyle='rgba(255,255,255,.5)';ctx.lineWidth=1;ctx.stroke()}
    if(n.isolated){ctx.strokeStyle=WARN;ctx.lineWidth=2;ctx.setLineDash([2,3]);ctx.beginPath();ctx.arc(x,y,r+5,0,7);ctx.stroke();ctx.setLineDash([])}
    if(view.k>0.7||n===focus||connected.has(n)||n.inDegree>=6){
      ctx.font=(n===focus?'600 13px':'12px')+' system-ui,sans-serif';ctx.fillStyle=dim?'#8b90a8':'#e6e8f2';ctx.textAlign='center';
      ctx.fillText(short(n.name),x,y+r+14)}
    ctx.globalAlpha=1;
  }
  if(hover){const [x,y]=toScreen(hover); const txt=hover.name+' — '+(hover.description||'(no description)')+'  ['+hover.inDegree+' in / '+hover.outDegree+' out]';
    ctx.font='12px system-ui,sans-serif'; const w=Math.min(380,ctx.measureText(txt).width+16);
    const lines=wrap(txt,w-16); const h=lines.length*16+10;
    let bx=x+16,by=y-h/2; if(bx+w>W-8)bx=x-16-w; if(by<70)by=70; if(by+h>H-8)by=H-8-h;
    ctx.fillStyle='rgba(15,17,32,.95)';ctx.strokeStyle='#3a4060';roundRect(bx,by,w,h,8);ctx.fill();ctx.stroke();
    ctx.fillStyle='#e6e8f2';ctx.textAlign='left';lines.forEach((l,i)=>ctx.fillText(l,bx+8,by+17+i*16))}
  step(); requestAnimationFrame(draw);
}
function short(n){return n.startsWith('web-')?n.slice(4):n}
function roundRect(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath()}
function wrap(text,maxW){const words=text.split(/\s+/),out=[];let line='';for(const w of words){const t=line?line+' '+w:w;if(ctx.measureText(t).width>maxW&&line){out.push(line);line=w}else line=t}if(line)out.push(line);return out}

function nodeAt(sx,sy){let best=null,bd=1e9;for(const n of nodes){if(!visible(n))continue;const [x,y]=toScreen(n);const d=Math.hypot(sx-x,sy-y);const r=Math.max(10,n.r*view.k+4);if(d<r&&d<bd){best=n;bd=d}}return best}
cv.addEventListener('mousedown',e=>{const n=nodeAt(e.offsetX,e.offsetY);
  if(n){const [wx,wy]=fromScreen(e.offsetX,e.offsetY);drag=n;drag._moved=false;drag._sx=e.offsetX;drag._sy=e.offsetY;drag._ox=n.x-wx;drag._oy=n.y-wy}
  else pan={x:e.offsetX,y:e.offsetY,vx:view.x,vy:view.y}; cv.style.cursor='grabbing'});
addEventListener('mousemove',e=>{const r=cv.getBoundingClientRect();const sx=e.clientX-r.left,sy=e.clientY-r.top;mouse=[sx,sy];
  if(drag){if(!drag._moved&&Math.hypot(sx-drag._sx,sy-drag._sy)>4)drag._moved=true;
    if(drag._moved){const [x,y]=fromScreen(sx,sy);drag.x=x+drag._ox;drag.y=y+drag._oy;alpha=Math.max(alpha,0.3)}}
  else if(pan){view.x=pan.vx+(sx-pan.x);view.y=pan.vy+(sy-pan.y)}
  else hover=nodeAt(sx,sy)});
addEventListener('mouseup',()=>{if(drag&&!drag._moved)openSide(drag);drag=null;pan=null;cv.style.cursor='grab'});
cv.addEventListener('wheel',e=>{e.preventDefault();const f=Math.exp(-e.deltaY*0.0012);const k=Math.min(4,Math.max(.15,view.k*f));view.x=e.offsetX-(e.offsetX-view.x)*(k/view.k);view.y=e.offsetY-(e.offsetY-view.y)*(k/view.k);view.k=k},{passive:false});
cv.addEventListener('dblclick',e=>{const n=nodeAt(e.offsetX,e.offsetY);if(n){view.k=1.6;view.x=W/2-n.x*view.k;view.y=H/2-n.y*view.k}});

function openSide(n){
  selected=n; const c=n.ghost?GHOST:COLORS[n.group];
  const out=edges.filter(e=>e.s===n), inn=edges.filter(e=>e.t===n);
  const li=(other,kind)=>'<li><a data-id="'+other.id+'">'+esc(other.name)+'</a> <small>'+kind+(other.ghost?' · not installed':'')+'</small></li>';
  document.getElementById('sideBody').innerHTML=
    '<h2>'+esc(n.name)+'</h2><div class="meta"><span class="tag" style="--c:'+c+'">'+esc(n.group)+'</span>'+
    (n.isolated?'<span class="flag">isolated</span>':'')+(n.ghost?'<span class="flag">not installed</span>':'')+(n.nameMismatch?'<span class="flag">name ≠ folder '+esc(n.folder)+'</span>':'')+(n.duplicate?'<span class="flag">duplicate name</span>':'')+
    (n.file?'<br>'+esc(n.file)+' · '+n.lines+' lines':'')+'</div>'+
    (n.description?'<p>'+esc(n.description)+'</p>':'')+
    (n.ghost?'<p style="color:var(--muted)">Other skills point at this name but no SKILL.md exists for it. Ask Claude to write it, or fix the reference.</p>'
            :'<b>First '+__PREVIEW__+' lines</b><pre>'+esc(n.preview||'(empty)')+'</pre>')+
    (n.file?'<div class="row"><button id="copyPath">Copy file path</button></div>':'')+
    '<div class="links"><b>Links out ('+out.length+')</b><ul>'+out.map(e=>li(e.t,e.kind)).join('')+'</ul>'+
    '<b>Linked from ('+inn.length+')</b><ul>'+inn.map(e=>li(e.s,e.kind)).join('')+'</ul></div>';
  document.getElementById('side').classList.add('open');
  document.querySelectorAll('#side .links a').forEach(a=>a.onclick=()=>{const m=byId[a.dataset.id];if(m){openSide(m);view.x=W/2-m.x*view.k;view.y=H/2-m.y*view.k}});
  const cp=document.getElementById('copyPath'); if(cp) cp.onclick=()=>navigator.clipboard&&navigator.clipboard.writeText(n.file).then(()=>status('Copied '+n.file));
}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
document.getElementById('close').onclick=()=>{document.getElementById('side').classList.remove('open');selected=null};
addEventListener('keydown',e=>{if(e.key==='Escape'){document.getElementById('side').classList.remove('open');selected=null}});
document.getElementById('relayout').onclick=()=>{for(const n of nodes){n.x+=(Math.random()-.5)*80;n.y+=(Math.random()-.5)*80}alpha=1};
document.getElementById('q').oninput=e=>{query=e.target.value.trim();alpha=Math.max(alpha,.5)};
document.getElementById('grp').onchange=e=>{filterGroup=e.target.value;alpha=1};
document.getElementById('isoBtn').onclick=e=>{isoOnly=!isoOnly;e.target.classList.toggle('on',isoOnly);alpha=1};
document.getElementById('mentionBtn').onclick=e=>{showMentions=!showMentions;e.target.classList.toggle('on',showMentions);alpha=1};

load(DATA); requestAnimationFrame(draw);
</script>
</body>
</html>
"""


def render(graph: dict) -> str:
    data = json.dumps(graph).replace("</", "<\\/")
    return HTML.replace("__DATA__", data).replace("__PREVIEW__", str(PREVIEW_LINES))


# --------------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", action="append", default=[], type=Path, help="an extra folder of <skill>/SKILL.md to scan (repeatable)")
    ap.add_argument("--project", action="append", default=[], type=Path, help="a project folder; its .claude/skills is scanned too (repeatable)")
    ap.add_argument("--no-user", action="store_true", help="skip ~/.claude/skills")
    ap.add_argument("--out", default=Path("skill-brain.html"), type=Path, help="where to write the page (default skill-brain.html)")
    ap.add_argument("--open", action="store_true", help="open the page in the browser when done")
    ap.add_argument("--json", action="store_true", help="print the graph as JSON and exit")
    a = ap.parse_args(argv)

    roots: list[Path] = [] if a.no_user else default_roots()
    roots += a.dir
    for p in a.project:
        roots.append(p / ".claude" / "skills")
    files = find_skill_files(roots)
    if not files:
        print("No SKILL.md files found.", file=sys.stderr)
        return 1

    graph = scan(files)
    real = [n for n in graph["nodes"] if not n["ghost"]]
    isolated = [n["name"] for n in real if n["isolated"]]
    dangling = [n["name"] for n in graph["nodes"] if n["ghost"]]
    kinds: dict[str, int] = {}
    for e in graph["edges"]:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    print(f"Scanned {len(files)} skills in {len(roots)} folder(s): {len(real)} skills, {len(graph['edges'])} links "
          f"({kinds.get('related', 0)} related, {kinds.get('mention', 0)} mentions, {kinds.get('dangling', 0)} dangling), "
          f"{len(graph['groups'])} groups, {len(isolated)} isolated, {len(dangling)} dangling targets", file=sys.stderr)
    if isolated:
        print("  isolated: " + ", ".join(isolated), file=sys.stderr)
    if dangling:
        print("  dangling: " + ", ".join(dangling), file=sys.stderr)

    if a.json:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        print(json.dumps(graph, indent=2, ensure_ascii=False))
        return 0

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(render(graph), encoding="utf-8")
    print(f"Wrote {a.out.resolve()}", file=sys.stderr)
    if a.open:
        webbrowser.open(a.out.resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
