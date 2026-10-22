---
name: skill-brain
description: Draw every installed Claude Code skill as a node in an interactive graph page, with "Related skills" links as wires, so orphans, broken references and duplicates stand out. Use whenever the user says "show my skills as a graph", "which skills are related", "skill map", "skill brain", "audit my skills", "find orphan skills", or asks what skills are installed.
---

# Skill Brain

A skills folder with a hundred SKILL.md files is a graph nobody can hold in their head: each file has a `## Related skills` list pointing at other skills by name, and those names drift as skills get renamed, merged or never written. This skill draws the whole thing as one force-directed canvas so the user can see which skills are hubs, which are orphans, and which references point at nothing. The script only reads; every change afterwards is a normal edit to a SKILL.md, made by Claude in the conversation.

## Pattern

One script, Python 3.10+, standard library only:

```bash
python <skill-dir>/scripts/build_skill_brain.py --out <scratchpad>/skill-brain.html --open
```

It scans `~/.claude/skills/*/SKILL.md`, writes one self-contained HTML page and opens it. It prints a one-line summary to stderr, for example `131 skills, 779 links (744 related, 35 mentions, 0 dangling), 16 groups, 1 isolated`, followed by the names of isolated skills. Read that line and repeat the interesting numbers to the user even when they only asked for the picture.

What the page shows:

- **Nodes** are skills, coloured by group: the segment after `web-` (`layout`, `form`, `a11y`...) or `other`. Size grows with in-degree, so the hubs everyone links to are the big ones.
- **Solid wires** come from `## Related skills` sections. **Faint wires** are mentions: a backticked skill name anywhere else in the body. The Mentions button hides them.
- **Dashed grey nodes** are dangling references: a name under Related skills that no installed skill has. Each is a typo, a renamed skill, or a skill worth writing.
- **Red dashed rings** mark isolated skills (nothing links in or out). "Isolated only" shows just those.
- **Click** a node for its description, file path, line count, the first 40 lines of the SKILL.md, and its links in and out (click any to jump). A flag appears when the frontmatter `name` differs from the folder name or two skills share a name.
- Search, a group dropdown, a clickable legend to hide groups, scroll to zoom, drag nodes, Shake to relayout.

What to do with what the user sees. Draw the page first, then edit files:

- **"Write the missing one"**: a dangling node means other skills already say when it should be used. Read the skills that link to it (`--json`: edges whose `target` is `dangling:<name>`) to learn the expected scope, write the SKILL.md in the same folder and style as its neighbours, then rerun the script and confirm the ghost became a real node.
- **"These two overlap"**: compare the bodies, merge into the one with the better name, repoint every Related bullet that named the loser, delete the loser's folder. Deleting is destructive: confirm first unless the user named both.
- **"Connect X to Y"**: add `` - `Y` `` under X's `## Related skills` (create the section if missing). Links are directional; add the reverse only if Y would genuinely send someone to X.
- **"Why is this isolated?"**: an isolated skill usually belongs to no pack. Suggest two or three neighbours from the same group or topic and offer to add links both ways.
- **"Fix the typo"**: a dangling name one edit away from a real one (`web-ui-button` vs `web-ui-buttons`) is a rename of the bullet, nothing more.

## Variations

| Want | Flags |
|---|---|
| Include the current project's `.claude/skills` | `--project .` (repeatable) |
| Include another folder of skills | `--dir D:/skills` (repeatable) |
| Only project or extra folders | `--no-user --project .` |
| The graph as data, to answer questions yourself | `--json` |
| Just write the file | leave out `--open` |

- **Answer from data, not recall.** `--json` prints `nodes`, `edges` and `groups`; each node has `inDegree`, `outDegree`, `isolated`, `ghost`, `nameMismatch`, `group`, `file`. Sort by `inDegree` for "my most referenced skill"; filter `isolated` or `ghost` for "what is broken or orphaned".
- **Show it inside the conversation.** The built-in browser cannot open `file://` pages; serve the folder with `python -m http.server --directory <folder>` or publish the HTML as an artifact.
- **Audit one pack.** Use the group dropdown, or `--no-user --dir <pack>/skills` to graph a repo of skills before installing it.

## Pitfalls

- Writing the page into `~/.claude/skills` makes it look like a broken skill folder. Write to the scratchpad or the project folder.
- A mention is only counted for a backticked token that exactly equals an installed skill name; plain-text names and plugin skills (`plugin:skill`) are not links. Do not treat a missing faint wire as missing knowledge.
- Ghost nodes only come from `## Related skills` sections. A heading spelled differently (`## See also`) yields no links; rename the heading rather than teaching the script new spellings.
- The page is a snapshot. After editing SKILL.md files, rerun the script before telling the user the graph is fixed.
- Keep edits to the Related section minimal and the frontmatter intact; the rest of each SKILL.md is the author's prose.
- Merging or deleting skills changes what triggers in every future session. Say which skill now covers the merged triggers.

## Related skills

- `memory-brain` for the same kind of graph over Claude's memory files
- `session-timeline` for what was built when, across projects
- `anthropic-skills:skill-creator` for writing or improving a skill once the graph shows it is missing
