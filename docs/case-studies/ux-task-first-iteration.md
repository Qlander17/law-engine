# Law Engine: A Real Founder-Feedback-Driven Product Iteration

*A short case study of one real product cycle — user feedback, root-cause diagnosis, an
accessibility fix, and a product reframing that changed the core learning mechanic. Written up as
what it actually is: a solo founder acting on his own product's real user feedback, not a formal
multi-user UX research study.*

## User feedback

Two real, separate pieces of feedback from the product's actual (and so far only) user, in his own
real environment (dark-mode Ubuntu, Firefox):

> "Two answer/action buttons display text that is effectively invisible... the text only becomes
> readable after selecting the button."

> "The first several interactions appear predominantly binary YES/NO. This does not match the
> intended learning model."

## Problem definition

Two distinct problems, correctly kept separate rather than conflated into one fix: an
**accessibility defect** (the product was, for a real user, in a real environment, partially
unusable) and a **product-model mismatch** (the product worked as built, but what was built didn't
match the stated pedagogical intent).

## Root-cause analysis

The button-visibility bug was diagnosed by direct code inspection, not guessing. Every answer
button set an explicit, hardcoded **light** `background` — but no explicit text `color` at all. On
a dark-mode browser, the button's text color fell through to the browser's own default form-control
color, which follows the OS/browser color scheme — light text on a light background. The bug
surfaced only "after selecting" because selection also disables the button, and disabled buttons
happen to render with different default text coloring in the browsers involved — a real, findable
mechanism, not a mystery.

## Product decision

Rather than patch the immediate bug and stop, the second piece of feedback was treated as the more
consequential one: the underlying learning model itself needed correcting, not just a color value.
Two real audits were run against the actual shipped UI (not assumptions): every stage across both
real transaction lifecycles was found to be a 2-option, Yes/No-framed decision — some legitimately
binary, several artificially forced into that shape when the real underlying decision had more than
two real options. The product decision: build a genuine Task Ladder as the primary experience,
without deleting or apologizing for the legitimately-binary content that remained valid.

## UX decision

**The fix, deliberately not a redesign.** Explicit, fixed, high-contrast colors per interaction
state (default, hover, focus, selected-correct, selected-incorrect) — not "make all text white,"
which would have been visually simpler but wrong (white text against these buttons' light
backgrounds would still be invisible; the actual fix required understanding *why* the bug happened,
not just reversing its symptom). For the model mismatch: a four-option standard for genuine
knowledge checks (used only where the real facts support more than two real answers — not padded to
four for its own sake), and a shift to situation-first task framing (a real professional decision to
act on, not "which rule applies" as the opening move).

## Engineering implementation

- A new shared CSS Module (`AnswerButton.module.css`) applied via `className`, reused identically
  across every interactive surface in the product (transaction lifecycle, practice questions, and
  the new Task Ladder) — one fix, not three divergent patches.
- A real `Task`/`TaskOption` schema with a hard validation rule: a task citing legal authority that
  isn't a real, currently-ingested statute section fails to build at all. The fix for "quiz-like"
  content wasn't just new copy — it was a structural guarantee that new content can't drift into
  fabricated authority either.
- A first real, multi-step commercial-law simulation (Riverside Bistro: a restaurant owner facing a
  damaged/wrong-model delivery, then a disputed warranty disclaimer, then a real breach claim) —
  three chained decisions where facts accumulate and consequences carry forward, not three
  independent quiz questions with a shared theme.

## Accessibility

Contrast was checked, not assumed: the chosen colors (`#1a1a1a` on `#fff`, `#14532d` on `#e6f4ea`,
`#7f1d1d` on `#fdecea`) were computed against WCAG 2.1's relative-luminance formula and land well
above the 4.5:1 AA threshold for normal text (the green-on-green pairing computes to roughly 7.9:1).
An explicit `:focus-visible` outline was added — the previous version relied entirely on whatever
default the browser happened to provide.

## Testing

The fix was verified at three levels, not just "it compiles": unit/component tests (new coverage
for a component — `PracticeRunner.tsx` — that had zero tests before this cycle, plus regression
tests asserting every answer button always carries an explicit-color class); a real production
build; and a live check against the actual served page (fetching the real built CSS and confirming
the new color values are genuinely present in what a browser would receive) rather than trusting
the build succeeding as proof the fix shipped correctly.

## Iteration

The cycle repeated once more, immediately: after building the first real Task Ladder, a second
round of (self-directed) product review found that even the *new* content had quietly drifted back
toward "which rule applies" as its default opening move — the exact failure mode the second piece
of user feedback had already flagged. Rather than treat the Task Ladder as finished, the pedagogical
document itself was corrected (a durable, written amendment, not a silent rewrite) and a genuinely
different kind of task — the situation-first, multi-step simulation — was built as the concrete
proof the correction actually changed the output, not just the stated philosophy.

## Tradeoffs

- Chose a small, shared CSS Module over inline per-component styling, trading a little indirection
  for guaranteed consistency across every current and future interactive surface.
- Chose to keep existing, legitimately-binary quiz content rather than delete it wholesale — real
  professional decisions genuinely are binary sometimes, and treating "binary" as inherently wrong
  would have been an overcorrection.
- Chose one deep, three-step simulation over several more shallow tasks for this cycle, on the
  reasoning that proving the *mechanic* works end-to-end (accumulating facts, a real transfer point,
  real chained consequences) mattered more right now than raw content volume.

## Next metrics/experiments (once real users exist)

No user metrics are claimed here because none exist yet — this is a pre-launch, founder-only
iteration. Once the product has real learners, the natural next measurements are: completion rate
per task/simulation step (where do learners actually stop?), time-to-first-correct-action on a new
competency variant (a real proxy for whether "recognition without being told" is actually
happening), and a direct A/B of situation-first vs. question-first framing on the same underlying
competency, to test whether the product decision in this case study actually holds up against real
behavior and not just founder intuition.

---

*Prepared for public portfolio use — not yet published. This document itself is not part of the
Law Engine public repository; it is a standalone artifact for résumé/portfolio purposes.*
