---
name: memory-brain
description: Show every Claude Code memory on this machine as an interactive "brain" graph page, where each memory is a glowing node, the [[links]] between memories are the wires, and the user can click nodes to read them and draw new connections that get written back into the memory files. Use this whenever the user wants to see, browse, map, visualize, explore, audit or connect their memories, asks "what do you remember about me", "show my memories", "memory brain", "memory map", "memory graph", "link these memories", or wants to tidy up, merge or find gaps in what Claude has saved, even if they don't say the word "brain".
---

# Memory Brain

Claude Code keeps memories as one-fact Markdown files in `~/.claude/projects/<project>/memory/`, each with `name`, `description` and `metadata.type` in its frontmatter, and `[[other-memory]]` links in the body. That is a graph already; this skill just draws it. People find it far easier to spot stale facts, duplicates and missing links when they can see the whole thing at once than when reading an index file.

## Run it

The whole skill is one script with no dependencies beyond Python 3:

```bash
python <skill-dir>/scripts/build_brain.py --serve
```

That scans every memory folder under `~/.claude/projects`, opens `http://127.0.0.1:8765/` in the browser, and keeps a tiny local server running so that connections drawn in the page are saved straight into the memory files (as `Related: [[name]]` lines). Run it in the background or in a terminal tab so the conversation can continue while the page is open. The page refreshes itself every few seconds, so memories you write during the conversation appear without a reload.

Useful variations:

| Want | Command |
|---|---|
| Just a file, nothing running | `python build_brain.py --out memory-brain.html` |
| Only the current project | `python build_brain.py --serve --only <part of the project folder name>` |
| A specific memory folder | `python build_brain.py --serve --memory-dir <path>` |
| The graph as data (to reason about it yourself) | `python build_brain.py --json --no-open` |
| Different port | `--port 9000` |

The current session's memory folder is the `memory/` directory the system prompt names; pass it with `--memory-dir` when the user only cares about this project.

## What the page shows

- **Nodes** coloured by memory type: pink `user`, orange `feedback`, blue `project`, green `reference`. Size grows with how many links touch the node.
- **Dashed grey nodes** are memories that something links to but that have not been written yet. These are the most interesting part for the user: each one is a fact Claude thought worth remembering and never wrote. Offer to write them.
- **Wires** are `[[links]]`; a pulse travels along them so the direction is visible. Hovering a node highlights its neighbourhood.
- **Click** a node to read the full memory, its file path, and its links in and out. **⚡ Connect** mode: click one node then another to add a link. In a served page this edits the file immediately; the static page instead tells the user which line to add, and they will usually just ask you to do it.
- Search, a project filter, zoom, drag and a "Shake" button to relayout.

## When the user asks you to act on what they see

Draw the page first, then do the work in the files. Typical follow-ups and how to handle them:

- **"Connect X to Y"**: add `[[Y]]` to X's body (a `Related:` line is the convention the script uses, but a link inside a sentence is better when there is a natural place for it). Links are directional; ask, or use judgement, about whether Y should link back.
- **"Write the missing ones"**: for each ghost node, ask what the fact is if it is not already clear from the memories that link to it, then create the file with proper frontmatter and add it to that folder's `MEMORY.md` index.
- **"These two are the same"**: merge into the one with the better name, point all `[[links]]` at it, delete the other, fix `MEMORY.md`.
- **"This is wrong / outdated"**: edit or delete the file and its index line. Deleting is a destructive action, so confirm before removing anything the user did not explicitly name.

Memory files are the user's; keep their frontmatter intact and never rewrite bodies wholesale when a one-line edit does the job.

## Reading the graph yourself

`--json` gives you the same nodes and edges the page uses. Use it when the user asks questions like "what do you know about my job" or "which memories are isolated", so you answer from the actual files rather than from recall. Nodes with zero links and `ghost: true` targets are the usual cleanup candidates.
