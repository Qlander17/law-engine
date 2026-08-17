# Zero-Trust Legal Epistemology

**Doctrine document, not a lesson.** This formalizes a Law Engine reasoning
discipline: the rule that governs how the system treats *any* claim made by
*any* actor, before that claim is surfaced to a learner. It does not resolve
any of the substantive claims discussed as examples below (e.g. mortgage
funding mechanics) — see `banking-mortgage-research-plan.md` for the
in-progress research on those. This document is about the *method*, not the
answer.

---

## 1. The core rule

Do not begin by assuming an institution, party, or conventional explanation
is correct. Do not begin by assuming it is corrupt or malicious either.

Both starting postures are the same error wearing different clothes: both
substitute a prior about the *speaker* for an examination of the *claim*.
"Banks wouldn't lie about this" and "banks always lie about this" are both
non-sequiturs — neither sentence contains any evidence about the specific
claim in front of the system. The only defensible starting posture is:
**the claim is unverified until independently checked**, regardless of who
said it, how official they sound, how long they've said it, or how
sympathetic or unsympathetic their position is.

This is a *symmetric* skepticism, not a cynical one. Zero-trust does not mean
"assume the worst" — assuming the worst is just corruption-first suspicion
with a better public reputation. It means "assume nothing," and then do the
work.

## 2. No actor receives an epistemic exemption

Every actor in a legal or financial dispute is a source of *claims*, not a
source of *truth*. Institutional size, credentials, formal role in a
proceeding, or moral sympathy do not change this. The table below applies
the rule explicitly to every actor category this system will encounter,
including itself.

| Actor | What exemption would look like (rejected) | What zero-trust actually requires |
|---|---|---|
| **Borrower** | Assuming a homeowner's account of what they signed or were told is automatically accurate because they are the sympathetic party in a foreclosure. | Their factual claims (what was disclosed, what was signed, what was said on a call) are checked against documents, timestamps, and other independent records, same as anyone else's. |
| **Lender** | Assuming a bank's standard account of its own accounting or servicing conduct is correct because it is the "official," institutional, mainstream position. | A lender's factual claims about origination, servicing, and accounting are checked against its own ledger entries, its own filings, and independent standards (e.g. the accounting mechanics described in Bank of England, McLeay/Radia/Thomas, *"Money creation in the modern economy,"* Quarterly Bulletin 2014 Q1), not accepted because the speaker is a regulated institution. |
| **Bank (as institution, distinct from "lender" in a specific transaction)** | Treating a bank's public-facing description of "how lending works" as definitionally true because banks are the domain experts. | Domain expertise is evidence the claim is *worth checking against primary sources* (statute, regulation, the bank's own filed accounting), not evidence the claim is *already correct*. |
| **Servicer** | Assuming a servicer's payment history or default notice is accurate because it is the document of record the servicer produced. | Servicer-produced records are treated as the servicer's factual *claim* about the account, cross-checked against the borrower's own payment records and, where available, the original creditor's records — servicers have an independently documented history of ledger errors in reported case law. |
| **Attorney** | Deferring to a lawyer's characterization of the law because they are a licensed professional. | An attorney's statement of law is a claim about AUTHORITY (see §3) that must resolve to an actual citation the system can independently locate and read — advocacy is a role, not a verification method. Opposing counsel's claims and the user's own attorney's claims are checked identically. |
| **Judge** | Treating a judicial opinion's factual findings or legal conclusions as unquestionably correct because a judge said so. | A judge's holding is the single strongest AUTHORITY signal this system recognizes for the jurisdiction and posture it was decided in — but the system must still record *what* was decided, on *what record*, at *what procedural stage* (e.g. motion to dismiss vs. full trial), and must not silently generalize a narrow holding into a broad one. Trial-court fact-finding is not immune from later reversal, and unpublished or superseded opinions are flagged as such. |
| **Regulator** | Assuming a regulatory FAQ, guidance letter, or press statement carries the force of the underlying statute/regulation it describes. | Regulator statements are classified as AUTHORITY only to the extent they cite the actual regulation or statute; a regulator's informal gloss is otherwise an INFERENCE or ALLEGATION about what the law means, not the law itself. |
| **Government (legislative/executive, distinct from courts and regulators)** | Assuming a government website's plain-language summary of a law is the law. | The enacted text (e.g. a state's Title 8.2/8.9A enactment, as already distinguished from `SourceLayer.MODEL` uniform text in this codebase — see §5) is the AUTHORITY; a government summary page is a convenience layer that must be checked against the actual enacted text before being relied on. |
| **Corporation (non-financial, e.g. a title company, a debt buyer)** | Assuming a corporate entity's records are accurate because they are a business record kept "in the ordinary course." | Business-record status is a hearsay-law concept about *admissibility*, not a truth-guarantee — the record is still a claim requiring independent corroboration where the dispute turns on its accuracy. |
| **Expert (retained or independent)** | Deferring to an expert's conclusion because of credentials or because they were "qualified as an expert" in a proceeding. | An expert's conclusion is an INFERENCE built on stated ASSUMPTIONS and cited FACTS — the system decomposes it into those parts and checks the inputs, rather than accepting the conclusion as a unit because a qualified person reached it. Being "qualified" establishes standing to offer an opinion in court, not the correctness of the opinion. |
| **Critic (of a conventional institution, theory, or actor)** | Assuming a critic's account is correct because they are challenging power, or because their critique is directionally sympathetic. | A critic's claims are checked with the same rigor as the claims they are criticizing — "this is corrupt" requires the same evidentiary chain as "this is normal and fine." |
| **Alternative-theory proponent** | Dismissing an unconventional claim (e.g. a fringe theory of mortgage funding) without independent verification, on the grounds that it is unconventional, associated with a discredited movement, or contradicts institutional consensus. | The claim is decomposed and checked exactly like a conventional claim — see the worked comparison in §4. Being unconventional is not evidence of falsity, just as being conventional is not evidence of truth. Where a real, converging pattern of judicial rejection exists (e.g. the "vapor money" theory — see `banking-mortgage-research-plan.md` Part 1.4, item 2), that is itself an AUTHORITY-grade finding that must be *cited*, not asserted as background knowledge. |
| **Law Engine itself** | Treating the system's own prior output, prior classification, or prior confidence label as settled once produced. | The system must be able to flag its own unverified outputs. Every claim the system has classified, scored, or surfaced carries its own `VerificationStatus`/`ConfidenceLabel` (§5) and is subject to the same re-examination as an external actor's claim if new evidence surfaces — including evidence that the system's own prior INFERENCE was wrong. A `ConfidenceLabel` the system assigned yesterday is not authority for a claim today; it is itself a claim, dated, and re-checkable. |

The common failure mode this table exists to prevent: treating *procedural
role* (party to litigation, holder of a credential, holder of public office,
holder of institutional legitimacy) as if it were *evidentiary weight*. Role
determines what kind of claim someone is positioned to make (a judge can
*hold*, a witness can *testify*, a bank can *produce a ledger*) — it does not
determine whether any particular claim they make is true.

## 3. Claim-classification taxonomy

Every claim the system processes — whether sourced from a party, a document,
an expert, a critic, or the system's own prior output — is classified into
exactly one of the following eight categories before any conclusion is built
on top of it. The categories are not a hierarchy of trustworthiness; they
are a description of *what kind of thing* the claim is, which then
determines what kind of verification is possible or required.

| Category | Definition | Real-world example |
|---|---|---|
| **FACT** | A proposition independently verifiable against a primary record (a document, a ledger entry, a recorded instrument, a timestamp) that both/all parties could in principle inspect. | The recorded deed of trust for a given parcel lists a specific origination date and original principal amount, verifiable by pulling the recorded instrument from the county recorder's office. |
| **AUTHORITY** | A proposition about what governing law, rule, or binding precedent says — verifiable by locating and reading the actual enacted text or opinion, not by trusting a description of it. | UCC § 3-301 (Cornell LII, `https://www.law.cornell.edu/ucc/3/3-301`) defines "person entitled to enforce" an instrument as including a non-owner holder — this is checkable by reading the section itself. |
| **INFERENCE** | A conclusion drawn from stated facts and/or authority using an explicit chain of reasoning, where the chain itself can be examined and challenged step by step. | From the FACT that a note was indorsed in blank and the AUTHORITY of UCC § 3-301, one can INFER that the current possessor is entitled to enforce the note — but this inference fails if a stated premise (e.g. actual possession) turns out false. |
| **ASSUMPTION** | An unstated or stated premise taken as given for purposes of an argument, not itself independently established. | A foreclosure timeline analysis that assumes the borrower received the required pre-acceleration notice by mail on the date the servicer's system logs it as "sent," without independent proof of mailing or receipt. |
| **ALLEGATION** | A factual assertion made by an interested party as part of advancing their position, not yet independently corroborated. | A borrower's complaint alleges that a loan-modification review was never actually performed despite the servicer's records showing a denial letter — this is an ALLEGATION until corroborated or rebutted by evidence beyond the party's own say-so. |
| **MOTIVE THEORY** | A claim about *why* an actor did something (intent, bad faith, conspiracy, profit motive) rather than *what* they did. | "The servicer delayed the modification review deliberately to run out the clock on foreclosure timelines" is a MOTIVE THEORY — distinct from the FACT that the review took 11 months, which is separately verifiable. |
| **DISPUTED FACT** | A factual proposition where the system has located genuinely conflicting primary evidence (not merely conflicting characterizations) and cannot currently resolve which account is correct. | The servicer's ledger shows a payment as "received late"; the borrower produces a bank statement and canceled-check record showing the payment cleared on time — both are primary records, and they conflict. |
| **UNKNOWN** | The system has not yet located evidence sufficient to classify the claim into any of the above categories — an honest placeholder, not a default toward belief or disbelief. | Whether a specific assignment of mortgage was recorded before or after a specific foreclosure filing, where no research into the actual county land records has yet been performed. |

A single narrative claim commonly decomposes into several of these at once —
e.g. "the bank defrauded the homeowner" bundles a MOTIVE THEORY ("defrauded"
implies intent) on top of one or more FACT or DISPUTED FACT claims (what
actually happened) and often an ASSUMPTION about what the bank knew and
when. The taxonomy's job is to force that decomposition before the system
lets the bundled claim stand or fall as a unit.

## 4. Adversarially testing a conventional claim and an unconventional claim, the same way

The method is identical regardless of which direction the claim leans
politically, institutionally, or emotionally. Neither a conventional claim
nor an unconventional one receives a presumption of correctness or of
falsity going in — both enter the pipeline as UNKNOWN and exit only after
the same four steps.

**Step 1 — Decompose.** Break the claim into its FACT/AUTHORITY/INFERENCE/
ASSUMPTION/ALLEGATION/MOTIVE THEORY components (§3). A bundled claim is not
tested as a unit.

**Step 2 — Locate primary authority or primary evidence for each component.**
For an AUTHORITY component, that means the actual statute, regulation, or
opinion — not a summary of it. For a FACT component, that means the actual
document, ledger, or record — not a restatement of it. "A source says this is
true" is not itself evidence; the source's *underlying* primary material is.

**Step 3 — Check the INFERENCE chain independently of whether the conclusion
is congenial.** Does each inferential step actually follow from the
component before it, or does it smuggle in an unstated ASSUMPTION?

**Step 4 — Assign `VerificationStatus`/`ConfidenceLabel` based on what was
actually found, not on priors about the claim's source.** See §5.

**Worked comparison — a bank's standard account vs. a fringe theory, both
about mortgage funding mechanics:**

- *Conventional claim:* "The bank simply lends out money it already has on
  deposit from other customers." Decomposed: this is an INFERENCE (a folk
  model of how lending works) resting on an ASSUMPTION about bank balance-
  sheet mechanics that is not, on inspection, how central-bank research
  describes loan origination. The AUTHORITY check here is the same Bank of
  England paper cited in `banking-mortgage-research-plan.md` Part 1.1
  (McLeay, Radia & Thomas 2014), which states that banks create a new
  deposit liability simultaneously with the new loan asset at origination —
  the "lending out existing deposits" folk model is not the mechanism that
  paper describes. The claim being the *conventional, popularly-assumed*
  account does not exempt it from being checked against the primary
  accounting-research source, and on that check, the folk version does not
  hold up as literally stated.
- *Unconventional claim:* "Because the bank created the deposit through
  accounting entries rather than transferring pre-existing funds, the
  borrower's obligation on the note is void — the bank 'lent nothing.'"
  Decomposed: the FACT premise (deposit creation happens at origination) is
  the *same* real accounting fact the conventional claim's correction rests
  on — `banking-mortgage-research-plan.md`'s own scope discipline (line 5)
  is built around keeping this fact separate from the legal-effect
  question. The INFERENCE step ("therefore the obligation is void") is
  where this claim actually stands or falls, and it is checked against the
  same class of AUTHORITY as any other claim about note enforceability:
  UCC § 3-303's definition of value/consideration, and the real, converging
  pattern of courts rejecting the "vapor money" theory on this exact
  inference (`banking-mortgage-research-plan.md` Part 1.4, item 2, and
  Part 2, row 2). The claim being *unconventional* did not exempt it from
  being checked, and did not entitle it to be dismissed without that check
  either — the AUTHORITY that ultimately weighs against it is real,
  citable, and specific to the inference, not a generic appeal to the
  theory's unpopularity.

Note what the two examples share: in both cases, the *popular summary* of
the claim (the folk "banks lend out deposits" model on one side, the folk
"banks lend nothing so the debt is void" model on the other) turns out to be
imprecise or wrong at the inference step, while the underlying FACT about
deposit creation is real and uncontested on both sides. Zero-trust treats
that as an ordinary, expected outcome of applying one method twice — not as
evidence that the method has a thumb on the scale, since it produced the
same kind of correction in both directions.

## 5. Mechanism: how this doctrine is actually implemented

This document is the doctrine; it is not the mechanism. The mechanism
already exists in `services/models.py` and this doctrine is implemented
*through* it, not alongside it:

- **`VerificationStatus`** (`services/models.py`) is the progression a
  source or claim moves through as it is actually checked — `DISCOVERED` →
  `RETRIEVED` → `SOURCE_VERIFIED` → `AUTHORITY_CLASSIFIED` →
  `CURRENTNESS_CHECKED` → `CROSS_VERIFIED` → `TRUSTED_FOR_ANALYSIS`, with
  `CONFLICT` and `UNKNOWN` as non-linear states. This is the field that
  answers "how much verification work has actually been done," independent
  of who the claim came from — the progression is identical whether the
  claim originated with a bank, a borrower, a critic, or the system itself.
  Per its own docstring, progression is not strictly linear (a government-
  site-sourced document can jump straight to `SOURCE_VERIFIED`) — but a
  status can only ever be *earned* by an actual retrieval/verification step
  taking place, never assigned because of who is asking or who is being
  described.
- **`ConfidenceLabel`** (`services/models.py`) is the caller-facing,
  coarse-grained label — `LIKELY`, `VERIFIED`, `UNVERIFIED`, `CONFLICTING` —
  that a user-facing surface is required to show, per that class's own
  docstring instruction that an inferred rule must never silently become a
  verified one. This is the field that prevents the "no epistemic
  exemptions" rule in §2 from being undermined at the last mile: even a
  claim about a sympathetic actor, an unsympathetic actor, or the system's
  own prior conclusion is shown with the label its actual verification
  state earns, not the label its narrative role would suggest.
- **`SourceLayer`** and **`AuthorityType`** (`services/models.py`) supply
  the orthogonal classification this doctrine's AUTHORITY category (§3)
  needs in practice — `SourceLayer` distinguishes uniform/model text from a
  specific jurisdiction's enactment from interpretive material (so the
  system never silently presents a state's enacted variation, or the
  ULC/ALI model text, as if it were universally-controlling "the law"), and
  `AuthorityType` distinguishes what *kind* of authority a source is
  (`STATUTE`, `CASE`, `CLAIM_ALTERNATIVE_THEORY`, etc.) independent of how
  verified it is — per that class's own docstring, a
  `CLAIM_ALTERNATIVE_THEORY` can be fully `SOURCE_VERIFIED` (the system
  correctly captured what the claim says) while never being `VERIFIED` as
  legally controlling. This is the concrete mechanism for §2's "alternative-
  theory proponent" row and §4's unconventional-claim example: the system
  can accurately and completely record what a fringe theory asserts without
  that recording implying the theory is authoritative.
- **`SourceManifest`** (`services/models.py`) is the record-level anchor
  that ties a `VerificationStatus` to an actual retrieved document (with
  `sha256_hash`, `retrieval_timestamp`, `official_source_url`) rather than
  to an unaudited assertion that verification happened — this is what makes
  Law Engine's own self-flagging (§2, "Law Engine itself") possible in
  practice: a claim without a `SourceManifest` behind it cannot be
  `SOURCE_VERIFIED` or better, no matter how the system itself phrased it.

This doctrine does not require new enum values or a new mechanism. It
requires that every actor-authored claim — including the system's own
output — actually be routed through the existing `VerificationStatus`/
`ConfidenceLabel`/`SourceLayer`/`AuthorityType`/`SourceManifest` machinery
before being surfaced, with no actor-specific shortcut past that routing.

## 6. Naming recommendation

Of the three candidate names, the recommendation is **"Zero-Trust Legal
Reasoning."**

Reasoning against the alternatives:

- **"Adversarial Epistemology"** is precise about §4's *method* (test both
  sides the same way, adversarially) but is silent about §2's core claim —
  that *no actor is exempted*, including sympathetic ones and the system
  itself. "Adversarial" also risks being read as endorsing a combative
  posture toward claims generally, when the actual doctrine is neutral, not
  combative — a FACT that checks out is simply confirmed, not "defeated."
- **"Forensic Legal Reasoning"** describes §4's rigor (careful,
  evidence-first, primary-source-driven) well, but "forensic" carries a
  strong connotation of *investigating wrongdoing* — it implies a target
  under suspicion, which cuts against §1's explicit rule that the system
  must not start by assuming corruption any more than it starts by
  assuming legitimacy. It is also the name already claimed by the
  companion document in this same folder
  (`forensic-transaction-reconstruction-method.md`) for a *different*
  concept (end-to-end transaction tracing), and reusing "forensic" for both
  would blur two distinct tools: one is a method for reconstructing what
  happened (transaction reconstruction), the other is a method for
  deciding what to believe about *any* claim, including claims that have
  nothing to do with reconstructing a transaction (e.g. "is this the
  correct reading of a statute").
- **"Zero-Trust Legal Reasoning"** borrows a term (zero-trust) that already
  has a precise, widely understood meaning in security engineering — never
  grant trust by default based on network location or role; verify every
  request independently, every time, regardless of source. That mapping is
  almost exact for this doctrine: never grant epistemic trust by default
  based on institutional position or role (§2); verify every claim
  independently (§3-4), every time, including requests/claims from the
  system's own prior output (§2, "Law Engine itself"; §5). It is also the
  name that most directly signals the doctrine's actual novelty relative to
  ordinary "check your sources" practice: ordinary source-checking still
  routinely exempts institutional or credentialed claims from scrutiny by
  default (an attorney's citation is trusted because they're an attorney,
  a bank statement is trusted because it's a business record) — zero-trust
  explicitly names the rejection of exactly that shortcut.

No better name was found; "Zero-Trust Legal Reasoning" is the recommendation.
