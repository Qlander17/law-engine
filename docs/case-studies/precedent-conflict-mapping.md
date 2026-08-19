# Same Law, Different Outcome: How Law Engine Maps Authority, Facts, and Legal Uncertainty

*A case study of Law Engine's Precedent Conflict Mapper prototype — a real, bounded system for
explaining why two courts, applying the same underlying rule, can reach different results without
either one being wrong.*

## The problem this addresses

Legal disagreement across jurisdictions is usually presented one of two ways: as if courts are simply
inconsistent, or smoothed over as if one answer is obviously "the law." Both framings are dishonest
about how case law actually works. Courts frequently apply the *same* substantive rule and still reach
different results, because the rule interacts with different procedural postures, different statutory
generations, or different facts. Explaining *why* two outcomes can both be legitimate — not just that
they differ — is a genuinely hard, checkable problem, and it's the one this prototype targets.

## The flagship question

**Who is entitled to enforce a transferred promissory note?** This sits squarely inside UCC Article 3
(negotiable instruments) — a domain Law Engine already ingests from Virginia's own enacted statute
text (Va. Code Ann. § 8.3A-301, § 8.3A-104, § 8.3A-308). The doctrine itself is simple: a holder who
possesses a note indorsed to them, or indorsed in blank, is generally entitled to enforce it. The real
complexity — and the reason this question was chosen as the first flagship — is a well-documented,
real-world split that emerged from the 2008-era foreclosure litigation wave, over a question the bare
statutory text doesn't answer by itself: *when*, exactly, must holder status be established?

## Case A: Florida — standing must exist at filing

**Rodriguez v. Wells Fargo Bank, N.A.**, 178 So. 3d 62 (Fla. 4th DCA 2015).

- **Court**: District Court of Appeal of the State of Florida, Fourth District. Binding on trial
  courts within the Fourth District's own territorial jurisdiction; persuasive elsewhere in Florida
  and outside it.
- **Statutory basis**: Fla. Stat. § 673.3011 (person entitled to enforce) and § 671.201(21)(a)
  (holder) — Florida's own enactment of the same underlying UCC concept Virginia codifies at
  § 8.3A-301/8.3A-104.
- **Procedural posture**: a judicial foreclosure complaint, in which the plaintiff — suing as
  *servicer*, not in its own name as holder — had its standing challenged.
- **Holding**: a party suing as servicer must prove, as of the date the complaint was filed, that it
  had real authority (via a power of attorney or pooling-and-servicing agreement) to enforce the note
  on the true holder's behalf. Bare possession of the note by the servicer's principal, without that
  authority documented in the record, does not establish the servicer-plaintiff's own standing.
- **What controlled the outcome**: the timing gap between filing and the point the servicer's
  enforcement authority was actually documented, combined with the fact that the plaintiff sued as
  servicer rather than as holder in its own name.

## Case B: North Carolina — production at the hearing is sufficient

**Greene v. Trustee Services of Carolina, LLC**, 244 N.C. App. 583, 781 S.E.2d 664 (N.C. App. 2016).

- **Court**: Court of Appeals of North Carolina. Binding on North Carolina's own trial courts and
  Clerks of Superior Court presiding over Chapter 45 power-of-sale foreclosure hearings; persuasive
  only outside North Carolina.
- **Statutory basis**: N.C. Gen. Stat. § 45-21.16(d) (the state's power-of-sale foreclosure statute,
  which requires the foreclosing party to show it is the holder of the note) — applied alongside North
  Carolina's own UCC holder-by-possession concept, the same underlying doctrine as Virginia's
  § 8.3A-301/8.3A-104/8.3A-308.
- **Procedural posture**: a non-judicial power-of-sale foreclosure hearing, appealed de novo to
  superior court. The underlying debt had a real procedural history: a first foreclosure attempt in
  2010 was stayed by the borrowers' bankruptcy and the debt was later discharged, before the bank's
  second, actually-litigated 2013 foreclosure proceeding — the one this appeal reviews.
- **Holding**: for a note indorsed in blank, production of the original note *at the hearing itself*
  is sufficient to prove holder status. The UCC's own text imposes no separate requirement to also
  document the note's full chain of prior transfer.
- **What controlled the outcome**: the nature of the proceeding itself — a power-of-sale hearing, not
  a filed civil complaint whose standing is tested as of a commencement date.

## Why both outcomes are legitimate, not a contradiction

Both states apply the *same* substantive rule: indorsement-in-blank plus possession establishes
holder status, and holder status is what makes a party entitled to enforce. They differ on a real,
distinct, procedural question — *when* that status must be established, and in *what kind of
proceeding*. Florida's rule answers a judicial-standing question (what must be true as of the date a
civil complaint is filed). North Carolina's rule answers a different question entirely (what must be
shown at a non-judicial hearing that has no "filing" moment in the same sense). A Florida advocate
would say North Carolina's rule doesn't reject the "must prove possession" requirement — it just
locates the proof moment differently because the proceeding itself is structured differently. A North
Carolina advocate would say Florida's standing doctrine is a judicial-complaint concept that doesn't
map onto a power-of-sale hearing at all. Both observations are correct. That is precisely the shape of
disagreement this system exists to make legible — jurisdiction and procedural posture doing real
explanatory work, not courts arbitrarily disagreeing about the same question.

## How the sources were verified

Both opinions carry `VerificationStatus.SOURCE_VERIFIED` — the complete official opinion was
independently retrieved and read in full, not summarized by an AI or taken from a secondary source.
Rodriguez was retrieved via CourtListener's stored mirror of the official Fourth DCA opinion PDF,
after the court's own original URL was confirmed dead. Greene was retrieved by direct read of the
North Carolina Judicial Branch's own official appellate-opinions PDF server. That verification process
caught and corrected four real errors that an earlier, secondary-source-derived draft of this same
research had introduced: a truncated quote from Rodriguez's complaint, a Rodriguez holding quote
mis-attributed from a concurring opinion to the majority, one misquoted word in Greene ("superior"
court, not "trial" court), and omitted procedural history in Greene (the 2010 foreclosure attempt
stayed by bankruptcy, before the 2013 proceeding actually litigated). All four are disclosed, not
swept aside, in the underlying source manifests.

## The proof model behind the mapping

Law Engine's Legal Proof Graph represents this reasoning as an explicit chain — not free-text
explanation, but structured nodes and edges a program can traverse and check:

- **Definitions and premises** — what "holder," "indorsement in blank," and "person entitled to
  enforce" mean, grounded in the ingested statutory text.
- **Governing authority** — the specific statutory provisions and judicial holdings in play for a
  given jurisdiction.
- **Propositions and inferences** — the intermediate reasoning steps connecting authority to a
  conclusion (e.g., "this proceeding is a judicial foreclosure complaint" → "Florida's filing-date
  standing rule applies").
- **Verified facts** — the real, source-tracked facts each case turned on.
- **Distinctions** — the specific facts or procedural features that separate one authority's holding
  from another's, rather than treating "the cases disagree" as unexplained.
- **Confidence** — every conclusion carries an explicit confidence label reflecting the verification
  status of its weakest supporting authority, not the strongest. With both case-law authorities now
  `SOURCE_VERIFIED` (matching the statutory authorities' own status), the flagship conclusion's
  confidence is `LIKELY` — a real improvement over the `UNVERIFIED` label it carried before both cases
  were independently verified, but honestly short of `VERIFIED` or `CROSS_VERIFIED`, tiers reserved
  for authority that has also been independently cross-checked against a second primary source. A
  single, complete, directly-read official opinion is real primary-source confirmation — it is not a
  second, independent confirmation of the same text.

## What this prototype can conclude, and what it deliberately cannot

Given a new fact pattern, the mapper can determine which jurisdiction's rule applies (by matching the
new pattern's jurisdiction and procedural posture — judicial complaint vs. power-of-sale hearing — to
the closer of the two precedents), and can state, with the honest confidence level above, which
authority controls and why. It explicitly declines to guess for anything outside that real, narrow
scope: a jurisdiction using neither a Florida-style judicial complaint nor a North Carolina-style
power-of-sale hearing gets an honest "undetermined" classification, not a forced answer.

This is a bounded, early prototype — exactly one flagship legal question, exactly two real,
source-verified cases, from one narrow doctrinal corner of UCC Article 3. It is not a general-purpose
legal-research tool, and it cannot determine the answer to legal questions outside this specific,
tested scope. Nothing it outputs is legal advice, and no attorney-client relationship is created by
using it — consult a licensed attorney in the relevant jurisdiction before acting on any real
transaction. What it demonstrates is narrower and, we think, more useful as a proof of approach: that
"why do these two authorities disagree" can be represented as a real, checkable, source-verified
structure instead of an unexplained assertion — and that a system built this way can say, honestly,
both what it knows and the exact edges of what it doesn't.
