#!/usr/bin/env python3
"""Build the three claude.ai plugin zips from this repo.

  python tools/build_plugins.py            # writes dist/<name>-plugin.zip for all three plugins

Each zip holds one top-level folder with .claude-plugin/plugin.json, README.md, LICENSE and
skills/<name>/SKILL.md, the layout claude.ai expects under Customize > Plugins > Upload plugin.
Each zip stays under 200 files.
"""
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
REPO = "https://github.com/therealvandad/claude-web-skills"
DESIGN_GROUPS = {"layout", "page", "section", "css", "nav", "form", "ui", "design", "craft", "motion"}


def skill_dirs(folder: Path) -> list[Path]:
    return sorted(d for d in folder.iterdir() if (d / "SKILL.md").is_file())


def plans():
    web = skill_dirs(ROOT / "skills")
    return [
        ("web-skills-design", "Web Skills: Layouts and Design",
         [d for d in web if d.name.split("-")[1] in DESIGN_GROUPS],
         "Layouts, whole pages, sections, CSS, navigation, forms, UI components, design system, motion and craft skills for building web sites with plain HTML, CSS, JavaScript and Tailwind CSS v4.",
         'Ask for what you want to build: "make me a pricing table", "a docs page", "the navbar breaks on mobile", "this looks AI generated". Claude loads the matching skill and follows its pattern, variations and pitfalls.'),
        ("web-skills-build", "Web Skills: Features and Shipping",
         [d for d in web if d.name.split("-")[1] not in DESIGN_GROUPS],
         "Accessibility, SEO, performance, shipping, JavaScript help, interactive features, e-commerce, charts, themes, languages, content pipelines, PWA, HTML email, plus runnable tools and workflows for plain HTML and Tailwind CSS v4 sites.",
         'Ask things like "add a shopping cart", "make it installable", "a receipt email that works in Outlook", "audit my site" or "scaffold a new site". Some skills include Python scripts that Claude runs in the code execution sandbox.'),
        ("creator-tools", "Creator Tools", skill_dirs(ROOT / "claude-skills"),
         "Six standalone skills: memory-brain and skill-brain graphs, a session timeline, a Windows tray app template, Arduino serial communication, and README and release help.",
         'Ask "show my memories as a graph", "what did I work on this week", "make a tray icon app", "talk to my Arduino over serial" or "write a README and a changelog". Some skills read local Claude Code files and work best in Claude Code.'),
    ]


def build(name, display, dirs, desc, use, version) -> Path:
    stage = DIST / name
    if stage.exists():
        shutil.rmtree(stage)
    (stage / ".claude-plugin").mkdir(parents=True)
    (stage / ".claude-plugin" / "plugin.json").write_text(json.dumps({
        "name": name, "displayName": display, "version": version, "description": desc,
        "author": {"name": "therealvandad", "url": REPO}, "license": "MIT", "homepage": REPO,
    }, indent=2) + "\n", encoding="utf-8")
    (stage / "README.md").write_text(
        f"# {display}\n\n{desc}\n\n## Use it\n\n{use}\n\n## Data\n\nThis plugin contains only instructions "
        f"and small local scripts. It sends no data anywhere and stores nothing itself.\n\nSource and full skill list: {REPO}\n",
        encoding="utf-8")
    shutil.copy(ROOT / "LICENSE", stage / "LICENSE")
    for d in dirs:
        shutil.copytree(d, stage / "skills" / d.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "evals"))
    out = DIST / f"{name}-plugin.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                z.write(p, f"{name}/{p.relative_to(stage).as_posix()}")
    count = len(zipfile.ZipFile(out).namelist())
    if count >= 200:
        sys.exit(f"{out.name} has {count} files; claude.ai accepts fewer than 200")
    shutil.rmtree(stage)
    print(f"{out.relative_to(ROOT)}: {len(dirs)} skills, {count} files")
    return out


def main() -> int:
    version = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    DIST.mkdir(exist_ok=True)
    for plan in plans():
        build(*plan, version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
