# Law Engine

A structured legal-intelligence and learning platform — real provenance tracking, real authoritative
source text, real citations, and a deterministic legal-reasoning architecture. Current domain:
Uniform Commercial Code Articles 1 (general provisions), 2 (sale of goods), 3 (negotiable
instruments), and 9 (secured transactions), sourced from the Commonwealth of Virginia's own enacted
statute text (Va. Code Ann. Titles 8.1A, 8.2, 8.3A, and 8.9A).

**Status: public, active development.**

## What's real here

- **`services/`** (Python) — provenance/verification data model (`models.py`: a 9-state verification
  hierarchy, explicit Model-UCC/state-Enactment/case-law-Interpretation source layering), real
  ingestion from the Commonwealth of Virginia's official legislative site (one ingestion module per
  Article), deterministic citation search (`retrieval.py`), a real learning-item engine
  (`learning.py`), a deterministic (non-ML) grammatical/structural-analysis tool for legal text
  (`syntax_engine.py`), a cross-Article transaction lifecycle (`transaction_lifecycle.py`,
  `cross_article_lifecycle.py`), asset/document/obligation-perspective intelligence, and a Legal
  Proof Graph implementing a definition → axiom → governing-authority → verified-fact →
  intermediate-proposition reasoning chain (`legal_proof_graph.py`). A real, passing, growing
  automated test suite (in the hundreds; grows with each new Article).
- **`apps/web/`** (TypeScript + Next.js 16 + React) — a real, building, type-checking application:
  browse every ingested section across all four Articles with full citation/definitions/
  cross-references, four real interactive learning scenarios (an Article 2 consumer-to-operator task
  ladder, and three multi-step real-world simulations — a restaurant purchase, a secured-financing
  scenario, and a negotiable-instrument/promissory-note scenario), a multi-lifecycle transaction
  learner, a conceptual UCC orientation page, a practice-question set, a language-analysis panel, and
  real `/api/search` and `/api/lifecycle` routes. Real component test suite (Vitest + React Testing
  Library). Zero known dependency vulnerabilities (`npm audit`, re-verified each release).
- **`library/`** — the real, immutable source extracts, their normalized JSON derivatives, and
  provenance manifests with real SHA-256 hashes and an explicit, checked public-domain licensing
  determination — see `NOTICE.md`.
- **`docs/`** — architecture, source inventory, product vision, and design documents for the
  reasoning architecture (Euclidean legal reasoning, zero-trust epistemology, forensic transaction
  reconstruction), the zero-assumption pedagogical model, and the public/private boundary policy.

## Bounded, early precedent-conflict prototype (read before trusting)

A small, explicitly bounded, **early prototype** case-law capability now exists alongside the
statutory work above — a Precedent Conflict Mapper (`services/precedent_conflict_mapper.py`) and a
Euclidean authority/proof extension to the Legal Proof Graph, applied to exactly one flagship
question (who is entitled to enforce a transferred promissory note) against exactly two real,
named, independently source-verified cases: *Rodriguez v. Wells Fargo Bank, N.A.*, 178 So. 3d 62
(Fla. 4th DCA 2015), and *Greene v. Trustee Services of Carolina, LLC*, 244 N.C. App. 583 (2016).

**What "source-verified" means here, precisely**: both opinions were independently retrieved in full
from a real primary source — Rodriguez via CourtListener's stored mirror of the official 4th DCA
opinion (the court's own original URL now 404s), Greene by direct read of the North Carolina Judicial
Branch's own official appellate-opinions PDF — and read completely, end to end, not summarized. Both
carry `VerificationStatus.SOURCE_VERIFIED`. The verification process itself caught and fixed four
real errors along the way (a truncated quote, a quote misattributed from a concurrence to the
majority, a misquoted word, and omitted procedural history) — corrected, not swept aside; full detail
in `library/source/case-law/*.json`.

**What this is not**: a general or comprehensive case-law database, and not a claim that Law Engine
can resolve arbitrary legal questions. This is a **bounded, early prototype** — exactly one flagship
question, exactly two cases, both from one narrow doctrinal corner of UCC Article 3. The system's own
confidence output for this flagship correctly reflects that boundedness (`LIKELY`, not a higher tier
reserved for controlling, unambiguous authority) rather than overclaiming certainty a two-case, one-
question prototype hasn't earned. Treat this as real, working, verified technical evidence of the
underlying approach — not as a general-purpose legal-research tool.

## An honest distinction: orientation vs. ingested authority

`/learn/orientation` is real, deliberately-written conceptual content — "why does uniform commercial
law exist," "what does 'uniform' actually mean," "is the UCC itself binding law" — meant as a
plain-language on-ramp before a learner is dropped into section-by-section detail. It is **not**
itself a source of legal authority and cites none directly.

Everything under `/sections/*`, and every citation used inside a learning scenario, traces back to
one of the real, provenance-tracked statutory sections in `library/` — the Commonwealth of Virginia's
own enacted text, independently fetched, hashed, and recorded (see `library/manifests/*.json`). The
orientation content explains the *system*; the ingested sections *are* the authority.

## What this deliberately is not

Not a courtroom-tactics generator, not a scraper of sovereign-citizen "guru" content. See
`docs/source-inventory.md` for the full, honest account of that real scope decision.

Not a source of legal advice. This is an educational and technical demonstration; nothing it
generates is legal advice, and no attorney-client relationship is created by using it.

Not a general case-law database. The overwhelming majority of ingested content here is enacted
statutory text. Exactly two real, source-verified judicial opinions exist as an explicitly bounded,
early-prototype case-law layer (see above) — real, verified evidence for one narrow doctrinal
question, not a general-purpose legal-research capability. Expanding beyond these two cases, or to
any other legal question, remains real, deliberately unscoped future work — not something to assume
exists.

## Case studies

- [`docs/case-studies/ux-task-first-iteration.md`](docs/case-studies/ux-task-first-iteration.md) — a
  real founder-feedback-driven product-iteration cycle (accessibility fix, and a reframing of the core
  learning mechanic), written up honestly as one founder's own feedback loop, not formal multi-user UX
  research.
- [`docs/case-studies/product-architecture.md`](docs/case-studies/product-architecture.md) — the
  product overview: problem, user, MVP, what was deliberately not built, architecture, tradeoffs,
  roadmap, and risk.

## Running it

Requires Node.js **>=20.9.0** for `apps/web` (Next.js 16's own minimum). Python side has no version
constraint beyond the standard library.

```
cd services && python3 -m unittest discover -p "test_*.py"
cd apps/web && npm install && npm test && npm run build && npm run start
```

## License

Apache License, Version 2.0, for this project's own code — see `LICENSE`. The ingested statutory text
is public-domain government material, not this project's original work — see `NOTICE.md` for the full
explanation and the distinction between a state's enacted statute (public domain) and the ALI/ULC's
copyrighted "official" Model UCC text (not ingested here).
