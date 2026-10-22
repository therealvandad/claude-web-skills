---
name: web-interactive-quiz
description: Build a quiz or survey engine driven by JSON, with one question per screen, radio options, progress bar, scoring, per-question feedback, a results screen and copyable share text, no library. Use whenever a user asks for a "quiz", "trivia", "personality test", "survey one question at a time", "scored questionnaire" or "multi-step questions".
---

# Quiz engine from JSON

A quiz is data plus a tiny state machine: `{ index, answers[] }`. Keep questions in JSON so editors never touch code, render one question at a time from a `<template>`, and compute the score from `answers` at the end, never from the DOM. Native radio inputs inside a `<fieldset>` give you arrow-key navigation, grouping and screen reader labels for free, so the script only handles stepping, scoring and announcing.

## Pattern

```html
<section data-widget="quiz" class="mx-auto max-w-xl p-4" aria-labelledby="quiz-title">
  <h1 id="quiz-title" class="text-2xl font-semibold">How well do you know the web platform?</h1>
  <p data-js="status" aria-live="polite" class="sr-only"></p>
  <div data-js="progress" role="progressbar" aria-label="Quiz progress" aria-valuemin="0" aria-valuemax="4" aria-valuenow="0" class="mt-4 h-2 rounded-full bg-gray-200 dark:bg-gray-800">
    <div data-js="bar" class="h-full w-0 rounded-full bg-indigo-600 motion-safe:transition-[width]"></div>
  </div>
  <form data-js="question" class="mt-6" hidden>
    <fieldset class="space-y-2">
      <legend data-js="prompt" tabindex="-1" class="text-lg font-medium focus:outline-none"></legend>
      <div data-js="options" class="mt-3 space-y-2"></div>
    </fieldset>
    <p data-js="feedback" class="mt-3 min-h-6 text-sm"></p>
    <button data-js="next" type="submit" class="mt-4 rounded-lg bg-indigo-600 px-4 py-2 font-medium text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Check answer</button>
  </form>
  <div data-js="result" hidden class="mt-6 rounded-xl border border-gray-200 p-5 dark:border-gray-800">
    <h2 data-js="score" tabindex="-1" class="text-xl font-semibold focus:outline-none"></h2>
    <p data-js="verdict" class="mt-1 text-gray-600 dark:text-gray-400"></p>
    <textarea data-js="share" readonly rows="3" aria-label="Share text" class="mt-3 w-full rounded-lg border border-gray-300 p-2 text-sm dark:border-gray-700 dark:bg-gray-900"></textarea>
    <div class="mt-3 flex gap-2">
      <button data-js="copy" type="button" class="rounded-lg border border-gray-300 px-3 py-1.5 text-sm dark:border-gray-700">Copy result</button>
      <button data-js="restart" type="button" class="rounded-lg px-3 py-1.5 text-sm underline">Try again</button>
    </div>
  </div>
  <script type="application/json" data-js="data">
  { "questions": [
    { "q": "Which element should a clickable action use?", "options": ["div with onclick", "button", "span with role=link", "a without href"], "answer": 1, "why": "A button gives you focus, Enter and Space for free." },
    { "q": "What does the defer attribute do on a script tag?", "options": ["Loads it after the page is idle", "Runs it before parsing", "Downloads in parallel, runs after parsing", "Blocks rendering"], "answer": 2, "why": "Deferred scripts run in order once the HTML is parsed." },
    { "q": "Which unit is relative to the root font size?", "options": ["em", "rem", "ch", "vh"], "answer": 1, "why": "rem always reads html font-size, so it ignores nesting." },
    { "q": "Which value of loading delays offscreen images?", "options": ["lazy", "defer", "async", "idle"], "answer": 0, "why": "loading=\"lazy\" is built into img and iframe." }
  ], "verdicts": [[0, "Worth a weekend with MDN."], [2, "Solid fundamentals."], [4, "Spec-reader territory."]] }
  </script>
</section>
```

```js
// /js/quiz.js
export function initQuiz(root) {
  const $ = (n) => root.querySelector(`[data-js="${n}"]`);
  const { questions, verdicts } = JSON.parse($('data').textContent);
  const form = $('question'), options = $('options'), next = $('next'), feedback = $('feedback');
  let index = 0, answers = [], checked = false;

  const announce = (msg) => { $('status').textContent = msg; };
  function show(moveFocus = true) {
    const q = questions[index];
    checked = false;
    $('prompt').textContent = `${index + 1} of ${questions.length}. ${q.q}`;
    options.replaceChildren(...q.options.map((text, i) => {
      const label = document.createElement('label');
      label.className = 'flex cursor-pointer items-center gap-3 rounded-lg border border-gray-300 p-3 has-[:checked]:border-indigo-600 has-[:checked]:bg-indigo-50 has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-indigo-600 dark:border-gray-700 dark:has-[:checked]:bg-indigo-950';
      label.innerHTML = '<input type="radio" name="choice" required class="size-4 accent-indigo-600"><span></span>';
      label.firstElementChild.value = i; label.lastElementChild.textContent = text;
      return label;
    }));
    feedback.textContent = ''; next.textContent = 'Check answer';
    $('bar').style.width = `${(index / questions.length) * 100}%`;
    $('progress').setAttribute('aria-valuenow', index);
    if (moveFocus) $('prompt').focus();
  }
  function onSubmit(e) {
    e.preventDefault();
    const q = questions[index];
    if (!checked) {                                  // step 1: grade and explain
      const pick = Number(new FormData(form).get('choice'));
      answers[index] = pick; checked = true;
      const ok = pick === q.answer;
      feedback.textContent = `${ok ? 'Correct.' : `Not quite, the answer is “${q.options[q.answer]}”.`} ${q.why}`;
      feedback.className = `mt-3 min-h-6 text-sm ${ok ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'}`;
      options.querySelectorAll('input').forEach((i) => { i.disabled = true; });
      announce(feedback.textContent);
      next.textContent = index === questions.length - 1 ? 'See results' : 'Next question';
    } else if (++index < questions.length) show();   // step 2: advance
    else finish();
  }
  function finish() {
    const score = answers.filter((a, i) => a === questions[i].answer).length;
    const verdict = [...verdicts].reverse().find(([min]) => score >= min)[1];
    form.hidden = true; $('result').hidden = false;
    $('bar').style.width = '100%'; $('progress').setAttribute('aria-valuenow', questions.length);
    $('score').textContent = `You scored ${score} out of ${questions.length}`;
    $('verdict').textContent = verdict;
    $('share').value = `I got ${score}/${questions.length} on the web platform quiz. ${location.href}`;
    $('score').focus(); announce($('score').textContent);
  }
  const copy = async () => { await navigator.clipboard.writeText($('share').value); announce('Result copied.'); };
  const restart = () => { index = 0; answers = []; $('result').hidden = true; form.hidden = false; show(); };

  form.addEventListener('submit', onSubmit);
  $('copy').addEventListener('click', copy);
  $('restart').addEventListener('click', restart);
  form.hidden = false; show(false);
  return () => { form.removeEventListener('submit', onSubmit); $('copy').removeEventListener('click', copy); $('restart').removeEventListener('click', restart); };
}

document.querySelectorAll('[data-widget="quiz"]').forEach(initQuiz);
```

## Variations

- **Survey, no right answers**: drop `answer` and `why`, skip the "check" step (submit advances directly), and store `answers` for a summary or `fetch` POST; see `web-form-submit-with-fetch`.
- **Personality result**: give each option `{ text, tags: ["planner"] }`, tally tags, and show the highest. Break ties by first question answered.
- **Resume later**: write `{ index, answers }` to `localStorage` after each step (key `quiz:v1`); see `web-js-storage`.
- **Multiple answers**: swap `type="radio"` for `checkbox`, make `answer` an array and compare sorted values.
- **Native share**: if `navigator.share` exists, call it instead of copying, and fall back to the clipboard.

## Pitfalls

- Moving focus to the new question's `legend` (with `tabindex="-1"`) is what tells keyboard and screen reader users the screen changed. Without it focus stays on a button that has just vanished.
- Never put the correct answer in the DOM before grading (no `data-correct` attributes); it is visible in devtools and tells nothing the JSON does not. Real exams must grade server side.
- `navigator.clipboard` needs HTTPS or localhost; wrap in `try/catch` and select the textarea as the fallback.
- Shuffle with Fisher-Yates on a copy and keep each option's original index, or `answer` points at the wrong choice. `sort(() => Math.random() - 0.5)` is biased.
- Inline JSON must not contain `</script>`; escape `<` as `\u003c` when generating it from user content.
- Keep the progress bar's `aria-valuenow` in sync, but announce through the polite live region, not the bar.

## Related skills

- `web-form-choices`
- `web-form-multi-step`
- `web-js-state-and-render`
- `web-js-storage`
- `web-a11y-keyboard-and-focus`
- `web-motion-loading-and-progress`
