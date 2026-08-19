# Notice: Source Material and Licensing

This project's own code (Python services, the TypeScript/Next.js/React application, and the documentation prose in `docs/`) is licensed under the Apache License, Version 2.0 — see `LICENSE`.

## The ingested statutory text is not this project's work

The statutory text under `library/source/` and `library/normalized/` — currently the Commonwealth of Virginia's enacted Uniform Commercial Code, Title 8.1A (Article 1, general provisions), Title 8.2 (Article 2, sale of goods), Title 8.3A (Article 3, negotiable instruments), and Title 8.9A (Article 9, secured transactions) — is **public-domain government material**, not an original work of this project, and is not covered by the Apache License, Version 2.0 above.

**Why it's public domain**: an enacted state statute is a governmental edict. Under the government-edicts doctrine, most recently and controllingly affirmed by the U.S. Supreme Court in *Georgia v. Public.Resource.Org, Inc.*, 590 U.S. 255 (2020), officials empowered to speak with the force of law cannot hold copyright in the works they create in that capacity — annotated or not. This project's own real legal research on this point lives in `docs/legal-research/ucc-source-licensing-audit.md`, cited by name and with the real controlling authority, not asserted as a hand-wave.

**A separate, important distinction — do not confuse these two things**: the *official Uniform Commercial Code* as promulgated by the American Law Institute (ALI) and the Uniform Law Commission (ULC) is a **copyrighted work of a private organization**, not itself public domain. This project does not ingest, reproduce, or redistribute that ALI/ULC "Model" text. What is actually ingested here is a **state's own enacted statute** — the version of the UCC that state actually adopted into law, sourced directly from that state's own official legislative publication (`law.lis.virginia.gov`, the Commonwealth of Virginia's official legislative information system) — which is public domain regardless of how closely its wording tracks the ALI/ULC original.

Every ingested section carries a real, checkable provenance record (`library/manifests/*.json`): a SHA-256 hash of the exact source bytes, the official source URL, and an explicit `licensing_status` field stating this reasoning per-document, not just in this NOTICE.

## The two experimental case-law sources are also public domain, on a separate legal basis

`library/source/case-law/` contains exactly two judicial opinions (see the main README's own
"Experimental, bounded" section for what these are and their current verification status). Judicial
opinions are public-domain government material too, on the same government-edicts reasoning as
statutory text — a court speaking with the force of law cannot hold copyright in its own opinion
(*Banks v. Manchester*, 128 U.S. 244 (1888), the classic case establishing this for judicial opinions
specifically, predating and consistent with *Georgia v. Public.Resource.Org*'s later statutory
holding). This is a real, separate licensing basis from the statutory-text reasoning above — recorded
per-document in each case manifest's own `licensing_status` field, same discipline as every statutory
source. **This licensing determination is independent of, and does not resolve, the separate
`RETRIEVED`-vs-`SOURCE_VERIFIED` factual-accuracy question** — a source can be genuinely public domain
and still not yet independently byte-verified for accuracy; the two are different questions, both
disclosed honestly, neither substituting for the other.

## What this means practically

- You may use, modify, and redistribute this project's own code under the Apache License, Version 2.0.
- The ingested statutory text is government material you're already free to use regardless of this project's license — nothing here restricts it further, and nothing here claims ownership of it.
- If this project is extended to ingest additional jurisdictions or sources, each new source's licensing basis should be independently verified and recorded the same way, not assumed by analogy.

## Not legal advice

This project is an educational and technical demonstration. Nothing it generates — explanations, analysis, or otherwise — is legal advice, and no attorney-client relationship is created by using it.
