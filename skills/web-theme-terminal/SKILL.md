---
name: web-theme-terminal
description: 'Drop a tasteful dark terminal look onto a site in Tailwind v4: JetBrains Mono, a near-black green-tinted paper (never #000), pale ink, one phosphor accent (never #0f0), prompt and cursor motifs, 1px borders, no glow, real 4.5:1 contrast. Use whenever a user says "hacker look", "terminal", "console", "CLI aesthetic", "like a code editor", "retro computer", "matrix" or "developer tool vibe".'
---

# Terminal theme

The terminal look is a dark field, a monospace voice and one luminous colour that means "the machine is talking". Done badly it is `#000` with `#0f0` text, scanlines and a glow on everything, which is unreadable within a minute. Done well it is the colour scheme of a good editor: a dark paper with a hint of green, ink that is pale rather than neon, the phosphor reserved for prompts, links and the cursor, and typographic rhythm from the mono grid itself.

## Pattern

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400..700;1,400&display=swap">
```

```css
@import "tailwindcss";

@theme {
  --font-mono: "JetBrains Mono", ui-monospace, "Cascadia Code", "SF Mono", monospace;
  --font-sans: var(--font-mono);          /* everything is mono, body included */

  --color-paper:   oklch(17% 0.012 160);  /* not #000: shadows and borders need room below ink */
  --color-paper-2: oklch(21% 0.014 160);
  --color-paper-3: oklch(26% 0.016 160);
  --color-ink:     oklch(88% 0.02 150);   /* pale green-white, not neon */
  --color-ink-2:   oklch(64% 0.025 155);
  --color-line:    oklch(32% 0.018 160);
  --color-accent:      oklch(80% 0.17 150);  /* phosphor: prompts, links, cursor, focus */
  --color-accent-deep: oklch(68% 0.16 150);
  --color-accent-tint: oklch(26% 0.05 150);
  --color-warn: oklch(80% 0.15 80);       /* amber, for state only */
  --color-bad:  oklch(70% 0.17 25);

  --radius-*: initial;
  --radius-sm: 2px;                       /* enough to stop pixel corners looking broken */
  --shadow-*: initial;                    /* no glow, no drop shadows; depth comes from paper steps */

  --text-display: clamp(2rem, 1.2rem + 3vw, 3.75rem);
  --text-display--line-height: 1.1;
  --text-display--letter-spacing: -0.02em;
  --text-title: 1.5rem;
  --text-title--line-height: 1.3;
  --text-body: 0.9375rem;
  --text-body--line-height: 1.7;
  --text-label: 0.75rem;
  --text-label--line-height: 1.4;
  --text-label--letter-spacing: 0.04em;
}

@layer base {
  html { color-scheme: dark; }
  body { background: var(--color-paper); color: var(--color-ink); font-family: var(--font-mono); font-variant-ligatures: none; }
  h1, h2, h3 { font-weight: 600; text-wrap: balance; }
  h2::before { content: "## "; color: var(--color-ink-2); }
  a { color: var(--color-accent); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }
  a:hover { color: var(--color-accent-deep); background: var(--color-accent-tint); }
  hr { border: 0; border-top: 1px dashed var(--color-line); }
  :focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
  ::selection { background: var(--color-accent); color: var(--color-paper); }
  .prompt::before { content: "$ "; color: var(--color-accent); }
  .cursor::after { content: "▍"; color: var(--color-accent); animation: blink 1.1s steps(1) infinite; }
  @keyframes blink { 50% { opacity: 0; } }
  @media (prefers-reduced-motion: reduce) { .cursor::after { animation: none; } }
}
```

```html
<main class="mx-auto max-w-4xl px-6 py-12 text-body">
  <header class="flex flex-wrap items-baseline justify-between gap-3 border-b border-line pb-3 text-label">
    <p class="text-ink-2">quill ~ static site compiler</p>
    <nav class="flex gap-5"><a href="/docs" aria-current="page">docs</a><a href="/changelog">changelog</a><a href="https://github.com/example/quill">source</a></nav>
  </header>

  <section class="py-16">
    <p class="prompt text-ink-2">quill build --watch</p>
    <h1 class="mt-6 text-display">A site compiler that finishes before you alt-tab<span class="cursor" aria-hidden="true"></span></h1>
    <p class="mt-6 max-w-[62ch] text-ink-2">Markdown in, HTML out, 1,200 pages in 240 ms. No plugin API, no config file longer than ten lines, no runtime JavaScript unless you write it.</p>
    <div class="mt-8 flex flex-wrap gap-3">
      <a href="/docs/install" class="rounded-sm bg-accent px-4 py-2 font-semibold text-paper no-underline hover:bg-accent-deep hover:text-paper">Install, 1 binary</a>
      <a href="/docs/why" class="rounded-sm border border-line px-4 py-2 no-underline hover:border-accent">Read the design notes</a>
    </div>
  </section>

  <section class="border-t border-line py-10">
    <h2 class="text-title">Last build</h2>
    <pre class="mt-5 overflow-x-auto rounded-sm border border-line bg-paper-2 p-5 text-sm leading-7"><code><span class="text-ink-2">12:04:31</span> <span class="text-accent">ok</span>    content/posts/2026-10-19-caches.md   8 ms
<span class="text-ink-2">12:04:31</span> <span class="text-accent">ok</span>    content/docs/install.md              3 ms
<span class="text-ink-2">12:04:31</span> <span class="text-warn">warn</span>  content/docs/old-cli.md  front matter has no "date"
<span class="text-ink-2">12:04:31</span> <span class="text-ink-2">done</span>  1,204 pages, 241 ms, 0 errors</code></pre>
  </section>
</main>
```

What this theme does: one mono family at 15px with 1.7 leading, headings that prefix themselves like markdown, a `$` prompt and a blinking block cursor as the only motifs, three steps of dark paper for depth instead of shadows, the phosphor on prompts, links, the primary button, focus and `ok` state, amber and red for warnings and errors only.

What it never does: pure `#000` paper, pure `#0f0` or any accent above chroma 0.2, text glow or `text-shadow`, scanline or CRT overlays, more than one blinking element, ASCII art as decoration, typewriter animations on body text, a sans-serif anywhere, a light mode by default.

## Variations

- **Amber phosphor**: `--color-accent: oklch(80% 0.16 75)`, tints at hue 75, paper at hue 60. Same contrast, warmer, less "hacker".
- **Paper-white "man page" mode** for users who ask: `paper oklch(96% 0.006 150)`, `ink oklch(20% 0.02 160)`, accent `oklch(45% 0.14 150)`. Override in `.light` or `prefers-color-scheme: light`; the dark theme stays the default.
- **Window chrome** on one block: a title bar `flex gap-1.5 border-b border-line bg-paper-3 px-3 py-2` with three `size-2.5 rounded-[50%] bg-line` dots. One per page, not on every card.
- **Status line footer**: `fixed bottom-0 inset-x-0 border-t border-line bg-paper-2 px-4 py-1 text-label` with path, build time and `pb-[env(safe-area-inset-bottom)]`.

## Pitfalls

- `ink-2` at 64% on `paper` at 17% is 5.6:1; on `paper-3` at 26% it drops to 3.9:1. Secondary text goes on `paper` or `paper-2` only.
- A blinking cursor is a flashing element; keep it under 3 Hz (1.1s here), one per page, and disable it under `prefers-reduced-motion`.
- Ligatures (`=>` becoming an arrow) confuse readers in prose; `font-variant-ligatures: none` on body, re-enable only inside `<code>` if wanted.
- `h2::before` content is read by some screen readers as "number number"; if headings are navigated often, move the `##` to a `<span aria-hidden="true">` in the markup instead.
- Mono at 14px and below looks authentic and reads terribly on phones; 15px body, 13px labels minimum.
- `color-scheme: dark` makes native inputs and scrollbars dark, which is wanted, but the Play CDN loads after first paint; set `background` on `<html>` inline for a flash-free load.

## Related skills

- `web-craft-color-with-restraint`
- `web-craft-typography-with-character`
- `web-design-dark-mode`
- `web-css-variables-theming`
- `web-design-tokens-to-tailwind`
- `web-motion-reduced-motion`
- `web-theme-switcher`
