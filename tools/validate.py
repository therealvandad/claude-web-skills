#!/usr/bin/env python3
"""Validate every skills/<name>/SKILL.md in the pack against CONVENTIONS.md and SKILL-LIST.md.

Usage: python tools/validate.py [pack-root]
Exit code 1 if any hard error is found. Warnings do not fail the run.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
REQUIRED_HEADINGS = ["## Pattern", "## Variations", "## Pitfalls", "## Related skills"]
MIN_LINES, MAX_LINES = 60, 160
MAX_DESC_WORDS = 60


def expected_names() -> list[str]:
    text = (ROOT / "SKILL-LIST.md").read_text(encoding="utf-8")
    return re.findall(r"^\d+\.\s+(web-[a-z0-9-]+)\s+—", text, re.M)


def main() -> int:
    expected = expected_names()
    errors, warnings = [], []
    found = {}

    for d in sorted(SKILLS.iterdir()) if SKILLS.is_dir() else []:
        f = d / "SKILL.md"
        if not d.is_dir():
            continue
        if not f.is_file():
            errors.append(f"{d.name}: no SKILL.md")
            continue
        text = f.read_text(encoding="utf-8")
        lines = text.count("\n") + 1
        m = FM_RE.match(text)
        if not m:
            errors.append(f"{d.name}: missing or malformed frontmatter")
            continue
        fm = {}
        for raw in m.group(1).splitlines():
            if ":" in raw and not raw.startswith(" "):
                k, _, v = raw.partition(":")
                v = v.strip()
                if len(v) > 1 and v[0] == v[-1] == "'":
                    v = v[1:-1].replace("''", "'")
                fm[k.strip()] = v.strip('"')
        raw_desc = re.search(r"^description:[ 	]*(.*)$", m.group(1), re.M)
        if raw_desc and raw_desc.group(1)[:1] not in ("'", '"', ">", "|") and (": " in raw_desc.group(1) or " #" in raw_desc.group(1)):
            errors.append(f"{d.name}: unquoted description contains ': ' or ' #' (invalid YAML; wrap it in quotes)")
        name, desc = fm.get("name", ""), fm.get("description", "")
        found[name] = d.name
        if name != d.name:
            errors.append(f"{d.name}: name field is '{name}'")
        if "<" in desc or ">" in desc:
            errors.append(f"{d.name}: description contains angle brackets (the Claude app rejects them)")
        if not desc:
            errors.append(f"{d.name}: empty description")
        elif len(desc.split()) > MAX_DESC_WORDS:
            warnings.append(f"{d.name}: description is {len(desc.split())} words (max {MAX_DESC_WORDS})")
        body = text[m.end():]
        for h in REQUIRED_HEADINGS:
            if h not in body:
                errors.append(f"{d.name}: missing section '{h}'")
        if lines < MIN_LINES:
            warnings.append(f"{d.name}: only {lines} lines (min {MIN_LINES})")
        elif lines > MAX_LINES + 40:
            warnings.append(f"{d.name}: {lines} lines (max {MAX_LINES})")
        if "tailwind.config" in body and "v3" not in body and "not" not in body.lower():
            warnings.append(f"{d.name}: mentions tailwind.config.js (pack targets Tailwind v4 @theme)")
        if "```" not in body:
            errors.append(f"{d.name}: no code block")
        for ref in re.findall(r"`(web-[a-z0-9-]+)`", body.split("## Related skills")[-1]):
            if ref not in expected:
                warnings.append(f"{d.name}: related skill '{ref}' is not in the pack")

    missing = [n for n in expected if n not in found]
    extra = [n for n in found if n not in expected]
    for n in missing:
        errors.append(f"missing skill: {n}")
    for n in extra:
        warnings.append(f"skill not in SKILL-LIST.md: {n}")

    print(f"{len(found)} skills found, {len(expected)} expected")
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
