---
name: web-craft-self-review
description: Run a pre-ship self-review as a fixed sequence with pass/fail checks: squint test, read every sentence aloud, swap test, keyboard walk, 375px pass, delete pass, side-by-side against a site you admire, then an ordered fix list. Use when a user says "review before I ship", "does this look done", "does it look AI generated" or "is it ready".
---

# Self-review before shipping

The last pass on a page is the one most often skipped, and it is where "vibe coded" is decided. A review is only useful if it is a ritual: the same checks in the same order, each with a pass or fail you can state in one sentence, ending in a list you fix top down. Do it with the page open in a browser, not by rereading the source. Twenty minutes; stop when every check passes or is consciously waived.

## Pattern

Run the seven checks in order. Write the result of each as one line in `REVIEW.md` or in the reply, then fix.

```markdown
### 1. Squint test
Blur the page (step back, or `html { filter: blur(6px) }` in DevTools for ten seconds).
PASS: one thing is clearly biggest, one is second; sections read as different shapes.
FAIL: an even grey soup of same-size cards, or three equal headings competing.
Fix: one `text-display` headline per page, one accent element per section, vary section
shape (full-bleed, split, single column) instead of card-row, card-row, card-row.

### 2. Read every sentence aloud
Every heading, paragraph, button and alt text, out loud, as if to a colleague.
PASS: you could say it to a person without wincing.
FAIL: "Unlock seamless, effortless workflows." "Learn more." "Get started today."
Fix: say what it does and to whom, with a noun and a number: "Close the month in 2 days,
not 11." Buttons name the outcome: "Start a free ledger", "See the queue".

### 3. Swap test
Cover the logo. Could this hero sit above any other product in the category?
PASS: the headline, screenshot or first sentence names something only this product does.
FAIL: "The modern platform for teams" over an abstract gradient could be anyone's.
Fix: lead with the specific mechanism or result; show the real screen, not a blob.

### 4. Keyboard walk
Click the address bar, then Tab through the whole page to the footer.
PASS: focus is visible on every stop, order follows reading order, Esc closes anything
that opened, nothing is reachable by mouse only, no focus trap outside dialogs.
FAIL: focus disappears on cards, jumps into the hidden mobile menu, or Tab skips a button.
Fix: `focus-visible:` rings on every interactive element; `hidden`/`inert` on closed
panels; real `<button>`s, not `<div onclick>`.

### 5. 375px pass
DevTools, iPhone SE width, no zoom.
PASS: no horizontal scroll, nothing touches the edge, tap targets at least 44px,
headline wraps to at most three lines, tables scroll inside their own box.
FAIL: a `w-[600px]` screenshot overflowing, `text-6xl` headline eight lines deep.
Fix: `px-4` on the outer container, `max-w-full`, `text-4xl sm:text-6xl`, `overflow-x-auto`.

### 6. Delete pass
For each section, and each element inside the hero, hide it (`display:none` in DevTools)
and ask: did the page get worse? If not, keep it deleted.
Usual casualties: the "trusted by" row with four grey logos, the third CTA, the stats
block with round numbers, the decorative blob, the second testimonial that says the
same as the first, the icon next to every feature title.

### 7. Side-by-side
Open one real site you admire at the same width: linear.app, stripe.com, vercel.com,
arc.net or posthog.com. Compare, do not copy: how many type sizes on their first screen
(usually three), how dense the nav is, how much of the viewport is empty, where the
first screenshot sits, how quiet the footer is. Name two concrete differences.
PASS: you can say what they do that you do not, in specifics (not "it feels cleaner").
```

```js
// Optional helper for check 4: logs the focus order so you can read it instead of counting Tabs.
// Paste into the console, Tab through the page, then read the list.
const seen = [];
document.addEventListener('focusin', ({ target }) => {
  seen.push(`${target.tagName.toLowerCase()}${target.id ? '#' + target.id : ''} "${(target.textContent || target.getAttribute('aria-label') || '').trim().slice(0, 30)}"`);
  console.table(seen.slice(-1));
});
```

Then write the fix list, ordered by how many checks each item failed:

```markdown
### Fix, in order
1. Hero headline "Supercharge your workflow" fails 2, 3 and 7: rewrite around closing the month.
2. Replace gradient hero background with the invoices table mock (fails 3, 6).
3. Card grid in "Features" has no focus ring on links (fails 4).
4. Screenshot overflows at 375px: `max-w-full h-auto` (fails 5).
5. Delete the stats row and the logo wall (fails 6).
6. Squint: two h2s at `text-4xl`; drop section headings to `text-h2` (fails 1).
```

## Variations

- **Dashboard or app screen.** Replace the swap test with the "empty test": load it with zero rows, one row, and 400 rows. Replace the side-by-side with Linear or Vercel's settings pages rather than a marketing home.
- **Ten-minute version.** Checks 1, 2, 4 and 5 only; the others need the fuller pass but these four catch most of what a visitor notices in the first five seconds.
- **Someone else's page.** Same sequence, but write each FAIL as an observation ("At 375px the headline wraps to 8 lines") rather than an instruction; the ordered fix list at the end is the deliverable.
- **Re-review after fixes.** Only re-run the checks that failed, then one final squint. Reviewing everything again invites new changes, and the page never ships.

## Pitfalls

- Reviewing in the editor instead of the browser: half the checks (squint, keyboard, 375px) cannot be done on source code, and the other half are easier with the page in front of you.
- Treating the admired site as a template. The point of check 7 is to notice restraint and hierarchy, not to adopt Linear's dark palette or Stripe's gradient; see `web-craft-anti-generic-design`.
- Letting "fail" become "add": a weak hierarchy is fixed by removing competitors for attention, not by making the headline bigger and adding a badge. Check 6 exists to counter this reflex.
- Skipping the read-aloud because the copy was "already edited": the test catches marketing cadence that reads fine silently and sounds absurd spoken.
- Doing the keyboard walk with the mouse nearby. Unplug it, or you will click past the broken spot without noticing.
- Reviewing before the content is real: lorem ipsum and placeholder screenshots pass the squint test and fail in production. Run `web-craft-real-content` first.

## Related skills

- `web-craft-real-content`
- `web-craft-copy-that-sounds-human`
- `web-craft-consistency-audit`
- `web-craft-layout-with-intention`
- `web-design-ui-polish-checklist`
- `web-a11y-keyboard-and-focus`
- `web-ship-launch-checklist`
