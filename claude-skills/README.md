# claude-skills

Standalone Claude Code skills that are not about web sites. Each folder is one skill: a `SKILL.md`
and, where needed, a `scripts/` folder. Install by copying a folder into `~/.claude/skills/`, or run
`python install.py`.

| Skill | What |
|---|---|
| `memory-brain` | draws every Claude Code memory as a node in an interactive brain graph; with `--serve` you can draw new links that are written back into the memory files |
| `skill-brain` | draws every installed skill as a node in an interactive graph, with "related skills" links as wires |
| `session-timeline` | reads Claude Code session logs and renders a timeline page of what was built when, across projects |
| `windows-tray-app` | scaffold for small Windows utilities with a tray icon, settings file, autostart and installer, in C# or Python |
| `arduino-serial` | talking to an Arduino or other microcontroller over serial from a desktop app, with a protocol template |
| `readme-and-release` | write a README with screenshots, a changelog from commits, and cut a GitHub release with assets |

These follow the same writing conventions as the web-skills pack (`../web-skills/CONVENTIONS.md`):
frontmatter with `name` and a pushy `description` under 60 words, then Pattern / Variations /
Pitfalls / Related skills, 60 to 200 lines, minus the Tailwind-specific rules.
