---
name: web-flow-ship-it
description: Run the launch sequence for a plain HTML + Tailwind site as one command, scripts/ship.py: validate the HTML, vibe check, build Tailwind, commit, push, deploy to GitHub Pages, Cloudflare Pages or Netlify, then report the URL. Use when a user says "ship it", "deploy", "publish my site", "put it online", "go live" or "push this live".
---

# Ship it

Launching is a fixed sequence, and the failures come from skipping a step: a page without a `<title>`, a link to a file that was never copied, a stale `dist/`, `node_modules` committed, a push to a repo with no Pages workflow. `scripts/ship.py` runs the steps in order and stops at the first failing gate, so a broken site never reaches the host. It uses only the standard library and works on Windows and Unix.

## Pattern

**1. Always dry-run first.** `--dry-run` runs the two gates for real (validate, vibe check) and only prints what building, committing, pushing and deploying would do. Nothing is built, written, committed or pushed.

```bash
python <skill-dir>/scripts/ship.py ./ember --dry-run
```

```
1. validate HTML
  ok   src\index.html  (0 errors, 0 warnings)
  4 pages, 0 errors
2. vibe check
  clean    src\index.html  (1 findings)
3. build
  $ npm run build
4. commit and push
  $ git init -b main
  $ git add -A -- .
  $ git commit -m "Ship site"
  no 'origin' remote. Create one, then run again:
    gh repo create ember --public --source . --push
5. deploy to github-pages
  .github/workflows/deploy.yml deploys on push to main.
dry run complete: every gate passed; run again without --dry-run to ship.
```

**2. Read the gates, fix, repeat.** Exit code 0 means every gate passed, 1 means a gate failed, 2 means a usage error.

| Gate | Fails on | Fix with |
|---|---|---|
| validate | missing doctype or `<title>`; `<img>` without `alt`; duplicate ids; unclosed or stray tags; a link or asset whose file does not exist | the error line it prints (`line 41: ...`) |
| vibe check | a "generic" verdict from `web-craft-consistency-audit/scripts/vibe_check.py` | `web-craft-anti-generic-design` |
| build | `npm run build` fails (it runs `npm install` first when `node_modules` is missing) | the npm output it prints |
| git | `.env` or `node_modules` exists and is not in `.gitignore` | add it to `.gitignore` |

Warnings do not stop the run: a missing `lang` or viewport meta, a `#anchor` with no matching id, or a page without exactly one `<h1>` (an embed wrapper page often has none). Read them anyway.

**3. Get a clear yes before the real run.** The real run commits and pushes, and a push is public. Tell the user the files, the commit message, the remote and the target, and wait for "go". Never ship on your own initiative.

```bash
python <skill-dir>/scripts/ship.py ./ember -m "Launch Ember Roasters"
python <skill-dir>/scripts/ship.py ./ember --target cloudflare-pages --project-name ember
```

**4. Report the URL.** GitHub Pages prints `https://<user>.github.io/<repo>/` once an `origin` remote exists (a repo named `<user>.github.io` gets the bare domain). The one-time step the script cannot do is Settings, Pages, Source: GitHub Actions; say so. `gh run watch` follows the deploy.

## Variations

- **Cloudflare Pages or Netlify.** `--target cloudflare-pages` runs `npx wrangler pages deploy dist --project-name <name>`; `--target netlify` runs `npx netlify deploy --dir dist --prod`. When the CLI is not installed the script prints the install, login and deploy commands instead of failing, plus the dashboard alternative (build `npm run build`, output `dist`).
- **No build step.** A folder of plain `.html` files with no `build` script in `package.json` is published as it is; the HTML root is the folder itself.
- **Different branch.** `--branch master` for `git init`; an existing repository keeps its current branch.
- **Skip the vibe gate.** `--skip-vibe` exists for a page that is deliberately odd; put the reason in `-m` so the history says why.

## Pitfalls

- A dry run proves the gates, not the host. The first real deploy can still fail on a missing Pages setting or a Node version in the workflow, so watch the run.
- The script never creates the remote. With no `origin` it commits locally and prints `gh repo create ...`; the user decides whether the repo is public.
- `git add -A` stages everything not ignored. Check `.gitignore` covers `node_modules/`, `dist/`, `.env` before the real run; the script refuses the first two only if they exist.
- A site sitting inside a bigger repository is staged by folder only (`git add -A -- .`), but the push still sends the whole branch. Say so when the folder is not the repo root.
- Validation checks structure, not truth. Placeholder copy, a missing favicon or a wrong canonical URL pass the gates; run the checklist skill for those.
- Never run the real command while testing the skill; use `--dry-run` on a scaffold in a temp folder.

## Related skills

- `web-ship-launch-checklist`
- `web-ship-static-hosting`
- `web-ship-tailwind-production`
- `web-craft-consistency-audit`
- `web-craft-self-review`
- `web-seo-meta-tags`
- `web-seo-sitemap-robots-urls`
- `web-flow-new-site`
