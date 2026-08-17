# UCC Source & Licensing Audit

Research pass, written 2026-08-15, grounding the sourcing decision already made
in `services/ingestion.py` (Virginia's *enacted* Title 8.2 statute text, not
the ALI/ULC "official" UCC text) in real, current, cited law. This document
does not propose any code change. It exists so future runs — Virginia's
remaining Article 2 sections, other states' enactments, the 2022 digital-asset
amendments, official comments, secondary sources — have a real licensing
answer to check against before ingestion, not a guess.

## 1. Who owns what, and why it matters here

There are at least three legally distinct categories of "UCC text" that this
project's sourcing choice already treats as different, but that the codebase
does not yet name as three separate `AuthorityType`/provenance categories.
This audit gives them names for use in `SourceManifest.licensing_status` and
`SourceManifest.notes` (see §4) without proposing any change to
`services/models.py` itself.

### (a) ALI/ULC "official" Model UCC text and official comments — copyrighted

The Uniform Commercial Code as such is a joint work of the **American Law
Institute (ALI)** and the **Uniform Law Commission (ULC, formerly NCCUSL —
National Conference of Commissioners on Uniform State Laws)**. The two
organizations jointly copyright the official text, and the **Permanent
Editorial Board (PEB)**, a joint ALI/ULC committee, is charged with
maintaining uniformity and approving amendments.
[ALI — Uniform Commercial Code](https://www.ali.org/publications/uniform-commercial-code),
[ALI — PEB Report on Official Text of the UCC](https://www.ali.org/sites/default/files/2025-10/PEB%20Report-Official-Text-of-UCC.pdf).

The 2022 UCC Amendments' own published "Final Act with Comments" carries an
explicit notice: **"Copyright © 2022 by the American Law Institute and the
National Conference of Commissioners on Uniform State Laws. All rights
reserved."** — confirmed directly from the document text
([UCC Amendments (2022), Final Act with Comments, PDF mirror](https://www.restructuring-globalview.com/wp-content/uploads/sites/21/2023/10/UCC-Amendments_2022_Final-Act-with-Comments_8-1.pdf)).
This is the clearest, most current confirmation that ALI/ULC actively assert
and print copyright on both the model statutory text *and* the official
comments as drafted by ALI/ULC — not just the comments. The official,
publisher-sold volume is distributed commercially (e.g., via Thomson Reuters)
([ALI — Uniform Commercial Code](https://www.ali.org/publications/uniform-commercial-code)).

The **ULC's own Terms of Use** (`uniformlaws.org/termsofuse`) states the
site's uniform-act content is protected by copyright, and permits
**non-commercial viewing/copying/printing/distribution with attribution**
(not modification), plus a broader **legislative-use exception**: content may
be viewed, copied, distributed, *and modified* specifically "for legislative
purposes," provided it carries a prominent acknowledgment that it comes from
the ULC. That legislative-use carve-out is precisely why a *state legislature
enacting* the UCC into its own code is lawful and produces a public-domain
result (§1(b) below) even though the ULC's own draft text remains its
copyrighted starting point.

**Practical conclusion:** the ALI/ULC official Model UCC text, and
especially the official comments accompanying each section (including the
2022 Article 12 / digital-asset amendments), must be treated in this project
as **copyrighted, third-party-owned material** — not something to bulk-ingest
or republish, regardless of how it's obtained.

### (b) A state's own enactment of the UCC — public domain (government edicts doctrine)

The Supreme Court's **`Georgia v. Public.Resource.Org, Inc.`, 590 U.S. 255
(2020)** is the controlling, current statement of the **government edicts
doctrine**: works created by officials empowered to speak with the force of
law, in the course of their official legislative duties — including
explanatory/procedural material they produce in that legislative capacity —
are not copyrightable, because "no one can own the law."
([Georgia v. Public.Resource.Org opinion, Supreme Court](https://www.supremecourt.gov/opinions/19pdf/18-1150_7m58.pdf);
summary: [Mintz — Supreme Court Holds States Cannot Copyright Annotated
Statutes](https://www.mintz.com/insights-center/viewpoints/2231/2020-04-29-supreme-court-holds-states-cannot-copyright-annotated);
background doctrine: [Wikipedia — Government edicts
doctrine](https://en.wikipedia.org/wiki/Government_edicts_doctrine)).

When a state legislature enacts its own version of UCC Article 2 into its own
code — e.g., Virginia's Title 8.2, sourced directly from
`law.lis.virginia.gov`, the Commonwealth's own official legislative
information system, as this project's Mission 13/16/17 ingestion already
does — that **enacted statutory text is a public-domain government edict**,
regardless of the fact that the ULC's draft language was its starting point.
This is exactly the distinction `services/ingestion.py`'s own docstring
already draws, and `Georgia v. PRO` is the current, real, citable authority
for it.

**Important limit on this holding:** `Georgia v. PRO` is specifically about
*official annotations* prepared by/for a legislative body (there, Georgia's
OCGA annotations, produced under contract with Lexis for Georgia's Code
Revision Commission) — not about privately-authored secondary commentary sold
separately from the statute. It does **not** hold that ALI/ULC's official
comments become public domain merely because a state also enacted the
underlying statute; the state's *enacted text* is public domain, but ALI/ULC
retains its own, separate copyright interest in comments it authored and
that the state did not itself adopt as statutory text (see §1(a)).

### (c) Case law and commentary interpreting the UCC — mixed, source-dependent

- **Judicial opinions** applying UCC provisions are themselves government
  edicts and public domain under the same doctrine (judicial opinions are
  explicitly named in the doctrine's core cases going back to *Wheaton v.
  Peters*, 33 U.S. (8 Pet.) 591 (1834); see the *Government edicts doctrine*
  background above). A court's *published opinion text* can be stored/
  republished; a commercial reporter's added headnotes/syllabi/pagination
  (West headnotes, star-pagination editorial features) are a separate,
  privately-copyrighted layer and should not be scraped from a paid reporter
  service without checking that service's own terms.
- **Treatises, practitioner guides, and law review commentary** (e.g., the
  *ABCs of the UCC* and other titles noted in
  `docs/source-inventory.md`'s legitimate-treatise list) are ordinary
  copyrighted secondary authority, owned by their publishers/authors — no
  edicts-doctrine exception applies at all. These require ordinary
  copyright clearance (license, fair-use analysis, or exclusion) before any
  storage beyond personal/research use.
- **UNCITRAL/CISG materials** are a *different* body entirely (see the
  companion CISG document) and are UN-published; treat separately.

## 2. The 2022 UCC Amendments — current status (checked 2026-08-15)

The 2022 amendments (adding Article 12 — Controllable Electronic Records —
and touching most other Articles, to address digital-asset transactions) were
jointly approved by ALI and ULC, with the official Final Act and Comments
under the ALI/ULC copyright notice quoted in §1(a).

As of the most current information found:

- **New York** enacted the 2022 amendments in **December 2025**, becoming
  approximately the **33rd jurisdiction** (32 other states plus D.C.) to do
  so, completing adoption in all three of Delaware, New York, and D.C. — the
  jurisdictions of greatest practical weight for secured-transactions
  practice.
  ([Orrick — New York Enacts 2022 UCC Amendments](https://www.orrick.com/en/Insights/2025/12/New-York-Enacts-2022-UCC-Amendments-A-New-Era-for-Digital-Asset-Transactions);
  [Cadwalader — Big Digital Apple](https://www.cadwalader.com/resources/clients-friends-memos/big-digital-apple--new-york-adopts-the-2022-ucc-amendments))
- As of **February 4, 2025**, 25 jurisdictions had enacted the amendments,
  including **Virginia** — meaning this project's own sourcing jurisdiction
  has already adopted the 2022 changes, so any future ingestion of Virginia's
  Title 8.2 beyond the current 11-section Article 2 slice should check
  whether newly-touched sections reflect post-2022-amendment text.
  ([Mayer Brown — Choice-of-Law Issues as the UCC 2022 Amendments Come Into
  Effect](https://www.mayerbrown.com/en/insights/publications/2025/02/choice-of-law-issues-as-the-ucc-2022-amendments-come-into-effect);
  [Duane Morris — Countdown to the New Digital Asset UCC
  Rules](https://www.duanemorris.com/alerts/countdown_new_digital_asset_ucc_rules_is_your_state_on_board_0724.html))
- More than half of all states had **not yet** enacted (some not even
  introduced) the amendments as of that same check.
- The ULC maintains its own live enactment tracker for this specific
  amendment package:
  [ULC — UCC, 2022 Amendments to (committee/status
  page)](https://www.uniformlaws.org/committees/community-home?CommunityKey=1457c422-ddb7-40b0-8c76-39a1991651ac).
  **Recommendation:** any future run touching UCC sections affected by the
  2022 amendments (Articles 1, 9, and the new Article 12 especially) should
  re-check this live tracker rather than trusting this document's snapshot,
  since adoption is actively in progress state-by-state.

**Practical implication for Law Engine:** because Article 2 (Sales) itself
was not a primary target of the 2022 amendments (Articles 1, 9, and 12 were),
this project's current 11-section Article 2 vertical slice is not directly
affected — but any future expansion into Article 9 (secured transactions) or
Article 12 sourcing must check the *enacting state's* specific 2022-amendment
status before treating a source extract as current.

## 3. What may be stored privately / republished publicly / only linked

This maps directly onto the three-category split in §1 and gives concrete
handling rules, consistent with the existing `docs/public-private-boundary.md`
policy (which already requires every `SourceManifest.licensing_status` to be
checked before public release).

| Source category | Store privately (internal `library/`)? | Republish publicly (future public repo)? | Link/cite only? |
|---|---|---|---|
| **State-enacted statute text** (e.g., Virginia Title 8.2, as already ingested) | Yes — already the project's approach | **Yes** — public-domain government edict under `Georgia v. PRO`; safe to republish verbatim with citation to the official state source | N/A (may republish, but always keep `official_source_url` as attribution) |
| **Published judicial opinions** applying UCC provisions (the court's own text) | Yes | Yes, if pulled from a public-domain-clean source (e.g., a court's own website, or a citation-only extract) — **not** from a commercial reporter's copyrighted headnotes/pagination layer | If sourced only from a paid reporter service, link/cite rather than republish the reporter's added material |
| **ALI/ULC official Model UCC text** (uniformlaws.org draft text) | Yes, for internal reference/comparison only, under the ULC's own non-commercial Terms of Use | **No** — do not republish in a future public repo without separately negotiated ALI/ULC permission | Yes — always safe: link to `uniformlaws.org` or the ALI's own catalog page |
| **ALI/ULC official comments** (including 2022 amendment comments) | Yes, for internal reference only | **No** — explicitly copyrighted, "All rights reserved," per the 2022 Final Act notice; do not copy comment text into any future public repo, public-facing doc, or trained model output presented as project content | Yes — cite by section number and refer readers to the official ALI/ULC-published volume |
| **Treatises / practitioner guides** (*ABCs of the UCC*, etc.) | Only if lawfully acquired (purchased/licensed copy); do not scrape | No, absent a license | Yes — cite title/edition/author |
| **Chairman's own Law Engine vision document** | Yes (already the case) | Not applicable — it's a product-planning input, not a legal-authority source (see `source-inventory.md`) | N/A |

**The single clearest rule to carry forward:** *enacted statute text is safe
to republish; ALI/ULC official comments are never safe to republish without
a license, no matter how the underlying statute was sourced.* This project's
existing choice to source Virginia's enacted text rather than the ALI/ULC
official text was already the right call under this rule — this audit
confirms it with current, cited authority rather than leaving it as an
undocumented assumption.

## 4. Concrete `SourceManifest.licensing_status` conventions

`services/models.py`'s `SourceManifest.licensing_status: str` field already
exists and is already populated with a descriptive sentence for the Virginia
ingestion (`"public domain -- enacted state statute (edict of government),
not the separately-copyrighted ALI/ULC official UCC text"`). This audit does
not propose changing the field's type or adding a new enum — only
recommends holding future values to a small, consistent vocabulary so the
field stays machine-filterable (e.g., for the public/private boundary check
in `docs/public-private-boundary.md`) while remaining human-readable. Suggested
canonical prefixes, each followed by a short case-specific clause as already
practiced in `ingestion.py`:

- `"public domain -- enacted state statute (edict of government)"` — for any
  state's own enacted code text (current convention; keep using it verbatim
  for consistency, appending the "not the ALI/ULC official text" clause when
  relevant).
- `"public domain -- judicial opinion (edict of government)"` — for court
  opinion text sourced from a court's own site or a public-domain-clean
  aggregator (not a commercial reporter's copyrighted layer).
- `"copyrighted -- ALI/ULC official text, internal reference only, not for
  public republication"` — for any ALI/ULC Model Act text or official
  comment stored for internal comparison/QA purposes.
- `"copyrighted -- third-party secondary authority, internal reference only"`
  — for treatises, practitioner guides, law review articles.
- `"copyrighted -- commercial reporter enhancement, do not republish"` — for
  any headnote/annotation/pagination layer obtained from a paid reporter
  service.
- `"unreviewed -- licensing status not yet checked"` — an explicit
  placeholder value so an unchecked source is never mistaken for a cleared
  one; `docs/public-private-boundary.md`'s existing rule ("never publish a
  manifest whose licensing status hasn't been checked") can grep for this
  literal string as a hard gate before any future publish step.

This keeps the field a plain string (unchanged from the current dataclass)
while giving future runs — and any future automated public/private boundary
check — a stable, greppable set of prefixes to test against, rather than
free text that has to be read by a human every time.

## Sources consulted

- [ALI — Uniform Commercial Code (publications page)](https://www.ali.org/publications/uniform-commercial-code)
- [ALI — PEB Report on Official Text of the Uniform Commercial Code (PDF)](https://www.ali.org/sites/default/files/2025-10/PEB%20Report-Official-Text-of-UCC.pdf)
- [UCC Amendments (2022), Final Act with Comments — copyright notice](https://www.restructuring-globalview.com/wp-content/uploads/sites/21/2023/10/UCC-Amendments_2022_Final-Act-with-Comments_8-1.pdf)
- [Uniform Law Commission — Terms of Use](https://www.uniformlaws.org/termsofuse)
- [Uniform Law Commission — UCC, 2022 Amendments to (status/committee page)](https://www.uniformlaws.org/committees/community-home?CommunityKey=1457c422-ddb7-40b0-8c76-39a1991651ac)
- [Georgia v. Public.Resource.Org, Inc., 590 U.S. 255 (2020) — full opinion](https://www.supremecourt.gov/opinions/19pdf/18-1150_7m58.pdf)
- [Mintz — Supreme Court Holds That States Cannot Copyright Annotated Versions of Their Statutes](https://www.mintz.com/insights-center/viewpoints/2231/2020-04-29-supreme-court-holds-states-cannot-copyright-annotated)
- [Wikipedia — Government edicts doctrine](https://en.wikipedia.org/wiki/Government_edicts_doctrine) (background/orientation only; primary authority is the Supreme Court opinion above)
- [Orrick — New York Enacts 2022 UCC Amendments: A New Era for Digital Asset Transactions](https://www.orrick.com/en/Insights/2025/12/New-York-Enacts-2022-UCC-Amendments-A-New-Era-for-Digital-Asset-Transactions)
- [Cadwalader — Big Digital Apple: New York Adopts the 2022 UCC Amendments](https://www.cadwalader.com/resources/clients-friends-memos/big-digital-apple--new-york-adopts-the-2022-ucc-amendments)
- [Mayer Brown — Choice-of-Law Issues as the UCC 2022 Amendments Come Into Effect](https://www.mayerbrown.com/en/insights/publications/2025/02/choice-of-law-issues-as-the-ucc-2022-amendments-come-into-effect)
- [Duane Morris — Countdown to the New Digital Asset UCC Rules: Is Your State on Board?](https://www.duanemorris.com/alerts/countdown_new_digital_asset_ucc_rules_is_your_state_on_board_0724.html)
- `law-engine/services/models.py`, `law-engine/services/ingestion.py`, `law-engine/docs/source-inventory.md`, `law-engine/docs/public-private-boundary.md` (internal, this repository)
