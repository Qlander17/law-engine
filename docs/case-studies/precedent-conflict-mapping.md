# Apparent Conflict, Different Question: How Procedural Posture Changes the Proof of Enforcement Authority

A secondary summary attributed this sentence to the court:

> The case law says the critical time for determining the status of the two core elements is the date the suit is filed.

Reading the official opinion showed that the sentence is Conner, J.’s special concurrence in *Rodriguez v. Wells Fargo Bank, N.A.*, 178 So. 3d 62, 65 (Fla. 4th DCA 2015) — not Ciklin, C.J.’s majority. Taylor, J. concurred in the majority; Conner, J. concurred specially with a separate opinion.

That is not a citation nit. Majority holding, concurrence, and later paraphrase have different precedential force. A data model that stores “quoted language from the case” without speaker and opinion segment will treat them as interchangeable. After the correction, they are not.

The flagship pair in this prototype — *Rodriguez* (Florida) and *Greene v. Trustee Services of Carolina, LLC*, 244 N.C. App. 583, 781 S.E.2d 664 (N.C. App. 2016) — is usually introduced as a foreclosure-era split over *when* holder status must be shown. The stronger reading, and the one the proof graph actually encodes, is narrower:

**The two cases answer different questions. Different outcomes do not, without more, mean doctrinal conflict.**

---

## Why the concurrence error changed the model

Live Run 1.59’s secondary-source draft of this research introduced four classes of error, all caught when the complete opinions were read:

| Error class | What was wrong | Why it matters |
|---|---|---|
| Truncated quotation | *Rodriguez* complaint quoted as “the holder of the Mortgage Note and Mortgage,” omitting “and/or is entitled to enforce the Mortgage Note and Mortgage” | The omitted disjunctive is the allegation the servicer-authority holding turns on |
| Concurrence misattributed to the majority | Timing sentence stored as unqualified court language | Concurrence is not majority holding; later citation of that sentence (e.g. *Caraccia*) is citing Conner, J., not the majority ratio |
| Altered procedural terminology | *Greene* quoted as “the [trial] court”; the opinion says “the superior court” | The proof moment is the de novo superior-court hearing, not the clerk’s original hearing |
| Omitted procedural history | *Greene*’s 2010 foreclosure attempt, bankruptcy stay, and discharge dropped | The litigated proceeding is the 2013 power-of-sale path, not a judicial complaint filed in 2010 |

Speaker, opinion segment, proceeding, and proof moment therefore have to survive ingestion. `AuthorityType` now includes `JUDICIAL_HOLDING`, `DICTA`, and `PERSUASIVE_OPINION` rather than a single `CASE` bucket. *Rodriguez*’s source file keeps the Conner sentence, labeled as concurrence, because it elaborates the majority’s timing point — and because hiding it would repeat the original sin in reverse.

Both opinions are `VerificationStatus.SOURCE_VERIFIED`: *Rodriguez* via CourtListener’s stored mirror of the official Fourth DCA PDF after the court’s original URL 404’d; *Greene* by direct read of the North Carolina Judicial Branch PDF at `appellate.nccourts.org`. `SOURCE_VERIFIED` means the text in the capture matches the retrieved opinion. It does not mean the proposition is still good law, is holding rather than dicta, or controls a new forum.

---

## Proposition matrix

The comparison is not “Florida vs. North Carolina on UCC holder status.” It is two encoded propositions.

| Dimension | *Rodriguez* (Fla. 4th DCA 2015) | *Greene* (N.C. App. 2016) |
|---|---|---|
| Party seeking enforcement | Wells Fargo Bank, N.A., d/b/a America’s Servicing Company — a **servicer** suing in its own name | U.S. Bank, N.A., as **claimed holder** by possession (Trustee Services as substitute trustee); challenger is Shaka Greene, HOA-sale purchaser, not the original mortgagors |
| Proceeding | Judicial foreclosure complaint | Chapter 45 power-of-sale foreclosure, appealed de novo to superior court (consolidated with a quiet-title action) |
| Relevant time | Date the complaint was filed | Production at the hearing (superior court on de novo review) |
| Proof demanded | Authority to enforce for the holder as of filing (power of attorney or pooling-and-servicing agreement in the record) | Original note, indorsed in blank, in the party’s possession |
| Actual proposition decided | A servicer-plaintiff who does not prove that authority at filing lacks standing; later filing of the original blank-indorsed note does not cure the gap. Bare pre-suit possession by the servicer, without documented authority, was not enough. | Because the note was indorsed in blank and U.S. Bank had possession, the superior court properly found U.S. Bank the holder. The UCC text, as applied there, does not require a documented chain of transfer. |
| Encoded precedential scope | District Court of Appeal of Florida, Fourth District (`hierarchy_level` 2 in its own system). Stored `binding_scope` records the original precedential scope as represented by the opinion and court hierarchy at ingestion (4th DCA territorial reach; persuasive elsewhere), subject to currentness and subsequent-history verification. This document does not claim the opinion remains controlling today. | Court of Appeals of North Carolina (`hierarchy_level` 2). Stored `binding_scope` records the original precedential scope as represented by the opinion and court hierarchy at ingestion (statewide for this proceeding type; persuasive outside NC), subject to currentness and subsequent-history verification. This document does not claim the opinion remains controlling today. |
| Source status | `SOURCE_VERIFIED` (complete 8-page PDF, majority + special concurrence) | `SOURCE_VERIFIED` (complete 21-page official PDF) |
| Disposition | Reversed and remanded; involuntary dismissal | Affirmed (foreclosure authorization and related orders) |

*Rodriguez* is not a “possession-timing” case in the way the first secondary summary described it. The bank’s witness put possession since 2007 — before the 2010 filing. What was missing was servicer authority in the record as of filing, and proof that the blank indorsement was on the note that day. *Greene* is not a decision that Florida’s filing-date standing rule is wrong. It is a decision about N.C. Gen. Stat. § 45-21.16(d) in a power-of-sale hearing.

The proof graph therefore connects the two intermediate propositions with a `DISTINGUISHED_BY` edge, not `NEGATED_BY`. Using `NEGATED_BY` would store an adverse-authority relation the opinions do not actually announce.

---

## Worked chain (flagship graph)

`build_promissory_note_enforcement_proof_graph()` in `services/legal_proof_graph.py` is the encoded form. Compressed to the layers this prototype actually distinguishes:

| Layer | What is stored | What it is not |
|---|---|---|
| Official / statutory authority | Va. Code Ann. § 8.3A-301 (person entitled to enforce); § 8.3A-308(b) (producing the instrument / proving entitlement). Florida’s Fla. Stat. §§ 673.3011, 671.201(21)(a) and North Carolina’s § 45-21.16(d) are identified in interpretive steps, not ingested as Virginia-style `StatuteSection` records. | Virginia text is not Florida law and not North Carolina procedure |
| Source metadata / hash | Manifests with SHA-256, retrieval URL, timestamp, `SOURCE_VERIFIED` | Hash ≠ subsequent history |
| Normalized definition | “Person entitled to enforce” from § 8.3A-301; holder-by-possession for a blank indorsement is the shared substantive idea | Definition ≠ the timing rule either court applied |
| Verified / stipulated fact | “The note is indorsed in blank, and the party produces the original in its possession” — `FactStatus.ASSUMED`, `TRUSTED_FOR_ANALYSIS` (stipulated pattern, not a docket finding) | Not a finding that any live party is a holder |
| Authored intermediate propositions | Florida: status/authority as of filing; North Carolina: production at the hearing sufficient | Not interchangeable “standing” labels |
| Interpretive step (contestable) | *Rodriguez*: McLean standing-at-filing + servicer-agency proof. *Greene*: Chapter 45 holder showing + UCC non-requirement of transfer chain | Author-written summaries of the court’s reasoning; not the opinions themselves |
| Conclusion | Who may enforce a blank-indorsed note **depends on jurisdiction and proceeding type**; the graph treats the divergence as procedural, not as a substantive split on holder-by-possession | Not a choice-of-law holding |
| Confidence | Weakest-link over supporting *authorities*, mapped `SOURCE_VERIFIED` → `LIKELY`. `CROSS_VERIFIED` is unused here (one complete read per opinion, not a second independent capture of the same text). | `LIKELY` is not “both holdings remain good law” |

The concurrence sits inside *Rodriguez*’s source record as labeled quoted language, not as `rule_text` on the `GoverningAuthorityNode` (that node uses majority language: standing to foreclose must be shown at filing).

---

## Four confidence dimensions, not one

`SOURCE_VERIFIED` collapsing into “we are confident about the law” is the failure mode this prototype is trying to make expensive. They are separate:

| Dimension | What this pair currently supports | What it does not |
|---|---|---|
| **Source authenticity** | Complete opinion PDFs read end-to-end; four capture errors corrected and left in the manifests | Authenticity of a 2015/2016 PDF is not a 2026 citator result |
| **Precedential status** | Author, concurrence, disposition, `hierarchy_level`, `binding_scope`, `override_mechanism` as author-filled fields describing encoded/original scope | No `CURRENTNESS_CHECKED` assignment. No search for later limitation, overruling, or intra-state conflict. `superseded: false` is a stored default. Neither opinion is asserted to remain controlling today. |
| **Jurisdictional authority** | Stored binding-scope text as encoded at ingestion: 4th DCA territorial; NC Court of Appeals statewide for this proceeding type — original scope, not a 2026 citator result | Does not decide whether a new forum would treat either opinion as persuasive, or which state’s law applies |
| **Applicability / inference** | Mapper matches a small fact pattern (jurisdiction, proceeding type, blank indorsement, possession at the relevant time, Florida servicer-without-authority flag) against these two encodings | Does not decide that a new client’s facts *are* those facts |

A source can be perfectly verified while a legal conclusion remains weak. The flagship conclusion’s `LIKELY` label follows from authority verification status, not from a currentness or choice-of-law engine.

---

## What the mapper actually does

`classify_precedent_conflict()` in `services/precedent_conflict_mapper.py` takes a `NewFactPattern` and the flagship graph. Known jurisdictions are the set `{"Florida", "North Carolina"}`. Known proceeding types are `JUDICIAL_FORECLOSURE_COMPLAINT`, `POWER_OF_SALE_HEARING`, and `UNDETERMINED_OR_HYBRID`.

Given those inputs, it can:

- say a blank-indorsed Florida judicial-complaint pattern with the servicer-without-authority flag on matches *Rodriguez*’s encoded distinguishing fact (`FACT_SENSITIVE_DISTINGUISHABLE`);
- say a blank-indorsed Florida judicial-complaint pattern with possession at filing and that flag off, or a blank-indorsed North Carolina power-of-sale pattern with possession at the hearing, matches the corresponding encoding closely enough for the internal classifier to emit `HIGH_CONFIDENCE_CONTROLLING_AUTHORITY`;
- say a note *not* indorsed in blank is not the fact pattern either court decided;
- say a known jurisdiction with the *other* proceeding type may not transfer cleanly;
- say an unknown jurisdiction is at most `PERSUASIVE_DISAGREEMENT`, or `GENUINE_UNRESOLVED_UNCERTAINTY` if the proceeding type matches neither encoded form.

`HIGH_CONFIDENCE_CONTROLLING_AUTHORITY` is an internal classifier label over those encoded features and supplied flags. It is not a citator result, not a currentness determination, and not a finding that *Rodriguez* or *Greene* remains controlling today. The function emits it when a known-jurisdiction pattern matches the encoded proceeding type, blank-indorsement, and possession flags (and, for Florida, when the servicer-without-authority flag is off). No contrary authority *inside this two-opinion graph* is retrieved. The engine does not search later cases, intra-state conflict, legislative amendment, or subsequent history.

The category name overstates that function. “High confidence” and “controlling authority” are not earned by a bounded flag match. The explanation strings in `precedent_conflict_mapper.py` still say, in present tense, that each opinion “is real, binding authority,” was “decided under the current statutory version,” and that “no unresolved subsequent history was found.” Those strings are a remaining code issue. They are not restated here as findings.

The mapper does **not** independently resolve choice of law, subsequent history, intra-state appellate conflict, unencoded procedural variants, or whether the supplied facts are true. A flag match is not a determination that a jurisdiction’s rule “applies” in the conflicts-of-law sense.

Scope remains: one doctrinal question, two opinions, UCC Article 3 / foreclosure-enforcement posture. Not legal advice.

---

## Strongest counterargument: these cases may not conflict at all

They may not. Different plaintiffs (servicer vs. claimed holder), different proceedings (judicial complaint vs. power-of-sale hearing), different proof objects (agency authority at filing vs. the physical note at the hearing), different times. Two courts can both apply “blank indorsement plus possession can make a holder” and reach opposite *dispositions* without disagreeing about that sentence.

The prototype is useful *because* of that possibility, not in spite of it. Flattening two captions into “split authority on standing” is the default move of a case summary. Distinguishing an apparent conflict from two different propositions is a legal-research operation: it tells the next reader which facts would have to be true before either opinion is even a candidate, and it refuses to manufacture a circuit split out of a posture mismatch.

What this document will not say: that “both outcomes are legitimate” as a normative conclusion, or that each observation about the other state’s procedure is “correct.” The supported claim is narrower. Once plaintiff capacity, proceeding type, and proof-moment are held constant, the holdings are not facially inconsistent. Whether either remains controlling in its own system is a subsequent-history question this prototype does not perform.

---

## Strongest remaining counterargument: the comparison ontology is hand-authored

The mapper does not independently discover which dimensions are legally material.

Humans encoded plaintiff capacity (servicer vs. claimed holder), proceeding type, proof object, proof moment, blank-indorsement, possession, and the Florida servicer-without-authority flag. `classify_precedent_conflict()` then matches supplied flags against those encodings. A different designer could have treated “standing” as a single dimension, omitted servicer capacity, or collapsed filing-date vs. hearing into a generic “timing” field. The `DISTINGUISHED_BY` conclusion can therefore be influenced by the comparison ontology chosen before any new fact pattern is classified.

Reducing that risk would require some combination of: additional ingested authority beyond these two opinions; alternative feature formulations tested against the same pair; counter-hypothesis testing (does a different ontology produce a `NEGATED_BY` relation the current one hides?); subsequent-history / currentness review; and human legal review of the encodings. None of those have been performed. This document does not treat the ontology as discovered by the engine or as settled.

---

## Reconstructable chain

- **Definition.** “Conflict” here means two holdings that cannot both be true of the same proposition. `DISTINGUISHED_BY` means the propositions are materially different. `SOURCE_VERIFIED` means the captured text matches the retrieved opinion.
- **Premise.** Speaker, opinion segment, proceeding type, and proof moment have to survive ingestion, or majority, concurrence, and paraphrase become interchangeable.
- **Observed fact.** A secondary summary attributed a timing sentence to the court; the official *Rodriguez* PDF places it in Conner, J.’s special concurrence. The pair differs in plaintiff capacity, proceeding, proof object, and proof moment. The graph stores a `DISTINGUISHED_BY` edge, not `NEGATED_BY`.
- **Proposition.** Different outcomes do not, without more, mean doctrinal conflict.
- **Inference.** Once those encoded dimensions are held constant, the holdings are not facially inconsistent. The mapper classifies a new pattern only against those encodings.
- **Counterexample / contradiction.** The first summary flattened the pair into a split. Remaining counters: (1) a different hand-authored ontology could hide or invent conflict; (2) neither opinion has a currentness / subsequent-history review, so present-tense “is binding” is not supported; (3) `HIGH_CONFIDENCE_CONTROLLING_AUTHORITY` names more than the classifier computes.
- **Conclusion.** Only as strong as the encodings and the two source-verified opinions: the prototype distinguishes an apparent split from two different questions. It does not adjudicate which rule applies, and it does not claim either opinion remains controlling today.
- **Residual uncertainty.** No citator pass. No additional authority. No alternative-ontology test. No human legal review of the feature set. `SOURCE_VERIFIED` is not legal confidence.
