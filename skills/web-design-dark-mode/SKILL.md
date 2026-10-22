---
name: web-design-dark-mode
description: 'Add dark mode to a Tailwind v4 site: a three-way light/dark/system toggle persisted in localStorage with no flash on load, `color-scheme` for native controls, and rules for images, shadows, borders and brand colors in dark. Use whenever a user asks for dark mode, a theme switcher, "night mode", or complains the site flashes white on reload.'
---

# Dark mode

Dark mode is a token swap plus three details people forget: the choice must apply before first paint (or the page flashes), native controls and scrollbars must follow via `color-scheme`, and shadows, borders and photos need different treatment because there is no darker-than-black to cast a shadow into. Tailwind v4's `dark:` variant follows `prefers-color-scheme` by default; one `@custom-variant` line makes it follow a class instead, which is what a user-controlled toggle needs.

## Pattern

```css
@import "tailwindcss";
/* Make dark: respond to a .dark class on <html> (or any ancestor) instead of the OS setting. */
@custom-variant dark (&:where(.dark, .dark *));

@layer base {
  html { color-scheme: light; }
  html.dark { color-scheme: dark; }   /* form controls, scrollbars, <select> popups go dark too */
}
```

```html
<head>
  <!-- Inline and FIRST in <head>: runs before any paint, so no flash. -->
  <script>
    (() => {
      const stored = localStorage.getItem('theme');          // 'light' | 'dark' | null (= system)
      const system = matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', stored ? stored === 'dark' : system);
    })();
  </script>
  <meta name="color-scheme" content="light dark">
</head>

<body class="bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
  <fieldset class="inline-flex rounded-lg border border-gray-200 p-1 dark:border-gray-800" id="theme">
    <legend class="sr-only">Theme</legend>
    <label class="cursor-pointer rounded-md px-3 py-1.5 text-sm has-checked:bg-gray-100 dark:has-checked:bg-gray-800">
      <input type="radio" name="theme" value="light" class="sr-only">Light</label>
    <label class="cursor-pointer rounded-md px-3 py-1.5 text-sm has-checked:bg-gray-100 dark:has-checked:bg-gray-800">
      <input type="radio" name="theme" value="dark" class="sr-only">Dark</label>
    <label class="cursor-pointer rounded-md px-3 py-1.5 text-sm has-checked:bg-gray-100 dark:has-checked:bg-gray-800">
      <input type="radio" name="theme" value="system" class="sr-only">System</label>
  </fieldset>

  <!-- A card: borders instead of shadows in dark, raised surface a step lighter than the page. -->
  <article class="mt-6 rounded-xl bg-white p-6 shadow-md ring-1 ring-gray-200
                  dark:bg-gray-900 dark:shadow-none dark:ring-gray-800">
    <img src="chart-light.png" alt="Monthly revenue" class="dark:hidden">
    <img src="chart-dark.png"  alt="Monthly revenue" class="hidden dark:block">
    <p class="mt-3 text-gray-600 dark:text-gray-400">Photos dim slightly so they do not glare:</p>
    <img src="photo.jpg" alt="" class="mt-2 rounded-lg dark:brightness-90">
  </article>
</body>
```

```js
const group = document.getElementById('theme');
const media = matchMedia('(prefers-color-scheme: dark)');

function apply(choice) {
  const dark = choice === 'system' ? media.matches : choice === 'dark';
  document.documentElement.classList.toggle('dark', dark);
}

// Reflect the stored choice in the radios, then listen for changes.
const current = localStorage.getItem('theme') ?? 'system';
group.querySelector(`[value="${current}"]`).checked = true;

group.addEventListener('change', (e) => {
  const choice = e.target.value;
  if (choice === 'system') localStorage.removeItem('theme'); else localStorage.setItem('theme', choice);
  apply(choice);
});
media.addEventListener('change', () => { if (!localStorage.getItem('theme')) apply('system'); });
```

The radios are real inputs, so keyboard arrows switch themes and the state survives a script failure as a plain form. `has-checked:` styles the selected label without JS.

## Variations

- **Two-state button.** Swap the radios for one `<button aria-pressed>` that toggles `dark`; keep the inline head script identical. Set `aria-label="Switch to dark theme"` and update it on toggle.
- **Semantic tokens instead of `dark:` everywhere.** Define `--color-surface`, `--color-fg` in `@theme` and re-point them under `.dark { }`; then components use `bg-surface` with no `dark:` prefix at all. See `web-design-color-system`.
- **Dark-only site.** Skip the toggle, put `class="dark"` on `<html>`, set `color-scheme: dark`, and still write the light values so a future switch is cheap.
- **Transition on switch.** Add `transition-colors duration-300` to `body` and large surfaces only, inside `motion-safe:`; animating every element's color is janky.

## Pitfalls

- Putting the theme script at the end of `<body>` or in a deferred module brings the white flash back; it must be inline, synchronous, and before any stylesheet-dependent content.
- Forgetting `color-scheme` leaves white scrollbars, white `<select>` dropdowns and white date pickers inside a dark page.
- Shadows disappear on dark backgrounds. Replace `shadow-lg` with `dark:shadow-none dark:ring-1 dark:ring-white/10` or make the raised surface a lighter step than the page; see `web-design-shadows-and-elevation`.
- Pure white text (`#fff`) on near-black halos on many displays; use `gray-100` or `gray-200` for body copy and keep white for headings only.
- Saturated brand colors from light mode (e.g. `brand-600`) look muddy on dark; move accents two steps lighter (`dark:bg-brand-400`, `dark:text-brand-300`).
- Logos and illustrations with transparent backgrounds and dark strokes vanish. Ship a second asset or use `dark:invert` only for pure black single-color marks.

## Related skills

- `web-design-color-system`
- `web-css-variables-theming`
- `web-design-shadows-and-elevation`
- `web-js-storage`
- `web-a11y-color-contrast`
