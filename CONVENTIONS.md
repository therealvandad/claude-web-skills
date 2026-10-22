# web-skills pack: conventions for every skill

Target stack: **plain HTML, CSS and JavaScript with Tailwind CSS v4**. No React, Vue, Svelte or
build-time framework. A skill may mention a tool (Tailwind CLI, Vite as a dev server) only where
the topic is about tooling.

## Folder and file

```
skills/<skill-name>/SKILL.md        # required, the only required file
skills/<skill-name>/example.html    # optional: a complete runnable page, only when it adds real value
```

`<skill-name>` is lowercase-with-hyphens and always starts with `web-`. The `name:` in the
frontmatter must equal the folder name exactly.

## SKILL.md shape

```markdown
---
name: web-layout-hero
description: <one to three sentences, max 60 words. First what the skill produces, then when to use it, worded a little pushily so Claude reaches for it: name the words a user would actually say. Example: "Build a hero section (headline, subcopy, call-to-action, optional image) with Tailwind. Use whenever a user asks for a landing page top, a banner, a 'first screen', or a page intro, even if they don't say 'hero'.">
---

# <Title>

<One short paragraph: what this is and why it matters. Explain the reasoning, not just the rule.>

## Pattern

<The main code. Complete, copy-pasteable HTML with Tailwind utility classes, plus any CSS or JS
needed. It must work when dropped into a page that loads Tailwind. Prefer one solid example over
five thin ones. 20 to 80 lines of code.>

## Variations

<Two to four bullet points: how to adapt it (sizes, dark mode, alignment, with/without image...).
Each bullet one or two sentences, with a class or snippet where helpful.>

## Pitfalls

<Three to six bullets of things that commonly go wrong and how to avoid them: responsive breakage,
accessibility, performance, Tailwind-specific gotchas.>

## Related skills

<Bullets naming other skills from the pack by exact name, e.g. `web-nav-responsive-navbar`.>
```

Length: 60 to 160 lines total. Not shorter (then it is not useful), not longer (it is loaded into
context every time it triggers).

## Code rules

- **Tailwind v4** conventions: utilities as usual; theming via `@theme { --color-brand: ... }` in CSS,
  not `tailwind.config.js`. Dark mode via the `dark:` variant (default `prefers-color-scheme`; note
  the `@custom-variant dark (&:where(.dark, .dark *));` line when a class toggle is wanted).
  For quick prototypes the Play CDN is `<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>`;
  for production, `@tailwindcss/cli` (`npx @tailwindcss/cli -i src/input.css -o dist/output.css --watch`).
- **Mobile first**: base classes for small screens, then `sm:` `md:` `lg:` upward.
- **Semantic HTML first**: `<header> <nav> <main> <section> <article> <aside> <footer>`, real
  `<button>`s, `<a>` only for navigation, labels tied to inputs.
- **Accessible by default**: visible focus (`focus-visible:` rings), `aria-*` only where native
  semantics are not enough, keyboard works for everything a mouse can do, respect
  `prefers-reduced-motion` for any animation.
- **JavaScript**: modern (ES2022+), `const`/`let`, `addEventListener`, no jQuery, no globals
  except what is deliberately exported. Small, named functions. Progressive enhancement: the HTML
  should still make sense if the script fails.
- **No external libraries** unless the skill is specifically about one; then pin a version.
- Code blocks are fenced with the right language: ```html ```css ```js ```bash.
- Keep prose tight. Explain *why* once, then show the code.

## Tone

Write for a capable developer who wants to move fast. Imperative mood ("Use", "Wrap", "Avoid").
No filler, no marketing voice, no "In this skill we will".
