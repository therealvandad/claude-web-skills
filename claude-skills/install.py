#!/usr/bin/env python3
"""Install or remove the standalone claude-skills.

  python install.py                 # copy every skill folder here into ~/.claude/skills
  python install.py --only skill-brain session-timeline
  python install.py --uninstall     # remove them again
"""
import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--uninstall", action="store_true")
    a = ap.parse_args()
    dest = Path.home() / ".claude" / "skills"
    dest.mkdir(parents=True, exist_ok=True)
    skills = [d for d in sorted(HERE.iterdir()) if d.is_dir() and (d / "SKILL.md").is_file() and (not a.only or d.name in a.only)]
    if not skills:
        print("nothing matched", file=sys.stderr)
        return 1
    for d in skills:
        target = dest / d.name
        if target.is_dir():
            shutil.rmtree(target)
        if not a.uninstall:
            shutil.copytree(d, target, ignore=shutil.ignore_patterns("__pycache__"))
    print(f"{'removed' if a.uninstall else 'installed'} {len(skills)} skills: {', '.join(d.name for d in skills)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
