#!/usr/bin/env python3
"""
session-timeline: read every Claude Code session log and render a timeline page
of what was worked on when, across projects.

Usage
  python build_timeline.py                      # last 30 days, write session-timeline.html
  python build_timeline.py --days 7 --open      # last week, open in the browser
  python build_timeline.py --days 0             # everything ever logged
  python build_timeline.py --root D:/other/.claude/projects --out t.html
  python build_timeline.py --json               # the per-session data as JSON instead of HTML

Where the logs are
  ~/.claude/projects/<project-slug>/<session-id>.jsonl, one JSON object per line.
  Only lines of type "user" and "assistant" carry the conversation; tool calls are
  {"type":"tool_use","name":"Write","input":{"file_path":...}} blocks inside
  assistant message.content.

What is computed per session
  project label, start, end, wall-clock span, active minutes and active stretches
  (gaps over 30 min are not counted), user turns, tool-use counts by tool name, files
  written or edited (Write / Edit / MultiEdit / NotebookEdit), git commits (Bash
  commands that run `git commit`, with the first line of -m), and a title: the
  session's custom title if one was set, else the first 80 characters of the first
  user message. No other message text is kept.

Robustness
  Lines that are not JSON objects are skipped and counted as badLines; fields with an
  unexpected shape are ignored; a log that cannot be read is skipped with a warning.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import webbrowser
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

GAP_MINUTES = 30            # a pause longer than this does not count as active time
TITLE_CHARS = 80
EDIT_TOOLS = {"Write": "file_path", "Edit": "file_path", "MultiEdit": "file_path", "NotebookEdit": "notebook_path"}
_WORD = r"""(?:"[^"]*"|'[^']*'|[^\s"';&|])+"""     # one shell word, quotes allowed
# `git commit` at the start of a command or after &&, ;, ||, a newline or "(" -- with or without
# git's global options in between (git -c user.name="x" -C dir --no-pager commit ...)
COMMIT_RE = re.compile(
    r"(?:^|&&|;|\|\||\n|\()\s*git(?:\s+(?:-[cC]\s+" + _WORD + r"|--[\w-]+(?:=" + _WORD + r")?|-[pP]))*\s+commit(?![\w-])")
COMMIT_MSG_RE = re.compile(
    r"""(?:\s-a?m\s*|\s--message[= ])(?:"((?:[^"\\]|\\.)*)"|'([^']*)'|\$'([^']*)'|([^\s"';&|]+))""")
HEREDOC_RE = re.compile(r"""<<-?\s*['"]?(\w+)['"]?[^\n]*\n(.*?)\n\s*\1\b""", re.S)
INJECTED_RE = re.compile(
    r"<(system-reminder|local-command-[a-z]+|command-std(?:out|err)|bash-std(?:out|err)|bash-input)>.*?</\1>", re.S)


# --------------------------------------------------------------------------- helpers

def parse_ts(value) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def project_label(slug: str) -> str:
    """C--Users-Me-Downloads-FanControlApp -> Downloads-FanControlApp (best effort: the slug's
    dashes are ambiguous, so the home prefix and drive letter are dropped and the rest kept)."""
    home_slug = re.sub(r"[\\/:]", "-", str(Path.home())).strip("-")
    s = slug
    if s.startswith(home_slug):
        s = s[len(home_slug):].lstrip("-") or "home"
    s = re.sub(r"^[A-Za-z]-+", "", s)
    # scratch workspaces have a very long id-laden slug; keep the tail that still identifies them
    m = re.search(r"(scratch-\d{4}-\d{2}-\d{2}-[0-9a-f]+)$", s)
    if m:
        return "scratch/" + m.group(1)[8:]
    if len(s) > 60:
        s = "..." + s[-57:]
    return s or slug


def prompt_text(content) -> str:
    """What the user typed, cleaned and cut to TITLE_CHARS: a string, or the first text block that is
    not injected context. Tool results, images and <system-reminder> blocks give ""."""
    if isinstance(content, str):
        return clean_title(content)
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str):
                t = clean_title(block["text"])
                if t:
                    return t
    return ""


def commits_in(cmd: str, when: str) -> list[dict]:
    """One entry per `git commit` in a Bash command, with the first line of its -m message (if any)."""
    out = []
    matches = list(COMMIT_RE.finditer(cmd))
    for i, m in enumerate(matches):
        rest = cmd[m.end(): matches[i + 1].start() if i + 1 < len(matches) else len(cmd)]
        subject = ""
        mm = COMMIT_MSG_RE.search(rest)
        if mm:
            subject = next((g for g in mm.groups() if g), "")
            if "<<" in subject:                       # -m "$(cat <<'EOF' ... EOF)"
                hd = HEREDOC_RE.search(rest)
                subject = hd.group(2) if hd else ""
            subject = subject.replace("\\n", "\n").strip()
            subject = subject.splitlines()[0].strip() if subject else ""
        out.append({"when": when, "subject": subject[:TITLE_CHARS]})
    return out


def clean_title(text: str) -> str:
    """At most TITLE_CHARS characters, with injected blocks (<system-reminder>...) and tags removed."""
    text = INJECTED_RE.sub(" ", text[:20000])
    text = re.sub(r"</?[A-Za-z][\w-]{0,40}(?:\s[^>]{0,80})?>", " ", text)   # <command-name> style tags
    text = re.sub(r"\s+", " ", text).strip()
    return text[:TITLE_CHARS]


# --------------------------------------------------------------------------- parsing

def parse_session(path: Path, project: str, slug: str) -> dict | None:
    stamps: list[datetime] = []
    user_turns = 0
    tools: Counter = Counter()
    files: dict[str, Counter] = {}
    commits: list[dict] = []
    title = ""
    custom_title = ""
    session_id = path.stem
    models: Counter = Counter()
    lines_total = lines_bad = 0

    try:
        fh = path.open("r", encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"warning: cannot read {path}: {e}", file=sys.stderr)
        return None
    with fh:
        for raw in fh:
            lines_total += 1
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                lines_bad += 1
                continue
            if not isinstance(obj, dict):
                lines_bad += 1
                continue
            kind = obj.get("type")
            if kind == "custom-title" and isinstance(obj.get("customTitle"), str) and not custom_title:
                custom_title = clean_title(obj["customTitle"])
                continue
            if kind not in ("user", "assistant"):
                continue
            ts = parse_ts(obj.get("timestamp"))
            if ts:
                stamps.append(ts)
            msg = obj.get("message")
            if not isinstance(msg, dict):
                continue
            content = msg.get("content")
            if kind == "user":
                if obj.get("isSidechain") or obj.get("isMeta") or obj.get("isCompactSummary") or "toolUseResult" in obj:
                    continue
                text = prompt_text(content)    # already cut to TITLE_CHARS; no longer message text is kept
                if text:
                    user_turns += 1
                    if not title:
                        title = text
                continue
            # assistant
            model = msg.get("model")
            if isinstance(model, str):
                models[model] += 1
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name = block.get("name")
                if not isinstance(name, str):
                    continue
                tools[name] += 1
                inp = block.get("input")
                if not isinstance(inp, dict):
                    continue
                if name in EDIT_TOOLS:
                    fp = inp.get(EDIT_TOOLS[name])
                    if isinstance(fp, str) and fp:
                        files.setdefault(fp, Counter())[name] += 1
                elif name == "Bash":
                    cmd = inp.get("command")
                    if isinstance(cmd, str) and "commit" in cmd:
                        commits.extend(commits_in(cmd, ts.isoformat() if ts else ""))

    if not stamps:
        return None
    stamps.sort()
    active = timedelta(0)
    segments = [[stamps[0], stamps[0]]]          # runs of activity without a gap over GAP_MINUTES
    for a, b in zip(stamps, stamps[1:]):
        d = b - a
        if d <= timedelta(minutes=GAP_MINUTES):
            active += d
            segments[-1][1] = b
        else:
            segments.append([b, b])
    start, end = stamps[0], stamps[-1]
    return {
        "id": session_id,
        "file": str(path),
        "project": project,
        "slug": slug,
        "title": custom_title or title or "(untitled session)",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "spanMinutes": round((end - start).total_seconds() / 60, 1),
        "activeMinutes": round(active.total_seconds() / 60, 1),
        "segments": [[a.isoformat(), b.isoformat()] for a, b in segments],
        "userTurns": user_turns,
        "tools": dict(tools.most_common()),
        "toolCalls": sum(tools.values()),
        "files": [{"path": p, "ops": dict(c)} for p, c in sorted(files.items())],
        "commits": commits,
        "model": models.most_common(1)[0][0] if models else "",
        "badLines": lines_bad,
        "lines": lines_total,
    }


def scan(roots: list[Path], days: int) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days) if days > 0 else None
    sessions: list[dict] = []
    files_seen = 0
    for root in roots:
        if not root.is_dir():
            print(f"warning: not a directory: {root}", file=sys.stderr)
            continue
        for proj in sorted(root.iterdir()):
            if not proj.is_dir():
                continue
            label = project_label(proj.name)
            for f in sorted(proj.glob("*.jsonl")):
                files_seen += 1
                s = parse_session(f, label, proj.name)
                if s is None:
                    continue
                if cutoff and parse_ts(s["end"]) < cutoff:
                    continue
                sessions.append(s)
    sessions.sort(key=lambda s: s["start"])

    by_project: Counter = Counter()
    all_files: set[str] = set()
    for s in sessions:
        by_project[s["project"]] += s["activeMinutes"]
        all_files.update(f["path"] for f in s["files"])
    projects = [{"label": p, "activeMinutes": round(m, 1), "sessions": sum(1 for s in sessions if s["project"] == p)}
                for p, m in by_project.most_common()]
    summary = {
        "sessions": len(sessions),
        "logFiles": files_seen,
        "activeHours": round(sum(s["activeMinutes"] for s in sessions) / 60, 1),
        "spanHours": round(sum(s["spanMinutes"] for s in sessions) / 60, 1),
        "filesTouched": len(all_files),
        "commits": sum(len(s["commits"]) for s in sessions),
        "userTurns": sum(s["userTurns"] for s in sessions),
        "busiestProject": projects[0]["label"] if projects else "",
        "days": days,
        "generated": datetime.now(timezone.utc).isoformat(),
    }
    return {"sessions": sessions, "projects": projects, "summary": summary}


# --------------------------------------------------------------------------- html

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Session Timeline</title>
<style>
  :root{--bg:#07080f;--panel:#0f1120;--line:#1f2338;--text:#e6e8f2;--muted:#8b90a8;--accent:#5ad1ff;--lane:56px;--label:220px}
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:var(--bg);color:var(--text);font:14px/1.45 system-ui,Segoe UI,Roboto,sans-serif}
  body{display:flex;flex-direction:column;overflow:hidden}
  header{padding:12px 16px 8px;border-bottom:1px solid var(--line);background:linear-gradient(to bottom,#0b0d1a,#07080f)}
  h1{font-size:15px;margin:0 0 10px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
  h1 b{color:var(--text)}
  .cards{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px 14px;min-width:120px}
  .card b{display:block;font-size:20px;line-height:1.2}
  .card span{color:var(--muted);font-size:12px}
  .controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  input,select,button{background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:8px;padding:6px 10px;font:inherit;color-scheme:dark}
  button{cursor:pointer}button:hover{border-color:#3a4060}button.on{background:#2a2f52;border-color:#5a63a6}
  .controls label{color:var(--muted);font-size:12px}
  #wrap{flex:1;position:relative;overflow:auto}
  #axis{position:sticky;top:0;z-index:3;height:44px;background:#0b0d1a;border-bottom:1px solid var(--line)}
  .tick{position:absolute;top:0;bottom:0;border-left:1px solid #1a1e33;font-size:11px;color:var(--muted);padding:4px 0 0 4px;white-space:nowrap}
  .tick.major{border-left-color:#2c3252;color:var(--text)}
  .tick.now{border-left:1px dashed #ffb347;color:#ffb347}
  .lane{position:relative;min-height:var(--lane);border-bottom:1px solid #12152a}
  .lane:nth-child(even){background:rgba(255,255,255,.015)}
  .lane .name{position:sticky;left:0;z-index:2;width:var(--label);height:100%;padding:8px 10px;background:#0a0b17;border-right:1px solid var(--line);font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .lane .name small{display:block;color:var(--muted)}
  .bar{position:absolute;height:26px;border-radius:6px;background:color-mix(in srgb,var(--c) 22%,transparent);border:1px solid color-mix(in srgb,var(--c) 55%,transparent);cursor:pointer;overflow:hidden;font-size:11px;line-height:24px;color:#fff;white-space:nowrap}
  .bar:hover,.bar.sel,.bar:focus-visible{outline:2px solid #fff;z-index:1}
  .bar .seg{position:absolute;top:0;bottom:0;background:var(--c);opacity:.85;pointer-events:none;box-shadow:0 0 8px color-mix(in srgb,var(--c) 60%,transparent)}
  .bar .lbl{position:relative;padding:0 6px;text-shadow:0 0 3px #000,0 0 6px #000;pointer-events:none}
  .gridline{position:absolute;top:0;bottom:0;border-left:1px solid #12152a;pointer-events:none}
  #tip{position:fixed;z-index:10;background:rgba(15,17,32,.97);border:1px solid #3a4060;border-radius:8px;padding:8px 10px;font-size:12px;max-width:360px;pointer-events:none;display:none}
  #tip b{display:block;margin-bottom:4px;font-size:13px}
  #tip .m{color:var(--muted)}
  #side{position:fixed;top:0;right:0;bottom:0;width:min(480px,100%);background:rgba(15,17,32,.97);border-left:1px solid var(--line);transform:translateX(100%);transition:transform .2s;padding:18px;overflow:auto;z-index:20;backdrop-filter:blur(6px)}
  #side.open{transform:none}
  #side h2{margin:0 0 4px;font-size:17px;padding-right:28px;word-break:break-word}
  #side .meta{color:var(--muted);font-size:12px;margin-bottom:12px;word-break:break-all}
  #side .tag{display:inline-block;padding:1px 8px;border-radius:999px;font-size:11px;color:#000;background:var(--c);margin-right:6px}
  #side table{border-collapse:collapse;font-size:12px;margin:6px 0 12px}
  #side td{padding:2px 10px 2px 0;color:var(--muted)}#side td:first-child{color:var(--text)}
  #side details{margin:8px 0}#side summary{cursor:pointer;font-weight:600}
  #side ul{margin:6px 0;padding-left:18px;font:12px/1.5 ui-monospace,Consolas,monospace;word-break:break-all}
  #side ul small{color:var(--muted);font-family:system-ui,sans-serif}
  #close{position:absolute;top:10px;right:12px;border:none;background:none;color:var(--muted);font-size:20px;cursor:pointer}
  #empty{padding:40px;color:var(--muted);text-align:center}
  @media (max-width:700px){:root{--label:120px}.card{min-width:90px}}
</style>
</head>
<body>
<header>
  <h1>Session <b>Timeline</b></h1>
  <div class="cards" id="cards"></div>
  <div class="controls">
    <select id="proj"><option value="">all projects</option></select>
    <input id="q" type="search" placeholder="title, file or commit" aria-label="Filter sessions by title, file path or commit">
    <label>from <input type="date" id="from"></label>
    <label>to <input type="date" id="to"></label>
    <span style="width:8px"></span>
    <button data-zoom="day">Day</button><button data-zoom="week" class="on">Week</button><button data-zoom="month">Month</button>
    <button id="fit">Fit</button><button id="today">Today</button>
    <label id="count"></label>
  </div>
</header>
<div id="wrap"><div id="axis"></div><div id="lanes"></div><div id="empty" hidden>No sessions in this range.</div></div>
<div id="tip"></div>
<div id="side"><button id="close">×</button><div id="sideBody"></div></div>
<script>
const DATA = __DATA__;
const PALETTE=['#5ad1ff','#ff7ab6','#ffb347','#9cff8f','#c3b5ff','#ffe066','#4dd4c0','#ff8c69','#8fd3ff','#f49ac2','#b8e986','#ffd1a1','#a0a8ff','#7ee8fa'];
const COLORS={}; DATA.projects.forEach((p,i)=>COLORS[p.label]=PALETTE[i%PALETTE.length]);
const S = DATA.sessions.map(s=>Object.assign({},s,{t0:new Date(s.start).getTime(),t1:new Date(s.end).getTime(),
  segs:(s.segments||[]).map(([a,b])=>[new Date(a).getTime(),new Date(b).getTime()])}));
const DAY=86400000, ZOOM={day:1400/DAY, week:1400/(7*DAY), month:1400/(30*DAY)};
let pxPerMs=ZOOM.week, filterProj='', from=null, to=null, selected=null;
const $=id=>document.getElementById(id);
const fmtD=t=>new Date(t).toLocaleDateString(undefined,{weekday:'short',month:'short',day:'numeric'});
const fmtT=t=>new Date(t).toLocaleTimeString(undefined,{hour:'2-digit',minute:'2-digit'});
const fmtDT=t=>fmtD(t)+' '+fmtT(t);
const mins=m=>m>=60?(m/60).toFixed(1)+' h':Math.round(m)+' min';
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const base=s=>s.split(/[\\/]/).pop();

let query='';
const matches=s=>!query||s.title.toLowerCase().includes(query)||s.files.some(f=>f.path.toLowerCase().includes(query))||s.commits.some(c=>(c.subject||'').toLowerCase().includes(query));
function shown(){return S.filter(s=>(!filterProj||s.project===filterProj)&&(!from||s.t1>=from)&&(!to||s.t0<=to)&&matches(s))}

function cards(list){
  const files=new Set(); let act=0,commits=0,turns=0; const byP={};
  for(const s of list){s.files.forEach(f=>files.add(f.path));act+=s.activeMinutes;commits+=s.commits.length;turns+=s.userTurns;byP[s.project]=(byP[s.project]||0)+s.activeMinutes}
  const busiest=Object.entries(byP).sort((a,b)=>b[1]-a[1])[0];
  const c=[['sessions',list.length],['active hours',(act/60).toFixed(1)],['files touched',files.size],['commits',commits],['prompts',turns],['busiest project',busiest?busiest[0]:'—']];
  $('cards').innerHTML=c.map(([k,v])=>'<div class="card"><b>'+esc(v)+'</b><span>'+k+'</span></div>').join('');
}

function render(){
  const list=shown(); cards(list);
  $('count').textContent=list.length+' of '+S.length+' sessions · scroll sideways, hover a bar, click for files';
  const lanes=$('lanes'), axis=$('axis'); lanes.innerHTML=''; axis.innerHTML='';
  $('empty').hidden=list.length>0; if(!list.length){axis.style.width='';return}
  let lo=Math.min(...list.map(s=>s.t0)), hi=Math.max(...list.map(s=>s.t1),Date.now());
  const d0=new Date(lo); d0.setHours(0,0,0,0); lo=d0.getTime()-DAY*0.25; hi=hi+DAY*0.5;
  const LABEL=parseInt(getComputedStyle(document.documentElement).getPropertyValue('--label'))||220;
  const width=LABEL+(hi-lo)*pxPerMs; axis.style.width=lanes.style.width=width+'px';
  const X=t=>LABEL+(t-lo)*pxPerMs;
  // ticks
  const stepMs = pxPerMs*DAY>600 ? DAY/4 : pxPerMs*DAY>120 ? DAY : 7*DAY;
  const t=new Date(lo); t.setHours(0,0,0,0);
  for(let x=t.getTime(); x<hi; x+=stepMs){
    const d=new Date(x), midnight=d.getHours()===0, monday=d.getDay()===1;
    const major = stepMs<DAY ? midnight : stepMs===DAY ? monday : true;
    const el=document.createElement('div'); el.className='tick'+(major?' major':''); el.style.left=X(x)+'px';
    el.textContent= stepMs<DAY ? (midnight?fmtD(x):fmtT(x)) : fmtD(x); axis.appendChild(el);
  }
  const now=document.createElement('div'); now.className='tick now'; now.style.left=X(Date.now())+'px'; now.textContent='now'; axis.appendChild(now);
  // lanes, busiest first
  const order=DATA.projects.map(p=>p.label).filter(p=>list.some(s=>s.project===p));
  for(const p of order){
    const lane=document.createElement('div'); lane.className='lane';
    const ss=list.filter(s=>s.project===p); const act=ss.reduce((a,s)=>a+s.activeMinutes,0);
    lane.innerHTML='<div class="name" title="'+esc(p)+'">'+esc(p)+'<small>'+ss.length+' session'+(ss.length===1?'':'s')+' · '+mins(act)+'</small></div>';
    for(let x=t.getTime(); x<hi; x+=stepMs){const g=document.createElement('div');g.className='gridline';g.style.left=X(x)+'px';lane.appendChild(g)}
    // pack overlapping sessions (resumed sessions can span days) into rows inside the lane
    const rowEnd=[], ROW=30, gapMs=8/pxPerMs;
    for(const s of ss.slice().sort((a,b)=>a.t0-b.t0)){
      let r=rowEnd.findIndex(e=>e+gapMs<=s.t0); if(r<0){r=rowEnd.length;rowEnd.push(0)}
      rowEnd[r]=Math.max(s.t1, s.t0+6/pxPerMs);
      const b=document.createElement('div'); b.className='bar'+(selected===s?' sel':''); b.style.setProperty('--c',COLORS[p]);
      b.tabIndex=0; b.setAttribute('role','button'); b.setAttribute('aria-label',s.title+', '+fmtDT(s.t0));
      const w=Math.max(6,(s.t1-s.t0)*pxPerMs); b.style.left=X(s.t0)+'px'; b.style.width=w+'px'; b.style.top=(8+r*ROW)+'px';
      // solid blocks = active stretches; the faint bar between them = idle time while the session stayed open
      b.innerHTML=s.segs.map(([a,z])=>'<div class="seg" style="left:'+((a-s.t0)*pxPerMs)+'px;width:'+Math.max(3,(z-a)*pxPerMs)+'px"></div>').join('')+
        (w>40?'<span class="lbl">'+esc(s.title)+'</span>':'');
      b.onmousemove=e=>tip(e,s); b.onmouseleave=()=>{$('tip').style.display='none'}; b.onclick=()=>open(s);
      b.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open(s)}};
      lane.appendChild(b);
    }
    lane.style.height=Math.max(56,16+rowEnd.length*ROW)+'px';
    lanes.appendChild(lane);
  }
}
function tip(e,s){
  const top=Object.entries(s.tools).slice(0,4).map(([k,v])=>k+' '+v).join(', ');
  const el=$('tip'); el.style.display='block';
  el.innerHTML='<b>'+esc(s.title)+'</b><div class="m">'+esc(s.project)+'</div>'+fmtDT(s.t0)+' → '+fmtDT(s.t1)+
    '<div>'+mins(s.activeMinutes)+' active of '+mins(s.spanMinutes)+' · '+s.userTurns+' prompts · '+s.toolCalls+' tool calls</div>'+
    '<div>'+s.files.length+' files · '+s.commits.length+' commits'+(top?'<div class="m">'+esc(top)+'</div>':'')+'</div>';
  const w=el.offsetWidth,h=el.offsetHeight; let x=e.clientX+14,y=e.clientY+14;
  if(x+w>innerWidth-8)x=e.clientX-14-w; if(y+h>innerHeight-8)y=e.clientY-14-h; el.style.left=x+'px'; el.style.top=y+'px';
}
function open(s){
  selected=s; $('tip').style.display='none'; document.querySelectorAll('.bar.sel').forEach(b=>b.classList.remove('sel'));
  const tools=Object.entries(s.tools).map(([k,v])=>'<tr><td>'+esc(k)+'</td><td>'+v+'</td></tr>').join('');
  const files=s.files.map(f=>'<li title="'+esc(f.path)+'">'+esc(base(f.path))+' <small>'+Object.entries(f.ops).map(([k,v])=>k+'×'+v).join(' ')+' · '+esc(f.path)+'</small></li>').join('');
  const commits=s.commits.map(c=>'<li>'+(c.when?fmtDT(new Date(c.when).getTime())+' ':'')+'<small>'+esc(c.subject||'(no -m message captured)')+'</small></li>').join('');
  $('sideBody').innerHTML='<h2>'+esc(s.title)+'</h2><div class="meta"><span class="tag" style="--c:'+COLORS[s.project]+'">'+esc(s.project)+'</span>'+(s.model?esc(s.model):'')+'<br>'+esc(s.file)+'</div>'+
    '<table><tr><td>start</td><td>'+fmtDT(s.t0)+'</td></tr><tr><td>end</td><td>'+fmtDT(s.t1)+'</td></tr><tr><td>active</td><td>'+mins(s.activeMinutes)+' of '+mins(s.spanMinutes)+' span</td></tr>'+
    '<tr><td>prompts</td><td>'+s.userTurns+'</td></tr><tr><td>tool calls</td><td>'+s.toolCalls+'</td></tr>'+(s.badLines?'<tr><td>unparsed lines</td><td>'+s.badLines+'</td></tr>':'')+'</table>'+
    '<details open><summary>Files touched ('+s.files.length+')</summary><ul>'+(files||'<li><small>none</small></li>')+'</ul></details>'+
    '<details'+(s.commits.length?' open':'')+'><summary>Git commits ('+s.commits.length+')</summary><ul>'+(commits||'<li><small>none</small></li>')+'</ul></details>'+
    '<details><summary>Tools</summary><table>'+tools+'</table></details>'+
    '<div style="margin-top:10px"><button id="copyId">Copy session id</button> <button id="copyPath">Copy log path</button></div>';
  $('side').classList.add('open');
  $('copyId').onclick=()=>navigator.clipboard&&navigator.clipboard.writeText(s.id); $('copyPath').onclick=()=>navigator.clipboard&&navigator.clipboard.writeText(s.file);
  render();
}
$('close').onclick=()=>{$('side').classList.remove('open');selected=null;render()};
addEventListener('keydown',e=>{if(e.key==='Escape'){$('side').classList.remove('open');selected=null;render()}});
for(const p of DATA.projects){const o=document.createElement('option');o.value=p.label;o.textContent=p.label+' ('+p.sessions+')';$('proj').appendChild(o)}
$('proj').onchange=e=>{filterProj=e.target.value;render()};
$('q').oninput=e=>{query=e.target.value.trim().toLowerCase();render()};
$('from').onchange=e=>{from=e.target.value?new Date(e.target.value+'T00:00').getTime():null;render()};
$('to').onchange=e=>{to=e.target.value?new Date(e.target.value+'T23:59:59').getTime():null;render()};
document.querySelectorAll('[data-zoom]').forEach(b=>b.onclick=()=>{pxPerMs=ZOOM[b.dataset.zoom];document.querySelectorAll('[data-zoom]').forEach(x=>x.classList.toggle('on',x===b));render()});
$('fit').onclick=()=>{const l=shown(); if(!l.length)return; const lo=Math.min(...l.map(s=>s.t0)),hi=Math.max(...l.map(s=>s.t1),Date.now());
  pxPerMs=Math.max(ZOOM.month/4,( $('wrap').clientWidth-260)/Math.max(DAY,hi-lo+DAY)); document.querySelectorAll('[data-zoom]').forEach(x=>x.classList.remove('on')); render()};
$('today').onclick=()=>{const n=document.querySelector('.tick.now'); if(n)$('wrap').scrollLeft=n.offsetLeft-$('wrap').clientWidth+120};
$('wrap').addEventListener('wheel',e=>{if(e.shiftKey||Math.abs(e.deltaX)>0)return; if(e.ctrlKey){e.preventDefault();pxPerMs*=Math.exp(-e.deltaY*0.002);render()}},{passive:false});
render(); $('today').click();
</script>
</body>
</html>
"""


def render(data: dict) -> str:
    return HTML.replace("__DATA__", json.dumps(data).replace("</", "<\\/"))


# --------------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=30, help="only sessions that ended in the last N days (0 = all; default 30)")
    ap.add_argument("--root", action="append", default=[], type=Path, help="a projects folder to scan (default ~/.claude/projects; repeatable)")
    ap.add_argument("--out", default=Path("session-timeline.html"), type=Path, help="where to write the page")
    ap.add_argument("--open", action="store_true", help="open the page in the browser when done")
    ap.add_argument("--json", action="store_true", help="print the session data as JSON and exit")
    a = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):     # Windows consoles default to cp1252
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass

    roots = a.root or [Path.home() / ".claude" / "projects"]
    data = scan(roots, a.days)
    s = data["summary"]
    print(f"Scanned {s['logFiles']} log file(s): {s['sessions']} sessions {f'in the last {a.days} days' if a.days > 0 else 'in all logs'}, "
          f"{len(data['projects'])} projects, {s['activeHours']} active hours ({s['spanHours']} h span), "
          f"{s['filesTouched']} files touched, {s['commits']} commits, {s['userTurns']} prompts"
          + (f", busiest: {s['busiestProject']}" if s['busiestProject'] else ""), file=sys.stderr)

    if a.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0
    if not data["sessions"]:
        print("No sessions found; nothing written.", file=sys.stderr)
        return 1
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(render(data), encoding="utf-8")
    print(f"Wrote {a.out.resolve()}", file=sys.stderr)
    if a.open:
        webbrowser.open(a.out.resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
