#!/usr/bin/env python3
"""
memory-brain: render every Claude Code memory as a node in an interactive
"brain" graph, with [[wiki-links]] between memories drawn as synapses.

Usage
  python build_brain.py                       # scan ~/.claude/projects/*/memory, write memory-brain.html, open it
  python build_brain.py --serve               # same, but serve on http://127.0.0.1:8765 so the page can SAVE
                                              # new connections straight back into the memory files
  python build_brain.py --memory-dir DIR ...  # scan one or more specific memory folders instead
  python build_brain.py --out brain.html --no-open

Memory file format this understands (the Claude Code memory layout):

  ---
  name: some-slug
  description: one line
  metadata:
    type: user | feedback | project | reference
  ---
  body text with [[other-slug]] links

MEMORY.md (the index) is skipped. A [[link]] that points at a memory which does
not exist is shown as a dashed "ghost" node, so you can see what is still worth
writing.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.S)
LINK_RE = re.compile(r"\[\[([^\]\|#]+?)(?:[#|][^\]]*)?\]\]")
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`", re.S)  # fenced and inline code: [[x]] inside is syntax talk, not a link
TYPES = ("user", "feedback", "project", "reference")


# --------------------------------------------------------------------------- scanning

def default_roots() -> list[Path]:
    home = Path.home()
    return [home / ".claude" / "projects"]


def find_memory_dirs(roots: list[Path], explicit: list[Path]) -> list[Path]:
    dirs: list[Path] = []
    for d in explicit:
        if d.is_dir():
            dirs.append(d)
        else:
            print(f"warning: not a directory: {d}", file=sys.stderr)
    for root in roots:
        if not root.is_dir():
            continue
        for proj in sorted(root.iterdir()):
            mem = proj / "memory"
            if mem.is_dir():
                dirs.append(mem)
    # de-dupe, keep order
    seen, out = set(), []
    for d in dirs:
        key = str(d.resolve()).lower()
        if key not in seen:
            seen.add(key)
            out.append(d)
    return out


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Tiny YAML-ish parser: enough for name / description / metadata.type."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta: dict = {}
    current: dict | None = None
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if indent == 0:
            if val == "":
                current = {}
                meta[key] = current
            else:
                meta[key] = val
                current = None
        elif current is not None:
            current[key] = val
    return meta, text[m.end():]


def project_label(mem_dir: Path) -> str:
    """Turn a Claude project slug like C--Users-Me-Downloads-FanControlApp into something readable."""
    slug = mem_dir.parent.name
    home_slug = re.sub(r"[\\/:]", "-", str(Path.home())).strip("-")
    if slug.startswith(home_slug):
        slug = slug[len(home_slug):].lstrip("-") or "home"
    slug = re.sub(r"^C-+", "", slug)
    if len(slug) > 48:
        slug = "…" + slug[-47:]
    return slug


def scan(mem_dirs: list[Path]) -> dict:
    nodes: list[dict] = []
    by_name: dict[str, list[dict]] = {}
    for mem_dir in mem_dirs:
        project = project_label(mem_dir)
        pid = str(mem_dir.resolve())
        for f in sorted(mem_dir.glob("*.md")):
            if f.name.upper() == "MEMORY.MD":
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except Exception as e:  # noqa: BLE001
                print(f"warning: cannot read {f}: {e}", file=sys.stderr)
                continue
            meta, body = parse_frontmatter(text)
            name = str(meta.get("name") or f.stem).strip()
            mtype = ""
            md = meta.get("metadata")
            if isinstance(md, dict):
                mtype = str(md.get("type", "")).strip().lower()
            if mtype not in TYPES:
                mtype = "other"
            node = {
                "id": f"{pid}::{name}",
                "name": name,
                "description": str(meta.get("description", "")).strip(),
                "type": mtype,
                "project": project,
                "projectId": pid,
                "file": str(f),
                "body": body.strip(),
                "links": [l.strip() for l in LINK_RE.findall(CODE_RE.sub("", body))],
                "ghost": False,
            }
            nodes.append(node)
            by_name.setdefault(name, []).append(node)

    # resolve links: same project first, then any project, else a ghost node
    edges: list[dict] = []
    ghosts: dict[str, dict] = {}
    for n in nodes:
        for target in dict.fromkeys(n["links"]):  # unique, ordered
            cands = by_name.get(target, [])
            same = [c for c in cands if c["projectId"] == n["projectId"]]
            pick = (same or cands or [None])[0]
            if pick is None:
                gid = f"{n['projectId']}::{target}"
                if gid not in ghosts:
                    ghosts[gid] = {
                        "id": gid, "name": target, "description": "(not written yet)",
                        "type": "ghost", "project": n["project"], "projectId": n["projectId"],
                        "file": "", "body": "", "links": [], "ghost": True,
                    }
                pick = ghosts[gid]
            edges.append({"source": n["id"], "target": pick["id"]})

    projects = []
    seen = set()
    for n in nodes + list(ghosts.values()):
        if n["projectId"] not in seen:
            seen.add(n["projectId"])
            projects.append({"id": n["projectId"], "label": n["project"]})
    return {"nodes": nodes + list(ghosts.values()), "edges": edges, "projects": projects}


# --------------------------------------------------------------------------- editing

def add_link(source_file: Path, target_name: str) -> bool:
    """Append [[target_name]] to the memory body. Returns False if it was already there."""
    text = source_file.read_text(encoding="utf-8")
    if re.search(r"\[\[" + re.escape(target_name) + r"(?:[#|][^\]]*)?\]\]", text):
        return False
    m = FRONTMATTER_RE.match(text)
    head, body = (text[:m.end()], text[m.end():]) if m else ("", text)
    lines = body.rstrip("\n").split("\n") if body.strip() else []
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].lower().startswith("related:"):
            lines[i] = lines[i].rstrip() + f", [[{target_name}]]"
            break
    else:
        if lines:
            lines.append("")
        lines.append(f"Related: [[{target_name}]]")
    source_file.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")
    return True


def remove_link(source_file: Path, target_name: str) -> bool:
    text = source_file.read_text(encoding="utf-8")
    pat = re.compile(r"(,\s*)?\[\[" + re.escape(target_name) + r"(?:[#|][^\]]*)?\]\](\s*,)?")
    new, n = pat.subn(lambda m: "" if (m.group(1) or m.group(2)) else "", text)
    if n == 0:
        return False
    new = re.sub(r"^Related:\s*$\n?", "", new, flags=re.M)  # drop an emptied Related: line
    source_file.write_text(new, encoding="utf-8")
    return True


# --------------------------------------------------------------------------- html

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Memory Brain</title>
<style>
  :root{
    --bg:#07080f; --panel:#0f1120; --line:#1f2338; --text:#e6e8f2; --muted:#8b90a8;
    --user:#ff7ab6; --feedback:#ffb347; --project:#5ad1ff; --reference:#9cff8f; --other:#c3b5ff; --ghost:#5a5f7a;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:var(--bg);color:var(--text);font:14px/1.45 system-ui,Segoe UI,Roboto,sans-serif;overflow:hidden}
  #canvas{position:absolute;inset:0;display:block;cursor:grab}
  #canvas.linking{cursor:crosshair}
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
  .legend{display:flex;gap:10px;flex-wrap:wrap;color:var(--muted);font-size:12px}
  .legend span::before{content:"";display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;background:var(--c);box-shadow:0 0 8px var(--c)}
  #side{position:absolute;top:0;right:0;bottom:0;width:min(420px,100%);background:rgba(15,17,32,.96);border-left:1px solid var(--line);
        transform:translateX(100%);transition:transform .2s;padding:18px;overflow:auto;backdrop-filter:blur(6px)}
  #side.open{transform:none}
  #side h2{margin:0 0 4px;font-size:18px;word-break:break-word}
  #side .meta{color:var(--muted);font-size:12px;margin-bottom:12px;word-break:break-all}
  #side .tag{display:inline-block;padding:1px 8px;border-radius:999px;font-size:11px;color:#000;background:var(--c);margin-right:6px}
  #side pre{white-space:pre-wrap;word-break:break-word;background:#0a0b16;border:1px solid var(--line);border-radius:8px;padding:12px;font:13px/1.5 ui-monospace,Consolas,monospace}
  #side .links a{color:var(--project);cursor:pointer;text-decoration:none}
  #side .links a:hover{text-decoration:underline}
  #side .row{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
  #close{position:absolute;top:10px;right:12px;border:none;background:none;color:var(--muted);font-size:20px}
  #status{position:absolute;left:14px;bottom:12px;color:var(--muted);font-size:12px;max-width:60%}
  #hint{position:absolute;left:50%;top:60px;transform:translateX(-50%);background:#2a2f52;border:1px solid #5a63a6;border-radius:999px;padding:6px 14px;font-size:13px;display:none}
  .x{color:#ff8080;cursor:pointer;margin-left:4px}
  @media (max-width:700px){input{min-width:140px}}
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<div id="top">
  <h1>Memory <b>Brain</b></h1>
  <input id="q" placeholder="search memories…">
  <select id="proj"><option value="">all projects</option></select>
  <button id="linkBtn" title="Click one node, then another, to wire them together">⚡ Connect</button>
  <button id="relayout">↻ Shake</button>
  <div class="legend">
    <span style="--c:var(--user)">user</span><span style="--c:var(--feedback)">feedback</span>
    <span style="--c:var(--project)">project</span><span style="--c:var(--reference)">reference</span>
    <span style="--c:var(--ghost)">not written yet</span>
  </div>
</div>
<div id="hint"></div>
<div id="side"><button id="close">×</button><div id="sideBody"></div></div>
<div id="status"></div>
<script>
const DATA = __DATA__;
const SERVE = __SERVE__;
const COLORS = {user:'#ff7ab6',feedback:'#ffb347',project:'#5ad1ff',reference:'#9cff8f',other:'#c3b5ff',ghost:'#5a5f7a'};
const cv = document.getElementById('canvas'), ctx = cv.getContext('2d');
let W=0,H=0,DPR=1;
let nodes=[], edges=[], byId={};
let view={x:0,y:0,k:1}, drag=null, pan=null, hover=null, selected=null, linkMode=false, linkFrom=null, alpha=1;
let filterProj='', query='';
const status = (m)=>{document.getElementById('status').textContent=m};
const hint = (m)=>{const h=document.getElementById('hint'); h.style.display=m?'block':'none'; h.textContent=m||''};

function resize(){const ow=W,oh=H; DPR=window.devicePixelRatio||1; W=innerWidth; H=innerHeight; cv.width=W*DPR; cv.height=H*DPR; cv.style.width=W+'px'; cv.style.height=H+'px'; ctx.setTransform(DPR,0,0,DPR,0,0);
  // keep the graph centred: shift by half the size change, or centre outright if the window had no size yet (embedded panes start at 0x0)
  if(ow>0&&oh>0){view.x+=(W-ow)/2; view.y+=(H-oh)/2} else {view.x=W/2; view.y=H/2}}
addEventListener('resize',resize); resize();

function load(data, keepPos){
  const prevN=nodes.length, prevE=edges.length;
  const old = keepPos ? Object.fromEntries(nodes.map(n=>[n.id,n])) : {};
  const projIdx = Object.fromEntries(data.projects.map((p,i)=>[p.id,i]));
  const P = Math.max(1,data.projects.length);
  nodes = data.nodes.map(n=>{
    const o = old[n.id];
    // seed each project in its own "lobe" around a ring so clusters don't start on top of each other
    const a = (projIdx[n.projectId]/P)*Math.PI*2, R = P>1 ? Math.min(W,H)*0.28 : 0;
    const cx = Math.cos(a)*R, cy = Math.sin(a)*R;
    return Object.assign({}, n, {
      x: o?o.x:cx+(Math.random()-.5)*160, y: o?o.y:cy+(Math.random()-.5)*160, vx:0, vy:0,
      lobeX:cx, lobeY:cy, deg:0, r: n.ghost?6:8,
    });
  });
  byId = Object.fromEntries(nodes.map(n=>[n.id,n]));
  edges = data.edges.map(e=>({s:byId[e.source], t:byId[e.target]})).filter(e=>e.s&&e.t);
  for(const e of edges){e.s.deg++; e.t.deg++}
  for(const n of nodes) n.r = (n.ghost?5:7) + Math.min(8, n.deg*1.3);
  const sel = document.getElementById('proj'); sel.innerHTML='<option value="">all projects ('+nodes.length+' memories)</option>';
  for(const p of data.projects){const o=document.createElement('option');o.value=p.id;o.textContent=p.label;sel.appendChild(o)}
  sel.value=filterProj;
  if(selected) selected = byId[selected.id]||null;
  if(!keepPos){view={x:W/2,y:H/2,k:1}}
  // only re-heat the layout when something actually changed; the periodic refresh must not keep the graph jiggling
  if(!keepPos || nodes.length!==prevN || edges.length!==prevE) alpha=1;
  status(nodes.length+' memories · '+edges.length+' connections · drag nodes, scroll to zoom, click a node to read it');
}

function visible(n){
  if(filterProj && n.projectId!==filterProj) return false;
  if(query){const q=query.toLowerCase(); return (n.name+' '+n.description+' '+n.body+' '+n.project).toLowerCase().includes(q)}
  return true;
}

function step(){
  if(alpha<0.003) return;
  const vis = nodes.filter(visible);
  // repulsion
  for(let i=0;i<vis.length;i++){const a=vis[i];
    for(let j=i+1;j<vis.length;j++){const b=vis[j];
      let dx=b.x-a.x, dy=b.y-a.y, d2=dx*dx+dy*dy+0.01, d=Math.sqrt(d2);
      if(d>400) continue;
      const f = 2600/d2;
      dx/=d; dy/=d;
      a.vx-=dx*f; a.vy-=dy*f; b.vx+=dx*f; b.vy+=dy*f;
    }}
  // springs
  for(const e of edges){ if(!visible(e.s)||!visible(e.t)) continue;
    let dx=e.t.x-e.s.x, dy=e.t.y-e.s.y, d=Math.sqrt(dx*dx+dy*dy)+0.01;
    const f=(d-90)*0.015; dx/=d; dy/=d;
    e.s.vx+=dx*f; e.s.vy+=dy*f; e.t.vx-=dx*f; e.t.vy-=dy*f;
  }
  // gentle pull to the project's lobe + to centre
  for(const n of vis){
    n.vx+=(n.lobeX-n.x)*0.004; n.vy+=(n.lobeY-n.y)*0.004;
    n.vx-=n.x*0.0008; n.vy-=n.y*0.0008;
    if(drag===n){n.vx=n.vy=0; continue}
    n.vx*=0.82; n.vy*=0.82;
    n.x+=n.vx*alpha; n.y+=n.vy*alpha;
  }
  alpha*=0.99;
}

function toScreen(n){return [view.x+n.x*view.k, view.y+n.y*view.k]}
function fromScreen(sx,sy){return [(sx-view.x)/view.k,(sy-view.y)/view.k]}

let t0=performance.now();
function draw(now){
  const t=(now-t0)/1000;
  ctx.clearRect(0,0,W,H);
  // soft brain-ish glow background
  const g=ctx.createRadialGradient(W/2,H/2,20,W/2,H/2,Math.max(W,H)*0.7);
  g.addColorStop(0,'#141733'); g.addColorStop(1,'#07080f'); ctx.fillStyle=g; ctx.fillRect(0,0,W,H);

  const connected = new Set();
  const focus = hover||selected;
  if(focus) for(const e of edges){ if(e.s===focus) connected.add(e.t); if(e.t===focus) connected.add(e.s) }

  // edges as curved synapses with a travelling pulse
  for(const e of edges){ if(!visible(e.s)||!visible(e.t)) continue;
    const [x1,y1]=toScreen(e.s),[x2,y2]=toScreen(e.t);
    const mx=(x1+x2)/2+(y2-y1)*0.15, my=(y1+y2)/2-(x2-x1)*0.15;
    const hot = focus && (e.s===focus||e.t===focus);
    ctx.beginPath(); ctx.moveTo(x1,y1); ctx.quadraticCurveTo(mx,my,x2,y2);
    ctx.strokeStyle = hot ? 'rgba(255,255,255,.75)' : (e.t.ghost ? 'rgba(120,125,160,.35)' : 'rgba(120,140,255,.28)');
    ctx.lineWidth = hot?2:1.2; ctx.setLineDash(e.t.ghost?[4,5]:[]); ctx.stroke(); ctx.setLineDash([]);
    // pulse
    const p=((t*0.35)+(e.s.x*0.001))%1, u=1-p;
    const px=u*u*x1+2*u*p*mx+p*p*x2, py=u*u*y1+2*u*p*my+p*p*y2;
    ctx.beginPath(); ctx.arc(px,py,hot?2.6:1.6,0,7); ctx.fillStyle=hot?'#fff':'rgba(160,180,255,.8)'; ctx.fill();
  }
  // pending link line
  if(linkMode&&linkFrom&&mouse){const [x1,y1]=toScreen(linkFrom); ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(mouse[0],mouse[1]);ctx.strokeStyle='#fff';ctx.setLineDash([6,6]);ctx.lineWidth=1.5;ctx.stroke();ctx.setLineDash([])}

  // nodes
  for(const n of nodes){ if(!visible(n)) continue;
    const [x,y]=toScreen(n); const c=COLORS[n.type]||COLORS.other;
    const dim = focus && n!==focus && !connected.has(n);
    const r=n.r*Math.min(1.6,Math.max(.6,view.k)) * (n===focus?1.25:1);
    ctx.globalAlpha = dim?0.25:1;
    const glow=ctx.createRadialGradient(x,y,r*0.3,x,y,r*3.2);
    glow.addColorStop(0,c+'66'); glow.addColorStop(1,c+'00'); ctx.fillStyle=glow;
    ctx.beginPath(); ctx.arc(x,y,r*3.2,0,7); ctx.fill();
    ctx.beginPath(); ctx.arc(x,y,r,0,7);
    if(n.ghost){ctx.strokeStyle=c;ctx.setLineDash([3,3]);ctx.lineWidth=1.5;ctx.stroke();ctx.setLineDash([]);ctx.fillStyle='#0b0c18';ctx.fill()}
    else {ctx.fillStyle=c; ctx.fill(); ctx.strokeStyle='rgba(255,255,255,.5)'; ctx.lineWidth=1; ctx.stroke()}
    if(n===linkFrom){ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.beginPath();ctx.arc(x,y,r+4,0,7);ctx.stroke()}
    if(view.k>0.55 || n===focus || connected.has(n)){
      ctx.font=(n===focus?'600 13px':'12px')+' system-ui,sans-serif'; ctx.fillStyle=dim?'#8b90a8':'#e6e8f2';
      ctx.textAlign='center'; ctx.fillText(n.name,x,y+r+14);
    }
    ctx.globalAlpha=1;
  }
  // hover tooltip
  if(hover){const [x,y]=toScreen(hover); const txt=hover.description||'(no description)';
    ctx.font='12px system-ui,sans-serif'; const w=Math.min(360,ctx.measureText(txt).width+16);
    const lines=wrap(txt,w-16); const h=lines.length*16+10;
    let bx=x+16, by=y-h/2; if(bx+w>W-8) bx=x-16-w; if(by<70) by=70; if(by+h>H-8) by=H-8-h;
    ctx.fillStyle='rgba(15,17,32,.95)'; ctx.strokeStyle='#3a4060'; roundRect(bx,by,w,h,8); ctx.fill(); ctx.stroke();
    ctx.fillStyle='#e6e8f2'; ctx.textAlign='left'; lines.forEach((l,i)=>ctx.fillText(l,bx+8,by+17+i*16));
  }
  step(); requestAnimationFrame(draw);
}
function roundRect(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath()}
function wrap(text,maxW){const words=text.split(/\s+/),out=[];let line='';for(const w of words){const t=line?line+' '+w:w;if(ctx.measureText(t).width>maxW&&line){out.push(line);line=w}else line=t}if(line)out.push(line);return out}

// ---------------- interaction
let mouse=null;
function nodeAt(sx,sy){let best=null,bd=1e9;for(const n of nodes){if(!visible(n))continue;const [x,y]=toScreen(n);const d=Math.hypot(sx-x,sy-y);const r=Math.max(10,n.r*view.k+4);if(d<r&&d<bd){best=n;bd=d}}return best}
cv.addEventListener('mousedown',e=>{const n=nodeAt(e.offsetX,e.offsetY);
  if(n){const [wx,wy]=fromScreen(e.offsetX,e.offsetY); drag=n; drag._moved=false; drag._sx=e.offsetX; drag._sy=e.offsetY; drag._ox=n.x-wx; drag._oy=n.y-wy}
  else pan={x:e.offsetX,y:e.offsetY,vx:view.x,vy:view.y}; cv.style.cursor='grabbing'});
addEventListener('mousemove',e=>{const r=cv.getBoundingClientRect(); const sx=e.clientX-r.left, sy=e.clientY-r.top; mouse=[sx,sy];
  if(drag){ // a click is a press that stays within a few pixels; only a real move becomes a drag
    if(!drag._moved && Math.hypot(sx-drag._sx,sy-drag._sy)>4) drag._moved=true;
    if(drag._moved){const [x,y]=fromScreen(sx,sy); drag.x=x+drag._ox; drag.y=y+drag._oy; alpha=Math.max(alpha,0.3)}}
  else if(pan){view.x=pan.vx+(sx-pan.x);view.y=pan.vy+(sy-pan.y)}
  else hover=nodeAt(sx,sy);
});
addEventListener('mouseup',e=>{ if(drag && !drag._moved) clickNode(drag); drag=null; pan=null; cv.style.cursor=linkMode?'crosshair':'grab'});
cv.addEventListener('wheel',e=>{e.preventDefault();const f=Math.exp(-e.deltaY*0.0012);const k=Math.min(4,Math.max(.2,view.k*f));view.x=e.offsetX-(e.offsetX-view.x)*(k/view.k);view.y=e.offsetY-(e.offsetY-view.y)*(k/view.k);view.k=k},{passive:false});
cv.addEventListener('dblclick',e=>{const n=nodeAt(e.offsetX,e.offsetY); if(n){view.k=1.6;view.x=W/2-n.x*view.k;view.y=H/2-n.y*view.k}});

function clickNode(n){
  if(linkMode){
    if(!linkFrom){ if(n.ghost){status('A memory that is not written yet cannot link out. Pick a real one as the start.');return} linkFrom=n; hint('Now click the memory to connect "'+n.name+'" to  (Esc to cancel)'); return }
    if(n===linkFrom){linkFrom=null;hint('Click the first memory to connect');return}
    connect(linkFrom,n); linkFrom=null; hint('Click the first memory to connect'); return;
  }
  selected=n; openSide(n);
}
function openSide(n){
  const c=COLORS[n.type]; const out=edges.filter(e=>e.s===n), inn=edges.filter(e=>e.t===n);
  const li=(e,other,rm)=>'<li><a data-id="'+other.id+'">'+esc(other.name)+'</a> <small style="color:var(--muted)">'+esc(other.project)+'</small>'+(rm&&SERVE?' <span class="x" data-rm="'+e.s.id+'|'+e.t.name+'" title="remove this link">✕</span>':'')+'</li>';
  document.getElementById('sideBody').innerHTML =
    '<h2>'+esc(n.name)+'</h2><div class="meta"><span class="tag" style="--c:'+c+'">'+n.type+'</span>'+esc(n.project)+(n.file?'<br>'+esc(n.file):'')+'</div>'+
    (n.description?'<p>'+esc(n.description)+'</p>':'')+
    (n.ghost?'<p style="color:var(--muted)">This memory is linked to but has not been written yet. Ask Claude to write it, or remove the link.</p>':'<pre>'+esc(n.body||'(empty)')+'</pre>')+
    '<div class="row"><button id="connectFrom">⚡ Connect this to…</button>'+(n.file?'<button id="copyPath">Copy file path</button>':'')+'</div>'+
    '<div class="links"><b>Links out ('+out.length+')</b><ul>'+out.map(e=>li(e,e.t,true)).join('')+'</ul>'+
    '<b>Linked from ('+inn.length+')</b><ul>'+inn.map(e=>li(e,e.s,false)).join('')+'</ul></div>';
  document.getElementById('side').classList.add('open');
  document.querySelectorAll('#side .links a').forEach(a=>a.onclick=()=>{const m=byId[a.dataset.id]; if(m){selected=m;openSide(m);view.x=W/2-m.x*view.k;view.y=H/2-m.y*view.k}});
  document.querySelectorAll('#side .x').forEach(x=>x.onclick=()=>{const [sid,tname]=x.dataset.rm.split('|'); disconnect(byId[sid],tname)});
  document.getElementById('connectFrom').onclick=()=>{setLinkMode(true); linkFrom=n; hint('Now click the memory to connect "'+n.name+'" to  (Esc to cancel)'); document.getElementById('side').classList.remove('open')};
  const cp=document.getElementById('copyPath'); if(cp) cp.onclick=()=>navigator.clipboard&&navigator.clipboard.writeText(n.file).then(()=>status('Copied '+n.file));
}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
document.getElementById('close').onclick=()=>{document.getElementById('side').classList.remove('open');selected=null};
function setLinkMode(on){linkMode=on;linkFrom=null;document.getElementById('linkBtn').classList.toggle('on',on);cv.classList.toggle('linking',on);hint(on?'Click the first memory to connect':'')}
document.getElementById('linkBtn').onclick=()=>setLinkMode(!linkMode);
addEventListener('keydown',e=>{if(e.key==='Escape'){setLinkMode(false);document.getElementById('side').classList.remove('open');selected=null}});
document.getElementById('relayout').onclick=()=>{for(const n of nodes){n.x+=(Math.random()-.5)*80;n.y+=(Math.random()-.5)*80}alpha=1};
document.getElementById('q').oninput=e=>{query=e.target.value.trim();alpha=Math.max(alpha,.5)};
document.getElementById('proj').onchange=e=>{filterProj=e.target.value;alpha=1};

async function connect(a,b){
  if(edges.some(e=>e.s===a&&e.t===b)){status('"'+a.name+'" already links to "'+b.name+'"');return}
  if(!SERVE){
    const line='[['+b.name+']]';
    status('Static page: add '+line+' to '+a.file+' (or ask Claude: "connect '+a.name+' to '+b.name+'")');
    edges.push({s:a,t:b,pending:true}); a.deg++; b.deg++; alpha=1; return;
  }
  const r=await fetch('/api/connect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source:a.id,target:b.id})});
  const j=await r.json(); status(j.message||JSON.stringify(j)); if(j.ok) await refresh();
}
async function disconnect(a,tname){
  const r=await fetch('/api/disconnect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source:a.id,targetName:tname})});
  const j=await r.json(); status(j.message||JSON.stringify(j)); if(j.ok){await refresh(); if(selected) openSide(selected)}
}
let lastSig=JSON.stringify(DATA);
async function refresh(){
  try{const r=await fetch('/api/graph'); const j=await r.json(); const sig=JSON.stringify(j);
    if(sig===lastSig) return;            // nothing changed on disk: leave the page (and whatever the user is reading) alone
    lastSig=sig; load(j,true); if(selected)openSide(selected)}
  catch(e){status('The memory-brain server has stopped; connections can no longer be saved from this page. Re-run build_brain.py --serve.')}
}

load(DATA,false); requestAnimationFrame(draw);
if(SERVE) setInterval(refresh, 5000);   // pick up memories Claude writes while the page is open
</script>
</body>
</html>
"""


def render(graph: dict, serve: bool) -> str:
    data = json.dumps(graph).replace("</", "<\\/")
    return HTML.replace("__DATA__", data).replace("__SERVE__", "true" if serve else "false")


# --------------------------------------------------------------------------- server

def make_handler(mem_dirs: list[Path]):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # quiet
            pass

        def _send(self, code: int, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path.startswith("/api/graph"):
                self._send(200, json.dumps(scan(mem_dirs)).encode(), "application/json")
            else:
                self._send(200, render(scan(mem_dirs), True).encode(), "text/html; charset=utf-8")

        def do_POST(self):
            n = int(self.headers.get("Content-Length", "0"))
            try:
                req = json.loads(self.rfile.read(n) or b"{}")
            except json.JSONDecodeError:
                return self._send(400, b'{"ok":false,"message":"bad json"}', "application/json")
            graph = scan(mem_dirs)
            by_id = {x["id"]: x for x in graph["nodes"]}
            src = by_id.get(req.get("source", ""))
            if not src or not src["file"]:
                return self._send(404, b'{"ok":false,"message":"source memory not found"}', "application/json")
            if self.path == "/api/connect":
                tgt = by_id.get(req.get("target", ""))
                if not tgt:
                    return self._send(404, b'{"ok":false,"message":"target memory not found"}', "application/json")
                changed = add_link(Path(src["file"]), tgt["name"])
                msg = f'Wrote [[{tgt["name"]}]] into {src["name"]}' if changed else "That link already exists"
            elif self.path == "/api/disconnect":
                changed = remove_link(Path(src["file"]), req.get("targetName", ""))
                msg = f'Removed [[{req.get("targetName")}]] from {src["name"]}' if changed else "Link not found"
            else:
                return self._send(404, b'{"ok":false,"message":"unknown endpoint"}', "application/json")
            self._send(200, json.dumps({"ok": True, "changed": changed, "message": msg}).encode(), "application/json")

    return Handler


# --------------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--memory-dir", action="append", default=[], type=Path, help="a specific memory folder (repeatable)")
    ap.add_argument("--root", action="append", default=[], type=Path, help="a projects root to scan for */memory (default ~/.claude/projects)")
    ap.add_argument("--only", default="", help="only memory folders whose path contains this text")
    ap.add_argument("--out", default="memory-brain.html", type=Path, help="where to write the static page")
    ap.add_argument("--serve", action="store_true", help="serve the page so connections can be saved back to the files")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-open", action="store_true", help="do not open a browser")
    ap.add_argument("--json", action="store_true", help="print the graph as JSON and exit")
    a = ap.parse_args(argv)

    roots = a.root or (default_roots() if not a.memory_dir else [])
    mem_dirs = find_memory_dirs(roots, a.memory_dir)
    if a.only:
        mem_dirs = [d for d in mem_dirs if a.only.lower() in str(d).lower()]
    if not mem_dirs:
        print("No memory folders found.", file=sys.stderr)
        return 1

    graph = scan(mem_dirs)
    real = [n for n in graph["nodes"] if not n["ghost"]]
    print(f"Scanned {len(mem_dirs)} memory folder(s): {len(real)} memories, {len(graph['edges'])} links, "
          f"{len(graph['nodes']) - len(real)} not-yet-written targets", file=sys.stderr)

    if a.json:
        print(json.dumps(graph, indent=2))
        return 0

    if a.serve:
        srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(mem_dirs))
        url = f"http://127.0.0.1:{a.port}/"
        print(f"Memory Brain is live at {url}  (connections you draw are saved into the memory files; Ctrl+C to stop)", file=sys.stderr)
        if not a.no_open:
            threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
        return 0

    a.out.write_text(render(graph, False), encoding="utf-8")
    print(f"Wrote {a.out.resolve()}", file=sys.stderr)
    if not a.no_open:
        webbrowser.open(a.out.resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
