#!/usr/bin/env python3
"""new_site.py: scaffold a plain HTML + Tailwind v4 site from the web-skills pack patterns.

Usage:
  python new_site.py --name "Ember Roasters" --kind landing --pages home,about,contact,pricing --tone editorial --out ./ember

  --kind   landing | blog | portfolio | docs | shop        (decides which sections the home page gets)
  --pages  comma list of: home about contact pricing blog docs work shop faq, or any other word for a plain page
  --tone   editorial | swiss | corporate | playful | terminal   (one hue, tinted neutrals, named fonts)
  --out    folder to create (must not already contain a src/ folder)
  --force  overwrite an existing scaffold

Writes: src/*.html, src/input.css, src/js/main.js, src/404.html, scripts/copy.mjs, package.json,
.gitignore, .editorconfig, README.md and .github/workflows/deploy.yml. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ----------------------------------------------------------------------------- tones

TONES = {
    "editorial": dict(
        hue=55, dark=False, display="Fraunces", body="IBM Plex Sans", mono="IBM Plex Mono",
        fonts_url="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;1,9..144,300..600&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400&display=swap",
        display_stack='"Fraunces", "Iowan Old Style", Georgia, serif', body_stack='"IBM Plex Sans", system-ui, sans-serif',
        mono_stack='"IBM Plex Mono", ui-monospace, monospace', radius=("2px", "4px", "8px"), weight=450, tracking="-0.01em",
        accent_c=0.16, note="warm serif display, tinted stone neutrals, terracotta accent"),
    "swiss": dict(
        hue=25, dark=False, display="Inter Tight", body="Inter", mono="JetBrains Mono",
        fonts_url="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400&display=swap",
        display_stack='"Inter Tight", "Helvetica Neue", Arial, sans-serif', body_stack='"Inter", "Helvetica Neue", Arial, sans-serif',
        mono_stack='"JetBrains Mono", ui-monospace, monospace', radius=("0px", "0px", "0px"), weight=600, tracking="-0.03em",
        accent_c=0.20, note="grid, black ink, one red, square corners, tight tracking"),
    "corporate": dict(
        hue=250, dark=False, display="Source Serif 4", body="Source Sans 3", mono="Source Code Pro",
        fonts_url="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&family=Source+Sans+3:wght@400;600&family=Source+Code+Pro:wght@400&display=swap",
        display_stack='"Source Serif 4", Georgia, serif', body_stack='"Source Sans 3", "Segoe UI", system-ui, sans-serif',
        mono_stack='"Source Code Pro", ui-monospace, monospace', radius=("4px", "6px", "10px"), weight=500, tracking="-0.01em",
        accent_c=0.14, note="calm blue, serif headings, cool neutrals, modest radii"),
    "playful": dict(
        hue=85, dark=False, display="Bricolage Grotesque", body="DM Sans", mono="DM Mono",
        fonts_url="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=DM+Sans:wght@400;500&family=DM+Mono:wght@400&display=swap",
        display_stack='"Bricolage Grotesque", "Avenir Next", system-ui, sans-serif', body_stack='"DM Sans", system-ui, sans-serif',
        mono_stack='"DM Mono", ui-monospace, monospace', radius=("8px", "14px", "24px"), weight=700, tracking="-0.02em",
        accent_c=0.17, note="amber accent, chunky display face, rounded corners, warm paper"),
    "terminal": dict(
        hue=150, dark=True, display="JetBrains Mono", body="JetBrains Mono", mono="JetBrains Mono",
        fonts_url="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap",
        display_stack='"JetBrains Mono", ui-monospace, "Cascadia Mono", monospace', body_stack='"JetBrains Mono", ui-monospace, "Cascadia Mono", monospace',
        mono_stack='"JetBrains Mono", ui-monospace, monospace', radius=("0px", "2px", "4px"), weight=700, tracking="0",
        accent_c=0.17, note="dark paper, phosphor green accent, mono everywhere, hairlines"),
}

PAGE_LABELS = {"home": "Home", "about": "About", "contact": "Contact", "pricing": "Pricing", "blog": "Journal",
               "docs": "Docs", "work": "Work", "shop": "Shop", "faq": "FAQ"}
PAGE_ALIASES = {"index": "home", "portfolio": "work", "projects": "work", "products": "shop", "store": "shop",
                "journal": "blog", "news": "blog", "documentation": "docs", "questions": "faq", "prices": "pricing"}
DEFAULT_PAGES = {"landing": ["home", "about", "pricing", "contact"], "blog": ["home", "about", "contact"],
                 "portfolio": ["home", "work", "about", "contact"], "docs": ["home", "docs", "about"],
                 "shop": ["home", "shop", "about", "contact"]}

# which pack skill explains each section, for the README
SKILL_FOR = {
    "navbar": "web-nav-responsive-navbar", "hero": "web-layout-hero", "features": "web-layout-feature-grid",
    "steps": "web-section-steps-timeline", "stats": "web-section-stats-band", "testimonials": "web-layout-testimonials",
    "faq": "web-ui-accordion", "cta": "web-section-cta-band", "footer": "web-layout-footer",
    "posts": "web-page-blog-index", "newsletter": "web-section-newsletter-signup", "work": "web-page-portfolio",
    "guides": "web-page-docs", "quickstart": "web-page-docs", "products": "web-ecommerce-product-grid-filters",
    "story": "web-layout-split-section", "team": "web-section-team-grid", "values": "web-layout-feature-grid",
    "contact-form": "web-page-contact", "plans": "web-layout-pricing-table", "docs-shell": "web-nav-sidebar",
    "prose": "web-seo-content-structure", "404": "web-page-404-and-legal",
}


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "site"


# ----------------------------------------------------------------------------- content

def make_ctx(name: str, kind: str, tone: str, pages: list[str]) -> dict:
    short = name.split()[0]
    t = TONES[tone]
    has = set(pages)
    email = f"hello@{slugify(name)}.example"

    def href(page: str, fallback: str) -> str:
        # only ever link to pages that exist; otherwise fall back to an anchor on home or to email
        return f"./{page}.html" if page in has else fallback

    contact = href("contact", f"mailto:{email}")
    c = dict(name=name, short=short, slug=slugify(name), kind=kind, tone=tone, t=t, pages=pages,
             email=email, city="Leeds", year="2026", contact=contact,
             about=href("about", ""), docs=href("docs", "./index.html#quickstart"),
             cta=("Read the journal" if kind == "blog" else "Start a project" if kind == "portfolio"
                  else "Get started" if kind == "docs" else "Shop the range" if kind == "shop" else "Order before launch"),
             cta_href={"blog": "./index.html#posts", "portfolio": contact, "docs": "./index.html#quickstart",
                       "shop": "./index.html#products"}.get(kind) or href("pricing", contact))
    c["tagline"] = {"landing": f"made by hand in {c['city']}, shipping 3 November", "blog": "essays every other Thursday",
                    "portfolio": f"design and build studio in {c['city']}", "docs": "documentation and guides",
                    "shop": f"made in small runs in {c['city']}"}[kind]
    heads = {
        "landing": (f"{name} starts shipping on 3 November.",
                    f"Three years of making it by hand, now at a price that works for a two-person team. Order before launch and the first month costs nothing."),
        "blog": (f"Notes from {name}.",
                 "Essays on the work, published every other Thursday since March 2024. No sponsors, no pop-ups, one email a fortnight if you want it."),
        "portfolio": (f"{name}. Design and build, for studios and small companies that want to be taken seriously.",
                      "Identity, website, the words on it. Four projects a year, each one finished properly. Taking bookings for January."),
        "docs": (f"{name} documentation.",
                 "Install, configure, deploy. Most people are done in twenty minutes; the troubleshooting page covers the other ten."),
        "shop": (f"{name}. Made in small runs, shipped on Tuesdays.",
                 "Everything on this page was made within forty miles of the workshop. Free delivery over 40 pounds; returns within 30 days, no form to fill in."),
    }
    c["h1"], c["sub"] = heads[kind]
    c["description"] = c["sub"].split(". ")[0] + "."
    c["footer_blurb"] = {
        "landing": f"{name} is made by two people in {c['city']}. We answer email ourselves, usually within a day.",
        "blog": f"Writing from {name}, every other Thursday. Archive back to March 2024.",
        "portfolio": f"{name} works with four clients a year from a studio in {c['city']}.",
        "docs": f"Documentation for {name}, version 2.4. Found a mistake? Edit the page on GitHub.",
        "shop": f"{name}. Workshop and shop in {c['city']}, open Thursday to Saturday, 10 to 5.",
    }[kind]
    return c


# ----------------------------------------------------------------------------- html pieces

SECTION_OPEN = '<section id="{id}" class="{cls}" aria-labelledby="{id}-heading">\n    <div class="mx-auto max-w-6xl px-6">'
SECTION_CLOSE = "    </div>\n  </section>"


def section(id: str, inner: str, band: bool = False, skill: str | None = None) -> str:
    cls = "border-t border-line py-16 sm:py-24" + (" bg-paper-2" if band else "")
    comment = f"  <!-- {id}: {SKILL_FOR.get(skill or id, 'web-layout-page-shell')} -->\n"
    return comment + "  " + SECTION_OPEN.format(id=id, cls=cls) + "\n" + inner + "\n" + SECTION_CLOSE


def eyebrow(n: int, text: str) -> str:
    return (f'<p class="font-mono text-xs uppercase tracking-[0.18em] text-ink-2">'
            f'<span class="text-accent-deep">{n:02d}</span>&ensp;{text}</p>')


def h2(id: str, text: str) -> str:
    return f'<h2 id="{id}-heading" class="mt-3 max-w-2xl text-title">{text}</h2>'


def btn(href: str, label: str, primary: bool = True) -> str:
    base = "inline-flex h-11 items-center rounded-md px-5 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
    look = " bg-accent text-paper hover:bg-accent-deep" if primary else " border border-line text-ink hover:bg-paper-2"
    return f'<a href="{href}" class="{base}{look}">{label}</a>'


def head(c: dict, title: str) -> str:
    return f"""<!doctype html>
<html lang="en" class="h-full scroll-pt-20 scroll-smooth motion-reduce:scroll-auto">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{c['description']}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="{c['t']['fonts_url']}">
  <link rel="stylesheet" href="./output.css">
  <script type="module" src="./js/main.js"></script>
</head>
<body class="flex min-h-full flex-col bg-paper font-sans text-ink antialiased">
  <a href="#main" class="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:rounded-md focus:bg-accent focus:px-4 focus:py-2 focus:text-paper">Skip to main content</a>
"""


def navbar(c: dict, pages: list[str], current: str) -> str:
    items = []
    for p in pages:
        if p == "home":
            continue
        cur = (' aria-current="page" class="block py-2 text-ink underline decoration-accent decoration-2 underline-offset-[6px]"'
               if p == current else ' class="block py-2 text-ink-2 hover:text-ink"')
        items.append(f'          <li><a href="./{p}.html"{cur}>{PAGE_LABELS.get(p, p.title())}</a></li>')
    return f"""
  <!-- navbar: {SKILL_FOR['navbar']} -->
  <header class="sticky top-0 z-40 border-b border-line bg-paper/90 backdrop-blur">
    <nav aria-label="Main" class="mx-auto flex max-w-6xl items-center justify-between gap-6 px-6 py-4">
      <a href="./index.html" class="font-display text-lg font-medium tracking-tight focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">{c['name']}</a>
      <button type="button" data-nav-toggle aria-expanded="false" aria-controls="site-menu"
        class="inline-flex size-10 items-center justify-center rounded-md hover:bg-paper-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent md:hidden">
        <span class="sr-only">Open menu</span>
        <svg data-icon="open" class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
        <svg data-icon="close" class="hidden size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
      </button>
      <div id="site-menu" data-nav-menu
        class="absolute inset-x-0 top-full hidden border-b border-line bg-paper p-6 md:static md:flex md:items-center md:gap-8 md:border-0 md:bg-transparent md:p-0">
        <ul class="flex flex-col gap-1 text-sm md:flex-row md:gap-6">
{chr(10).join(items)}
        </ul>
        <div class="mt-4 md:mt-0">{btn(c['cta_href'], c['cta'])}</div>
      </div>
    </nav>
  </header>
  <main id="main" class="flex-1">
"""


def footer(c: dict, pages: list[str]) -> str:
    links = "\n".join(f'          <li><a href="./{"index" if p == "home" else p}.html" class="text-ink-2 hover:text-ink">{PAGE_LABELS.get(p, p.title())}</a></li>' for p in pages)
    t = c["t"]
    fonts = t["display"] if t["display"] == t["body"] else f"{t['display']} and {t['body']}"
    return f"""  </main>

  <!-- footer: {SKILL_FOR['footer']} and web-craft-finishing-details (colophon) -->
  <footer class="border-t border-line bg-paper-2">
    <div class="mx-auto grid max-w-6xl gap-10 px-6 py-16 md:grid-cols-[1.4fr_1fr_1fr]">
      <div>
        <p class="font-display text-lg font-medium">{c['name']}</p>
        <p class="mt-2 max-w-sm text-sm text-ink-2">{c['footer_blurb']}</p>
      </div>
      <nav aria-label="Pages">
        <h2 class="font-mono text-xs uppercase tracking-[0.18em] text-ink-2">Pages</h2>
        <ul class="mt-4 space-y-2 text-sm">
{links}
        </ul>
      </nav>
      <div>
        <h2 class="font-mono text-xs uppercase tracking-[0.18em] text-ink-2">Contact</h2>
        <ul class="mt-4 space-y-2 text-sm text-ink-2">
          <li><a href="mailto:{c['email']}" class="hover:text-ink">{c['email']}</a></li>
          <li>14 Calls Lane, {c['city']}</li>
          <li>Thursday to Saturday, 10 to 5</li>
        </ul>
      </div>
    </div>
    <div class="border-t border-line">
      <div class="mx-auto flex max-w-6xl flex-col gap-2 px-6 py-6 text-xs text-ink-2 sm:flex-row sm:justify-between">
        <p>&copy; {c['year']} {c['name']}</p>
        <p>Set in {fonts}. Built with plain HTML and Tailwind CSS v4. Hosted on GitHub Pages. No tracking.</p>
      </div>
    </div>
  </footer>
</body>
</html>
"""


# ----------------------------------------------------------------------------- sections

def hero(c: dict) -> str:
    return f"""  <!-- hero: {SKILL_FOR['hero']} (split variant, left-aligned, web-craft-layout-with-intention) -->
  <section class="py-20 sm:py-28" aria-labelledby="hero-heading">
    <div class="mx-auto grid max-w-6xl gap-12 px-6 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
      <div>
        {eyebrow(0, "Est. 2023 &middot; " + c['city'])}
        <h1 id="hero-heading" class="mt-5 max-w-3xl text-display">{c['h1']}</h1>
        <p class="mt-6 max-w-xl text-lg leading-8 text-ink-2">{c['sub']}</p>
        <div class="mt-8 flex flex-wrap gap-3">
          {btn(c['cta_href'], c['cta'])}
          {btn(c['about'], 'How it is made', primary=False) if c['about'] else btn(c['contact'], 'Ask a question', primary=False)}
        </div>
      </div>
      <figure class="border border-line bg-paper-2 p-6">
        <dl class="grid grid-cols-2 gap-6 font-mono text-sm tabular-nums">
          <div><dt class="text-xs uppercase tracking-[0.18em] text-ink-2">Since</dt><dd class="mt-1 text-2xl">2023</dd></div>
          <div><dt class="text-xs uppercase tracking-[0.18em] text-ink-2">Team</dt><dd class="mt-1 text-2xl">2 people</dd></div>
          <div><dt class="text-xs uppercase tracking-[0.18em] text-ink-2">Reply time</dt><dd class="mt-1 text-2xl">&lt; 1 day</dd></div>
          <div><dt class="text-xs uppercase tracking-[0.18em] text-ink-2">Next batch</dt><dd class="mt-1 text-2xl">3 Nov</dd></div>
        </dl>
        <figcaption class="mt-6 text-xs text-ink-2">Replace this panel with a real photograph of the product or the people (web-craft-real-content).</figcaption>
      </figure>
    </div>
  </section>"""


def features(c: dict, n: int = 1) -> str:
    items = [("Made in one place", f"Every order leaves the same workshop in {c['city']}. Nothing is drop-shipped, nothing is relabelled."),
             ("Priced per month, not per surprise", "One number on the invoice. Cancel from the account page; no call, no retention script."),
             ("Support from the people who made it", "Email goes to the two of us. Replies take under a day, usually under an hour.")]
    cards = "\n".join(f"""        <li class="border-t border-line pt-6">
          <p class="font-mono text-xs tabular-nums text-ink-2">{i:02d}</p>
          <h3 class="mt-3 text-lg font-medium">{t}</h3>
          <p class="mt-2 text-sm leading-6 text-ink-2">{d}</p>
        </li>""" for i, (t, d) in enumerate(items, 1))
    inner = f"""      {eyebrow(n, 'What you get')}
      {h2('features', f'Three reasons people choose {c["short"]} over the big catalogue.')}
      <ul role="list" class="mt-12 grid gap-8 md:grid-cols-3">
{cards}
      </ul>"""
    return section("features", inner)


def steps(c: dict, n: int) -> str:
    items = [("Choose", "Pick a size and a cadence. The page shows the next dispatch date before you pay."),
             ("We make it", "Orders are made on Monday and Tuesday and never sit on a shelf longer than a week."),
             ("It arrives", "Royal Mail 48, tracked. Not right? Reply to the dispatch email and we sort it the same day.")]
    lis = "\n".join(f"""        <li class="grid gap-4 border-t border-line py-6 sm:grid-cols-[6rem_1fr]">
          <p class="font-mono text-sm tabular-nums text-accent-deep">Step {i}</p>
          <div><h3 class="text-lg font-medium">{t}</h3><p class="mt-1 max-w-xl text-sm leading-6 text-ink-2">{d}</p></div>
        </li>""" for i, (t, d) in enumerate(items, 1))
    inner = f"""      {eyebrow(n, 'How it works')}
      {h2('how', 'From order to doorstep in three steps.')}
      <ol class="mt-12">
{lis}
      </ol>"""
    return section("how", inner, band=True, skill="steps")


def stats(c: dict, n: int) -> str:
    items = [("412", "orders in the first month"), ("4.8 / 5", "across 96 reviews"), ("31", "days to return, no form"), ("2", f"people, {c['city']}")]
    dl = "\n".join(f'        <div class="border-l border-line pl-5"><dt class="text-sm text-ink-2">{d}</dt><dd class="order-first font-display text-3xl tabular-nums">{v}</dd></div>' for v, d in items)
    inner = f"""      {eyebrow(n, 'In numbers')}
      <h2 id="stats-heading" class="sr-only">{c['name']} in numbers</h2>
      <dl class="mt-8 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
{dl}
      </dl>"""
    return section("stats", inner)


def testimonials(c: dict, n: int) -> str:
    quotes = [("We switched in March and have not thought about it since, which is the best review I can give.", "Priya Natarajan", "Operations lead, Halden &amp; Co."),
              ("The dispatch email had a person's name on it. I replied with a question and the same person answered.", "Tomasz Wierzbicki", "Founder, Ledger Street Bakery")]
    figs = "\n".join(f"""        <figure class="border border-line bg-paper p-8">
          <blockquote class="font-display text-xl leading-snug">&ldquo;{q}&rdquo;</blockquote>
          <figcaption class="mt-6 text-sm"><span class="font-medium">{who}</span><span class="text-ink-2"> &middot; {role}</span></figcaption>
        </figure>""" for q, who, role in quotes)
    inner = f"""      {eyebrow(n, 'From customers')}
      {h2('testimonials', 'Two people who did not have to be asked twice.')}
      <div class="mt-12 grid gap-6 md:grid-cols-2">
{figs}
      </div>"""
    return section("testimonials", inner, band=True)


def faq(c: dict, n: int, standalone: bool = False) -> str:
    qs = [("When do orders ship?", "Monday and Tuesday. Anything placed by Sunday night goes out that week."),
          ("Can I pause instead of cancelling?", "Yes, for up to three months, from the account page. Nothing is charged while paused."),
          ("Do you ship outside the UK?", "To the EU and Ireland, tracked, from 6 pounds. Further afield by arrangement; write to us."),
          ("What if it arrives damaged?", "Reply to the dispatch email with a photo and a replacement goes out the next working day.")]
    details = "\n".join(f"""        <details class="group border-t border-line py-5" {'open' if i == 1 else ''}>
          <summary class="flex cursor-pointer list-none items-center justify-between gap-4 text-lg font-medium [&::-webkit-details-marker]:hidden">
            {q}
            <svg class="size-5 shrink-0 text-ink-2 transition-transform group-open:rotate-45" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
          </summary>
          <p class="mt-3 max-w-2xl text-sm leading-6 text-ink-2">{a}</p>
        </details>""" for i, (q, a) in enumerate(qs, 1))
    inner = f"""      {eyebrow(n, 'Questions')}
      {h2('faq', 'Things people ask before ordering.')}
      <div class="mt-10 max-w-3xl border-b border-line">
{details}
      </div>"""
    return section("faq", inner, band=standalone)


def cta(c: dict, n: int) -> str:
    inner = f"""      <div class="grid gap-8 md:grid-cols-[1fr_auto] md:items-center">
        <div>
          {eyebrow(n, 'Next step')}
          <h2 id="cta-heading" class="mt-3 max-w-2xl text-title">{ {'portfolio': 'Two slots left for January.', 'blog': 'One email a fortnight, nothing else.', 'docs': 'Twenty minutes from install to deploy.', 'shop': 'The next run ships Tuesday 3 November.'}.get(c['kind'], 'Order before 3 November and the first month costs nothing.') }</h2>
        </div>
        <div class="flex flex-wrap gap-3">{btn(c['cta_href'], c['cta'])}{btn(c['contact'], 'Ask a question', primary=False)}</div>
      </div>"""
    return section("cta", inner, band=True)


def posts(c: dict, n: int) -> str:
    items = [("What we got wrong about pricing", "9 Oct 2026", "7 min", "Three price changes in two years, and the lesson from each one, with the actual numbers."),
             ("The tool we replaced with a spreadsheet", "25 Sep 2026", "5 min", "Not every workflow deserves software. Here is the sheet, the formulas and what it saves us."),
             ("A year of Tuesday deliveries", "11 Sep 2026", "9 min", "Fifty-two dispatch days, two missed, one flood. What a fixed shipping day did to the workshop.")]
    arts = "\n".join(f"""        <article class="grid gap-3 border-t border-line py-8 md:grid-cols-[10rem_1fr]">
          <p class="font-mono text-xs tabular-nums text-ink-2">{d}<br>{m} read</p>
          <div>
            <h3 class="text-xl font-medium"><a href="#" class="hover:underline decoration-accent decoration-2 underline-offset-4">{t}</a></h3>
            <p class="mt-2 max-w-2xl text-sm leading-6 text-ink-2">{s}</p>
          </div>
        </article>""" for t, d, m, s in items)
    inner = f"""      {eyebrow(n, 'Latest')}
      {h2('posts', 'Recent essays.')}
      <div class="mt-8 border-b border-line">
{arts}
      </div>"""
    return section("posts", inner)


def newsletter(c: dict, n: int) -> str:
    inner = f"""      <div class="grid gap-8 md:grid-cols-2 md:items-center">
        <div>
          {eyebrow(n, 'By email')}
          {h2('newsletter', 'One email every other Thursday.')}
          <p class="mt-3 max-w-md text-sm leading-6 text-ink-2">The essay, a photo from the workshop, and nothing to buy. 1,140 people read it; the unsubscribe link is at the top, not the bottom.</p>
        </div>
        <form class="flex flex-col gap-3 sm:flex-row" action="#" method="post" data-newsletter>
          <label class="sr-only" for="nl-email">Email address</label>
          <input id="nl-email" name="email" type="email" required autocomplete="email" placeholder="you@example.com"
            class="h-11 flex-1 rounded-md border border-line bg-paper px-4 text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">
          <button type="submit" class="inline-flex h-11 items-center justify-center rounded-md bg-accent px-5 text-sm font-medium text-paper hover:bg-accent-deep focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">Subscribe</button>
        </form>
      </div>"""
    return section("newsletter", inner, band=True)


def work(c: dict, n: int) -> str:
    items = [("Halden &amp; Co.", "Identity and website", "2026"), ("Ledger Street Bakery", "Online ordering", "2026"),
             ("Marrow Press", "Catalogue and shop", "2025"), ("North Pier Dental", "Booking flow", "2025")]
    cards = "\n".join(f"""        <li>
          <a href="#" class="group block focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent">
            <div class="aspect-[4/3] border border-line bg-paper-2 transition-colors group-hover:bg-accent-tint" role="img" aria-label="Placeholder for a screenshot of the {t} project"></div>
            <div class="mt-4 flex items-baseline justify-between gap-4">
              <h3 class="text-lg font-medium">{t}</h3>
              <p class="font-mono text-xs tabular-nums text-ink-2">{y}</p>
            </div>
            <p class="mt-1 text-sm text-ink-2">{d}</p>
          </a>
        </li>""" for t, d, y in items)
    inner = f"""      {eyebrow(n, 'Selected work')}
      {h2('work', 'Four projects, each finished properly.')}
      <ul role="list" class="mt-12 grid gap-10 sm:grid-cols-2">
{cards}
      </ul>"""
    return section("work", inner)


def quickstart(c: dict, n: int) -> str:
    inner = f"""      {eyebrow(n, 'Quick start')}
      {h2('quickstart', 'Install and run in four commands.')}
      <pre class="mt-8 max-w-3xl overflow-x-auto border border-line bg-paper-2 p-6 font-mono text-sm leading-7"><code>npm create {c['slug']}@latest my-project
cd my-project
npm install
npm run dev        <span class="text-ink-2"># opens http://localhost:3000</span></code></pre>
      <p class="mt-4 max-w-2xl text-sm leading-6 text-ink-2">Requires Node 20 or newer. On Windows use PowerShell or Git Bash; both are tested in CI.</p>"""
    return section("quickstart", inner)


def guides(c: dict, n: int) -> str:
    items = [("Installation", "Node, the CLI, and the one environment variable you need."), ("Configuration", f"Every key in {c['slug']}.config.js, with defaults."),
             ("Deploying", "GitHub Pages, Cloudflare Pages and Netlify, with the exact config files."), ("Troubleshooting", "The ten errors people actually hit, and the fix for each.")]
    cards = "\n".join(f"""        <li class="border border-line p-6 hover:bg-paper-2">
          <h3 class="text-lg font-medium"><a href="{c['docs']}" class="after:absolute after:inset-0 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">{t}</a></h3>
          <p class="mt-2 text-sm leading-6 text-ink-2">{d}</p>
        </li>""" for t, d in items)
    inner = f"""      {eyebrow(n, 'Guides')}
      {h2('guides', 'Read in order the first time, then jump around.')}
      <ul role="list" class="mt-12 grid gap-4 sm:grid-cols-2 [&>li]:relative">
{cards}
      </ul>"""
    return section("guides", inner, band=True)


def products(c: dict, n: int) -> str:
    items = [("The Everyday", "250 g", "9.50"), ("The Weekend", "250 g", "11.00"), ("Set of three", "3 &times; 250 g", "28.00"),
             ("Workshop mug", "Stoneware, 300 ml", "18.00"), ("Gift card", "Any amount from 20", "20.00"), ("Subscription", "Fortnightly, 250 g", "14.00")]
    cards = "\n".join(f"""        <li>
          <a href="#" class="group block focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent">
            <div class="aspect-square border border-line bg-paper-2 transition-colors group-hover:bg-accent-tint" role="img" aria-label="Placeholder for a product photo of {t}"></div>
            <div class="mt-3 flex items-baseline justify-between gap-4">
              <h3 class="font-medium">{t}</h3>
              <p class="font-mono text-sm tabular-nums">&pound;{p}</p>
            </div>
            <p class="mt-1 text-sm text-ink-2">{d}</p>
          </a>
        </li>""" for t, d, p in items)
    inner = f"""      {eyebrow(n, 'The range')}
      {h2('products', 'Six things, all in stock today.')}
      <ul role="list" class="mt-12 grid gap-x-6 gap-y-10 sm:grid-cols-2 lg:grid-cols-3">
{cards}
      </ul>"""
    return section("products", inner)


def story(c: dict, n: int) -> str:
    inner = f"""      <div class="grid gap-12 lg:grid-cols-[0.8fr_1.2fr]">
        <div>
          {eyebrow(n, 'The story')}
          {h2('story', f'{c["name"]} started in a rented unit with one machine and a Tuesday deadline.')}
        </div>
        <div class="space-y-5 text-lg leading-8 text-ink-2">
          <p>In spring 2023 Maren Holt left a job she was good at to make something she could stand behind. The first orders went to friends; the first complaint came from one of them, and it changed the packaging.</p>
          <p>Diego Salcedo joined the following January. There are still two of us. We have turned down an investor, a marketplace and a 40 percent discount deal, because each one would have changed what we send you.</p>
          <p>This page is the only place we talk about ourselves. Everywhere else, the work should do it.</p>
        </div>
      </div>"""
    return section("story", inner)


def team(c: dict, n: int) -> str:
    people = [("Maren Holt", "Founder, makes the thing"), ("Diego Salcedo", "Workshop and dispatch"), ("Aiko Tanabe", "Customer letters, part time")]
    lis = "\n".join(f"""        <li class="border-t border-line pt-5">
          <div class="aspect-[4/5] max-w-[14rem] border border-line bg-paper-2" role="img" aria-label="Placeholder for a portrait of {nm}"></div>
          <h3 class="mt-4 font-medium">{nm}</h3>
          <p class="text-sm text-ink-2">{r}</p>
        </li>""" for nm, r in people)
    inner = f"""      {eyebrow(n, 'People')}
      {h2('team', 'Three people, no org chart.')}
      <ul role="list" class="mt-12 grid gap-8 sm:grid-cols-3">
{lis}
      </ul>"""
    return section("team", inner, band=True)


def contact_form(c: dict, n: int) -> str:
    field = 'class="mt-1 block w-full rounded-md border border-line bg-paper px-4 py-2.5 text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"'
    inner = f"""      <div class="grid gap-12 lg:grid-cols-[1fr_0.8fr]">
        <form action="#" method="post" class="max-w-xl space-y-5" data-contact-form novalidate>
          <div>
            <label for="cf-name" class="text-sm font-medium">Name</label>
            <input id="cf-name" name="name" type="text" required autocomplete="name" {field}>
          </div>
          <div>
            <label for="cf-email" class="text-sm font-medium">Email</label>
            <input id="cf-email" name="email" type="email" required autocomplete="email" {field}>
          </div>
          <div>
            <label for="cf-message" class="text-sm font-medium">What can we help with?</label>
            <textarea id="cf-message" name="message" rows="6" required {field}></textarea>
          </div>
          <p class="text-xs text-ink-2">We reply from {c['email']}, usually the same day.</p>
          <button type="submit" class="inline-flex h-11 items-center rounded-md bg-accent px-5 text-sm font-medium text-paper hover:bg-accent-deep focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">Send message</button>
        </form>
        <aside class="space-y-8 text-sm leading-6">
          <div><h3 class="font-mono text-xs uppercase tracking-[0.18em] text-ink-2">Visit</h3><p class="mt-2">14 Calls Lane<br>{c['city']} LS2 7EH<br>Thursday to Saturday, 10 to 5</p></div>
          <div><h3 class="font-mono text-xs uppercase tracking-[0.18em] text-ink-2">Write</h3><p class="mt-2"><a href="mailto:{c['email']}" class="underline decoration-accent decoration-2 underline-offset-4">{c['email']}</a></p></div>
          <div><h3 class="font-mono text-xs uppercase tracking-[0.18em] text-ink-2">Press and wholesale</h3><p class="mt-2">Same address, put the word in the subject line and Aiko picks it up first.</p></div>
        </aside>
      </div>"""
    return section("contact", inner, skill="contact-form")


def plans(c: dict, n: int) -> str:
    tiers = [("Monthly", "24", "month", "500 g, two bags, roasted the Monday before they ship.", False),
             ("Fortnightly", "14", "fortnight", "250 g every two weeks. Always fresh, never on a shelf.", True),
             ("Workshop", "90", "month", "2 kg for cafes and offices, invoice billing, same-day replies.", False)]
    cards = "\n".join(f"""        <li class="flex flex-col border border-line p-8 {'bg-accent-tint' if hi else 'bg-paper'}">
          {'<p class="font-mono text-xs uppercase tracking-[0.18em] text-accent-deep">Most chosen</p>' if hi else '<p class="font-mono text-xs uppercase tracking-[0.18em] text-ink-2">Plan</p>'}
          <h3 class="mt-2 text-2xl font-medium">{t}</h3>
          <p class="mt-1 text-sm text-ink-2">{d}</p>
          <p class="mt-6 text-4xl font-medium tabular-nums">&pound;{p}<span class="text-base text-ink-2"> / {per}</span></p>
          <ul class="mt-6 space-y-2 text-sm text-ink-2">
            <li>Free UK delivery</li><li>Pause for up to 3 months</li><li>Cancel from the account page</li>
          </ul>
          <div class="mt-8">{btn(c['contact'], 'Choose ' + t.lower(), primary=hi)}</div>
        </li>""" for t, p, per, d, hi in tiers)
    inner = f"""      {eyebrow(n, 'Pricing')}
      {h2('plans', 'Three plans. The middle one is what most people pick.')}
      <ul role="list" class="mt-12 grid gap-6 lg:grid-cols-3">
{cards}
      </ul>
      <p class="mt-6 text-sm text-ink-2">Prices include VAT. Invoice billing on request for the Workshop plan.</p>"""
    return section("plans", inner)


def docs_shell(c: dict, n: int) -> str:
    nav_items = "".join(f'<li><a href="#{slugify(x)}" class="block py-1 text-ink-2 hover:text-ink">{x}</a></li>' for x in ["Installation", "Configuration", "Deploying", "Troubleshooting"])
    return f"""  <!-- docs shell: {SKILL_FOR['docs-shell']} + web-page-docs + web-nav-scroll-spy-toc -->
  <section class="py-12" aria-labelledby="docs-heading">
    <div class="mx-auto grid max-w-6xl gap-12 px-6 lg:grid-cols-[14rem_1fr]">
      <nav aria-label="Documentation" class="lg:sticky lg:top-24 lg:self-start">
        <p class="font-mono text-xs uppercase tracking-[0.18em] text-ink-2">Guides</p>
        <ul class="mt-3 space-y-1 text-sm">{nav_items}</ul>
      </nav>
      <article class="max-w-3xl">
        <h1 id="docs-heading" class="text-title">Installation</h1>
        <p class="mt-4 text-lg leading-8 text-ink-2">{c['name']} runs anywhere Node 20 runs. The CLI is a single package; there is no global install.</p>
        <h2 id="configuration" class="mt-12 text-2xl font-medium">Configuration</h2>
        <p class="mt-3 leading-7">Create <code class="rounded-sm bg-paper-2 px-1.5 py-0.5 font-mono text-sm">{c['slug']}.config.js</code> in the project root. Every key is optional; the defaults below are what you get without the file.</p>
        <pre class="mt-4 overflow-x-auto border border-line bg-paper-2 p-6 font-mono text-sm leading-7"><code>export default {{
  outDir: "dist",
  port: 3000,
  minify: true,
}};</code></pre>
        <h2 id="deploying" class="mt-12 text-2xl font-medium">Deploying</h2>
        <p class="mt-3 leading-7">Run <code class="rounded-sm bg-paper-2 px-1.5 py-0.5 font-mono text-sm">npm run build</code> and publish the <code class="rounded-sm bg-paper-2 px-1.5 py-0.5 font-mono text-sm">dist</code> folder. The repository ships a GitHub Pages workflow; Cloudflare Pages and Netlify need the build command and output folder set in their dashboards.</p>
        <h2 id="troubleshooting" class="mt-12 text-2xl font-medium">Troubleshooting</h2>
        <p class="mt-3 leading-7">If the dev server starts but styles are missing, the Tailwind watcher is not running: check that <code class="rounded-sm bg-paper-2 px-1.5 py-0.5 font-mono text-sm">npm run dev</code> printed two processes, not one.</p>
      </article>
    </div>
  </section>"""


def prose_page(c: dict, title: str) -> str:
    return f"""  <!-- plain page: {SKILL_FOR['prose']} -->
  <section class="py-16 sm:py-24" aria-labelledby="page-heading">
    <div class="mx-auto max-w-6xl px-6">
      {eyebrow(1, title)}
      <h1 id="page-heading" class="mt-3 max-w-3xl text-display">{title}</h1>
      <div class="mt-8 max-w-2xl space-y-5 text-lg leading-8 text-ink-2">
        <p>This page was requested by name, so the scaffold gave it a heading and room for text. Write the real content here, then delete this paragraph.</p>
        <p>Keep the measure (max-w-2xl), the leading and the eyebrow; they match every other page on the {c['name']} site.</p>
      </div>
    </div>
  </section>"""


# ----------------------------------------------------------------------------- pages

def home_sections(c: dict) -> list[str]:
    k = c["kind"]
    if k == "landing":
        return [hero(c), features(c, 1), steps(c, 2), stats(c, 3), testimonials(c, 4), faq(c, 5), cta(c, 6)]
    if k == "blog":
        return [hero(c), posts(c, 1), newsletter(c, 2)]
    if k == "portfolio":
        return [hero(c), work(c, 1), testimonials(c, 2), cta(c, 3)]
    if k == "docs":
        return [hero(c), quickstart(c, 1), guides(c, 2), cta(c, 3)]
    return [hero(c), products(c, 1), stats(c, 2), newsletter(c, 3)]  # shop


def page_sections(c: dict, page: str) -> tuple[str, list[str]]:
    """Return (title, sections) for a non-home page."""
    n = c["name"]
    builders = {
        "about": (f"About {n}", [story(c, 1), team(c, 2), cta(c, 3)]),
        "contact": (f"Contact {n}", [contact_form(c, 1)]),
        "pricing": (f"Pricing at {n}", [plans(c, 1), faq(c, 2, standalone=True)]),
        "blog": (f"Journal from {n}", [posts(c, 1), newsletter(c, 2)]),
        "docs": (f"{n} documentation", [docs_shell(c, 1)]),
        "work": (f"Work by {n}", [work(c, 1), cta(c, 2)]),
        "shop": (f"Shop at {n}", [products(c, 1), faq(c, 2, standalone=True)]),
        "faq": (f"Questions about {n}", [faq(c, 1, standalone=True), cta(c, 2)]),
    }
    if page in builders:
        return builders[page]
    return (f"{page.replace('-', ' ').title()} at {n}", [prose_page(c, page.replace("-", " ").title())])


def page_html(c: dict, pages: list[str], page: str) -> str:
    if page == "home":
        title, secs = f"{c['name']}: {c['tagline']}", home_sections(c)
    else:
        title, secs = page_sections(c, page)
    # non-home pages open with a page heading unless the first section carries its own h1
    opener = ""
    if page != "home" and "<h1" not in secs[0]:
        label = PAGE_LABELS.get(page, page.title())
        opener = f"""  <section class="pt-16 sm:pt-24" aria-labelledby="page-heading">
    <div class="mx-auto max-w-6xl px-6">
      {eyebrow(0, label)}
      <h1 id="page-heading" class="mt-3 max-w-3xl text-display">{title}</h1>
    </div>
  </section>
"""
    return head(c, title) + navbar(c, pages, page) + opener + "\n\n".join(secs) + "\n" + footer(c, pages)


def not_found_html(c: dict, pages: list[str]) -> str:
    body = f"""  <!-- 404: {SKILL_FOR['404']} -->
  <section class="py-24 sm:py-32" aria-labelledby="page-heading">
    <div class="mx-auto max-w-6xl px-6">
      {eyebrow(404, 'Not found')}
      <h1 id="page-heading" class="mt-3 max-w-3xl text-display">That page is not here.</h1>
      <p class="mt-6 max-w-xl text-lg leading-8 text-ink-2">The link may be old or mistyped. The pages that do exist are in the menu above and the footer below.</p>
      <div class="mt-8">{btn('./index.html', 'Back to the start')}</div>
    </div>
  </section>
"""
    return head(c, f"Page not found: {c['name']}") + navbar(c, pages, "404") + body + footer(c, pages)


# ----------------------------------------------------------------------------- css, js, config

def input_css(c: dict) -> str:
    t, hue = c["t"], c["t"]["hue"]
    if t["dark"]:
        colors = f"""  --color-paper:       oklch(16% 0.012 var(--hue));
  --color-paper-2:     oklch(20% 0.014 var(--hue));
  --color-paper-3:     oklch(25% 0.016 var(--hue));
  --color-ink:         oklch(93% 0.010 var(--hue));
  --color-ink-2:       oklch(70% 0.012 var(--hue));
  --color-line:        oklch(30% 0.014 var(--hue));
  --color-accent:      oklch(78% {t['accent_c']:.2f} var(--hue));
  --color-accent-deep: oklch(86% {t['accent_c'] - 0.02:.2f} var(--hue));
  --color-accent-tint: oklch(24% 0.05 var(--hue));"""
    else:
        colors = f"""  --color-paper:       oklch(98% 0.006 var(--hue));
  --color-paper-2:     oklch(95% 0.010 var(--hue));
  --color-paper-3:     oklch(91% 0.014 var(--hue));
  --color-ink:         oklch(22% 0.015 var(--hue));
  --color-ink-2:       oklch(45% 0.015 var(--hue));
  --color-line:        oklch(85% 0.012 var(--hue));
  --color-accent:      oklch(55% {t['accent_c']:.2f} var(--hue));
  --color-accent-deep: oklch(45% {t['accent_c'] - 0.01:.2f} var(--hue));
  --color-accent-tint: oklch(94% 0.04 var(--hue));"""
    r = t["radius"]
    return f"""/* {c['name']}: tone "{c['tone']}" ({t['note']}).
   One hue, neutrals tinted toward it, one accent used only where the user acts.
   Change --hue to recolour the whole site. See web-craft-color-with-restraint and
   web-craft-typography-with-character for the reasoning behind every value here. */
@import "tailwindcss";

/* the one hue everything is tinted toward; outside @theme so it is always emitted */
:root {{ --hue: {hue}; }}

@theme {{
{colors}

  /* second hue for state only, never decoration */
  --color-ok:   oklch(55% 0.14 150);
  --color-warn: oklch(70% 0.15 80);
  --color-bad:  oklch(55% 0.19 25);

  --font-display: {t['display_stack']};
  --font-sans:    {t['body_stack']};
  --font-mono:    {t['mono_stack']};

  --text-display: clamp(2.5rem, 1.6rem + 3.2vw, 4.5rem);
  --text-display--line-height: 1.04;
  --text-display--letter-spacing: {t['tracking']};
  --text-title: clamp(1.75rem, 1.3rem + 1.5vw, 2.5rem);
  --text-title--line-height: 1.15;
  --text-title--letter-spacing: {t['tracking'] if t['tracking'] != '0' else '0'};

  /* three radii for the whole site: controls, buttons, containers */
  --radius-sm: {r[0]};
  --radius-md: {r[1]};
  --radius-lg: {r[2]};
}}

@layer base {{
  html {{ font-synthesis: none; }}
  body {{ background: var(--color-paper); color: var(--color-ink); font-feature-settings: "kern", "liga"; }}
  h1, h2, h3 {{ font-family: var(--font-display); font-weight: {t['weight']}; font-optical-sizing: auto; text-wrap: balance; }}
  ::selection {{ background: var(--color-accent-tint); }}
  @media (prefers-reduced-motion: no-preference) {{ html {{ scroll-behavior: smooth; }} }}
}}
"""


MAIN_JS = """// main.js: progressive enhancement only. The pages work without this file.
// Navbar toggle: web-nav-responsive-navbar
const toggle = document.querySelector("[data-nav-toggle]");
const menu = document.querySelector("[data-nav-menu]");

function setMenu(open) {
  if (!toggle || !menu) return;
  toggle.setAttribute("aria-expanded", String(open));
  menu.classList.toggle("hidden", !open);
  toggle.querySelector('[data-icon="open"]')?.classList.toggle("hidden", open);
  toggle.querySelector('[data-icon="close"]')?.classList.toggle("hidden", !open);
}

toggle?.addEventListener("click", () => setMenu(toggle.getAttribute("aria-expanded") !== "true"));
document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });
menu?.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setMenu(false)));

// Forms post nowhere yet. Wire them up with web-form-submit-with-fetch, then delete this block.
for (const form of document.querySelectorAll("[data-contact-form], [data-newsletter]")) {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const note = document.createElement("p");
    note.className = "mt-3 text-sm text-ok";
    note.setAttribute("role", "status");
    note.textContent = "Not connected yet: see README, section Forms.";
    form.append(note);
  });
}
"""

COPY_MJS = """// copy.mjs: copies everything except input.css from src to dist; --watch keeps going.
import { cp, watch } from "node:fs/promises";
const copy = () => cp("src", "dist", { recursive: true, filter: (p) => !p.endsWith("input.css") });
await copy();
if (process.argv.includes("--watch")) {
  console.log("watching src/");
  for await (const _ of watch("src", { recursive: true })) await copy();
}
"""

DEPLOY_YML = """# GitHub Pages via Actions. Repo Settings > Pages > Source: GitHub Actions. See web-ship-static-hosting.
name: Deploy
on: { push: { branches: [main] } }
permissions: { contents: read, pages: write, id-token: write }
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with: { path: dist }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: { name: github-pages, url: "${{ steps.d.outputs.page_url }}" }
    steps:
      - id: d
        uses: actions/deploy-pages@v4
"""

GITIGNORE = "node_modules/\ndist/\n.DS_Store\nThumbs.db\n.env\n"
EDITORCONFIG = "root = true\n\n[*]\nindent_style = space\nindent_size = 2\nend_of_line = lf\ncharset = utf-8\ninsert_final_newline = true\n"


def package_json(c: dict) -> str:
    return json.dumps({
        "name": c["slug"], "version": "0.1.0", "private": True, "type": "module",
        "engines": {"node": ">=20"},
        "scripts": {
            "dev": "concurrently -k -n css,copy,serve npm:dev:css npm:dev:copy npm:dev:serve",
            "dev:css": "tailwindcss -i src/input.css -o dist/output.css --watch",
            "dev:copy": "node scripts/copy.mjs --watch",
            "dev:serve": "serve dist -l 3000",
            "build": "node scripts/copy.mjs && tailwindcss -i src/input.css -o dist/output.css --minify",
            "preview": "serve dist",
        },
        "devDependencies": {"@tailwindcss/cli": "^4.1.0", "tailwindcss": "^4.1.0", "serve": "^14.2.0", "concurrently": "^9.0.0"},
    }, indent=2) + "\n"


def readme(c: dict, pages: list[str], files: dict[str, list[tuple[str, str]]]) -> str:
    t = c["t"]
    rows = []
    for p in pages:
        fn = "index.html" if p == "home" else f"{p}.html"
        for sec, skill in files[fn]:
            rows.append(f"| `src/{fn}` | {sec} | `{skill}` |")
    rows.append(f"| `src/404.html` | not found | `{SKILL_FOR['404']}` |")
    rows.append("| every page | navbar, footer | `web-nav-responsive-navbar`, `web-layout-footer`, `web-craft-finishing-details` |")
    rows.append("| `src/input.css` | colours, fonts, radii | `web-craft-color-with-restraint`, `web-craft-typography-with-character`, `web-css-variables-theming` |")
    rows.append("| `src/js/main.js` | menu toggle, form stubs | `web-js-modules-and-structure`, `web-form-submit-with-fetch` |")
    rows.append("| `.github/workflows/deploy.yml` | deploy | `web-ship-static-hosting`, `web-flow-ship-it` |")
    return f"""# {c['name']}

Scaffolded with `web-flow-new-site` from the web-skills pack.

- **What:** a {c['kind']} site
- **Pages:** {", ".join(pages)} (plus 404)
- **Tone:** {c['tone']} ({t['note']}); hue {t['hue']}, {t['display']} for headings, {t['body']} for text

## Run it

```bash
npm install          # creates package-lock.json; commit it, the deploy workflow needs it
npm run dev          # Tailwind watcher + copier + http://localhost:3000
npm run build        # production dist/
```

## What to do next, in order

1. Replace the copy. Every sentence is a believable placeholder written for the name, not for the business. Read `web-craft-copy-that-sounds-human` and `web-craft-real-content`, then rewrite the hero first.
2. Replace the grey panels (`role="img"` placeholders) with real photographs or screenshots. `web-design-images`, `web-perf-images`.
3. Wire the forms. They currently show a notice instead of sending. `web-form-submit-with-fetch`, or Netlify Forms via `web-ship-static-hosting`.
4. Review: `web-craft-self-review`, then run `vibe_check.py` from `web-craft-consistency-audit`.
5. Ship: `python <pack>/skills/web-flow-ship-it/scripts/ship.py . --target github-pages`.

## Forms

Both forms post to `#` and `src/js/main.js` intercepts the submit. Point `action` at a real endpoint and delete the stub block.

## Which skill to consult for each part

| File | Section | Skill |
|---|---|---|
{chr(10).join(rows)}

## Changing the look

- Recolour: change `--hue` in `src/input.css`. Every neutral and the accent follow.
- Fonts: swap the Google Fonts `<link>` in each page head and the three `--font-*` tokens.
- Corners: the three `--radius-*` tokens. Do not add a fourth.
- Dark mode: this scaffold is single-theme. `web-design-dark-mode` adds the second palette.
"""


# ----------------------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    ap.add_argument("--kind", default="landing", choices=sorted(DEFAULT_PAGES))
    ap.add_argument("--pages", default="")
    ap.add_argument("--tone", default="editorial", choices=sorted(TONES))
    ap.add_argument("--out", required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)

    pages: list[str] = []
    for raw in (a.pages.split(",") if a.pages else DEFAULT_PAGES[a.kind]):
        p = PAGE_ALIASES.get(raw.strip().lower(), slugify(raw))
        if p and p not in pages:
            pages.append(p)
    if "home" not in pages:
        pages.insert(0, "home")
    if "home" in pages and pages[0] != "home":
        pages.remove("home"); pages.insert(0, "home")

    out = Path(a.out)
    if (out / "src").exists() and not a.force:
        print(f"error: {out / 'src'} already exists; pass --force to overwrite", file=sys.stderr)
        return 2
    c = make_ctx(a.name, a.kind, a.tone, pages)

    written: dict[str, list[tuple[str, str]]] = {}
    files: dict[str, str] = {}
    sec_names = re.compile(r"<!-- ([a-z0-9 -]+?): (web-[a-z0-9-]+)")
    for p in pages:
        fn = "index.html" if p == "home" else f"{p}.html"
        html = page_html(c, pages, p)
        files[f"src/{fn}"] = html
        written[fn] = [(sec, skill) for sec, skill in sec_names.findall(html) if sec not in ("navbar", "footer")]
    files["src/404.html"] = not_found_html(c, pages)
    files["src/input.css"] = input_css(c)
    files["src/js/main.js"] = MAIN_JS
    files["scripts/copy.mjs"] = COPY_MJS
    files["package.json"] = package_json(c)
    files[".gitignore"] = GITIGNORE
    files[".editorconfig"] = EDITORCONFIG
    files[".github/workflows/deploy.yml"] = DEPLOY_YML
    files["README.md"] = readme(c, pages, written)

    for rel, content in files.items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"  wrote {rel}  ({content.count(chr(10)) + 1} lines)")
    print(f"\n{c['name']}: {a.kind} site, tone {a.tone}, pages {', '.join(pages)} -> {out.resolve()}")
    print("next: cd into it, npm install, npm run dev. README.md lists the skill for every section.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
