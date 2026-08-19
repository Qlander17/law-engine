# Law Engine — Product Overview

## Problem

Commercial law (the UCC, and the broader web of law surrounding ordinary transactions) is real,
consequential, and largely invisible to the people it governs until something goes wrong. Existing
legal-education tools tend toward one of two failure modes: bar-exam-style doctrinal drilling
(optimizes for passing a test, not for functioning competently in a real transaction), or generic
AI chat answering legal questions with no real, checkable source behind the answer.

## User

Initially: the founder himself, learning and demonstrating commercial-law competence as part of a
real career transition. The design is built for a broader "person who needs to function
competently in a real commercial situation" — a small-business owner, an operations/procurement
professional, a new hire handling contracts they were never formally trained on — not a law student.

## Product vision

A learner becomes increasingly capable of functioning competently in real commercial situations by
*doing* — acting on realistic scenarios, seeing real consequences, and only then receiving the
terminology and authority needed to understand what happened — rather than by memorizing doctrine
in the abstract.

## Current MVP

- A real, provenance-tracked statutory corpus (UCC Articles 1, 2, 3, and 9, Virginia enactment) —
  every citation traces to an official government source with a recorded SHA-256 hash, never
  invented.
- A statute browser/search surface, an orientation page covering all 11 UCC Articles conceptually
  (even the 7 not yet ingested — clearly labeled as such), and a deterministic (non-ML)
  structural-analysis tool for statutory sentences.
- A real Legal Proof Graph engine implementing a definition → authority → verified-fact →
  conclusion reasoning chain — now extended with a real, honestly-labeled experimental case-law
  layer (exactly two judicial opinions, explicitly marked `RETRIEVED` not `SOURCE_VERIFIED` pending
  a real primary-source-verification pass — see the main README's own "Experimental, bounded"
  section; not presented as citable legal authority yet).
- A Task Ladder and four real multi-step commercial-law simulations (a consumer-to-operator Article 2
  ladder, a real-world restaurant-purchase simulation, a secured-financing simulation, and a
  negotiable-instrument/promissory-note simulation): the learner acts on a real situation, sees a
  real consequence, and only then receives the relevant terminology and authority — the flagship
  expression of the product's real pedagogical bet.
- Public, open-source, Apache-2.0 licensed: github.com/Qlander17/law-engine (pending a real,
  currently-prepared sync to bring the public copy current with this local state — see the
  Chairman's own escalation queue for the exact, ready diff).

## Key design principles

1. **Never assert legal authority that isn't real and currently ingested.** Every citing structure
   in the codebase — Tasks, MCQs, the Proof Graph — fails to build rather than allow a fabricated
   or not-yet-ingested citation.
2. **Do before explain.** The default task opens with a real decision to make, not a doctrinal
   question to answer; terminology and authority are introduced because the learner needs them to
   understand what just happened.
3. **A metaphor is never load-bearing.** Simplified illustrations are structurally, type-level
   separated from governing text (`PedagogicalMetaphor` always self-labels as non-authoritative) —
   they can never silently substitute for the real rule.
4. **Repetition means practicing a competency across changing facts, not repeating a question.**
   The same underlying professional skill is exercised across different roles, industries, and
   stakes — never a relabeled repeat of the same fact pattern.
5. **Binary is sometimes correct — the point is not to force everything into four options, or into
   an action, when the real professional decision genuinely is a yes/no call.**

## Decisions made

- UCC-first, not "all of law." A real, bounded, citable corpus was prioritized over broad but thin
  coverage.
- A single jurisdiction (Virginia) initially, to keep every citation genuinely verifiable against
  one real, checkable government source rather than thinly covering fifty states.
- Deterministic, rule-based reasoning (the syntax-analysis engine, the Proof Graph) over a
  generic LLM-answers-legal-questions architecture — slower to build breadth, but every output
  traces to a real, checkable source.
- Apache-2.0, not MIT, for the code license — the added patent grant was judged worth the (minimal)
  extra complexity given real monetization intent for the broader Ghostlines venture.

## What was deliberately not built

- **Personalized legal advice.** Nothing in Law Engine is positioned as, or should be read as,
  advice for a real reader's real legal situation — it is an educational and technical
  demonstration. This boundary was treated as a hard constraint on the simulation content itself,
  not an afterthought disclaimer.
- **A large Mastery Engine**, before there is real usage data to track. A competency-state model
  (`UNSEEN` → `MASTERED`) is fully designed but deliberately not implemented — building tracking
  infrastructure for data that doesn't exist yet was judged lower-value than shipping the thing
  that generates the data.
- **Breadth over depth.** Seven of eleven UCC Articles remain orientation-only (conceptually
  explained, not ingested as citable statutory text) — a real, disclosed scope boundary, not a
  hidden gap.
- **A live, publicly deployed product.** The public artifact today is the source code and a local
  demo; standing up real hosting infrastructure is a separate, larger, deliberately deferred
  decision from making the code itself public and inspectable.

## Roadmap (next, not yet built)

1. **Done since this document was first written**: the Task/simulation corpus was extended into
   Article 9 (secured transactions) and Article 3 (negotiable instruments), both using the same
   situation-first, multi-step model.
2. Independently verify the two case-law sources underlying the new, experimental Precedent Conflict
   Mapper against their official court sources (currently `RETRIEVED`, not `SOURCE_VERIFIED`) — a
   real, bounded, near-term next step, not a general case-law buildout.
3. Wire the Legal Proof Graph's UCC-statute reasoning path further into the learner-facing UI —
   the case-law/precedent extension is built and tested on the backend, but has no dedicated learner
   UI surface yet.
4. Implement the designed competency-state tracking once real task-attempt data exists to track.
5. A first bounded decision-support wizard (e.g., "is this a true lease or a disguised security
   interest?") reusing already-written orientation content.

## Risks

- **Single-maintainer risk.** All current evidence is self-directed, solo work — no external
  contributors or reviewers yet.
- **Jurisdiction/scope narrowness.** Real, valuable competence today is bounded to Virginia UCC
  Articles 1/2/3/9 — a reviewer expecting broader coverage will find a real, disclosed gap, not a
  hidden one.
- **No real usage data yet** to validate that the situation-first redesign actually improves
  outcomes versus the prior question-first version — the product decision in this cycle is
  reasoned, not yet empirically confirmed.

## Success metrics (once users exist)

Task/simulation completion rate; time-to-first-correct-action on a genuinely novel fact pattern for
an already-practiced competency (a real proxy for transfer, not just recall); ratio of
`INDEPENDENT`/`TRANSFERRED`-level performances to `ASSISTED` ones per competency over time. No
metrics are claimed as already measured — the product has no real users yet.
