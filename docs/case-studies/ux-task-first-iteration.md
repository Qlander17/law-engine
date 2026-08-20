# Why Renaming a Quiz a “Task” Did Not Make It Task-First

The first Task Ladder shipped. The interface said “task.” The content still asked which rule applied.

That is the product failure this case study is about. Changing the container did not change the cognition. The durable intervention was not a new component name. It was a written amendment to the pedagogical spec, plus one contrasting artifact that actually opens on a situation.

The falsified assumption: **a task-shaped interface is task-first cognition.**

This is a founder-only iteration, not UX research. The only user so far is the founder, using the product in his own environment (dark-mode Ubuntu, Firefox). Both observations below are his. A later self-review of the new Task Ladder is also his. None of that is independent validation.

---

## Two defects, two evidence standards

The same cycle produced two problems that are easy to conflate and should not be:

| Track | What was wrong | Evidence | What a fix has to show |
|---|---|---|---|
| **Accessibility defect** | Answer text was unreadable until a button was selected | Direct CSS inspection; reproduces from missing `color` on a hardcoded light `background` | The buttons always carry an explicit text color; contrast numbers; the built CSS contains those values |
| **Learning-model defect** | The product worked as built, but the built thing was a doctrinal quiz wearing a task label | Founder observation, then an audit of shipped stages, then a second self-review after the first redesign | A before/after interaction in which the opening move is an operational action, not “which rule applies” — still unvalidated against other learners |

The accessibility bug made the implementation unusable in one environment. The learning-model bug showed that the implementation faithfully instantiated the wrong model. Fixing contrast does not teach judgment. Shipping a Task schema does not either, if the prompts still cue recall.

---

## Track 1 — Accessibility

Observation, from the founder in dark-mode Firefox:

> “Two answer/action buttons display text that is effectively invisible… the text only becomes readable after selecting the button.”

Mechanism, from `apps/web/src/app/learn/AnswerButton.module.css` (comment records the same diagnosis): every answer button set an explicit light `background` and no explicit `color`. On a dark-mode browser, form-control text color follows the OS/browser scheme — light text on a light background. Selection disables the button; disabled buttons happen to pick a different default, so the text appeared after click.

The fix was not “make all text white.” White on these light backgrounds would still fail. The buttons’ backgrounds are intentionally fixed, not theme-aware. The missing half of that design was an explicit text color per state:

| State | Background | Text |
|---|---|---|
| default | `#fff` | `#1a1a1a` |
| selected correct | `#e6f4ea` | `#14532d` |
| selected incorrect | `#fdecea` | `#7f1d1d` |

Those pairs were checked against WCAG 2.1 relative luminance; they sit above the 4.5:1 AA threshold for normal text (green-on-green computes to roughly 7.9:1). `:focus-visible` is explicit (`2px solid #2563eb`). The previous version relied on the browser default outline.

The same module is applied via `className` on every interactive surface that uses answer buttons (`LifecycleRunner`, `PracticeRunner`, `TaskRunner`) — one rule, not three patches.

**What was verified.** Component tests assert every answer button carries the explicit-color class before and after selection (`LifecycleRunner.test.tsx`, new coverage on `PracticeRunner.tsx`). A production build was run. The served CSS was fetched and checked for the new color values.

**What was not verified.** There is no Playwright/Cypress visual suite, no automated Firefox dark-mode run, and no external accessibility review. Contrast is one dimension of accessibility. The document does not establish cross-browser visual behavior.

---

## Track 2 — Learning model

Second observation, same founder, same environment:

> “The first several interactions appear predominantly binary YES/NO. This does not match the intended learning model.”

An audit of the shipped transaction-lifecycle stages found that every stage was a two-option, Yes/No-framed decision. Some of those decisions are binary in the underlying law. Several were forced into that shape.

The first product response was a Task Ladder plus a four-option format for knowledge checks. Four options is a **format rule**: when more than two plausible actions exist, do not squash them into Yes/No; do not pad to four for its own sake. It is not the pedagogical breakthrough. Cardinality of answers and authenticity of the task are different variables.

Then the cycle repeated. After the first Task Ladder shipped, a self-directed review found the new content had drifted back to “which rule applies” as the opening move — the failure the second observation had already named. The interface had changed. The content-production habit had not.

The durable correction is `docs/task-first-pedagogy-and-task-ladder-architecture.md` (Live Run 1.49 amendment), not a silent rewrite of the first ladder. The contrasting artifact is the Riverside Bistro simulation: three chained decisions in which facts accumulate and a later step depends on an earlier one.

### Target competence, as the current design actually supports it

The Task schema can carry situation, options, consequence, authority, and a next-step pointer. What the current corpus actually exercises:

| Competence | Support in current design |
|---|---|
| Issue spotting | Partial. Riverside opens on damaged/wrong-model ovens already in view; the learner is not required to notice an unannounced defect in a document. |
| Information gathering | Weak. `facts_provided` are given up front. `discoverable_actions` is empty on the shipped simulation steps. |
| Sequencing | Present. Three steps; later rights depend on earlier acceptance/rejection and on the invoice-term analysis. |
| Risk recognition | Present as authored keyed options. Silent use is keyed as a path that does not exercise the § 8.2-601 rejection/acceptance menu; a total warranty disclaimer is treated as a material alteration, not an automatic term. Those are task-authored readings, not independently verified holdings. |
| Operational action selection | Present, in the simulation. Options are actions (accept/reject/split/stay silent), not doctrinal labels. |
| Authority explanation | Present, *after* the choice. `governing_citations`, `reasoning_chain`, and `professional_terminology` are revealed in feedback, not as the opening prompt. |

A Task citing a section that is not currently ingested fails to build (`Task.validate()` → `get_section`). That check proves only that the task cannot cite a governing section absent from the ingested corpus. It does not, by itself, establish correct interpretation of the cited section, applicability to the authored facts, currentness, or that an authored proposition in the task is true. A well-cited quiz still builds.

Binary items were kept where the professional decision is in fact binary. Treating “binary” as inherently wrong would have been an overcorrection.

---

## One exact before / after

### Before — Task Ladder, still a quiz

From `library/normalized/tasks/article-2-consumer-to-operator-ladder.json`, task `a2-t1-buy-a-laptop`.

**Old prompt.** “You walk into an electronics store and buy a laptop for personal use, paying cash and taking it home the same day.” Objective: “Identify whether UCC Article 2 applies to this purchase, and why.”

**What it tested.** Recall of scope: is a laptop “goods,” and does Article 2 therefore apply. The correct option is “Yes — Article 2 applies because a laptop is ‘goods.’” The other options are doctrinal mistakes (store purchase is a service; electronics are excluded). Consequence text is feedback about being right or wrong about a statute, not a change in the learner’s position in a transaction.

That is a knowledge check with a scenario skin. The learner is cued to name the rule.

### After — situation, action, consequence, authority last

From `library/normalized/tasks/riverside-bistro-simulation.json`, step `sim-bistro-1-delivery`.

**New situation.** “You own Riverside Bistro, opening in four days. You emailed an order for six commercial ovens… The ovens just arrived: two are visibly dented, one is the wrong model entirely, and three are exactly what you ordered. You’re standing in your kitchen looking at the shipment right now.”

**Information available.** Six ordered; two dented, one wrong model, three correct. Opening night in four days. No combined signed contract — only the order email and the invoice. Both parties are in the restaurant-equipment business (used in step 2).

**Choices / action (step 1).**

1. Accept all six as-is, to protect the supplier relationship.  
2. Accept the three correct ovens; reject the two dented and the wrong-model one. *(keyed correct)*  
3. Reject the entire shipment, including the three correct ovens.  
4. Say nothing and start using whichever ovens work.

**Consequence of the correct action.** The learner keeps the three usable ovens for opening day and formally rejects the nonconforming units. Accepting all six would accept those nonconforming units along with the conforming ones. Rejecting the entire shipment would also reject the ovens the restaurant needs on Friday. Both of those paths sit on the menu in Va. Code Ann. § 8.2-601: reject the whole, accept the whole, or accept any commercial unit(s) and reject the rest. The fourth authored option — remaining silent and using whatever works — is keyed as a path that does not exercise that rejection/acceptance menu. The governing citation on this step is § 8.2-601 only. That section states the menu; it does not itself define when silence or use constitutes acceptance.

**Authority / explanation, afterward.** Va. Code Ann. § 8.2-601: if goods fail to conform, the buyer may reject the whole, accept the whole, or accept any commercial unit(s) and reject the rest. Terminology (`reject`, `commercial unit`) is introduced because the learner just had to act, not as a gate before the decision.

Step 2 then puts a “no warranty, all sales final” line on the invoice that was never in the order. Step 3, one week after opening, has an accepted oven fail; the supplier points at that same invoice language. The learner who treated step 1 and step 2 as independent quizzes cannot use what they just decided. The learner who treated them as one transaction can.

Four options appear here because four operational paths exist, not because four is a pedagogy.

---

## Counter-hypotheses

Situation-first, multi-step tasks may also impose greater extraneous cognitive load on novices: more facts to hold, a time-pressure frame, and no cue about which doctrine is being tested. A learner who would have answered “does Article 2 apply?” correctly might stall when asked to split a shipment. The current design bets that this load is the competence. That bet has not been measured. There are no users other than the founder, so there is no completion-rate, time-to-first-correct-action, or A/B of situation-first vs. question-first on the same competency.

A second, independent limit: choosing the keyed action among authored options demonstrates recognition among presented choices. It does not establish that the learner could independently generate the correct action without options.

The shipped Task schema requires a finite `options` list and exactly one `is_correct` flag (`Task.validate()`). Riverside step 1 therefore cannot, as currently built, test whether a learner would produce “accept the conforming commercial units and reject the rest” if those buttons were not there. Recognition and independent action generation are different competences. Treating a correct click as operational mastery would collapse them.

Future learning evaluation, once users other than the founder exist, should keep those measurements separate:

| What is scored | What it can support | What it cannot support |
|---|---|---|
| Selection among authored options | Recognition of a keyed action in a presented set | That the learner would have generated that action unprompted |
| Free production of an action (not currently implemented) | Independent action generation, if scored against a rubric that does not leak the option list | That the generated action is the unique legally correct move in a live dispute |

No such evaluation has been run. This document does not invent user evidence for either column.

Until those measurements exist, the claim is narrower: the first redesign reproduced the quiz; the second artifact does not, on its face, open with “which rule applies.”

---

## Reconstructable chain

- **Definition.** A “task” is the schema (`situation`, `options`, `consequence`, `authority`). Task-first cognition is an opening move that is an operational action, not “which rule applies.”
- **Premise.** The only user so far is the founder. These observations are not UX research. Accessibility (contrast, explicit color) and pedagogy (what the prompt asks the learner to do) are different defects with different evidence standards. Four options are a format rule, not the pedagogical intervention.
- **Observed fact.** The first Task Ladder opened on scope-recall (`a2-t1-buy-a-laptop`). Riverside step 1 opens on a mixed shipment. Contrast pairs were checked against WCAG relative luminance and the served CSS; dark-mode Firefox visual behavior was not automated.
- **Proposition.** A task-shaped interface is not, by itself, task-first cognition.
- **Inference.** The durable correction is the written pedagogy amendment plus a contrasting artifact whose first prompt is an action.
- **Counterexample / contradiction.** The first shipped ladder falsified the UI-rename assumption. Remaining counter-hypotheses: situation-first may raise extraneous cognitive load; a correct choice among authored options is recognition, not independent generation.
- **Conclusion.** Only as strong as those facts: the first redesign reproduced the quiz; the second artifact, on its face, does not open with “which rule applies.”
- **Residual uncertainty.** No other learners. No measurement of load, transfer, recognition versus generation, or unique legal correctness of the keyed option in a live dispute. Section-presence validation is not currentness, applicability, or interpretive truth.
