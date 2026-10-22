---
name: web-craft-copy-that-sounds-human
description: 'Rewrite copy so it sounds like a person who knows the product: banned words (seamless, unlock, elevate, empower, effortless, supercharge), headline formulas with real nouns and numbers, button labels that say what happens, no John Doe or Acme. Use whenever a user says "copy sounds fake", "sounds like AI", "sounds like marketing", or wants better headlines, taglines or button text.'
---

# Copy that sounds human

Generated copy is recognisable in one line because it is built from words that apply to every product and therefore describe none: "Seamlessly unlock effortless productivity." Each word is a placeholder for a fact the writer did not have. Human copy is specific: it names what the thing does, for whom, with a number where one exists, and it tells the reader what happens when they click. The rewrite method is mechanical: delete the abstract word, ask "what concretely is true here?", and write that.

## Pattern

```html
<!-- BEFORE -->
<section class="mx-auto max-w-7xl px-6 py-24 text-center">
  <p class="text-sm font-semibold uppercase text-indigo-600">Introducing Acme</p>
  <h1 class="mt-4 text-5xl font-bold">Transform the way you work 🚀</h1>
  <p class="mt-6 text-lg text-gray-600">Seamlessly unlock effortless collaboration. Built for the modern team.</p>
  <button class="mt-8 rounded-lg bg-indigo-600 px-6 py-3 text-white">Get Started</button>
  <button class="mt-8 ml-3 px-6 py-3">Learn More</button>
  <blockquote class="mt-20 text-gray-600">"Acme is a game changer!" — John Doe, CEO, Acme Inc</blockquote>
</section>
```

```html
<!-- AFTER: same section, every abstraction replaced by a fact -->
<section class="mx-auto max-w-6xl px-6 py-24">
  <p class="font-mono text-xs uppercase tracking-widest text-stone-500">Shared inbox for support teams of 2 to 20</p>
  <h1 class="mt-4 max-w-[20ch] text-5xl font-medium leading-tight text-balance">
    Answer every support email once, from one inbox, with the order next to it.
  </h1>
  <p class="mt-6 max-w-[60ch] text-lg leading-relaxed text-stone-600">
    Lantern pulls support@ into one queue, shows the customer's last three orders beside the thread,
    and lets two people reply without replying twice.
  </p>
  <div class="mt-8 flex flex-wrap items-center gap-4">
    <a href="/signup" class="rounded-md bg-stone-900 px-5 py-3 text-sm font-medium text-white">Connect your support inbox</a>
    <a href="/tour" class="text-sm font-medium underline underline-offset-4">Watch the 3-minute tour</a>
  </div>
  <p class="mt-3 text-sm text-stone-500">Works with Gmail and Outlook. Free for the first 200 conversations a month.</p>

  <figure class="mt-20 max-w-xl border-l-2 border-stone-300 pl-6">
    <blockquote class="text-lg leading-relaxed">
      "We went from three people checking the same inbox to one queue. Nobody has answered a ticket twice since March."
    </blockquote>
    <figcaption class="mt-3 text-sm text-stone-500">Priya Raman, support lead at Kettle &amp; Co, a 14-person kitchenware shop in Leeds</figcaption>
  </figure>
</section>
```

Banned words and what to write instead (each one means "I did not have the fact"):

- **Seamless, effortless, frictionless** → say what step is gone: "No CSV export. Orders appear in the thread."
- **Unlock, elevate, empower, supercharge, transform, revolutionise** → the plain verb: send, sort, reply, print, save.
- **Built for the modern team / modern businesses** → who, with a number: "for support teams of 2 to 20".
- **Take your X to the next level, game changer, cutting edge, best-in-class** → delete; nothing is lost.
- **Lightning fast, blazing** (with ⚡) → the measurement: "Search returns in under 200 ms on 1M rows."
- **Powerful, robust, intuitive, beautiful** → adjectives are claims; replace with the feature that proves it.
- **Lorem ipsum, John Doe, Jane Smith, Acme Inc** → real-looking content from the start; see below.

Headline formulas that produce specific lines (fill in with real nouns):

- **Outcome + condition**: "Send the invoice before you close the laptop."
- **What it is, for whom**: "Shared inbox for support teams of 2 to 20."
- **Number, not adjective**: "Paid in 9 days instead of 34."
- **The thing you stop doing**: "Stop retyping your timesheet into Word."
- **A sentence a customer actually said**: the testimonial as the headline, in quotes, with their name under it.

Buttons: verb + object, and a line under the button saying what happens next.

- "Get Started" → "Start a free account" / "Connect your support inbox" / "Create your first invoice"
- "Learn More" → "Watch the 3-minute tour" / "Read how billing works" / "See the sample report (PDF)"
- "Submit" → "Send message" / "Save changes" / "Place order, 42.00 €"
- "Contact us" → "Book a 20-minute call" / "Email the founders"

Names and numbers: use names from more than one culture (Priya Raman, Tomasz Wiśniewski, Amara Okafor, Luis Herrera), companies with a trade and a place ("Kettle & Co, kitchenware, Leeds"), and numbers that are not round (14 people, 9 days, 1,240 words). Round numbers and English-only names read as placeholders.

## Variations

- **Section headings**: a label is a template ("Features", "Testimonials", "Why us"); a sentence is content ("What happens after you log an hour", "Three shops that switched last quarter"). Keep the eyebrow label only when it adds a fact.
- **Enterprise/B2B**: the rules hold; "enterprise-grade security" becomes "SOC 2 Type II, SSO via SAML, data stored in Frankfurt".
- **Errors and empty states**: say what happened and what to do: "Couldn't save. Your connection dropped; your edits are still here. Try again." not "Oops! Something went wrong."
- **Dev-time lint**: drop this in a `<script>` during development and the console flags every banned word on the page.

```js
const banned = /\b(seamless(ly)?|unlock|elevate|empower|effortless(ly)?|supercharge|game.?chang\w+|next level|revolutioni[sz]\w*|cutting.?edge|lorem ipsum|john doe|acme)\b/i;
for (const el of document.querySelectorAll("h1, h2, h3, p, a, button, li, figcaption")) {
  const hit = el.textContent.match(banned);
  if (hit) console.warn(`Generic copy: "${hit[0]}"`, el);
}
```

## Pitfalls

- Invented statistics are worse than adjectives. If there is no real number, write the mechanism instead ("a pay button in the email") and get the number later.
- Specific does not mean long. A headline over 12 words wraps into three lines on a laptop; cut the clause, not the noun.
- Over-correcting into cleverness ("Inboxes, but make them calm") is the same emptiness with a wink. Plain sentences win.
- Exclamation marks and emoji in UI text read as unsure. One exclamation mark per site, in a success message, at most.
- Mixing "we" and "you" mid-page is a tell of assembled copy. Pick one: the product speaks to "you", testimonials speak as "we".
- Keep the product's own nouns consistent (thread vs conversation vs ticket). Write a five-line glossary before writing the page.

## Related skills

- `web-craft-anti-generic-design`
- `web-craft-real-content`
- `web-craft-self-review`
- `web-layout-hero`
- `web-layout-testimonials`
- `web-design-empty-and-error-states`
- `web-ui-buttons`
