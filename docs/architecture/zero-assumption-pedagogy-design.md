# Zero-Assumption Pedagogy — Design Note

Design/product-requirement note. **No code was written or changed for this
note; no ingestion, no new schema fields, no tests.** It records a
progressive-disclosure teaching model and a separate, optional learner
diagnostic for all future Law Engine learning-content work.

## The default assumption

**Law Engine assumes ZERO PRIOR LEGAL EDUCATION for every public-facing
learner by default.** No term, however basic-seeming to a lawyer ("party,"
"remedy," "breach," "statute"), is used unexplained on first appearance.

This is **not** a license to discard legal precision. It is a sequencing
requirement: complexity must be *revealed in order*, not *hidden*. A
learner who only ever reads Level 1 below should walk away with something
true, just partial — never something false-but-simple. A learner who reads
through Level 6 should end up exactly as precise as a lawyer reading the
statute directly. Nothing is dumbed down; everything is staged.

This extends, and does not replace, the existing four-layer discipline in
`docs/layman-first-pedagogy-principle.md` (legal term → plain-English
meaning → intuitive example → precise rule/authority), which itself extends
the structural fields already on `PedagogicalContract`
(`services/models.py`, `docs/pedagogical-contract-schema.md`). That
four-layer note is about **what** every unfamiliar term needs; this note is
about **how many stages** the full teaching arc for a concept has, in what
order, ending in genuine mastery rather than a definition. Where the two
overlap (four-layer Layers 1–4 map cleanly onto Levels 3–4 below), this note
treats the existing four-layer content as the authority for wording and
adds the levels around it.

---

## The six-level progressive-disclosure model

Every teachable Law Engine concept should support up to six levels. A
learner may stop at any level; nothing past Level 1 is required reading. A
learner may also jump straight to a later level (see the optional
diagnostic, below) — but Level 1 access is never removed for anyone.

The worked example below runs **one concept — Perfection** — through all
six levels, because progressive disclosure means *deepening* a single
concept, not switching examples partway through. Two prerequisite terms
(**collateral**, **security interest/attachment**) are introduced briefly
where Perfection depends on them, cross-referencing their own existing
four-layer treatment in `docs/layman-first-pedagogy-principle.md` rather
than re-deriving them.

### LEVEL 1 — SIMPLE EXPLANATION (no unexplained jargon)

> When you borrow money and offer something you own as backup — your car,
> your equipment, your business's inventory — the lender usually needs to
> take one more step, beyond just having your agreement, to protect their
> claim to that thing if other people also end up wanting a piece of it
> (another lender, a bankruptcy, a buyer). That extra step is what turns a
> *private* claim between you and the lender into one that holds up against
> the rest of the world. Lawyers call that step "perfection."

No statute, no citation, no undefined term. "Claim," "backup," and "step"
are all ordinary words. The one legal word used ("perfection") is
immediately named as the thing being defined, not assumed.

### LEVEL 2 — REAL-WORLD EXAMPLE

> A small landscaping business buys a $40,000 mower on credit from a
> dealership. The dealership agrees to let the business pay over three
> years, and in exchange the business signs an agreement giving the
> dealership a claim on the mower if payments stop. That claim exists
> between the business and the dealership the moment the agreement is
> signed and the mower is delivered. But the dealership doesn't stop there
> — it also files a public notice (a one-page form, at the state's UCC
> filing office) listing the business and the mower. That filing is what
> makes the dealership's claim count if the business later goes bankrupt,
> or tries to borrow against the same mower from a second lender, or sells
> the mower to someone who didn't know about the loan.

This is the same fact pattern already used in
`services/cross_article_lifecycle.py`'s
`build_equipment_purchase_on_credit_lifecycle()` — reused here rather than
invented, so the teaching example and the engine's own real transaction
model describe the same real scenario.

### LEVEL 3 — LEGAL VOCABULARY

The real professional terms for what Level 1–2 just described, without yet
citing the statute:

- **Collateral** — the mower (the property backing the loan).
- **Security interest** — the dealership's claim on the mower.
- **Attachment** — the moment that claim becomes enforceable between the
  business and the dealership (signing + delivery + value given).
- **Perfection** — the extra step (here, filing) that makes the claim
  effective against everyone else, not just the business.
- **Financing statement** — the public notice document that gets filed.

("Collateral" and "attachment" already have their own full four-layer
treatment as terms 1 and 4 in `docs/layman-first-pedagogy-principle.md`;
this level names them rather than re-explaining them.)

### LEVEL 4 — PRECISE RULE / AUTHORITY

Real, ingested statutory text (`services/retrieval.get_section()` returns
all four sections below — verified against
`library/normalized/ucc/article-9-sections.json`):

- **Va. Code Ann. § 8.9A-308(a):** *"[A] security interest is perfected if
  it has attached and all of the applicable requirements for perfection in
  §§ 8.9A-310 through 8.9A-316 have been satisfied. A security interest is
  perfected when it attaches if the applicable requirements are satisfied
  before the security interest attaches."*
- **Va. Code Ann. § 8.9A-310(a):** *"[A] financing statement must be filed
  to perfect all security interests and agricultural liens"* (except as
  otherwise provided in subsection (b) and § 8.9A-312(b) — narrow
  exceptions not detailed at this level).
- Supporting: **§ 8.9A-203(a)** (attachment, quoted in the existing
  `docs/layman-first-pedagogy-principle.md` term 1) and **§
  8.9A-102(12)** (collateral, term 4 in the same document).

### LEVEL 5 — EXCEPTIONS / EDGE CASES

Where "just file and you're perfected, done" stops being sufficient:

- **Unperfected security interests can still lose to someone who wasn't
  even part of the original deal.** Va. Code Ann. § 8.9A-317(a): an
  unperfected security interest is "subordinate to the rights of ...
  a person entitled to priority under § 8.9A-322 ... [and] a person that
  becomes a lien creditor before" perfection happens. Filing late, or not
  at all, doesn't just weaken the claim — it can let a *later* creditor
  jump ahead of it entirely.
- **Two perfected lenders on the same collateral don't tie — timing
  decides, and it isn't always "who signed first."** Va. Code Ann. §
  8.9A-322(a)(1): conflicting perfected interests "rank according to
  priority in time of filing or perfection," dated from "the earlier of
  the time a filing covering the collateral is first made or the security
  interest ... is first perfected" — a lender can file *before* the
  security interest even attaches, and that earlier filing date can still
  control.
- **A later-in-time lender can still leapfrog an earlier, broader one.**
  Va. Code Ann. § 8.9A-324(a) (purchase-money priority): a perfected
  purchase-money security interest in goods (other than inventory or
  livestock) "has priority over a conflicting security interest in the
  same goods ... if the purchase-money security interest is perfected
  when the debtor receives possession of the collateral or within twenty
  days thereafter" — the general first-to-file rule from § 8.9A-322 is
  itself subject to this exception.

The simple Level 1 story ("file, and you're protected") is true as far as
it goes, but by Level 5 it's clear "protected" is a *ranked*, *timed*
position relative to specific other claimants — not a flat yes/no.

### LEVEL 6 — ADVANCED APPLICATION

> On March 1, First Bank files a financing statement against "all present
> and after-acquired equipment" of the landscaping business, securing a
> general working-capital loan — but the business doesn't actually acquire
> the mower until later, so no security interest in the mower has attached
> yet as of March 1. On June 1, the business buys the mower on credit from
> the dealership, signing a security agreement giving the dealership a
> purchase-money security interest in the mower specifically. The
> dealership files its own financing statement against the mower on June
> 18. Who has priority in the mower — First Bank or the dealership, and
> under which section?

A learner working only from Level 4's plain filing rule would likely
(incorrectly) conclude First Bank wins, since its financing statement was
filed first (March 1, before June 18). The correct analysis requires Level
5's exception: the dealership's interest is a purchase-money security
interest in goods, perfected (filed June 18) within twenty days of the
business receiving possession (June 1) — so § 8.9A-324(a) gives the
dealership priority over First Bank's earlier-filed general interest,
despite § 8.9A-322(a)(1)'s normal first-to-file rule. This is a genuinely
novel fact pattern (not the Level 2 story restated), and solving it
requires combining §§ 8.9A-308, 8.9A-310, 8.9A-322, and 8.9A-324 — the
kind of multi-section synthesis Level 1–4 alone cannot produce.

---

## The SIMPLIFICATION INADEQUATE flag

**Rule:** before a Level 1 explanation is authored or shown for a concept,
the author (human or Law Engine content-generation logic) must check
whether a true, non-misleading Level 1 explanation is actually possible for
that concept *taken as a single unit*. If it is not — if any honest
one-paragraph, jargon-free version would materially misstate what the
concept is or does — the system must emit:

```
SIMPLIFICATION INADEQUATE -- DECOMPOSE CONCEPT FIRST
```

instead of publishing a misleading simple explanation, and must instead
break the concept into smaller sub-concepts that *can* each individually
pass a genuine Level 1 explanation, teach those first, and only then
compose them back into the original concept (typically resurfacing as a
Level 3+ vocabulary term once the pieces are in place). This mirrors the
repo's existing discipline of stating an honest gap rather than inventing
content to fill it (e.g. the "Honest gap" / "Honest scope limit" notes
already present in `docs/layman-first-pedagogy-principle.md` for
"Default," "Assignment," and "PMSI") — applied here to *pedagogical*
completeness rather than *citation* completeness.

**This is a design rule for future content generation, not a new schema
field or enum.** The smallest real implementation slice (not yet built)
would be a boolean-returning check function
content-authoring tooling calls before persisting a Level 1 string, plus a
`SIMPLIFICATION_INADEQUATE` sentinel value that a `PedagogicalContract`'s
(future) Level-1 field could hold in place of prose — see the schema-gap
discussion below.

### A real example where this flag should legitimately trigger

**"Good faith purchaser."** This looks, on its surface, like an ordinary
single concept ("someone who buys something honestly and doesn't get
punished for a hidden problem with the seller's title") — but checking it
against what's *actually* ingested shows why a single Level 1 explanation
would be misleading:

- Article 9's own ingested § 8.9A-102 defines **"Good faith"** alone
  (subsection (43): *"'Good faith' means honesty in fact and the
  observance of reasonable commercial standards of fair dealing"*) —
  but has no single, unified "good faith purchaser" definition. Instead,
  § 8.9A-102's own definitions list *points outward* to two other,
  narrower, Article-specific purchaser concepts — *"'Protected purchaser'
  § 8.8A-303"* and *"'Qualifying purchaser' § 8.12-102"* — **neither of
  which is ingested** (Article 8 and Article 12 sections are entirely
  outside Law Engine's current 24-section scope).
- Article 2's own good-faith-purchaser-for-value doctrine (historically §
  8.2-403 in Virginia's Title 8.2) is likewise **not one of the 11
  ingested Article 2 sections**
  (`services/ingestion.py`'s own disclosed 11-section list).
- What the term actually means shifts by *which* Article and *which*
  transaction type is in play: an Article 9 priority context, an Article 2
  sale-of-goods context, and an Article 8 investment-securities context
  are three different rules with three different tests, not one rule with
  three applications.

A forced Level 1 explanation ("someone who buys honestly is protected")
would be true often enough to sound right and wrong often enough to be
dangerous — exactly the "real distortion" this flag exists to prevent. The
correct response is `SIMPLIFICATION INADEQUATE -- DECOMPOSE CONCEPT FIRST`,
followed by first teaching the narrower pieces that *do* have real,
citable Level 1 explanations once ingested (Article 9's own "good faith,"
term 43; a properly scoped "protected purchaser" once § 8.8A-303 is
ingested; a properly scoped Article 2 buyer-in-ordinary-course concept once
its governing section is ingested) — never inventing a unified definition
none of the ingested sources actually state.

### Where this would live in the schema (not yet built)

`PedagogicalContract` has no field today for "the concept could not be
simplified" — its closest existing honesty mechanism is leaving an optional
field empty rather than fabricating content (the same discipline
`docs/pedagogical-contract-schema.md`'s "Building a new one" step 3
already states: *"Leave the rest at their default ... rather than filling
them with filler text"*). The six-level model above is a materially
different shape from `PedagogicalContract`'s current flat field set (which
has no notion of ordered levels at all — `what_it_is`, `how_to_recognize`,
etc. are all "shown at once," not progressively disclosed). Reusing
`PedagogicalContract` for six-level content would need either: (a) a new
`levels: list[LevelContent]` field, where each `LevelContent` can itself be
either real prose or the `SIMPLIFICATION_INADEQUATE` sentinel plus a
`decomposition_hint` pointing at the sub-concepts to teach first, or (b) a
separate new schema entirely, analogous to how `PedagogicalContract` itself
was added as a third reusable shape alongside `StatuteSection` and
`TransactionLifecycle` rather than overloading either of those. This note
takes no position on which — that decision belongs to whoever actually
implements this, informed by how many concepts turn out to need the flag in
practice.

---

## The optional learner diagnostic (a separate, related concept)

This is **personalization layered on top of** the zero-assumption default,
not a different default and not a gate. The two must never be conflated:

- **Curriculum default:** every learner starts at Level 1, for every
  concept, unless they take an explicit, opt-in action.
- **Diagnostic:** an *optional* pre-assessment an experienced learner may
  take to identify which concepts/levels they can skip *for themselves*.

### Who the learners actually are

Real, stated population for Law Engine: the Chairman, a law student, a
practicing lawyer, a business owner, a lender, a borrower, or a member of
the general public — a first-year law student and a commercial lending
officer arrive with wildly different real prior knowledge, and treating
them identically wastes the lending officer's time exactly the way
skipping Level 1 for the member of the public would fail them.

### Diagnostic mechanics

1. **Opt-in only.** The diagnostic is never presented as a required gate
   before content is reachable. A learner who declines it, ignores it, or
   fails it in some way gets exactly the same zero-assumption Level 1
   start as if the diagnostic didn't exist.
2. **Concept- and level-scoped, not learner-scoped.** The diagnostic
   doesn't label a learner "beginner" or "expert" as a global trait — it
   answers "does this specific learner already have Level 1–3 command of
   *this specific* concept?" per concept, using the same real, checkable
   question format `services/learning.py` already implements
   (`MultipleChoiceQuestion`, with real citation-grounded
   `why_correct`/`incorrect_choices`), not a self-reported skill claim.
3. **Result is a suggestion, never a lock.** A learner who tests out of
   Levels 1–3 for "Perfection" is offered a "skip to Level 4" shortcut —
   but the UI must always also expose "teach me from the beginning"
   as a live, equally-reachable option for that same concept, regardless
   of diagnostic result. This is the one non-negotiable design
   constraint in this whole document: **diagnostic results must never
   remove access to foundational material.**
4. **Wrong diagnostic answers are informative, not punitive.** A learner
   who "fails" the diagnostic isn't blocked from anything — they simply
   don't get the skip-ahead offer, and land exactly where the
   zero-assumption default already puts everyone.

### Cross-reference: how this maps onto the Mastery Engine design

`docs/ghostos-mastery-engine-design.md` already defines two GhostOS-level
components this diagnostic is a **Law-Engine-specific instantiation of** —
this note deliberately does not re-derive either from scratch:

- **Diagnostic Baseline** (`ghostos-mastery-engine-design.md`, Core
  components): *"Before teaching anything, determine what the learner
  already knows — a real pre-assessment against the competency model and
  prerequisite graph, not an assumption of zero prior knowledge."* The
  optional learner diagnostic above **is** a Diagnostic Baseline, scoped
  to Law Engine content. The one addition this note makes explicit (not
  present verbatim in the Mastery Engine note, though consistent with it):
  a Diagnostic Baseline's *default absence* must resolve to zero assumed
  knowledge, never to an assumed midpoint — the Mastery Engine note says a
  baseline replaces "an assumption of zero prior knowledge" *when run*; this
  note specifies what happens *when it is not run or not completed*: full
  zero-assumption default, not a guess.
- **Prerequisite Graph** (same document): *"A real dependency structure —
  what must be understood before what... a diagnostic baseline ... can skip
  anything the learner already has."* For Law Engine, the six levels above
  are themselves prerequisite-graph nodes **within one concept** (Level 1 →
  2 → 3 → 4 → 5 → 6, strictly ordered), and concepts are prerequisite-graph
  nodes **across concepts** (e.g. "Collateral" and "Attachment" as
  prerequisites of "Perfection," exactly as Level 1–3 above uses them). A
  diagnostic result of "already has Perfection Levels 1–3" doesn't just
  skip those levels for Perfection — per the Prerequisite Graph's own
  stated purpose, it can also inform (never force) skip-eligibility for
  concepts that list Perfection as their own prerequisite, e.g. Priority
  (§§ 8.9A-317, 8.9A-322, 8.9A-324), which Level 5–6 above already leans on.
- **Curriculum Optimization** (same document) explicitly warns against
  "skipping a real prerequisite to save time" producing "a learner who
  can't actually transfer the knowledge" — the same reasoning this note
  uses to justify *never* letting a diagnostic result silently remove the
  "teach me from the beginning" option. The Mastery Engine note's warning
  is about the *system* skipping a step for speed; this note's constraint
  is about the *learner* always retaining the right to override that skip.
- **Mastery Threshold / Mastery-type distinction** (same document, "Exam
  Mastery" vs. "Practitioner Mastery" vs. "Conceptual Mastery" vs.
  "Task-Specific Mastery"): the diagnostic's skip-offer should itself be
  mastery-type-aware once that selection layer exists — e.g. a learner
  declaring Task-Specific Mastery ("what happens if I buy equipment on
  credit and default") has a materially different, narrower Level 4–6
  bar to test out of than one declaring Practitioner Mastery. This note
  does not design that interaction fully; it flags it as the natural next
  join point between this diagnostic and the Mastery Engine's own
  mastery-type table once both exist as real code.

**Smallest real implementation slice for the diagnostic (not built this
run):** a single `ConceptDiagnostic` check for exactly one concept
(Perfection, using the six-level content already worked out above), scored
against 2–3 real `MultipleChoiceQuestion` items in the existing
`services/learning.py` shape, returning a per-level skip suggestion — with
an explicit test asserting that a "perfect diagnostic score" result still
leaves Level 1 content reachable through some code path, not merely
absent from a UI button. That last assertion is the one this whole
diagnostic design exists to protect, so it should be the first thing a real
implementation tests.

---

## Sources / grounding

- `law-engine/services/ingestion_article9.py`,
  `law-engine/services/ingestion.py` (internal, this repository, read-only
  — the real ingested Article 9 / Article 2 section sets and their
  disclosed scope limits, checked directly for this note's candidate
  concepts and the "good faith purchaser" gap)
- `law-engine/library/normalized/ucc/article-9-sections.json` (internal,
  this repository, read-only — real statutory paragraph text quoted at
  Level 4–5 above, copied verbatim, not restated from memory)
- `law-engine/docs/layman-first-pedagogy-principle.md` (internal, this
  repository — existing four-layer term discipline, extended not
  duplicated by Levels 3–4 above)
- `law-engine/docs/pedagogical-contract-schema.md`,
  `law-engine/services/models.py`,
  `law-engine/services/pedagogical_contract.py` (internal, this
  repository, read-only — existing `PedagogicalContract` schema and its
  one real built instance, referenced in the schema-gap discussion above)
- `law-engine/services/cross_article_lifecycle.py` (internal, this
  repository, read-only — real source of the Level 2 equipment-purchase
  fact pattern, reused rather than invented)
- `law-engine/services/learning.py` (internal, this repository, read-only
  — real `MultipleChoiceQuestion`/`Flashcard` shape proposed as the
  diagnostic's question format)
- `docs/ghostos-mastery-engine-design.md` (internal, this repository,
  read-only — GhostOS-level Diagnostic Baseline and Prerequisite Graph
  components this note's diagnostic instantiates for Law Engine,
  explicitly cross-referenced rather than re-derived)
