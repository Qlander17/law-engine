# Forensic Transaction Reconstruction Method

**Design document, not a lesson.** This designs a reusable method for
tracing a legal/economic transaction end to end, so that discrepancies
between what *should* have happened (per governing authority and the
parties' own documents) and what *actually* happened (per the observed
record) can be identified as fact questions — never as pre-packaged
conclusions about anyone's motive. The residential mortgage is used as the
worked example because it is the transaction type this codebase already has
real primary sources for; the method itself is general and is intended to
be reusable for other multi-party, multi-document, multi-ledger legal
disputes (a construction-lien dispute, a UCC Article 9 secured-transaction
default, a probate accounting dispute, etc.).

This document reuses and extends the real primary sources already found in
`banking-mortgage-research-plan.md` rather than re-researching them. Per
that document's own discipline, several of those sources are still at
search-snippet or secondary-report confidence, not directly-fetched-and-read
confidence — that caveat is carried forward here at each affected step
rather than silently upgraded.

---

## 1. Why end-to-end tracing, specifically

A mortgage dispute is rarely actually *about* the single document or single
event a party is pointing at (a missed payment, a robo-signed assignment, an
unclear payoff figure). It is about whether that one event is consistent
with everything upstream and downstream of it — the same loan's own
origination terms, the same servicer's own prior ledger entries, the same
note's own chain of holders. A method that only looks at the disputed event
in isolation cannot tell the difference between an isolated clerical error,
a systemic accounting problem, and a fully correct outcome that merely looks
surprising out of context. Tracing the *entire* transaction — from the
borrower's application through final distribution of sale proceeds — is
what makes that distinction possible, because it is what lets the system
compare an EXPECTED figure derived from the transaction's own governing
documents and authority against the OBSERVED figure from the actual record
(§4).

## 2. Per-step fields

For every step in the sequence, this method records the same nine fields,
so that steps are comparable to each other and gaps are visible as gaps
rather than silently skipped:

1. **Actor** — who takes the action at this step.
2. **Asset created/extinguished** — what asset comes into existence or is
   retired at this step, if any.
3. **Liability created/extinguished** — what liability comes into existence
   or is retired at this step, if any.
4. **Document** — the instrument or record that should exist to evidence
   this step.
5. **Ledger/accounting entry** — the bookkeeping entry, on whose books, that
   should exist, where relevant (not every step has one).
6. **Legal right** — what right this step creates or transfers.
7. **Legal obligation** — what obligation this step creates or transfers.
8. **Governing authority** — the real statute, case, or accounting standard
   that governs this step, cited where research actually found one; marked
   as an open gap where it did not.
9. **Evidence that should exist** — the concrete records a reconstruction
   would need to pull to confirm this step happened as described.
10. **Unresolved factual questions** — the specific, checkable questions
    this step leaves open (not motive questions — see §4's rule).

## 3. The sequence, worked for a residential mortgage

### 3.1 Application

- **Actor:** Borrower (applicant), loan originator/loan officer.
- **Asset created/extinguished:** None yet — no loan asset exists until
  underwriting approves and the note is executed.
- **Liability created/extinguished:** None yet.
- **Document:** Uniform Residential Loan Application (Fannie Mae/Freddie Mac
  Form 1003), income/asset verification documents, credit report
  authorization.
- **Ledger/accounting entry:** None — pre-transaction.
- **Legal right:** None created yet; the applicant has, at most, whatever
  rights arise under application-stage consumer-protection statutes (e.g.
  Equal Credit Opportunity Act, Truth in Lending Act disclosure timing
  requirements) — not researched in depth in this codebase yet, flagged as
  an open gap.
- **Legal obligation:** Applicant's obligation to provide accurate
  information; originator's disclosure obligations under TILA/RESPA
  (federal consumer-protection statutes — not yet ingested into this
  codebase; open gap, consistent with `banking-mortgage-research-plan.md`'s
  own finding that no state or federal consumer-protection statute has been
  ingested here).
- **Evidence that should exist:** The completed application, the
  originator's file notes, the credit pull record, initial disclosures with
  timestamps.
- **Unresolved factual questions:** Was the application the borrower
  actually submitted, or was it altered after submission (a real, litigated
  fact pattern in some origination-fraud disputes)? Were required initial
  disclosures actually provided within the statutory timing window?

### 3.2 Underwriting

- **Actor:** Underwriter (lender employee or delegated underwriter).
- **Asset created/extinguished:** None yet.
- **Liability created/extinguished:** None yet.
- **Document:** Underwriting approval/conditions memo, appraisal report,
  title commitment.
- **Ledger/accounting entry:** None yet on the lender's books (the loan is
  not yet an asset).
- **Legal right:** None new for the borrower; the lender's internal
  decision to extend credit is not itself a right or obligation running to
  the borrower until closing documents are executed.
- **Legal obligation:** None new.
- **Governing authority:** Investor/agency underwriting guidelines (e.g.
  Fannie Mae/Freddie Mac Selling Guide) where the loan is intended for
  sale — not a statute, but a real, checkable contractual standard;
  specific citation not researched in this codebase yet, open gap.
- **Evidence that should exist:** The underwriter's written conditions and
  sign-off, the appraisal, the title search/commitment showing the
  property's then-current title state (critical for later comparing to the
  eventual foreclosure-sale title chain).
- **Unresolved factual questions:** Were stated underwriting conditions
  actually satisfied before closing, or waived without documentation?

### 3.3 Note

- **Actor:** Borrower (as maker/issuer), lender (as original payee).
- **Asset created:** The note itself is the lender's asset — a negotiable
  instrument evidencing the borrower's promise to pay, per UCC § 3-104
  (definition of "negotiable instrument") — Cornell LII,
  `https://www.law.cornell.edu/ucc/3/3-104`, already cited in
  `banking-mortgage-research-plan.md` Part 1.2, item 2.
- **Liability created:** The borrower's payment obligation — this is the
  liability side of the same instrument that is the lender's asset.
- **Document:** The promissory note itself (original, "wet ink" or
  compliant e-note under UETA/E-SIGN).
- **Ledger/accounting entry:** Not yet — booked at origination/funding
  (§3.6), not at signature alone.
- **Legal right:** The lender's (or later, whoever is the "person entitled
  to enforce" under UCC § 3-301, Cornell LII,
  `https://www.law.cornell.edu/ucc/3/3-301`, already cited in
  `banking-mortgage-research-plan.md` Part 1.2, item 2) right to demand
  payment per the note's terms.
- **Legal obligation:** The borrower's (maker's) obligation to pay per the
  note's stated terms — UCC § 3-103/§ 3-104 define the maker as the one who
  signs the promise to pay, per `banking-mortgage-research-plan.md` Part
  1.4, item 1.
- **Governing authority:** UCC Article 3 (negotiable instruments) —
  explicitly **not yet ingested into this codebase**, per
  `banking-mortgage-research-plan.md` Part 3, item 1; the three sections
  above were confirmed via Cornell LII (model/uniform text, not any one
  state's enactment — the same `SourceLayer.MODEL` vs. `SourceLayer.
  ENACTMENT` distinction flagged in that document's Part 1.2, item 2 caveat
  applies here).
- **Evidence that should exist:** The original note, any indorsements on
  its face or attached allonge, a record of who has had physical possession
  of the original note at each point in time (critical for later "holder"
  analysis at foreclosure).
- **Unresolved factual questions:** Is the note produced in a later
  foreclosure the same instrument executed at closing (same terms, same
  indorsement chain), or has it been altered, lost, or replaced with a lost-
  note affidavit?

### 3.4 Deed of trust / mortgage

- **Actor:** Borrower (as trustor/mortgagor), lender or nominee (e.g. MERS,
  as beneficiary/mortgagee), trustee (deed-of-trust states only).
- **Asset created:** A security interest in the real property, held by the
  lender/beneficiary — a lien, not ownership of the property itself.
- **Liability created:** None new beyond the note's payment obligation; the
  security instrument does not itself create a new debt, it secures the
  existing note debt against the property.
- **Document:** The deed of trust or mortgage instrument, recorded in the
  county land records.
- **Ledger/accounting entry:** None directly (recording is a public-records
  act, not a bookkeeping entry), though the lender's loan-servicing system
  should reflect the lien's recording data (book/page or instrument
  number).
- **Legal right:** The lender/beneficiary's right to foreclose the lien on
  default, subject to the instrument's own terms and state foreclosure law.
- **Legal obligation:** The borrower's obligation not to impair the
  collateral (e.g. maintain insurance, pay property taxes) per the
  instrument's covenants.
- **Governing authority:** State real-property recording statutes; the
  judicial-vs-nonjudicial foreclosure distinction and which instrument type
  each state uses is per Nolo's chart (search-snippet-confirmed only, per
  `banking-mortgage-research-plan.md` Part 1.3, item 1) and Cornell LII Wex,
  *"non-judicial foreclosure,"* `https://www.law.cornell.edu/wex/non-judicial_foreclosure`
  (found but not yet directly fetched per that same entry).
- **Evidence that should exist:** The recorded instrument (with recording
  stamp/instrument number), the county land-records chain of title from
  that recording forward.
- **Unresolved factual questions:** Was the instrument recorded in the
  correct county, promptly, and does the recorded copy match the executed
  copy (a real, litigated fact pattern — e.g. MERS-related standing
  disputes; see Culhane below).

### 3.5 Execution/signature

- **Actor:** Borrower, notary (or equivalent witnessing officer), closing
  agent/settlement agent.
- **Asset/liability created/extinguished:** None new beyond what §§3.3-3.4
  already created — execution is what makes those instruments legally
  operative, not a separate substantive step.
- **Document:** Signed note, signed deed of trust/mortgage, closing
  disclosure/settlement statement, notary acknowledgment.
- **Ledger/accounting entry:** None yet.
- **Legal right/obligation:** Formalizes (does not newly create) the rights
  and obligations from §§3.3-3.4 — a note signed but never delivered, for
  example, raises a real question about whether the obligation ever became
  effective, which is why execution is tracked as its own step distinct
  from drafting.
- **Governing authority:** State notary/acknowledgment statutes; UETA/
  E-SIGN for electronic execution — not researched in this codebase yet,
  open gap.
- **Evidence that should exist:** The signed originals, notary journal
  entry, closing agent's file, borrower's own copy received at closing
  (useful for comparing against what the lender/servicer later produces).
- **Unresolved factual questions:** Do all copies in circulation (borrower's,
  lender's, any later-produced foreclosure copy) match exactly? Was the
  notarization contemporaneous with the actual signing (a real, litigated
  robo-signing fact pattern in post-2008 foreclosure cases)?

### 3.6 Origination/funding

- **Actor:** Lender (originating bank or non-bank originator with a
  funding-line relationship to a bank).
- **Asset created:** The loan receivable, booked on the originating
  lender's balance sheet.
- **Liability created:** If the originator is a depository bank funding
  from its own balance sheet: a new deposit liability to the borrower (or
  to the party the funds are disbursed to, e.g. the seller/title company),
  created simultaneously with the loan asset — this is the real, mainstream
  accounting mechanic described in Bank of England, McLeay/Radia/Thomas,
  *"Money creation in the modern economy,"* Quarterly Bulletin 2014 Q1,
  already cited in `banking-mortgage-research-plan.md` Part 1.1, item 1
  (note that document's own caveat: the paper itself was never successfully
  directly fetched — HTTP 403 — so its content here is still at
  search-snippet confidence, per that document's Part 3, item 4). If the
  originator is a non-bank lender, funding instead draws down an existing
  warehouse line of credit — a different mechanic not yet researched here,
  open gap.
- **Document:** Closing disclosure/settlement statement showing the
  disbursement; wire transfer or disbursement instructions.
- **Ledger/accounting entry:** Lender debits loan-receivable asset, credits
  either a deposit liability (bank-funded, per the BoE mechanic above) or a
  warehouse-line liability (non-bank-funded).
- **Legal right:** The lender's right to receive repayment per the note.
- **Legal obligation:** The lender's obligation to disburse the agreed loan
  amount per the closing disclosure.
- **Governing authority:** The BoE paper above for the accounting mechanic
  (still search-snippet confidence); TILA/RESPA for disbursement-disclosure
  accuracy (not yet ingested here, open gap). **Scope discipline, carried
  forward from `banking-mortgage-research-plan.md` line 5:** the accounting
  fact of how funding is booked is a separate question from whether that
  fact changes the borrower's obligation or the note's enforceability — see
  `zero-trust-legal-epistemology.md` §4 for the worked example of how this
  exact claim is tested without a presumption either way.
- **Evidence that should exist:** The lender's general-ledger entries at
  origination (asset and offsetting liability), the wire/disbursement
  record, the closing disclosure's stated disbursement amount.
- **Unresolved factual questions:** Does the disbursed amount match the
  note's stated principal? Does the lender's internal ledger entry for this
  loan actually exist and match the closing disclosure (this is a real,
  checkable question distinct from the abstract "how does bank funding
  work" question — see §4).

### 3.7 Bank ledger entries

- **Actor:** The funding bank's accounting system/back office.
- **Asset/liability created:** As in §3.6 — this step is the same
  origination-funding event viewed from the ledger side rather than the
  transaction side, tracked separately here because the *ledger record
  itself* (not just the fact that funding happened) is a distinct piece of
  evidence a reconstruction needs.
- **Document:** General ledger extract, trial balance entries for the
  relevant account codes.
- **Ledger/accounting entry:** The actual debit/credit pair for this specific
  loan, ideally traceable to a specific general-ledger transaction ID and
  timestamp.
- **Legal right/obligation:** None new — this step evidences §3.6's rights/
  obligations rather than creating new ones.
- **Governing authority:** GAAP/bank regulatory accounting standards for
  loan origination — not researched in this codebase yet; the BoE paper
  describes the mechanic in general terms but is not itself an accounting
  standard. Open gap, and explicitly flagged in
  `banking-mortgage-research-plan.md` Part 1.1, items 3-4 as unresearched
  (how principal repayment and interest are subsequently booked, and the
  bank's broader funding structure beyond deposits).
- **Evidence that should exist:** Actual general-ledger printouts or
  extracts for this specific loan's origination entries — not a policy
  description of how origination *generally* works, but the bank's *actual*
  entry for *this* loan.
- **Unresolved factual questions:** Does a real, discoverable ledger entry
  for this specific loan exist and match the disbursed amount? (This is
  usually the single most consequential unresolved question in a
  "the lender lent nothing" dispute — see §4.)

### 3.8 Deposit creation

- **Actor:** The funding bank (bank-funded originations only).
- **Asset/liability:** Already covered in §§3.6-3.7 as the liability side of
  origination — tracked here as its own step because deposit creation is
  the specific mechanic several popular claims turn on (per
  `banking-mortgage-research-plan.md` Part 1.4, items 1-2, 4-5), and a
  reconstruction should be able to point to exactly where in the sequence
  this fact lives rather than leaving it implicit inside "funding."
- **Document:** Same as §3.6-3.7.
- **Ledger/accounting entry:** The specific deposit-liability credit entry,
  and — critically for tracing what happens next — the record of that
  deposit being drawn down/disbursed to the seller, title company, or other
  payee at closing (a deposit created and then immediately disbursed is a
  different fact pattern from a deposit created and left sitting, and a
  reconstruction should trace which one actually occurred).
- **Legal right/obligation:** None new.
- **Governing authority:** Same BoE source as §3.6, same confidence caveat.
- **Evidence that should exist:** The deposit account ledger showing
  creation and immediate disbursement, tied to the same transaction ID as
  the loan-asset entry.
- **Unresolved factual questions:** Same as §3.7 — plus, where the deposit
  is disbursed to a third party (seller/title company) rather than held for
  the borrower, does that disbursement record match the closing
  disclosure's stated payees and amounts exactly?

### 3.9 Payment/settlement

- **Actor:** Title/settlement agent, seller (purchase-money mortgages),
  payoff lender (refinance transactions).
- **Asset created/extinguished:** For a purchase: seller's asset (the
  property) is extinguished as seller's asset and the funds asset is
  created for the seller. For a refinance: the old lender's loan-receivable
  asset is extinguished (paid off) and the new lender's loan-receivable
  asset is created.
- **Liability created/extinguished:** For a refinance: the borrower's old
  payment obligation is extinguished, the new one (§3.3) is already in
  place.
- **Document:** Settlement statement, payoff statement (refinance), wire
  confirmations to each payee.
- **Ledger/accounting entry:** Each payee's receipt of funds, on their own
  books.
- **Legal right/obligation:** Seller's right to sale proceeds; old lender's
  (refinance) right to payoff funds and corresponding obligation to release
  its lien on receipt.
- **Governing authority:** State settlement/escrow law; RESPA for
  settlement-statement accuracy — not yet ingested, open gap.
- **Evidence that should exist:** Wire confirmations, the settlement
  statement reconciling every dollar in and out, the old lender's lien
  release (refinance).
- **Unresolved factual questions:** Did every payee identified on the
  settlement statement actually receive the stated amount? Was the old
  lien actually released (refinance), and when, relative to when it should
  have been?

### 3.10 Property conveyance

- **Actor:** Seller (grantor), buyer/borrower (grantee) — purchase
  transactions only; not applicable to a refinance, which is flagged here
  as a real branch point the sequence must accommodate rather than force
  into a single linear path.
- **Asset created/extinguished:** Property ownership transfers from seller
  to buyer.
- **Liability created/extinguished:** None new beyond §§3.3-3.4.
- **Document:** The deed (warranty deed, grant deed, etc., per state
  practice).
- **Ledger/accounting entry:** Not applicable to real property in the same
  sense as a financial asset, though title insurers and closing agents
  maintain their own transaction records.
- **Legal right:** Buyer's fee-simple (or other conveyed estate) ownership,
  subject to the lien created in §3.4.
- **Legal obligation:** Seller's warranty obligations per the deed type.
- **Governing authority:** State real-property conveyance statutes — not
  yet ingested, open gap.
- **Evidence that should exist:** The recorded deed, title insurance
  policy, the title company's chain-of-title search.
- **Unresolved factual questions:** Does the recorded deed match the
  settlement statement's stated parties and legal description exactly?

### 3.11 Assignment

- **Actor:** Original lender/beneficiary (assignor), acquiring party
  (assignee) — e.g. a subsequent purchaser of the loan, or a securitization
  trust (§3.12).
- **Asset transferred:** The note (via negotiation/indorsement under UCC
  Article 3) and, separately, the mortgage/deed of trust security interest
  (via a written assignment instrument, recorded in the county land
  records) — these are two legally distinct transfers, and whether they
  actually traveled together is a real, litigated question (see below).
- **Liability:** None new; the borrower's obligation is unchanged by who
  holds it.
- **Document:** The assignment of mortgage/deed of trust; the note's
  indorsement or allonge.
- **Ledger/accounting entry:** The transferor's books remove the loan
  asset; the transferee's books add it (at whatever price/terms the
  transfer agreement specifies) — a distinct, checkable pair of entries a
  reconstruction should be able to compare against the recorded assignment
  date.
- **Legal right:** The assignee's right to enforce, contingent on actually
  qualifying as a "person entitled to enforce" under UCC § 3-301 (Cornell
  LII, cited above) — possession/indorsement of the note and a valid
  assignment of the mortgage are analytically separate requirements.
- **Legal obligation:** None new for the borrower.
- **Governing authority:** UCC Article 3 transfer/negotiation provisions
  (§§ 3-201 et seq. — **not yet ingested**, per
  `banking-mortgage-research-plan.md` Part 3, item 1); real case law on
  standing to challenge an assignment: ***Culhane v. Aurora Loan Services of
  Nebraska*, 708 F.3d 282 (1st Cir. 2013)** — confirmed via `WebSearch`
  (FindLaw and Massachusetts Real Estate Law Blog independently identify
  the same citation and holding: a mortgagor has standing to challenge a
  mortgage assignment even though not a party to it, in the MERS/
  securitization context), per `banking-mortgage-research-plan.md` Part
  1.3, item 3 — full text not yet independently pulled by this codebase, so
  this remains at the same confidence level that document assigned it
  (real and citable, not yet primary-source-confirmed by direct fetch).
  Also real but with citation/confirmation gaps carried forward unchanged
  from that same document: *U.S. Bank, N.A. v. Ibanez* (Massachusetts;
  citation not yet pinned down), and the *Glaski*/*Yvanova* (California)
  line on borrower standing to challenge a void assignment.
- **Evidence that should exist:** The recorded assignment instrument(s),
  the note's physical indorsement chain, the transfer agreement between
  assignor and assignee, both parties' ledger entries for the transfer.
- **Unresolved factual questions:** Does the recorded assignment's stated
  date precede or postdate the securitization trust's own closing date
  (§3.12), if any — a real, litigated fact pattern distinct from the
  general theory that assignment/securitization defeats enforceability,
  which `banking-mortgage-research-plan.md` Part 1.4, item 6 already flags
  as jurisdiction-dependent rather than resolvable in the abstract.

### 3.12 Securitization (if applicable)

- **Actor:** Depositor, sponsor, trustee of a securitization trust,
  certificate holders.
- **Asset created:** Mortgage-backed certificates issued to investors,
  backed by a pool of loans (including, potentially, this one) transferred
  into the trust.
- **Liability created:** The trust's obligation to pass through payments to
  certificate holders per the pooling and servicing agreement (PSA).
- **Document:** The PSA, the mortgage loan schedule (identifying which
  specific loans are in the pool), the trust's SEC filings (if publicly
  registered).
- **Ledger/accounting entry:** The trust's books reflect the pooled loans
  as assets; the originator/sponsor's books remove them (a "true sale" for
  accounting/bankruptcy-remoteness purposes is itself a real, checkable
  legal question, not an assumption).
- **Legal right:** Certificate holders' right to pass-through payments per
  the PSA's waterfall provisions; the trustee's right to act on the trust's
  behalf per the PSA and the trust's governing state trust law.
- **Legal obligation:** The trust/trustee's obligation to service or
  arrange servicing per the PSA.
- **Governing authority:** The specific PSA (a contract, not a statute —
  terms vary trust to trust); state trust law; for standing/enforceability
  disputes, the same *Culhane*/*Ibanez*/*Glaski*/*Yvanova* line as §3.11.
  Not independently researched further in this document — this step
  remains exactly where `banking-mortgage-research-plan.md` left it.
- **Evidence that should exist:** The PSA, the mortgage loan schedule
  showing this specific loan by loan number, the trust's SEC filings, the
  actual transfer documents moving the loan from originator to depositor to
  trust (a multi-step chain, each link of which is separately checkable).
- **Unresolved factual questions:** Was this specific loan actually
  transferred into the trust by the PSA's own cutoff date, with the
  documentation the PSA itself requires? This is the fact question
  underlying the general "securitization destroys enforceability" theory,
  and per `banking-mortgage-research-plan.md` Part 1.4, item 6, real courts
  have distinguished a *specific, documented defect* in this chain (which
  can support a claim) from a *generic* securitization-alone theory (which
  most courts have rejected) — the reconstruction method's job is to
  determine which fact pattern actually exists for a given loan, not to
  assume either one going in.

### 3.13 Servicing

- **Actor:** Loan servicer (may or may not be the note holder/trust
  itself).
- **Asset/liability:** None new — servicing is an agency function, not an
  asset transfer, though the servicing right itself (the right to collect
  servicing fees) is a separately tradeable asset not otherwise traced in
  this document.
- **Document:** The servicing agreement (between servicer and note
  holder/trust), the borrower-facing servicing records (payment history,
  escrow analysis, correspondence log).
- **Ledger/accounting entry:** The servicer's own sub-ledger for this loan
  (distinct from the note holder's ownership-level books) — this is the
  record most mortgage disputes actually turn on, since it is what the
  servicer produces as "the" payment history.
- **Legal right:** The servicer's right (as agent) to collect payments and
  communicate with the borrower on the holder's behalf.
- **Legal obligation:** The servicer's obligations under RESPA's servicing
  rules (e.g. error-resolution, loss-mitigation procedures) — not yet
  ingested into this codebase, open gap.
- **Governing authority:** RESPA/Regulation X servicing rules — open gap,
  not yet researched here.
- **Evidence that should exist:** The complete servicing transaction
  history (not a summary letter, the underlying transaction-level ledger),
  the servicing agreement, correspondence logs, escrow analyses.
- **Unresolved factual questions:** Does the servicer's ledger reconcile to
  the borrower's own payment records dollar-for-dollar? Has servicing been
  transferred between servicers, and if so, did the transferee's opening
  balance match the transferor's closing balance exactly?

### 3.14 Principal payments

- **Actor:** Borrower (payor), servicer (collector), note holder (ultimate
  recipient).
- **Asset extinguished:** A portion of the loan-receivable asset, reduced
  by the principal-payment amount, on the note holder's books.
- **Liability extinguished:** A corresponding portion of the borrower's
  payment obligation.
- **Document:** Payment records, monthly statements, amortization
  schedule.
- **Ledger/accounting entry:** Debit to cash/deposit, credit to loan-
  receivable asset (reducing it) — this is the specific bookkeeping
  question `banking-mortgage-research-plan.md` Part 1.1, item 3 flags as an
  **open, unresearched gap**: no source on how principal repayment is
  booked (as opposed to origination) was found in that run, and none is
  supplied here either — carried forward, not filled in.
- **Legal right/obligation:** Reduces, does not create, the rights/
  obligations from §3.3.
- **Governing authority:** Open gap, same as above.
- **Evidence that should exist:** The amortization schedule compared
  against actual posted payments, principal-balance history over time.
- **Unresolved factual questions:** Does the claim "principal repayment is
  pure lender profit" (`banking-mortgage-research-plan.md` Part 1.4, item
  3) hold up once the actual booking mechanic is researched? This document
  does not resolve that — it remains exactly the open gap the prior
  document identified.

### 3.15 Interest payments

- **Actor:** Borrower (payor), servicer (collector), note holder (ultimate
  recipient).
- **Asset created:** Interest income, recognized as revenue by the note
  holder — distinct from principal, which reduces an existing asset rather
  than creating income.
- **Liability:** None new.
- **Document:** Same payment records as §3.14.
- **Ledger/accounting entry:** Debit to cash/deposit, credit to interest-
  income revenue account.
- **Legal right/obligation:** The lender's right to interest per the note's
  stated rate; this is where UCC § 3-303's value/consideration definition
  (Cornell LII, `https://www.law.cornell.edu/ucc/3/3-303`, cited in
  `banking-mortgage-research-plan.md` Part 1.2, item 2 and Part 1.4, item
  4) bears directly on the "interest lacks consideration" claim — that
  section was captured via search snippet only in the prior research run,
  not yet directly fetched and quoted verbatim, a confidence gap carried
  forward here rather than resolved.
- **Governing authority:** UCC § 3-303 (as above, same confidence caveat);
  general contract-law consideration doctrine — not separately researched.
- **Evidence that should exist:** Interest-income ledger entries matching
  the note's stated rate applied to the outstanding principal balance over
  time.
- **Unresolved factual questions:** Does the actual interest charged match
  the note's stated rate and the amortization schedule at every payment,
  or are there unexplained rate or fee discrepancies?

### 3.16 Default

- **Actor:** Borrower (in default), servicer (declares/records the
  default).
- **Asset/liability:** No new asset/liability yet — default is a status
  change (the borrower is now in breach), not itself a transfer.
- **Document:** Notice of default, breach letter (as required by the note/
  deed of trust and, in many states, by statute before acceleration).
- **Ledger/accounting entry:** The servicer's records reclassify the loan
  as delinquent/in default; possible loan-loss reserve entries on the note
  holder's books — accounting-standard specifics not researched here, open
  gap.
- **Legal right:** The lender/servicer's right to pursue remedies per the
  note/deed of trust's default provisions, once any required cure-period
  notice has actually been given.
- **Legal obligation:** The lender/servicer's obligation to provide the
  cure notice/right-to-cure period the instrument and state law require
  before proceeding further.
- **Governing authority:** State pre-foreclosure notice statutes — not yet
  ingested, open gap; the deed of trust/mortgage's own default-notice
  clause (§3.4) is itself a real, checkable contractual source even before
  a statute is identified.
- **Evidence that should exist:** Proof the notice was actually sent (and,
  where required, actually received) on the date claimed, matching the
  instrument's and any applicable statute's required content and timing.
- **Unresolved factual questions:** Was the notice sent to the correct
  address, with the correct content, within the required timing — a
  frequently fact-disputed step in real foreclosure litigation.

### 3.17 Acceleration

- **Actor:** Lender/servicer/note holder (declares acceleration).
- **Asset/liability:** The entire remaining principal balance becomes
  immediately due — a status change to the existing asset/liability, not a
  new one.
- **Document:** Notice of acceleration/intent to foreclose.
- **Ledger/accounting entry:** The full balance is reclassified as due, and
  interest accrual treatment may change per the note's terms — specifics
  not researched here, open gap.
- **Legal right:** The lender's right to demand the full balance, per the
  note/deed of trust's acceleration clause and, where applicable, state
  law's own requirements for a valid acceleration.
- **Legal obligation:** Continued obligation to provide any state-required
  notice before or with acceleration.
- **Governing authority:** State foreclosure-initiation statutes — not yet
  ingested, open gap; the instrument's own acceleration clause is again a
  real, immediately-checkable contractual source.
- **Evidence that should exist:** The acceleration notice, proof of proper
  service, confirmation that any state-required cure period actually
  elapsed first.
- **Unresolved factual questions:** Did acceleration follow, rather than
  precede or coincide improperly with, the required default-notice cure
  period?

### 3.18 Foreclosure

- **Actor:** Lender/note holder/servicer (initiates); court (judicial-
  foreclosure states) or trustee (non-judicial/power-of-sale states); the
  which-track distinction is a real, state-by-state fact per Nolo's chart,
  search-snippet-confirmed in `banking-mortgage-research-plan.md` Part 1.3,
  item 1, and Cornell LII Wex's non-judicial-foreclosure definition (found,
  not yet directly fetched, same entry).
- **Asset/liability:** None new yet — foreclosure is the process, not the
  transfer; the transfer happens at sale (§3.19).
- **Document:** Complaint/petition (judicial) or notice of trustee's sale
  (non-judicial); proof of standing to foreclose (possession of the
  original note and/or a valid, recorded assignment — the same §3.11
  question surfacing again at the point it actually matters legally).
- **Ledger/accounting entry:** Legal/foreclosure-cost accrual on the note
  holder's or servicer's books (relevant later at §3.21's cost accounting).
- **Legal right:** The foreclosing party's right to sell the property to
  satisfy the debt, contingent on actually having standing (a real,
  litigated threshold question — see *Culhane*, §3.11).
- **Legal obligation:** Procedural obligations specific to judicial vs.
  non-judicial process (court filings and service, or statutory
  notice/publication requirements, respectively) — state-specific, not
  fully ingested here.
- **Governing authority:** State foreclosure procedure statutes (judicial
  or non-judicial per the state) — not yet ingested; NCLC's *"Survey of
  State Foreclosure Laws,"* `https://www.nclc.org/wp-content/uploads/2022/09/survey-foreclosure-card.pdf`,
  cited in `banking-mortgage-research-plan.md` Part 1.3, item 2, is the
  strongest starting point already identified for the state-variation
  research this would require.
- **Evidence that should exist:** The complaint or notice of sale, proof of
  standing (note possession/indorsement chain and recorded assignment
  chain — §3.11), proof of proper notice/service to the borrower and any
  junior lienholders (relevant at §3.22).
- **Unresolved factual questions:** Did the party foreclosing actually hold
  standing at the moment it initiated foreclosure (not merely by the time
  of sale)? Were all legally required parties (junior lienholders,
  occupants) properly notified?

### 3.19 Sale

- **Actor:** Trustee or sheriff/court officer (conducts the sale); winning
  bidder (often the foreclosing lender itself, via a credit bid).
- **Asset transferred:** The property, from borrower to winning bidder.
- **Liability extinguished:** The note obligation, to the extent the sale
  proceeds are applied against it (§3.21 traces exactly how much).
- **Document:** Trustee's deed or sheriff's deed/certificate of sale;
  auction/sale record (bid amounts, winning bidder).
- **Ledger/accounting entry:** The note holder's books remove the loan
  asset and record either a credit-bid "purchase" of the property as a new
  (real-estate-owned) asset, or cash proceeds if a third party outbid the
  lender.
- **Legal right:** The winning bidder's ownership right, subject to any
  post-sale redemption right the state provides.
- **Legal obligation:** The obligation to apply sale proceeds per the
  statutory/contractual priority order (§3.21-3.23).
- **Governing authority:** State foreclosure-sale statutes; the same NCLC
  survey as §3.18.
- **Evidence that should exist:** The sale record (all bids, not just the
  winning one — relevant to whether the price was fair-market-value, which
  matters for deficiency calculations in ~20 states per AllLaw/Nolo,
  `https://www.alllaw.com/articles/nolo/foreclosure/anti-deficiency-laws.html`,
  cited in `banking-mortgage-research-plan.md` Part 1.3, item 2), the
  trustee's/sheriff's deed.
- **Unresolved factual questions:** Was the sale properly noticed and
  conducted per statute? Was the winning bid a fair-market-value bid or a
  nominal credit bid, and does that distinction matter in this state's
  deficiency-calculation rule?

### 3.20 Payoff accounting

- **Actor:** Servicer/note holder (calculates and applies proceeds).
- **Asset/liability:** The note-holder's loan-receivable asset is formally
  closed out; the borrower's payment obligation is resolved (in full,
  partially, or with a remaining deficiency — §3.23).
- **Document:** The payoff statement/final accounting.
- **Ledger/accounting entry:** Sale proceeds applied first to the
  outstanding principal, then per the note's/state's specified order to
  accrued interest, fees, and costs — the specific order is itself a real,
  checkable contractual and/or statutory question, not assumed.
- **Legal right:** The homeowner's right to any surplus after the debt and
  authorized costs are satisfied — the general rule confirmed across
  multiple sources in `banking-mortgage-research-plan.md` Part 1.3, item 2,
  and reinforced by the equity-belongs-to-the-owner principle in **Tyler v.
  Hennepin County**, 598 U.S. 631 (2023) (tax-foreclosure-specific, not
  mortgage-foreclosure law, per that document's own explicit caveat — cited
  here for the same limited purpose that document cited it for: general,
  real, current Supreme Court authority for the underlying principle that
  surplus equity belongs to the homeowner, not for a mortgage-specific
  holding).
- **Legal obligation:** The note holder's obligation to account accurately
  and to remit any surplus.
- **Governing authority:** State surplus-funds statutes, per NCLC's survey
  above.
- **Evidence that should exist:** The full payoff accounting, itemized by
  category (principal, interest, costs — §3.21), reconciled against the
  actual sale proceeds figure.
- **Unresolved factual questions:** Does the itemized accounting actually
  reconcile — do the stated categories sum to the sale proceeds, with
  nothing unexplained? This is the central question §4's discrepancy-
  detection design exists to formalize.

### 3.21 Costs

- **Actor:** Note holder/servicer (incurs and claims costs); court (in
  judicial states, approves fee awards).
- **Asset/liability:** Foreclosure-related costs (attorney's fees, trustee's
  fees, publication/service costs, property preservation costs) are claimed
  against sale proceeds, reducing what remains for principal/interest or
  for surplus.
- **Document:** Itemized cost statements, attorney fee affidavits/invoices,
  court fee orders (judicial states).
- **Ledger/accounting entry:** Cost entries on the note holder's or
  servicer's books, and in the final payoff accounting (§3.20).
- **Legal right:** The note holder's contractual and/or statutory right to
  recover *reasonable, actually incurred* costs — not an unlimited right;
  "reasonable" and "actually incurred" are themselves the checkable
  standard.
- **Legal obligation:** The obligation not to claim costs beyond what was
  actually incurred or beyond what the instrument/statute authorizes.
- **Governing authority:** The deed of trust/mortgage's own fee provisions;
  state statutes/court rules on recoverable foreclosure costs — not yet
  ingested here, open gap.
- **Evidence that should exist:** Actual invoices/receipts for every
  claimed cost, not a summary total.
- **Unresolved factual questions:** Does every claimed cost trace to an
  actual, reasonable, incurred expense, or are some costs duplicated,
  estimated, or unsupported? Junk-fee and duplicate-fee disputes are a real,
  litigated fact pattern this step is specifically designed to surface.

### 3.22 Junior liens

- **Actor:** Junior lienholders (second mortgages, HOA liens, judgment
  liens, tax liens depending on state priority rules).
- **Asset extinguished:** Junior liens are typically extinguished by a
  senior foreclosure sale (subject to real state-specific and lien-type-
  specific exceptions — e.g. some tax liens survive).
- **Liability:** The junior lienholder's secured claim converts to an
  unsecured claim against the borrower (if any deficiency exists) once the
  lien itself is extinguished.
- **Document:** The junior lien instruments, notice-of-sale records showing
  junior lienholders were (or were not) properly notified (§3.18).
- **Ledger/accounting entry:** The junior lienholder's own books write down
  the secured asset.
- **Legal right:** Junior lienholders' right to any surplus remaining after
  the senior lien and authorized costs are satisfied, in priority order
  ahead of the borrower's own surplus claim.
- **Legal obligation:** The foreclosing party's obligation to properly
  notify known junior lienholders before sale.
- **Governing authority:** State lien-priority statutes; the same NCLC
  survey for state variation.
- **Evidence that should exist:** A complete, dated list of all liens of
  record at the time of sale, in priority order, with notice records for
  each.
- **Unresolved factual questions:** Were all junior lienholders of record
  actually identified and notified? Does the priority order applied in the
  actual distribution match the recorded lien-priority order?

### 3.23 Surplus/deficiency

- **Actor:** Note holder/trustee (calculates), borrower and junior
  lienholders (potential recipients of surplus, or potential targets of a
  deficiency claim).
- **Asset/liability:** If sale proceeds exceed the total of principal,
  interest, authorized costs, and junior liens: a surplus asset belongs to
  the borrower. If proceeds fall short: a deficiency liability may remain
  against the borrower, subject to state anti-deficiency law.
- **Document:** The final surplus/deficiency accounting; any deficiency-
  judgment complaint, if pursued.
- **Ledger/accounting entry:** Final closing entries on the note holder's
  books — deficiency written off or pursued as a separate unsecured claim;
  surplus recorded as a payable to the borrower.
- **Legal right:** Borrower's right to surplus (§3.20's Tyler v. Hennepin
  citation applies here specifically); in non-recourse states, no
  deficiency liability exists at all for at least ten states per AllLaw/
  Nolo's summary (Alaska, Arizona, California, Hawaii, Minnesota, Montana,
  North Dakota, Oklahoma, Oregon, Washington — per that source's search
  summary, not yet independently confirmed by direct fetch, per
  `banking-mortgage-research-plan.md` Part 1.3, item 2).
- **Legal obligation:** The note holder's obligation to actually remit any
  surplus, and to calculate any deficiency using the state's required
  method (bid-price vs. fair-market-value — ~20 states require fair-
  market-value per the same AllLaw/Nolo source, also not yet independently
  confirmed).
- **Governing authority:** State anti-deficiency and surplus-funds
  statutes, per NCLC's survey and the AllLaw/Nolo summary above — both at
  the confidence level those sources were already assigned; not upgraded
  here.
- **Evidence that should exist:** The final accounting, proof of any
  surplus actually paid to the borrower (or affirmatively unclaimed and
  where it went), any deficiency judgment actually entered.
- **Unresolved factual questions:** This is where §4's discrepancy
  framework is applied most directly — see below.

### 3.24 Actual distribution

- **Actor:** Whoever holds sale proceeds pending distribution (trustee,
  court registry, or the foreclosing lender directly, depending on state
  procedure).
- **Asset/liability:** Final transfer of actual dollars to each party
  entitled to them per §§3.20-3.23's accounting.
- **Document:** Distribution statement/disbursement records, canceled
  checks or wire confirmations to each payee.
- **Ledger/accounting entry:** Final cash disbursement entries, closing out
  the transaction on every remaining party's books.
- **Legal right/obligation:** No new rights — this step is where the rights
  established throughout §§3.20-3.23 either are or are not actually
  honored in practice, which is precisely why it must be traced as its own
  step rather than assumed to follow automatically from the accounting.
- **Governing authority:** Same as §3.23.
- **Evidence that should exist:** Proof of actual payment (not just a
  stated obligation to pay) to every party the accounting says is owed
  money — surplus to the borrower, remaining amounts to junior lienholders
  in priority order.
- **Unresolved factual questions:** Does the *actual* distribution match
  the *stated* accounting from §§3.20-3.23, dollar for dollar? A mismatch
  here — money the accounting says should have gone somewhere, that
  observably did not — is the clearest possible instance of the Z
  discrepancy defined in §4, and the step most directly worth independent
  verification in any real dispute.

## 4. Discrepancy detection: the X/Y/Z framework

The entire point of tracing every step in §3 with the same nine fields is
to make the following comparison possible, at any step where money moves or
an obligation is discharged:

| Term | Definition | Where it comes from |
|---|---|---|
| **X — Expected distribution** | What the transaction's own governing documents (note, deed of trust, PSA, servicing agreement) and applicable statute/case law say *should* happen at this step, calculated from the FACT and AUTHORITY components (per `zero-trust-legal-epistemology.md` §3) traced in §3 above. | The "Legal right," "Legal obligation," and "Governing authority" fields for the relevant step(s). |
| **Y — Observed distribution** | What the actual records (ledger entries, disbursement confirmations, canceled checks, recorded instruments) show *did* happen. | The "Ledger/accounting entry" and "Evidence that should exist" fields, populated with what was actually retrieved — not what should exist in theory. |
| **Z — Unexplained difference** | X minus Y, to the extent it cannot be accounted for by a documented, evidenced adjustment (an authorized fee, a permitted cost, a correctly-applied state-law variation). | Computed, not assumed — Z is only "unexplained" after a genuine attempt has been made to explain it using the actual record, not merely asserted because a gap exists. |

**The rule, stated explicitly:** A discrepancy (Z ≠ 0) identifies a **fact
question requiring further evidence.** It must never, by itself, be used to
infer **motive** — fraud, bad faith, or conspiracy. A nonzero Z is
consistent with many explanations: a clerical error, a timing difference
between when an event occurred and when it was recorded, a legitimate but
undocumented adjustment, a data-transfer error during a servicing
transfer, or — yes — misconduct. The reconstruction method's job stops at
identifying *that* a gap exists and *where*; it does not extend to deciding
*why*. This mirrors `zero-trust-legal-epistemology.md` §3's own
classification: a discrepancy is evidence toward a FACT or DISPUTED FACT
determination ("did the accounting reconcile") — converting it into a
MOTIVE THEORY claim ("and therefore they did it on purpose") requires
separate, independent evidence about intent that the discrepancy alone does
not supply, no matter how large or how suspicious in timing.

Applied to §3's sequence specifically: a Z discrepancy between the
principal/interest/cost totals in §3.20-3.21's payoff accounting and the
sale proceeds in §3.19 identifies that *something* in the accounting or the
underlying ledger entries needs explaining. It does not, by itself, tell
the system whether that something is a servicing-transfer data error (a
real, common, non-malicious cause), a legitimate cost this reconstruction's
"Evidence that should exist" field simply hasn't been given yet, or
something worse. Under `zero-trust-legal-epistemology.md`'s no-exemptions
rule, this applies symmetrically: a discrepancy that happens to favor the
lender is not presumed to be fraud, and a discrepancy that happens to favor
the borrower is not presumed to be a borrower error — both are simply Z,
pending further evidence, until that evidence actually resolves which of
the FACT-question explanations applies.

## 5. Reusability beyond mortgages

The nine-field structure in §2 and the X/Y/Z framework in §4 do not depend
on anything mortgage-specific — they depend only on there being (a) a
sequence of steps with actors, documents, and ledger entries, and (b) a
governing-authority source that specifies what *should* happen at each
step. The same structure applies directly to, for example, a UCC Article 9
secured-transaction default-and-disposition sequence (already partially
modeled in this codebase's `services/cross_article_lifecycle.py` and
`services/obligation_perspective.py`), a construction-lien priority
dispute, or a probate estate accounting. Extending this method to another
transaction type is a matter of re-running §3's per-step decomposition for
that transaction's real sequence, not of redesigning the method itself.

---

## Verification

`python3 -m unittest discover -s law-engine/services -p "test_*.py"` was run
after both documents were written; results and confirmation that no code
files were touched are reported in the accompanying summary.
