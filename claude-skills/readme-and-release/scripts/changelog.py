#!/usr/bin/env python3
"""Generate a Markdown changelog from git history, grouped by conventional-commit type.

Standard library only. Examples:

    python scripts/changelog.py                         # since the latest tag (or all history if no tags)
    python scripts/changelog.py --since v1.1.0          # commits after v1.1.0 up to HEAD
    python scripts/changelog.py --since v1.1.0 --version v1.2.0 --output notes.md
    python scripts/changelog.py --repo C:/src/fanctl --all   # ignore tags, whole history

Commit subjects are expected to look like `feat(serial): add reconnect` or `fix: typo`
(Conventional Commits). Plain subjects such as "Add tray icon" or "Fix crash on unplug" are
sorted by their first word unless --strict is given. Anything still unknown lands under
"Other changes" so nothing is silently dropped. If HEAD itself carries the newest tag (you
tagged first), the default range starts at the tag before it and the heading uses that tag.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from collections import OrderedDict

# Section title per commit type, in output order. Types not listed fall into "Other changes".
SECTIONS = OrderedDict([
    ("feat", "Features"),
    ("fix", "Bug fixes"),
    ("perf", "Performance"),
    ("docs", "Documentation"),
    ("refactor", "Refactoring"),
    ("test", "Tests"),
    ("build", "Build and dependencies"),
    ("ci", "Build and dependencies"),
    ("style", "Chores"),
    ("chore", "Chores"),
    ("revert", "Reverts"),
])
OTHER = "Other changes"
BREAKING = "Breaking changes"

SUBJECT_RE = re.compile(r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?:\s*(?P<desc>.+)$")
# Fallback for non-conventional subjects: first word (lowercased) -> type. Checked after DOC_RE.
FIRST_WORD = {
    "add": "feat", "adds": "feat", "added": "feat", "implement": "feat", "support": "feat",
    "introduce": "feat", "allow": "feat", "new": "feat",
    "fix": "fix", "fixes": "fix", "fixed": "fix", "correct": "fix", "resolve": "fix", "handle": "fix",
    "speed": "perf", "optimize": "perf", "optimise": "perf",
    "doc": "docs", "docs": "docs", "document": "docs",
    "refactor": "refactor", "rename": "refactor", "move": "refactor", "clean": "refactor",
    "simplify": "refactor", "restructure": "refactor", "split": "refactor",
    "test": "test", "tests": "test",
    "bump": "build", "upgrade": "build", "build": "build",
    "revert": "revert",
    "remove": "chore", "delete": "chore", "update": "chore", "tidy": "chore",
}
DOC_RE = re.compile(r"\b(readme|docs?|documentation|license|changelog|typo)\b", re.IGNORECASE)

BREAKING_RE = re.compile(r"^BREAKING[ -]CHANGE:\s*(.+)$", re.MULTILINE)
RECORD_SEP, FIELD_SEP = "\x1e", "\x1f"   # ASCII record/unit separators: never appear in commit text


def git(repo: str, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout


def latest_tag(repo: str, rev: str = "HEAD") -> str | None:
    """Newest tag reachable from rev, or None when there is none (git exits non-zero)."""
    result = subprocess.run(
        ["git", "-C", repo, "describe", "--tags", "--abbrev=0", rev],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return result.stdout.strip() if result.returncode == 0 else None


def default_range(repo: str) -> tuple[str | None, str | None]:
    """(since, tag_on_head). If HEAD is tagged, start from the tag before it."""
    tag = latest_tag(repo)
    if tag is None:
        return None, None
    head = git(repo, "rev-parse", "HEAD").strip()
    tagged = git(repo, "rev-list", "-n", "1", tag).strip()
    if tagged != head:
        return tag, None
    return latest_tag(repo, "HEAD^"), tag   # HEAD^ fails on a root commit: then None, whole history


def commit_url_base(repo: str) -> str | None:
    """Turn the origin remote into https://github.com/owner/repo so hashes can be linked."""
    result = subprocess.run(
        ["git", "-C", repo, "remote", "get-url", "origin"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    url = result.stdout.strip()
    match = re.match(r"(?:git@github\.com:|https://github\.com/)([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    return f"https://github.com/{match.group(1)}/{match.group(2)}" if match else None


def classify(subject: str, strict: bool) -> tuple[str, str, str, bool]:
    """Return (type, scope, description, breaking_from_bang) for one subject line."""
    match = SUBJECT_RE.match(subject)
    if match and match.group("type").lower() in SECTIONS:
        return (match.group("type").lower(), match.group("scope") or "",
                match.group("desc").strip(), bool(match.group("bang")))
    if strict:
        return "", "", subject, False
    # "README: add clone instructions" is not a conventional type; keep the whole subject.
    first = re.split(r"[\s:(]", subject, maxsplit=1)[0].lower()
    if DOC_RE.search(subject) and FIRST_WORD.get(first) not in ("fix", "revert"):
        return "docs", "", subject, False
    return FIRST_WORD.get(first, ""), "", subject, False


def read_commits(repo: str, since: str | None, strict: bool = False) -> list[dict]:
    rev_range = f"{since}..HEAD" if since else "HEAD"
    fmt = FIELD_SEP.join(["%H", "%h", "%s", "%b"]) + RECORD_SEP
    raw = git(repo, "log", rev_range, "--no-merges", f"--format={fmt}")
    commits = []
    for record in raw.split(RECORD_SEP):
        record = record.strip("\r\n")
        if not record:
            continue
        full, short, subject, body = (record.split(FIELD_SEP) + ["", "", "", ""])[:4]
        ctype, scope, desc, bang = classify(subject.strip(), strict)
        note = BREAKING_RE.search(body)
        breaking = bang or bool(note)
        commits.append({"hash": full, "short": short, "type": ctype, "scope": scope,
                        "desc": desc, "breaking": breaking, "note": note.group(1).strip() if note else ""})
    return commits


def render(commits: list[dict], version: str, url_base: str | None) -> str:
    groups: dict[str, list[str]] = OrderedDict()
    for title in [BREAKING, *SECTIONS.values(), OTHER]:
        groups.setdefault(title, [])

    for c in commits:
        link = f"[{c['short']}]({url_base}/commit/{c['hash']})" if url_base else f"`{c['short']}`"
        scope = f"**{c['scope']}:** " if c["scope"] else ""
        line = f"- {scope}{c['desc']} ({link})"
        groups[SECTIONS.get(c["type"], OTHER)].append(line)
        if c["breaking"]:   # the footer text says what users must change; prefer it over the subject
            groups[BREAKING].append(f"- {scope}{c['note']} ({link})" if c["note"] else line)

    today = dt.date.today().isoformat()
    out = [f"## {version} ({today})", ""]
    if not commits:
        out.append("_No changes._")
    for title, lines in groups.items():
        if lines:
            out += [f"### {title}", "", *lines, ""]
    return "\n".join(out).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".", help="path to the git repository (default: current directory)")
    parser.add_argument("--since", metavar="TAG", help="only commits after this tag or ref (default: latest tag)")
    parser.add_argument("--all", action="store_true", help="whole history, ignore tags")
    parser.add_argument("--version", help="heading for this block, e.g. v1.2.0 (default: tag on HEAD, else Unreleased)")
    parser.add_argument("--strict", action="store_true", help="only Conventional Commit prefixes, no first-word guessing")
    parser.add_argument("--output", metavar="FILE", help="write here instead of stdout")
    parser.add_argument("--no-links", action="store_true", help="plain short hashes, no GitHub commit links")
    args = parser.parse_args()

    git(args.repo, "rev-parse", "--git-dir")   # fail early with git's message if this is not a repo
    head_tag = None
    if args.all:
        since = None
    elif args.since:
        since = args.since
        check = subprocess.run(["git", "-C", args.repo, "rev-parse", "--verify", "--quiet", f"{since}^{{commit}}"],
                               capture_output=True, text=True)
        if check.returncode != 0:
            tags = git(args.repo, "tag", "--sort=-creatordate").split()[:5]
            raise SystemExit(f"--since {since}: no such tag or commit. Recent tags: {', '.join(tags) or '(none)'}")
    else:
        since, head_tag = default_range(args.repo)
    commits = read_commits(args.repo, since, args.strict)
    url_base = None if args.no_links else commit_url_base(args.repo)
    markdown = render(commits, args.version or head_tag or "Unreleased", url_base)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(markdown)
        print(f"wrote {len(commits)} commits ({since or 'start'}..HEAD) to {args.output}", file=sys.stderr)
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8")   # Windows consoles default to a legacy code page
        except AttributeError:
            pass
        sys.stdout.write(markdown)


if __name__ == "__main__":
    main()
