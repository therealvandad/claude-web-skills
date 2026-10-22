---
name: session-timeline
description: 'Render a timeline page from the Claude Code session logs: what was worked on when, across projects, with files changed and commits per session. Use when the user asks "what did I work on this week", "session history", "timeline of my sessions", "which session wrote X", or wants standup notes.'
---

# Session Timeline

Every Claude Code session is logged as JSON lines in `~/.claude/projects/<project-slug>/<session-id>.jsonl`. Those logs already answer "what did I do this week" and "when did this file change", but nobody reads them raw. This skill turns them into one page: a swimlane per project, one bar per session on a time axis, and the files and commits behind each bar. It keeps only metadata: no message text beyond an 80-character title.

## Pattern

One script, Python 3.10+, standard library only:

```bash
python <skill-dir>/scripts/build_timeline.py --days 7 --out <scratchpad>/session-timeline.html --open
```

It prints one summary line to stderr, for example `15 sessions in the last 30 days, 8 projects, 23.3 active hours (409.5 h span), 133 files touched, 8 commits, 238 prompts, busiest: Downloads-FanControlApp`. Quote the numbers that answer the user's question; do not make them open the page for a count.

Bad input never stops the run: a line that is not valid JSON, or has an unexpected shape, is skipped and counted in `badLines`; an unreadable log file is skipped with a warning.

Per session the script records: project label (from the folder slug), start, end, wall-clock span, active minutes (gaps over 30 minutes are idle), user turns, tool calls by name, files written or edited (Write / Edit / MultiEdit / NotebookEdit inputs), git commits found in Bash inputs (with the first line of `-m`), and a title: the session's custom title, else the first 80 characters of the first prompt.

What the page shows:

- **Summary cards**: sessions, active hours, files touched, commits, prompts, busiest project. They follow the filters.
- **Swimlanes** per project, busiest first. A session is a faint bar from first to last message; solid blocks inside it are the stretches of real activity. Overlapping sessions stack in rows.
- **Day / Week / Month** zoom, Fit, Today, ctrl+scroll to zoom freely.
- **Hover** a bar for times, active vs span, prompts, tool calls, files, commits and top tools.
- **Click** (or Enter) a bar for the side panel: every file touched with its operations and full path, commits with time and subject, the tool table, the log path and session id.
- **Filters**: project dropdown, from/to dates, and a search box matching titles, file paths and commit subjects.

## Variations

| Want | Flags |
|---|---|
| This week | `--days 7` |
| Everything ever logged | `--days 0` |
| Data to reason over instead of a page | `--json` (stdout; summary still on stderr) |
| Another machine's or a backup's logs | `--root D:/backup/.claude/projects` (repeatable) |

- **Summarise a week.** Run `--days 7 --json`, group sessions by project, and write a short list per project: the session titles, active hours, the files that matter (skip lockfiles and scratch output) and commit subjects. That is a standup note; offer it as text, not just the page.
- **Find the session where a file changed.** Run `--days 0 --json` and filter `sessions[].files[].path` for the file name (paths are as Claude wrote them: absolute, mixed slashes). Report the session title, project, start time, the operations (`Write×1 Edit×3`) and the log path. If the user wants the why, open that one `.jsonl` and read around the matching `tool_use` block; read only what answers the question.
- **Show it inside the conversation.** The built-in browser cannot open `file://` pages; serve the folder with `python -m http.server --directory <folder>` or publish the HTML as an artifact.

- **List every session on one line.** `python <skill-dir>/scripts/build_timeline.py --days 0 --json | python -c "import json,sys; [print(s['start'][:16], s['project'], s['title']) for s in json.load(sys.stdin)['sessions']]"` lists every session as one line.

## Pitfalls

- Span is not effort. A session resumed two days later has a long faint bar; use `activeMinutes` for "how long did I spend", never `spanMinutes`.
- Only edits made through Claude's file tools are listed. Files written by a Bash command, a script or the user's editor do not appear; say so when the user asks "did I change X" and the answer is no.
- Commits are detected in Bash commands, not from git. Commits the user made in a terminal are missing, and a commit that failed still counts. Check `git log` in the repo when it matters.
- Project labels come from folder slugs, where `/` and `-` are indistinguishable (`Downloads-FanControlApp` is `Downloads/FanControlApp`). Do not guess deeper structure from the label; the log path in the side panel is exact.
- The page contains file paths, project names and session titles. Write it to the scratchpad, not into a repo, and ask before publishing it anywhere shared.
- The only message text that reaches the output is the first 80 characters of the first real user prompt (a custom session title, if one was set, is cut to 80 as well). Assistant replies, tool results and file contents are never copied. Check it: `--json` and look at every `title`.
- Logs are append-only and can be large. Never paste raw log lines into the reply; the script exists so that the summary is all that leaves the logs.

## Related skills

- `memory-brain` for what Claude remembers, as opposed to what was done
- `skill-brain` for a graph of the installed skills
- `engineering:standup` for turning a week's sessions into a standup update
