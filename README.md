# Law Engine

A structured legal-intelligence and learning platform — real provenance tracking, real authoritative source text, real citations, and a deterministic legal-reasoning architecture. Current domain: UCC Article 2 (sale of goods) and Article 9 (secured transactions), sourced from the Commonwealth of Virginia's own enacted statute text (Va. Code Ann. Title 8.2 and Title 8.9A).

**Status: private, in development. Not yet published.**

## What's real here

- **`services/`** (Python) — provenance/verification data model (`models.py`: a 9-state verification hierarchy, explicit Model-UCC/state-Enactment/case-law-Interpretation source layering), real ingestion from the Commonwealth of Virginia's official legislative site (`ingestion.py`, `ingestion_article9.py`), deterministic citation search (`retrieval.py`), a real learning-item engine (`learning.py`), a deterministic (non-ML) grammatical/structural-analysis tool for legal text (`syntax_engine.py`), a cross-Article transaction lifecycle (`transaction_lifecycle.py`, `cross_article_lifecycle.py`), asset/document/obligation-perspective intelligence, and a Legal Proof Graph implementing a definition → axiom → governing-authority → verified-fact → intermediate-proposition reasoning chain (`legal_proof_graph.py`). **201 real, passing tests.**
- **`apps/web/`** (TypeScript + Next.js 16 + React) — a real, building, type-checking application: browse all 24 ingested sections across both Articles, read one with full citation/definitions/cross-references, an interactive multi-stage transaction-lifecycle learner, a language-analysis panel, and real `/api/search` and `/api/lifecycle` routes. Real component test suite (Vitest + React Testing Library). **Zero known dependency vulnerabilities** (`npm audit`, re-verified).
- **`library/`** — the real, immutable source extracts, their normalized JSON derivatives, and provenance manifests with real SHA-256 hashes and an explicit, checked public-domain licensing determination — see `NOTICE.md`.
- **`docs/`** — architecture, source inventory, product vision, and design documents for the reasoning architecture (Euclidean legal reasoning, zero-trust epistemology, forensic transaction reconstruction), the zero-assumption pedagogical model, and the public/private boundary policy.

## What this deliberately is not

Not a courtroom-tactics generator, not a scraper of sovereign-citizen "guru" content. See `docs/source-inventory.md` for the full, honest account of that real scope decision.

Not a source of legal advice. This is an educational and technical demonstration; nothing it generates is legal advice, and no attorney-client relationship is created by using it.

## Running it

Requires Node.js **>=20.9.0** for `apps/web` (Next.js 16's own minimum). Python side has no version
constraint beyond the standard library.

```
cd services && python3 -m unittest discover -p "test_*.py"
cd apps/web && npm install && npm test && npm run build && npm run start
```

## License

Apache License, Version 2.0, for this project's own code — see `LICENSE`. The ingested statutory text is public-domain government material, not this project's original work — see `NOTICE.md` for the full explanation and the distinction between a state's enacted statute (public domain) and the ALI/ULC's copyrighted "official" Model UCC text (not ingested here).
