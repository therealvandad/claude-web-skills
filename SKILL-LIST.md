# The 130 skills (13 groups × 10)

## Group 1: Page layouts (`web-layout-*`)
1. web-layout-page-shell — header / main / footer skeleton with sticky footer, max-width container, responsive padding
2. web-layout-hero — hero section: headline, subcopy, CTAs, optional image or illustration, variants (centered, split, with background)
3. web-layout-feature-grid — "features" section: icon + title + text cards in a responsive grid
4. web-layout-pricing-table — pricing tiers with highlighted plan, monthly/yearly toggle (JS)
5. web-layout-testimonials — testimonial cards / quote wall, with avatar, name, role; optional scroller
6. web-layout-footer — multi-column footer with links, newsletter form, social icons, legal row
7. web-layout-dashboard-sidebar — app shell: collapsible sidebar + topbar + content area
8. web-layout-landing-page — full landing page composition: order of sections, spacing rhythm, CTA placement
9. web-layout-card-grid — responsive card grid (blog posts, products) with equal-height cards and image handling
10. web-layout-split-section — two-column media/text sections that alternate, stack on mobile

## Group 2: CSS techniques (`web-css-*`)
11. web-css-responsive-grid — CSS grid auto-fit/auto-fill, `grid-template-areas`, Tailwind grid utilities
12. web-css-flexbox-patterns — the flexbox recipes: center, space-between bars, wrap with gap, push-right, holy-grail
13. web-css-container-queries — `@container` and Tailwind `@container` / `@md:` for component-level responsiveness
14. web-css-fluid-typography — `clamp()` type scale, Tailwind arbitrary values, fluid spacing
15. web-css-spacing-scale — a consistent spacing system; section rhythm; when to use gap vs margin
16. web-css-aspect-ratio-media — `aspect-ratio`, `object-fit`, responsive video embeds, image containers
17. web-css-sticky-and-fixed — sticky headers/sidebars/table headers, `position: fixed` safe areas, z-index strategy
18. web-css-variables-theming — CSS custom properties, Tailwind v4 `@theme`, semantic tokens (bg/fg/accent)
19. web-css-modern-reset — what Tailwind Preflight does, what to add (text-wrap balance, scrollbar, focus styles)
20. web-css-layers-and-organization — `@layer`, file structure for CSS, Tailwind `@layer components`, `@apply` guidance

## Group 3: Navigation (`web-nav-*`)
21. web-nav-responsive-navbar — top bar with logo, links, CTA, hamburger menu on mobile (accessible toggle)
22. web-nav-mega-menu — large hover/click menu with columns, keyboard and touch handling
23. web-nav-sidebar — collapsible vertical nav with sections, active state, icons
24. web-nav-breadcrumbs — breadcrumb trail with `nav aria-label`, truncation on mobile, JSON-LD hint
25. web-nav-tabs — accessible tab panels (roving tabindex, arrow keys), URL hash sync
26. web-nav-pagination — pagination controls, "load more", infinite scroll trade-offs
27. web-nav-dropdown-menu — accessible dropdown/menu button (Escape, arrow keys, click-outside)
28. web-nav-sticky-header — header that shrinks/hides on scroll, with reduced-motion fallback
29. web-nav-scroll-spy-toc — table of contents that highlights the current section (IntersectionObserver)
30. web-nav-anchor-and-smooth-scroll — in-page links, `scroll-margin-top` under sticky headers, smooth scrolling

## Group 4: Forms (`web-form-*`)
31. web-form-layout — form structure: fieldsets, labels, help text, error placement, responsive columns
32. web-form-validation — HTML constraint validation + JS enhancement, inline errors, `aria-describedby`, `aria-invalid`
33. web-form-input-states — focus, disabled, readonly, invalid, loading states; floating labels
34. web-form-select-and-combobox — native select styling; accessible custom combobox with filtering
35. web-form-file-upload — drag-and-drop file zone, previews, size/type checks
36. web-form-multi-step — wizard with progress, per-step validation, state kept in one object
37. web-form-search-suggestions — search input with debounced suggestions, keyboard selection
38. web-form-choices — checkboxes, radios, switches, segmented controls, styled with Tailwind
39. web-form-submit-with-fetch — submit via `fetch`, loading/success/error UI, honeypot, FormData
40. web-form-password-fields — show/hide toggle, strength meter, confirm match, autocomplete attributes

## Group 5: UI components (`web-ui-*`)
41. web-ui-modal-dialog — `<dialog>` element modals: open/close, focus trap, backdrop, scroll lock
42. web-ui-toast-notifications — toast stack with auto-dismiss, `aria-live`, queue
43. web-ui-accordion — `<details>/<summary>` accordion, exclusive mode via `name`, animation
44. web-ui-tooltip-and-popover — Popover API, tooltips on hover/focus, positioning without libraries
45. web-ui-carousel — scroll-snap carousel with buttons, dots, autoplay with pause
46. web-ui-data-table — responsive table, sortable columns, filter box, sticky header, mobile stacking
47. web-ui-cards — card anatomy: media, body, actions; clickable card pattern that stays accessible
48. web-ui-badges-chips-tags — status badges, removable chips, counts
49. web-ui-skeleton-and-loading — skeleton screens, spinners, progress bars, `aria-busy`
50. web-ui-buttons — button system: variants, sizes, icon buttons, loading, button groups

## Group 6: Design system (`web-design-*`)
51. web-design-typography-system — type scale, line-height, measure, headings vs body, Tailwind `@theme` fonts
52. web-design-color-system — palette building, semantic colors, Tailwind v4 `@theme` colors, contrast
53. web-design-dark-mode — class toggle with persistence, `color-scheme`, images and shadows in dark
54. web-design-icons — inline SVG, sprite with `<use>`, sizing with `currentColor`, when to use icon fonts (never)
55. web-design-images — `<picture>`, `srcset`/`sizes`, formats, art direction, placeholders
56. web-design-shadows-and-elevation — elevation scale, Tailwind shadows, layered shadows, dark-mode elevation
57. web-design-borders-radius-dividers — radius scale, borders vs rings, dividers, nesting radii correctly
58. web-design-empty-and-error-states — empty, error, offline and 404 states with helpful copy
59. web-design-tokens-to-tailwind — turning a design spec (Figma tokens) into a Tailwind v4 `@theme` block
60. web-design-ui-polish-checklist — the final pass: alignment, spacing, contrast, hover/focus, text wrapping, truncation

## Group 7: Motion (`web-motion-*`)
61. web-motion-transitions — transition basics, what to animate (transform/opacity), easing, durations
62. web-motion-keyframes — `@keyframes` and Tailwind `animate-*`, custom animations in `@theme`
63. web-motion-scroll-reveal — reveal-on-scroll with IntersectionObserver, staggering, reduced-motion
64. web-motion-view-transitions — View Transitions API for same-document and cross-document transitions
65. web-motion-hover-microinteractions — buttons, cards, links: subtle lift, underline grow, icon nudge
66. web-motion-loading-and-progress — spinners, indeterminate bars, skeleton shimmer
67. web-motion-parallax-and-scroll-driven — `animation-timeline: scroll()` / `view()`, subtle parallax
68. web-motion-page-transitions — fade/slide between pages or panels, preserving focus
69. web-motion-reduced-motion — `prefers-reduced-motion` strategy, `motion-safe:` / `motion-reduce:` in Tailwind
70. web-motion-counters-and-tickers — animated numbers, marquee/ticker with scroll-snap, pausing

## Group 8: Accessibility and SEO (`web-a11y-*`, `web-seo-*`)
71. web-a11y-semantic-html — landmarks, headings, lists, buttons vs links, native elements first
72. web-a11y-aria-patterns — when ARIA is needed, the common roles/states, the "no ARIA is better than bad ARIA" rule
73. web-a11y-keyboard-and-focus — focus order, focus-visible styling, focus trapping, restoring focus
74. web-a11y-color-contrast — WCAG ratios, checking contrast, non-color cues, Tailwind palette picks that pass
75. web-a11y-skip-links-and-landmarks — skip link, landmark structure, `aria-label` on repeated regions
76. web-a11y-images-and-media — alt text rules, decorative images, captions, transcripts, `prefers-reduced-motion` for video
77. web-seo-meta-tags — title/description, canonical, Open Graph, Twitter cards, favicons, viewport
78. web-seo-structured-data — JSON-LD for Organization, Article, Product, Breadcrumb, FAQ
79. web-seo-sitemap-robots-urls — sitemap.xml, robots.txt, clean URLs, trailing slashes, redirects
80. web-seo-content-structure — heading outline, one H1, internal linking, readable URLs, text in HTML not images

## Group 9: Performance and shipping (`web-perf-*`, `web-ship-*`)
81. web-perf-images — compression, WebP/AVIF, lazy loading, `fetchpriority`, dimensions to avoid CLS
82. web-perf-fonts — self-hosting, `font-display`, subsetting, preloading, variable fonts, fallbacks with `size-adjust`
83. web-perf-css-and-js-loading — critical CSS, `defer`/`type=module`, splitting, avoiding render blocking
84. web-perf-web-vitals — LCP/INP/CLS: what they are, how to measure, the usual fixes
85. web-perf-caching-and-service-worker — cache headers, immutable assets with hashes, a minimal offline service worker
86. web-ship-project-setup — folder structure, Tailwind CLI setup, npm scripts, live reload, `.gitignore`
87. web-ship-tailwind-production — production build, content detection in v4, minification, purging checks
88. web-ship-static-hosting — deploy to GitHub Pages, Netlify, Cloudflare Pages, Vercel: configs and gotchas
89. web-ship-analytics-and-privacy — lightweight analytics, consent, cookie-free options, privacy page
90. web-ship-launch-checklist — pre-launch checklist: 404 page, favicons, forms tested, meta, Lighthouse, broken links

## Group 10: JavaScript code help (`web-js-*`)
91. web-js-dom-utilities — tiny helpers (`$`, `$$`, delegation, `create`), when not to write a framework
92. web-js-fetch-and-apis — async/await, error handling, timeouts with AbortController, JSON, retries
93. web-js-state-and-render — small store + render function pattern for interactive widgets without a framework
94. web-js-storage — localStorage/sessionStorage with JSON, versioning, quota errors, IndexedDB pointer
95. web-js-events-debounce-throttle — event patterns, delegation, debounce/throttle, passive listeners, cleanup
96. web-js-modules-and-structure — ES modules, file layout, one-entry-per-page, importmaps, no bundler needed
97. web-js-web-components — custom elements for reusable widgets, shadow DOM or light DOM with Tailwind
98. web-js-errors-and-logging — try/catch strategy, global error handlers, user-facing error UI, console discipline
99. web-js-clean-code — naming, small functions, early returns, comments that explain why, data-attribute hooks
100. web-js-router-and-urls — URL state (query params, hash), History API, a minimal client-side router

## Group 11: Craft, so it does not look vibe-coded (`web-craft-*`)
101. web-craft-anti-generic-design — the tells of AI-generated pages (gradient text, purple-blue palette, glass cards, emoji icons, three identical cards, everything centred, decorative blobs) and the specific alternative for each
102. web-craft-typography-with-character — choosing and pairing fonts beyond the default sans, expressive headings, optical sizing, when a serif or mono earns its place
103. web-craft-copy-that-sounds-human — concrete, specific copy: banned words (seamless, unlock, elevate, empower, effortless), headline formulas with real nouns and numbers, button labels that say what happens
104. web-craft-layout-with-intention — asymmetry, varied section shapes, breaking the grid on purpose, whitespace as a tool, not every section a centred heading over a card row
105. web-craft-color-with-restraint — one accent, warm or cool neutrals instead of pure gray, no rainbow gradients, deriving a palette from a brand or photo, tinted surfaces
106. web-craft-finishing-details — hairline borders, numbered sections, small-caps labels, subtle texture, aligned baselines, consistent icon weight: the details that read as handmade
107. web-craft-real-content — design around real content, no lorem ipsum or placeholder avatars in demos, realistic data, real-sounding names and numbers, product screenshots that look like the product
108. web-craft-code-structure — the code tells of vibe coding (one 2,000-line file, repeated class strings, inline onclick, magic numbers, dead code, console.log) and how to restructure: partials, components, tokens, a utilities layer
109. web-craft-consistency-audit — audit a page for drift: radius, spacing, button and icon variants, heading sizes; run `scripts/vibe_check.py` to count distinct values and flag generic tells
110. web-craft-self-review — the pre-ship review ritual: squint test, read every sentence aloud, keyboard walk, phone pass, delete anything that does not earn its place, compare against one real site you admire

## Group 12: Whole-page layouts (`web-page-*`)
111. web-page-blog-post — article page: title block with meta, 65ch prose measure, sticky table of contents, figures with captions, author box, related posts
112. web-page-blog-index — post listing: featured post, magazine grid, category filter, pagination, RSS link
113. web-page-portfolio — project index grid plus a case-study page: problem, process, outcome, full-bleed images, next project link
114. web-page-about-team — about page: origin story, values, team grid with roles, timeline, press and contact
115. web-page-contact — contact page: form beside address, hours, map embed, alternative channels, success state
116. web-page-product-detail — e-commerce product page: image gallery with thumbnails, sticky buy box, variants, specs table, reviews
117. web-page-docs — documentation layout: left sidebar nav, content column, right "on this page", prev/next, code blocks, search box
118. web-page-auth — login, signup and password-reset pages: centred card and split-with-image variants, error and success states
119. web-page-help-center — help centre: search hero, category cards, article accordions, "still stuck" contact row
120. web-page-404-and-legal — 404, maintenance, privacy and terms pages: useful 404, legal page with sticky TOC and "last updated"

## Group 13: Section layouts (`web-section-*`)
121. web-section-stats-band — numbers band: 3 to 4 big figures with labels, source line, optional count-up, dark and light variants
122. web-section-logo-cloud — customer logo strip: grayscale row, wrap on mobile, marquee variant, "as seen in" variant
123. web-section-cta-band — final call-to-action band: headline, one button, reassurance line; dark, brand and bordered variants
124. web-section-steps-timeline — process steps: numbered horizontal steps, vertical timeline with dates, connecting lines in CSS
125. web-section-comparison-table — feature comparison: sticky first column, check and dash cells, highlighted plan, mobile card fallback
126. web-section-bento-grid — bento layout: mixed-size tiles with spans, one hero tile, dense packing, responsive collapse
127. web-section-gallery-masonry — image gallery: CSS columns masonry, grid with spans, lightbox via dialog, lazy loading
128. web-section-team-grid — people grid: photo, name, role, social links; compact list variant; hover and focus states
129. web-section-newsletter-signup — newsletter section: inline form, privacy line, success state, honeypot, dark variant
130. web-section-before-after-slider — before/after image comparison with a draggable range handle, keyboard support, labels
