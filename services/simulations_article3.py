"""Law Engine -- Article 3 Negotiable-Instrument Mini-Simulation (Live Run
1.57, Mission 8). Extends the Task-First pattern (services/simulations.py,
services/simulations_article9.py) into UCC Article 3 (negotiable
instruments) -- a real, bounded, 4-step chained scenario, not a second
parallel schema. A parallel module rather than an extension of either
prior simulation module, matching this codebase's own established
precedent for splitting by Article.

Grounded only in the 11 real sections services/ingestion_article3.py
ingested (Va. Code Ann. Title 8.3A) -- Task.validate() enforces this at
the data layer, and this module does not weaken that check. Real,
deliberate design choice, per docs/task-first-pedagogy-and-task-ladder-
architecture.md's Live Run 1.49/1.57 corrections: every step opens on a
real decision a small-business owner (then, in the transfer step, the
owner of a different small business who received the note) actually has
to make, with facts accumulating across steps as one continuous problem.
Doctrine (§§ 8.3A-104, 8.3A-109, 8.3A-201, 8.3A-203, 8.3A-204, 8.3A-205,
8.3A-301, 8.3A-302) is introduced only in the feedback/reasoning after the
learner has already acted. Every option is a real action with a real,
distinct consequence -- never a bare Yes/No legal-conclusion statement --
and each step includes a genuine partially-correct/risky middle option.

The story, in order: a freelance web designer is paid with a signed note
instead of cash and has to decide how to treat it before assuming it's
just as good as cash (negotiability); she then needs to actually use that
note to pay her own supplier, and has to negotiate it -- not just hand it
over -- to give the supplier real, independent enforcement rights
(negotiation/transfer); she has to decide what kind of indorsement to
put on it before mailing it, given real transit risk (indorsement type
and effect); and finally -- the "transfer" step, switching the learner
into the receiving business's own role -- once that business holds the
note, the original maker tries to brush off paying it by claiming only
the original payee can collect, and the learner has to recognize the
business's own real right to enforce it (person entitled to enforce).
"""

from __future__ import annotations

import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.tasks import Task, TaskOption


def build_freelance_note_simulation() -> list[Task]:
    """A real, bounded, 4-step simulation. No step opens with "which
    Article/section applies" -- every step is a real business (or, in the
    transfer step, note-holder-side) decision under real, accumulating
    facts."""

    step_1 = Task(
        task_id="sim-note-1-negotiability",
        scenario=(
            "You run a one-person web design studio. You just finished a $3,000 project for Morgan Reyes, "
            "who runs a local bakery. Morgan doesn't have the cash on hand today and hands you a signed, "
            "handwritten note instead: \"I, Morgan Reyes, promise to pay to the order of Jamie Alvarez the "
            "sum of $3,000 on demand.\" It's signed and dated, with nothing else written on it."
        ),
        learner_role="freelance small-business owner (web designer)",
        objective="Decide how to treat this note as payment for the invoice.",
        facts_provided=[
            "The note is a signed, dated, handwritten promise to pay $3,000.",
            "It says \"pay to the order of Jamie Alvarez\" (that's you) \"on demand.\"",
            "Nothing else is written on the note -- no other conditions or instructions.",
            "Morgan has never done this before; you've always been paid in cash or by transfer.",
        ],
        documents_provided=["Morgan's signed note"],
        options=[
            TaskOption(
                option_id="accept-without-review",
                label="Accept the note without reviewing its terms, since it's signed and states an amount.",
                is_correct=False,
                consequence=(
                    "You'd treat the note as equivalent to cash without ever checking what kind of "
                    "payment obligation it actually is -- and whether it's freely transferable and "
                    "enforceable the way commercial paper is, or just an ordinary IOU."
                ),
                plain_language_feedback=(
                    "A signed writing for a stated amount isn't automatically a negotiable instrument. "
                    "Whether it is turns on real, specific requirements -- worth checking before you rely "
                    "on it."
                ),
            ),
            TaskOption(
                option_id="verify-against-negotiability-requirements",
                label="Review the note's own language against the real negotiability requirements before deciding how to treat it.",
                is_correct=True,
                consequence=(
                    "You correctly confirm what kind of payment obligation you actually hold before relying "
                    "on it or trying to use it yourself."
                ),
                plain_language_feedback=(
                    "The note is an unconditional promise to pay a fixed amount ($3,000), payable to your "
                    "order, payable on demand, with no other undertaking attached -- it satisfies every real "
                    "requirement for a negotiable instrument. Checking this first is exactly the right move, "
                    "because it determines what you can actually do with the note next."
                ),
            ),
            TaskOption(
                option_id="treat-as-ordinary-iou",
                label="Accept the note, but just keep treating it as an ordinary IOU/contract claim rather than commercial paper.",
                is_correct=False,
                consequence=(
                    "This doesn't put you in any legal danger, but it forfeits real advantages -- easier "
                    "transfer and stronger enforcement rights for whoever ends up holding it -- that come "
                    "with recognizing it as the negotiable instrument it actually is."
                ),
                plain_language_feedback=(
                    "Treating a real negotiable instrument as if it were just an ordinary contract claim "
                    "isn't dangerous, but it's an unnecessarily cautious middle ground -- you'd be giving up "
                    "real, useful properties the note actually has without ever finding that out."
                ),
            ),
            TaskOption(
                option_id="refuse-and-escalate",
                label="Refuse the note and immediately involve a collections attorney to demand cash payment instead.",
                is_correct=False,
                consequence=(
                    "You'd escalate a routine payment-method question into a real conflict, and spend money "
                    "on a lawyer, over a note that turns out to be a perfectly normal, enforceable way to be "
                    "paid."
                ),
                plain_language_feedback=(
                    "Nothing about being handed a note instead of cash is inherently a problem -- a signed "
                    "note meeting the real negotiability requirements is a legitimate, commonly used form of "
                    "payment. Escalating before even checking what you have is a real overreaction."
                ),
            ),
        ],
        governing_sections=["8.3A-104", "8.3A-109"],
        professional_terminology={
            "negotiable instrument": "A signed, unconditional promise or order to pay a fixed amount of money, on demand or at a definite time, to bearer or to order, with no other undertaking attached.",
            "payable to order": "An instrument payable to a specifically identified person (or that person's order), rather than to whoever holds it.",
            "maker": "The person who signs a note, undertaking to pay it.",
        },
        reasoning_chain=[
            "§ 8.3A-104(a): a negotiable instrument is an unconditional promise or order to pay a fixed amount of money, payable to bearer or order, payable on demand or at a definite time, with no other undertaking or instruction attached.",
            "Morgan's note is a signed, unconditional promise to pay a fixed $3,000, on demand -- satisfying § 8.3A-104(a)(2) and the fixed-amount/unconditional-promise language directly.",
            "§ 8.3A-109(b): a promise payable \"to the order of\" an identified person is payable to order -- Morgan's note, payable \"to the order of Jamie Alvarez,\" satisfies § 8.3A-104(a)(1)'s payable-to-order-or-bearer requirement.",
            "Nothing else is written on the note, so there's no additional undertaking or instruction that would disqualify it under § 8.3A-104(a)(3) -- the note is a real, negotiable instrument.",
        ],
        common_mistakes=[
            "Assuming any signed, dated writing promising money is automatically a negotiable instrument without checking the real requirements.",
            "Treating a confirmed negotiable instrument as if it were just an ordinary contract claim, out of excess caution.",
            "Treating being paid with a note instead of cash as inherently suspicious or improper.",
        ],
        difficulty=1,
        next_task_id="sim-note-2-negotiation",
        prerequisite_task_id=None,
        business_or_personal_context="Your one-person web design studio; just finished a $3,000 project for a bakery client.",
        time_pressure="",
        financial_stakes="$3,000 -- the full project payment.",
        parties_involved=["You (Jamie Alvarez, web designer)", "Morgan Reyes (bakery owner, client)"],
        competency_id="determine-whether-a-payment-instrument-is-a-negotiable-instrument",
        business_effect=(
            "By confirming the note is a real negotiable instrument before relying on it, you know exactly "
            "what you actually hold -- a transferable, independently enforceable payment obligation, not "
            "just Morgan's personal promise."
        ),
        legal_effect=(
            "A writing doesn't need to say \"negotiable instrument\" anywhere on its face -- it either "
            "satisfies § 8.3A-104(a)'s real elements or it doesn't, and Morgan's note does."
        ),
        rights_created_waived_or_preserved=(
            "Nothing is waived by checking first; verifying negotiability preserves your ability to use the "
            "note's real, transferable properties later instead of accidentally treating it as less than it is."
        ),
        evidence_created_preserved_or_lost=(
            "The note itself, in its current signed and dated form, is the real evidence of Morgan's "
            "payment obligation -- nothing new needs to be created yet."
        ),
    )

    step_2 = Task(
        task_id="sim-note-2-negotiation",
        scenario=(
            "You owe Ridgeline Paper Co., your printing supplier, $3,000 for a past order -- the same amount "
            "as Morgan's note. Instead of writing Ridgeline a check, you'd like to just use Morgan's note to "
            "settle your own debt. Ridgeline has agreed to accept it, on the condition that Ridgeline "
            "actually gets full, independent rights to collect the $3,000 from Morgan directly."
        ),
        learner_role="freelance small-business owner (web designer)",
        objective="Decide how to actually transfer the note to Ridgeline so Ridgeline gets full, enforceable rights in it.",
        facts_provided=[
            "The note is payable to your order (\"pay to the order of Jamie Alvarez\"), not to bearer.",
            "You owe Ridgeline $3,000 and want to use the note to settle that debt.",
            "Ridgeline wants full, independent rights to collect from Morgan directly, not just your promise that you'll pay them once Morgan pays you.",
        ],
        options=[
            TaskOption(
                option_id="hand-over-without-signing",
                label="Just hand Ridgeline the note without signing anything on it, since the note itself already says $3,000.",
                is_correct=False,
                consequence=(
                    "Ridgeline would receive physical possession, but because the note is payable to your "
                    "order, Ridgeline wouldn't yet be a holder with full rights in its own name -- only a "
                    "right to demand that you sign it over."
                ),
                plain_language_feedback=(
                    "An order instrument requires both possession AND your indorsement to actually be "
                    "negotiated to someone else. Handing it over without signing leaves Ridgeline holding "
                    "paper it can't yet fully act on."
                ),
            ),
            TaskOption(
                option_id="indorse-then-deliver",
                label="Sign an indorsement on the note transferring it, then deliver it to Ridgeline.",
                is_correct=True,
                consequence=(
                    "Ridgeline becomes a real holder of the note, with full rights to enforce it directly "
                    "against Morgan in Ridgeline's own name."
                ),
                plain_language_feedback=(
                    "Because the note is payable to your order, negotiating it to Ridgeline requires both "
                    "transferring possession and your indorsement. Doing both is exactly what makes "
                    "Ridgeline a holder, not just someone holding your paper."
                ),
            ),
            TaskOption(
                option_id="separate-assignment-letter",
                label="Deliver the note along with a separate signed letter assigning your rights in it to Ridgeline, without indorsing the note itself.",
                is_correct=False,
                consequence=(
                    "Ridgeline would receive your real rights to enforce the note through the assignment, "
                    "but wouldn't become a holder through actual negotiation -- a real, partially effective "
                    "move, just not the clean, complete one available."
                ),
                plain_language_feedback=(
                    "Transferring the note (even without a proper indorsement) does give the transferee your "
                    "own enforcement rights -- but negotiation itself, and the holder status that comes with "
                    "it, doesn't happen until the note is actually indorsed. A separate letter is a real, "
                    "working substitute, but not the same as the note being properly indorsed and delivered."
                ),
            ),
            TaskOption(
                option_id="promise-to-pay-once-morgan-pays",
                label="Tell Ridgeline you'll pay them once Morgan pays you, without transferring the note at all.",
                is_correct=False,
                consequence=(
                    "You wouldn't actually use the note to settle your debt to Ridgeline at all -- you'd "
                    "still owe Ridgeline directly, and you'd still be the one waiting on Morgan."
                ),
                plain_language_feedback=(
                    "This doesn't accomplish what you actually want -- using the note itself to satisfy your "
                    "debt to Ridgeline now. It just keeps both debts exactly where they were."
                ),
            ),
        ],
        governing_sections=["8.3A-201", "8.3A-203", "8.3A-204"],
        professional_terminology={
            "negotiation": "Transferring possession of an instrument in a way that makes the transferee its holder -- for order paper, that requires both delivery and indorsement.",
            "transfer": "Delivering an instrument for the purpose of giving the recipient the right to enforce it -- broader than negotiation, but not the same as becoming a holder.",
            "indorsement": "A signature made on an instrument (or a paper affixed to it) for the purpose of negotiating it, restricting its payment, or accepting indorser's liability on it.",
        },
        reasoning_chain=[
            "§ 8.3A-201(a): negotiation is a transfer of possession of an instrument that makes the transferee its holder.",
            "§ 8.3A-201(b): because the note is payable to your order (an identified person), negotiating it requires both transfer of possession AND your indorsement as the current holder -- bearer paper alone would only need delivery, but this note isn't bearer paper.",
            "§ 8.3A-204(a): an indorsement is a signature made on the instrument for the purpose of negotiating it -- signing the note over to Ridgeline is exactly this.",
            "§ 8.3A-203(b): transferring the note, even without indorsement, does vest the transferee with your own enforcement rights -- but § 8.3A-203(c) confirms that negotiation itself doesn't occur until the indorsement is actually made, so an unindorsed transfer is real but incomplete compared to a proper indorsement and delivery.",
        ],
        common_mistakes=[
            "Assuming physical delivery of an order instrument, by itself, is enough to negotiate it.",
            "Not realizing that a transfer without indorsement still gives the recipient real (if less complete) rights.",
            "Confusing a promise to pay once a third party pays you with actually transferring the instrument itself.",
        ],
        difficulty=2,
        next_task_id="sim-note-3-indorsement-type",
        prerequisite_task_id="sim-note-1-negotiability",
        business_or_personal_context="Your web design studio; you want to use Morgan's note to settle your own $3,000 debt to your printing supplier.",
        time_pressure="",
        financial_stakes="$3,000 -- the same amount you owe Ridgeline.",
        parties_involved=["You (Jamie Alvarez, web designer)", "Morgan Reyes (maker of the note)", "Ridgeline Paper Co. (your supplier)"],
        competency_id="negotiate-an-instrument-to-transfer-full-enforcement-rights",
        business_effect=(
            "By indorsing and delivering the note, you fully settle your $3,000 debt to Ridgeline in one "
            "clean transaction, without writing a check you don't have the cash to cover."
        ),
        legal_effect=(
            "Because the note is order paper, negotiation to Ridgeline requires both delivery and your "
            "indorsement -- delivery alone, or a separate assignment, are real but legally different, less "
            "complete alternatives."
        ),
        rights_created_waived_or_preserved=(
            "Indorsing and delivering the note transfers your own rights in it to Ridgeline and creates "
            "Ridgeline's independent right to enforce the note directly against Morgan."
        ),
        evidence_created_preserved_or_lost=(
            "Your signed indorsement on the note becomes the real, permanent evidence of the transfer to "
            "Ridgeline -- unlike a separate letter, it travels with the note itself."
        ),
    )

    step_3 = Task(
        task_id="sim-note-3-indorsement-type",
        scenario=(
            "You've decided to indorse the note over to Ridgeline, but Ridgeline's accounts-receivable office "
            "is across the state, so you're planning to mail it rather than deliver it in person. You're "
            "aware mail can occasionally be lost or stolen, and you want to think about what you actually "
            "write when you sign the note before dropping it in the mail."
        ),
        learner_role="freelance small-business owner (web designer)",
        objective="Decide what kind of indorsement to actually write on the note before mailing it.",
        facts_provided=[
            "The note is currently payable to your order (\"pay to the order of Jamie Alvarez\").",
            "You're mailing the note to Ridgeline rather than delivering it in person.",
            "Mail can occasionally be lost or stolen in transit.",
        ],
        hidden_or_irrelevant_facts=[
            "Which specific postal carrier you use to mail the note isn't relevant to what kind of indorsement protects you.",
        ],
        options=[
            TaskOption(
                option_id="blank-indorsement",
                label="Sign a blank indorsement (just your signature) on the back before mailing it.",
                is_correct=False,
                consequence=(
                    "The note becomes payable to bearer the moment you sign it -- so if it's lost or stolen "
                    "in transit, whoever ends up with it could negotiate it further just by handing it off, "
                    "with no forged signature required."
                ),
                plain_language_feedback=(
                    "A blank indorsement -- just your signature, naming no one -- turns the note into bearer "
                    "paper. That's exactly the wrong property to create right before mailing something that "
                    "could be lost or stolen."
                ),
            ),
            TaskOption(
                option_id="special-indorsement",
                label="Sign a special indorsement naming Ridgeline Paper Co. specifically as the person to whom it's now payable, before mailing it.",
                is_correct=True,
                consequence=(
                    "The note stays order paper, now payable specifically to Ridgeline -- if it's lost or "
                    "stolen in transit, a finder can't negotiate it further without forging Ridgeline's own "
                    "indorsement."
                ),
                plain_language_feedback=(
                    "A special indorsement names the person the instrument now becomes payable to, and it "
                    "can only be further negotiated by that person's own indorsement. Naming Ridgeline "
                    "directly keeps the note safe from a finder even if the mail goes wrong."
                ),
            ),
            TaskOption(
                option_id="wait-and-send-separate-letter",
                label="Don't indorse it before mailing; wait until Ridgeline confirms receipt, then mail a second, separate indorsement letter.",
                is_correct=False,
                consequence=(
                    "This doesn't create the bearer-paper risk a blank indorsement would, since an "
                    "unindorsed order note still can't be negotiated by a finder without your own "
                    "indorsement -- but it delays Ridgeline's full rights and adds an unnecessary extra "
                    "mailing and delay."
                ),
                plain_language_feedback=(
                    "You're not creating new risk here -- the note isn't bearer paper yet, so a finder still "
                    "can't negotiate it without your signature. But this is a needlessly slow, two-step "
                    "process when a special indorsement accomplishes the same protection in one mailing."
                ),
            ),
            TaskOption(
                option_id="blank-indorsement-plus-account-info",
                label="Sign a blank indorsement and also write Ridgeline's full account number and bank routing number on the note for extra clarity.",
                is_correct=False,
                consequence=(
                    "You'd create the same bearer-paper risk as a plain blank indorsement, plus hand a "
                    "finder Ridgeline's real banking details on top of a note anyone could now negotiate."
                ),
                plain_language_feedback=(
                    "This compounds the blank-indorsement problem instead of fixing it -- the note is still "
                    "bearer paper, and now carries sensitive account details that make a lost or stolen note "
                    "even more dangerous."
                ),
            ),
        ],
        governing_sections=["8.3A-205", "8.3A-201"],
        professional_terminology={
            "special indorsement": "An indorsement that names the specific person the instrument becomes payable to, keeping it order paper.",
            "blank indorsement": "An indorsement consisting only of a signature, which makes the instrument payable to bearer.",
        },
        reasoning_chain=[
            "§ 8.3A-205(a): a special indorsement identifies the person to whom the instrument becomes payable, and the instrument may then only be negotiated by that person's own indorsement.",
            "§ 8.3A-205(b): a blank indorsement makes the instrument payable to bearer, negotiable by transfer of possession alone -- exactly the property you don't want on something you're about to put in the mail.",
            "§ 8.3A-201(b): because the note (until specially indorsed) is still payable to your order, a finder without your indorsement can't negotiate it -- so leaving it unindorsed is safe, just incomplete compared to a special indorsement that finishes the job in one step.",
        ],
        common_mistakes=[
            "Signing a blank indorsement out of habit without considering that it creates bearer paper.",
            "Adding sensitive account or banking details directly onto an instrument that could be lost or stolen.",
            "Assuming any indorsement is as safe as any other regardless of how the instrument will be transported.",
        ],
        difficulty=3,
        next_task_id="sim-note-4-enforcement",
        prerequisite_task_id="sim-note-2-negotiation",
        business_or_personal_context="Your web design studio; mailing the indorsed note to Ridgeline's out-of-town office.",
        time_pressure="You want to mail the note today to keep your account with Ridgeline current.",
        financial_stakes="$3,000 -- the full value of the note, at risk if it's lost or stolen in transit.",
        parties_involved=["You (Jamie Alvarez, web designer)", "Ridgeline Paper Co. (your supplier)"],
        competency_id="choose-the-right-type-of-indorsement-for-the-situation",
        business_effect=(
            "By specially indorsing the note before mailing it, you protect the full $3,000 value in transit "
            "while still completing the transfer to Ridgeline in a single mailing."
        ),
        legal_effect=(
            "The choice between a blank and special indorsement directly determines whether the note becomes "
            "bearer paper (negotiable by anyone in possession) or stays order paper payable only to "
            "Ridgeline."
        ),
        rights_created_waived_or_preserved=(
            "A special indorsement preserves your and Ridgeline's protection against a finder negotiating "
            "the note; a blank indorsement would waive that protection the moment it's signed."
        ),
        evidence_created_preserved_or_lost=(
            "The specific wording of the indorsement itself becomes the real evidence of who the note is "
            "now payable to, and how safely it can travel."
        ),
    )

    step_4 = Task(
        task_id="sim-note-4-enforcement",
        scenario=(
            "Ridgeline received the note, specially indorsed, without incident. Weeks later, you're now the "
            "person at Ridgeline handling accounts receivable -- stepping into Ridgeline's own shoes. "
            "Ridgeline presented the note to Morgan for payment, but Morgan refused, telling your colleague, "
            "\"This isn't Ridgeline's note to collect -- that was between me and Jamie.\" Your colleague asks "
            "you how to respond."
        ),
        learner_role="accounts receivable (Ridgeline Paper Co.) -- transfer",
        objective="Decide whether Ridgeline actually has the right to enforce the note against Morgan, and how to respond to Morgan's refusal.",
        facts_provided=[
            "Ridgeline has physical possession of the note, specially indorsed to Ridgeline Paper Co. by Jamie.",
            "Ridgeline gave real value for the note -- it settled Jamie's $3,000 debt to Ridgeline.",
            "Ridgeline had no notice of any problem with the note when it accepted it.",
            "The note shows no signs of forgery, alteration, or irregularity.",
        ],
        hidden_or_irrelevant_facts=[
            "The fact that Jamie, not Ridgeline, was the original payee doesn't by itself determine who can enforce the note now.",
        ],
        options=[
            TaskOption(
                option_id="concede-only-jamie-can-enforce",
                label="Concede that only Jamie can enforce the note against Morgan, since Jamie was the original payee.",
                is_correct=False,
                consequence=(
                    "Ridgeline would give up a real right it actually holds, and would have to go back to "
                    "Jamie to collect instead of enforcing the note directly -- an unnecessary extra step."
                ),
                plain_language_feedback=(
                    "Being the original payee isn't what determines who can currently enforce an instrument -- "
                    "whoever is the current holder through a real, completed negotiation can enforce it in "
                    "their own name, and that's now Ridgeline, not Jamie."
                ),
            ),
            TaskOption(
                option_id="assert-ridgelines-own-right",
                label="Present the note to Morgan and assert Ridgeline's own right to enforce it as the current holder, entitled to payment in its own name.",
                is_correct=True,
                consequence=(
                    "Ridgeline correctly stands on its own real, independent right to collect, rather than "
                    "treating its position as somehow borrowed or uncertain."
                ),
                plain_language_feedback=(
                    "Ridgeline is a holder of the note through Jamie's real, completed special indorsement, "
                    "which makes Ridgeline a person entitled to enforce the note in its own name -- Morgan's "
                    "claim that only Jamie can collect simply isn't accurate."
                ),
            ),
            TaskOption(
                option_id="ask-jamie-to-demand-payment",
                label="Ask Jamie to come along and personally demand payment from Morgan on Ridgeline's behalf, rather than asserting Ridgeline's own right.",
                is_correct=False,
                consequence=(
                    "This doesn't put Ridgeline in any legal danger, since Ridgeline's right to enforce the "
                    "note doesn't depend on Jamie showing up -- but it's an unnecessary, cumbersome extra "
                    "step that treats Ridgeline's own clear right as if it needed borrowing."
                ),
                plain_language_feedback=(
                    "Ridgeline doesn't need Jamie's help to enforce the note -- Ridgeline is the current "
                    "holder in its own right. Involving Jamie isn't wrong, exactly, but it's a real, "
                    "avoidable complication."
                ),
            ),
            TaskOption(
                option_id="sue-jamie-instead",
                label="Give up trying to collect on the note and instead sue Jamie directly for the underlying debt the note was meant to satisfy.",
                is_correct=False,
                consequence=(
                    "Ridgeline would abandon a real, presently enforceable right in the note itself, over a "
                    "debt that was already settled when Ridgeline accepted the note as payment."
                ),
                plain_language_feedback=(
                    "Ridgeline accepted the note to settle Jamie's debt -- going back to sue Jamie instead of "
                    "enforcing the note it actually holds gives up the cleaner, real right Ridgeline already "
                    "has against Morgan."
                ),
            ),
        ],
        governing_sections=["8.3A-301", "8.3A-302"],
        professional_terminology={
            "person entitled to enforce": "The holder of an instrument, a nonholder in possession with a holder's rights, or a person entitled to enforce a lost or destroyed instrument -- not necessarily the original payee.",
            "holder in due course": "A holder who took a genuine-looking instrument for value, in good faith, and without notice of any problem with it.",
        },
        reasoning_chain=[
            "§ 8.3A-301: \"person entitled to enforce\" an instrument means the holder of the instrument, or certain other limited categories -- not specifically or exclusively the original payee.",
            "Jamie's special indorsement and delivery to Ridgeline (step 2) completed a real negotiation, making Ridgeline the note's current holder.",
            "As the current holder, Ridgeline is a person entitled to enforce the note under § 8.3A-301, in its own name, regardless of who the original payee was.",
            "§ 8.3A-302(a): Ridgeline also took the note for value (settling Jamie's debt), in good faith, without notice of any problem, and the note shows no signs of forgery or irregularity -- so Ridgeline holds an especially strong position as a holder in due course, not just an ordinary holder.",
        ],
        common_mistakes=[
            "Assuming only the original payee named on an instrument can ever enforce it.",
            "Treating a real, independent right to enforce an instrument as if it still depended on the prior holder's participation.",
            "Giving up on enforcing the instrument itself in favor of re-litigating the debt it was given to satisfy.",
        ],
        difficulty=4,
        next_task_id=None,
        prerequisite_task_id="sim-note-3-indorsement-type",
        business_or_personal_context="You now represent Ridgeline Paper Co., the current holder of Morgan's note.",
        time_pressure="",
        financial_stakes="$3,000 -- the full value of the note Morgan is refusing to pay.",
        parties_involved=["Ridgeline Paper Co. (you)", "Morgan Reyes (maker of the note)", "Jamie Alvarez (original payee)"],
        competency_id="identify-who-is-a-person-entitled-to-enforce-an-instrument",
        business_effect=(
            "By asserting Ridgeline's own right to enforce the note, Ridgeline can collect the full $3,000 "
            "directly from Morgan without needing Jamie's further involvement."
        ),
        legal_effect=(
            "A real, completed negotiation transfers the current right to enforce an instrument to the new "
            "holder -- the original payee's role in the transaction doesn't limit who can enforce it now."
        ),
        rights_created_waived_or_preserved=(
            "Ridgeline's status as a holder in due course is preserved by asserting its own right rather than "
            "treating its position as merely derivative of Jamie's."
        ),
        evidence_created_preserved_or_lost=(
            "The specially indorsed note itself, still in Ridgeline's possession, is the real evidence of "
            "Ridgeline's status as the current holder entitled to enforce it."
        ),
    )

    steps = [step_1, step_2, step_3, step_4]
    for step in steps:
        step.validate()
    return steps
