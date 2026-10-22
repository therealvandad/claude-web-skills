#!/usr/bin/env python3
"""ship.py: the launch sequence for a plain HTML + Tailwind site, as one run.

Usage:
  python ship.py <site> [--target github-pages|cloudflare-pages|netlify] [--dry-run] [-m "message"]
                        [--project-name NAME] [--branch main] [--skip-vibe]

Steps, in order; the run stops at the first failing gate:
  1. validate   every .html in src/ (or the site root): doctype, lang, title, viewport, one h1,
                img alt, duplicate ids, unclosed or stray tags, internal links and assets that do not exist
  2. vibe check the pack's web-craft-consistency-audit/scripts/vibe_check.py; a "generic" verdict fails
  3. build      `npm run build` when package.json has a build script (npm install first if node_modules is missing)
  4. git        git init if needed, refuse if .env or node_modules would be committed, add -A, commit, push
  5. deploy     github-pages: the push deploys via .github/workflows; cloudflare-pages / netlify: run the
                CLI if installed, otherwise print the exact commands. Then print the expected URL.

--dry-run runs steps 1 and 2 for real and only prints what 3 to 5 would do: nothing is built,
committed, pushed or deployed. Exit code 0 = shipped (or would ship), 1 = a gate failed, 2 = usage error.
Standard library only; Windows and Unix.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve()
VIBE = HERE.parents[2] / "web-craft-consistency-audit" / "scripts" / "vibe_check.py"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
# end tags HTML lets you omit; never report these as unclosed
OPTIONAL_END = {"html", "head", "body", "p", "li", "dt", "dd", "option", "optgroup", "tr", "td", "th", "thead",
                "tbody", "tfoot", "colgroup", "caption", "rp", "rt"}
SKIP_DIRS = {"node_modules", "dist", ".git", "build", "_site", ".netlify", ".wrangler"}
EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|#|\{)", re.I)


class PageCheck(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, int]] = []
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.ids: dict[str, int] = {}
        self.refs: list[tuple[str, int]] = []
        self.doctype = self.lang = self.viewport = False
        self.h1 = 0
        self.title = ""
        self._in_title = False

    def handle_decl(self, decl: str) -> None:
        if decl.lower().startswith("doctype html"):
            self.doctype = True

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = {k: (v or "") for k, v in attrs}
        line = self.getpos()[0]
        if tag == "html" and a.get("lang"):
            self.lang = True
        if tag == "meta" and a.get("name", "").lower() == "viewport":
            self.viewport = True
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self._in_title = True
        if tag == "img" and "alt" not in a:
            self.errors.append(f"line {line}: <img src=\"{a.get('src', '')[:50]}\"> has no alt (use alt=\"\" if decorative)")
        if "id" in a:
            if a["id"] in self.ids:
                self.errors.append(f"line {line}: duplicate id=\"{a['id']}\" (first on line {self.ids[a['id']]})")
            self.ids.setdefault(a["id"], line)
        for attr in ("href", "src"):
            if a.get(attr) and not (tag == "link" and a.get("rel") in ("preconnect", "dns-prefetch")):
                self.refs.append((a[attr], line))
        if tag not in VOID:
            self.stack.append((tag, line))

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        stack_len = len(self.stack)
        self.handle_starttag(tag, attrs)
        del self.stack[stack_len:]  # <path/>, <br/>: nothing stays open

    def handle_endtag(self, tag: str) -> None:
        line = self.getpos()[0]
        if tag == "title":
            self._in_title = False
        if tag in VOID:
            return
        if not any(t == tag for t, _ in self.stack):
            self.errors.append(f"line {line}: stray </{tag}> with nothing open to close")
            return
        while self.stack:
            t, opened = self.stack.pop()
            if t == tag:
                break
            if t not in OPTIONAL_END:
                self.errors.append(f"line {opened}: <{t}> is never closed (hit </{tag}> on line {line})")

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data

    def finish(self) -> None:
        for t, opened in self.stack:
            if t not in OPTIONAL_END:
                self.errors.append(f"line {opened}: <{t}> is never closed")
        if not self.doctype:
            self.errors.append("no <!doctype html>")
        if not self.title.strip():
            self.errors.append("no <title> or it is empty")
        if not self.lang:
            self.warnings.append("<html> has no lang attribute")
        if not self.viewport:
            self.warnings.append("no <meta name=\"viewport\">: the page will render zoomed out on phones")
        if self.h1 != 1:
            self.warnings.append(f"{self.h1} <h1> elements (want exactly one)")


def build_outputs(site: Path) -> set[str]:
    """File names a build will create (e.g. output.css from `tailwindcss -o dist/output.css`)."""
    pkg = site / "package.json"
    if not pkg.is_file():
        return set()
    scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
    return {Path(m).name for s in scripts.values() for m in re.findall(r"(?:-o|--output)\s+(\S+)", s)}


def html_root(site: Path) -> Path:
    return site / "src" if (site / "src").is_dir() and any((site / "src").rglob("*.html")) else site


def validate(site: Path) -> bool:
    root = html_root(site)
    pages = [p for p in sorted(root.rglob("*.html")) if not SKIP_DIRS & set(p.relative_to(root).parts)]
    if not pages:
        print(f"  FAIL no .html files under {root}")
        return False
    built = build_outputs(site)
    n_err = 0
    for page in pages:
        chk = PageCheck()
        text = page.read_text(encoding="utf-8", errors="replace")
        chk.feed(text)
        chk.close()
        chk.finish()
        for ref, line in chk.refs:
            if EXTERNAL.match(ref):
                if ref.startswith("#") and len(ref) > 1 and ref[1:] not in chk.ids:
                    chk.warnings.append(f"line {line}: link to #{ref[1:]} but no element has that id")
                continue
            path = ref.split("#")[0].split("?")[0]
            if not path:
                continue
            target = (root / path.lstrip("/")) if path.startswith("/") else (page.parent / path)
            if path.endswith("/"):
                target = target / "index.html"
            if not target.exists() and target.name not in built:
                chk.errors.append(f"line {line}: '{ref}' does not exist")
        rel = page.relative_to(site)
        status = "FAIL" if chk.errors else "ok  "
        print(f"  {status} {rel}  ({len(chk.errors)} errors, {len(chk.warnings)} warnings)")
        for e in chk.errors[:12]:
            print(f"         error: {e}")
        for w in chk.warnings[:6]:
            print(f"         warn:  {w}")
        n_err += len(chk.errors)
    print(f"  {len(pages)} pages, {n_err} errors")
    return n_err == 0


def vibe(site: Path) -> bool:
    if not VIBE.is_file():
        print(f"  skip: {VIBE} not found (install the whole pack to get the vibe check)")
        return True
    root = html_root(site)
    r = subprocess.run([sys.executable, str(VIBE), str(root), "--json"], capture_output=True, text=True, encoding="utf-8")
    try:
        reports = json.loads(r.stdout)
    except json.JSONDecodeError:
        print("  skip: vibe_check.py gave no JSON:", (r.stderr or r.stdout)[:200])
        return True
    bad = 0
    for rep in reports:
        name = Path(rep["file"]).relative_to(site) if Path(rep["file"]).is_absolute() else rep["file"]
        print(f"  {rep['verdict']:<8} {name}" + (f"  ({len(rep['findings'])} findings)" if rep["findings"] else ""))
        if rep["verdict"] == "generic":
            bad += 1
            for f in rep["findings"]:
                print(f"           - {f['tell']}: {f['count']}" + (f"  [{f['detail']}]" if f.get("detail") else ""))
    if bad:
        print(f"  FAIL {bad} page(s) read as generic. Fix with web-craft-anti-generic-design, then run again.")
    return bad == 0


def run(cmd: list[str], cwd: Path, dry: bool, check: bool = True) -> subprocess.CompletedProcess | None:
    print("  $ " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
    if dry:
        return None
    exe = shutil.which(cmd[0]) or cmd[0]  # npm.cmd / npx.cmd on Windows
    r = subprocess.run([exe, *cmd[1:]], cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        print("    " + "\n    ".join(out.splitlines()[-15:]))
    if check and r.returncode != 0:
        raise SystemExit(f"  FAIL `{' '.join(cmd)}` exited {r.returncode}")
    return r


def git_out(site: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=site, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip() if r.returncode == 0 else ""


def build(site: Path, dry: bool) -> Path:
    pkg = site / "package.json"
    scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {}) if pkg.is_file() else {}
    if "build" not in scripts:
        print("  no build script in package.json; publishing the files as they are")
        return site
    if not shutil.which("npm"):
        raise SystemExit("  FAIL npm not found; install Node 20+ or remove the build script")
    if not (site / "node_modules").is_dir():
        run(["npm", "ci" if (site / "package-lock.json").is_file() else "install"], site, dry)
    run(["npm", "run", "build"], site, dry)
    return site / "dist"


def git_ship(site: Path, msg: str, branch: str, dry: bool) -> str:
    if not shutil.which("git"):
        raise SystemExit("  FAIL git not found")
    top = git_out(site, "rev-parse", "--show-toplevel")
    if not top:
        run(["git", "init", "-b", branch], site, dry)
    elif Path(top).resolve() != site:
        print(f"  note: {site.name} sits inside the repository at {top}; only this folder is staged")
    ignore = (site / ".gitignore").read_text(encoding="utf-8") if (site / ".gitignore").is_file() else ""
    for must in ("node_modules", ".env"):
        if must not in ignore and (site / must).exists():
            raise SystemExit(f"  FAIL {must} exists and is not in .gitignore; add it before committing")
    if "dist" not in ignore:
        print("  warn: dist/ is not in .gitignore; the build output will be committed")
    if top:
        changed = git_out(site, "status", "--porcelain", "--", ".").splitlines()
        more = f" and {len(changed) - 6} more" if len(changed) > 6 else ""
        print(f"  {len(changed)} changed path(s)" + (": " + ", ".join(c[3:] for c in changed[:6]) + more if changed else ""))
    else:
        changed = ["*"]
        print("  new repository: every file not in .gitignore goes into the first commit")
    if changed:
        run(["git", "add", "-A", "--", "."], site, dry)
        run(["git", "commit", "-m", msg], site, dry)
    remote = git_out(site, "remote", "get-url", "origin")
    cur = git_out(site, "branch", "--show-current") or branch
    if remote:
        run(["git", "push", "-u", "origin", cur], site, dry)
    else:
        print("  no 'origin' remote. Create one, then run again:")
        print(f"    gh repo create {site.resolve().name} --public --source . --push")
        print(f"    (or) git remote add origin https://github.com/<you>/{site.resolve().name}.git && git push -u origin {cur}")
    return remote


def pages_url(remote: str) -> str:
    m = re.search(r"github\.com[:/]([^/]+)/(.+?)(?:\.git)?$", remote or "")
    if not m:
        return "https://<user>.github.io/<repo>/"
    user, repo = m.group(1), m.group(2)
    return f"https://{user.lower()}.github.io/" if repo.lower() == f"{user.lower()}.github.io" else f"https://{user.lower()}.github.io/{repo}/"


def deploy(site: Path, target: str, out: Path, remote: str, project: str, dry: bool) -> None:
    rel = out.relative_to(site).as_posix() if out != site else "."
    if target == "github-pages":
        wf = [p for p in (site / ".github" / "workflows").glob("*.y*ml") if "deploy-pages" in p.read_text(encoding="utf-8")]
        if not wf:
            print("  FAIL no workflow uses actions/deploy-pages; copy deploy.yml from web-ship-static-hosting")
            raise SystemExit(1)
        print(f"  {wf[0].relative_to(site).as_posix()} deploys on push to main.")
        print("  once per repo: Settings > Pages > Source: GitHub Actions")
        print("  watch it:      gh run watch")
        print(f"  URL:           {pages_url(remote)}")
        return
    if target == "cloudflare-pages":
        cmd = ["npx", "wrangler", "pages", "deploy", rel, "--project-name", project]
        local = site / "node_modules" / ".bin" / "wrangler"
        url = f"https://{project}.pages.dev"
    else:
        cmd = ["npx", "netlify", "deploy", "--dir", rel, "--prod"]
        local = site / "node_modules" / ".bin" / "netlify"
        url = f"https://{project}.netlify.app (or the URL the CLI prints)"
    installed = local.exists() or local.with_suffix(".cmd").exists() or shutil.which(cmd[1])
    if installed:
        run(cmd, site, dry)
    else:
        tool = cmd[1]
        print(f"  {tool} is not installed here. Install and log in once, then run the deploy:")
        print(f"    npm i -D {'wrangler' if tool == 'wrangler' else 'netlify-cli'} && npx {tool} login")
        print("    " + " ".join(cmd))
        print("  or connect the repo in the dashboard: build command `npm run build`, output directory `dist`")
    print(f"  URL: {url}")


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("site")
    ap.add_argument("--target", default="github-pages", choices=["github-pages", "cloudflare-pages", "netlify"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-m", "--message", default="Ship site")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--project-name", default="")
    ap.add_argument("--skip-vibe", action="store_true", help="skip the generic-design gate (say why in the commit)")
    a = ap.parse_args(argv)
    site = Path(a.site).resolve()
    if not site.is_dir():
        print(f"error: {site} is not a folder", file=sys.stderr)
        return 2
    pkg_name = json.loads((site / "package.json").read_text(encoding="utf-8")).get("name", "") if (site / "package.json").is_file() else ""
    project = a.project_name or re.sub(r"[^a-z0-9]+", "-", (pkg_name or site.name).lower()).strip("-")
    dry = a.dry_run
    print(f"ship {site}  target={a.target}{'  (dry run: nothing is built, committed or pushed)' if dry else ''}")
    try:
        print("\n1. validate HTML")
        if not validate(site):
            print("\nstopped: fix the errors above and run again.")
            return 1
        print("\n2. vibe check")
        if a.skip_vibe:
            print("  skipped (--skip-vibe)")
        elif not vibe(site):
            print("\nstopped: the page reads as generic.")
            return 1
        print("\n3. build")
        out = build(site, dry)
        print("\n4. commit and push")
        remote = git_ship(site, a.message, a.branch, dry)
        print(f"\n5. deploy to {a.target}")
        deploy(site, a.target, out, remote, project, dry)
    except SystemExit as e:
        if isinstance(e.code, str):
            print(e.code)
        print("\nstopped.")
        return 1
    print("\n" + ("dry run complete: every gate passed; run again without --dry-run to ship." if dry else "shipped."))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
