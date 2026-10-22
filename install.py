#!/usr/bin/env python3
"""Install or remove the web-skills pack for Claude Code.

  python install.py                  # install all 207 skills into ~/.claude/skills (personal, every project)
  python install.py --only layout nav  # only groups whose prefix matches (web-layout-*, web-nav-*)
  python install.py --project PATH   # install into PATH/.claude/skills instead (one project only)
  python install.py --uninstall      # remove every web-* skill this pack installed
  python install.py --list           # show groups and counts

Each skill is one folder with a SKILL.md; installing copies the folder, uninstalling removes it.
"""
import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "skills"


def groups():
    g = {}
    for d in sorted(SRC.iterdir()):
        if d.is_dir() and (d / "SKILL.md").is_file():
            g.setdefault(d.name.split("-")[1], []).append(d)
    return g


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, help="install into this project's .claude/skills instead of ~/.claude/skills")
    ap.add_argument("--only", nargs="*", default=[], help="group prefixes to install (layout page section css nav form ui design motion a11y seo perf ship js craft interactive ecommerce data theme i18n content pwa email tool flow)")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    g = groups()
    if a.list:
        for k, v in g.items():
            print(f"{k:8} {len(v):3}  e.g. {v[0].name}")
        print(f"total {sum(len(v) for v in g.values())}")
        return 0

    dest = (a.project / ".claude" / "skills") if a.project else (Path.home() / ".claude" / "skills")
    dest.mkdir(parents=True, exist_ok=True)
    chosen = [d for k, v in g.items() if not a.only or k in a.only for d in v]
    if not chosen:
        print("no groups matched", a.only, "— try --list", file=sys.stderr)
        return 1

    n = 0
    for d in chosen:
        target = dest / d.name
        if a.uninstall:
            if target.is_dir():
                shutil.rmtree(target)
                n += 1
        else:
            if target.is_dir():
                shutil.rmtree(target)
            shutil.copytree(d, target)
            n += 1
    print(f"{'removed' if a.uninstall else 'installed'} {n} skills {'from' if a.uninstall else 'into'} {dest}")
    if not a.uninstall:
        print("Restart Claude Code (or start a new session) to pick them up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
