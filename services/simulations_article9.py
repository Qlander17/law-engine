"""Law Engine -- Article 9 Mini-Simulation (Live Run 1.50).

Extends the Article 2 Task-First pattern (services/simulations.py, Live
Run 1.49) into UCC Article 9 (secured transactions) -- a real, bounded,
4-step chained scenario, not a second parallel schema. A parallel module
rather than an extension of simulations.py, matching this codebase's own
established precedent for splitting by Article (ingestion.py vs
ingestion_article9.py): keeps each Article's own simulation(s)
independently reviewable and re-runnable, and keeps simulations.py from
growing unbounded as more Articles are added.

Real, deliberate design choice, per docs/task-first-pedagogy-and-task-
ladder-architecture.md's "Correction, Live Run 1.49" section: every step
opens on a real decision a small-business owner (then, in the transfer
step, a commercial lender) actually has to make, with facts accumulating
across steps as one continuous problem. Doctrine (§ 8.9A-102, § 8.9A-203,
§ 8.9A-204, § 8.9A-308, § 8.9A-310, § 8.9A-322, § 8.9A-324, § 8.9A-601,
§ 8.9A-609, § 8.9A-610) is introduced only in the feedback/reasoning
after the learner has already acted -- the same DO-first cycle
build_riverside_bistro_simulation() already follows.

The story, in order: a small-business owner discovers the equipment
financer's own paperwork never actually created a security interest
(attachment failure); the financer fixes that with a properly signed
security agreement but hasn't filed anything (perfection gap); a
competing, earlier-filed blanket lien turns out to outrank the financer
because it filed its financing statement more than twenty days after the
debtor took possession, missing purchase-money super-priority (§ 8.9A-
324(a)'s real, narrow window); and finally -- the "transfer" step,
switching the learner into the lender's own role -- what the (subordinate
but still real and perfected) financer can actually do once the debtor
defaults (§§ 8.9A-601, 8.9A-609, 8.9A-610's real, bounded self-help
rights).

Option-framing patch (Live Run 1.57, per docs/task-first-pedagogy-and-
task-ladder-architecture.md's "Exact Article 9 simulation patch"
section): every step's options are real actions with real, distinct
consequences -- never a bare Yes/No legal-conclusion statement -- and
each step includes a genuine partially-correct/risky middle option, not
just a binary right/wrong. Each step also populates the newer schema
fields (business_effect, legal_effect, rights_created_waived_or_preserved,
evidence_created_preserved_or_lost) Live Run 1.49 added to Task.
"""

from __future__ import annotations

import sys
from pathlib import Path

_LAW_ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(_LAW_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAW_ENGINE_ROOT))

from services.tasks import Task, TaskOption


def build_espresso_bar_financing_simulation() -> list[Task]:
    """A real, bounded, 4-step simulation. No step opens with "which
    Article/section applies" -- every step is a real business (or, in the
    transfer step, lender-side) decision under real, accumulating facts."""

    step_1 = Task(
        task_id="sim-espresso-1-attachment",
        scenario=(
            "You run Anna's Espresso Bar. Six months ago you financed a $14,000 commercial espresso "
            "machine from Roastline Equipment Co. on an 18-month payment plan. Roastline's own paperwork "
            "is just a credit application you filled out and the invoice you signed at delivery, which "
            "lists the machine and an attached payment schedule -- nothing in either document is titled "
            "\"security agreement,\" grants Roastline any interest in the machine, or says the machine "
            "secures anything. Roastline never took possession of the machine; it's been in your shop the "
            "whole time. You've just missed two payments, and Roastline's collections department called "
            "today, telling you it holds \"a security interest in the machine\" and will \"come get it\" "
            "if you don't pay. The rep says you can either catch up the two missed payments right away or "
            "sign some additional paperwork they'll send over to \"formalize\" things."
        ),
        learner_role="small-business owner (espresso bar)",
        objective="Decide what to do about this call.",
        facts_provided=[
            "The only paperwork is a credit application and a signed invoice with a payment schedule.",
            "Neither document is called a security agreement or says anything secures the debt.",
            "Roastline has never had possession of the machine -- it's been in your shop for six months.",
            "You've made payments for six months and just missed two.",
            "Roastline's rep wants you to either catch up the missed payments or sign new paperwork.",
        ],
        documents_provided=["Your credit application", "The signed invoice with attached payment schedule"],
        options=[
            TaskOption(
                option_id="comply-sign-without-review",
                label="Comply immediately -- sign whatever Roastline sends without reviewing it.",
                is_correct=False,
                consequence=(
                    "You could grant Roastline a brand-new, valid security interest in the machine -- giving "
                    "up the exact leverage the correct analysis would have preserved, for a claim Roastline "
                    "hadn't actually earned yet."
                ),
                plain_language_feedback=(
                    "Signing whatever Roastline sends could itself create the very security interest that "
                    "doesn't exist yet. Review any document before signing -- your signature is what actually "
                    "has legal effect here, not Roastline's phone call."
                ),
            ),
            TaskOption(
                option_id="verify-then-review",
                label=(
                    "Ask Roastline to identify the specific document creating their security interest, and "
                    "review your own paperwork before agreeing to anything."
                ),
                is_correct=True,
                consequence=(
                    "You correctly recognize that Roastline's collections call is asserting a right it never "
                    "actually secured, and you protect your position by not conceding anything until they "
                    "prove their claim."
                ),
                plain_language_feedback=(
                    "A security interest has to come from a real agreement that creates or provides for one. "
                    "Your credit application and invoice are financing terms, not that agreement -- so nothing "
                    "ever attached, no matter how long you've been paying. Asking Roastline to point to the "
                    "actual document is the real first move a competent business owner makes."
                ),
            ),
            TaskOption(
                option_id="keep-paying-say-nothing",
                label="Say nothing about the dispute and keep making payments exactly as before.",
                is_correct=False,
                consequence=(
                    "You don't make your position any worse, but you also don't do anything to protect it -- "
                    "Roastline's mistaken claim goes unchallenged and could resurface later."
                ),
                plain_language_feedback=(
                    "Continuing to pay without addressing the claim isn't dangerous the way signing blindly "
                    "is, but it's not an affirmative defense of your position either -- it leaves Roastline's "
                    "incorrect claim on the table instead of correcting it."
                ),
            ),
            TaskOption(
                option_id="stop-payments-immediately",
                label="Stop making payments immediately, since you don't believe Roastline has a real security interest.",
                is_correct=False,
                consequence=(
                    "You could trigger a real default under the underlying credit/payment terms, which exist "
                    "independent of whether a security interest ever attached."
                ),
                plain_language_feedback=(
                    "Whether or not a security interest attached, you still owe the underlying debt under "
                    "your payment plan. Stopping payments doesn't follow from winning the security-interest "
                    "argument, and creates a new, real problem."
                ),
            ),
        ],
        governing_sections=["8.9A-102", "8.9A-203"],
        professional_terminology={
            "security agreement": "An agreement that creates or provides for a security interest -- not just any financing or credit terms.",
            "attachment": "The moment a security interest becomes enforceable against the debtor with respect to specific collateral.",
            "equipment": "A real Article 9 collateral category: goods other than inventory, farm products, or consumer goods.",
        },
        reasoning_chain=[
            "§ 8.9A-102(a)(74): a \"security agreement\" is an agreement that creates or provides for a security interest -- not just any credit or financing terms.",
            "§ 8.9A-203(b): a security interest is enforceable (and can attach) only if value has been given, the debtor has rights in the collateral, and one of several agreement/possession/control conditions is met -- most commonly, the debtor signing a security agreement describing the collateral.",
            "Your credit application and the invoice's payment-schedule language never create or provide for a security interest in the machine -- they're financing terms, not a security agreement.",
            "Without a real security agreement (or possession/control by Roastline, which never happened), § 8.9A-203(b)(3) is never satisfied -- the security interest never attached.",
            "§ 8.9A-102(a)(33): the machine is \"equipment\" (goods other than inventory, farm products, or consumer goods) -- a real, valid collateral category, so that's not why attachment failed.",
        ],
        common_mistakes=[
            "Assuming any seller-financed purchase automatically creates a security interest.",
            "Assuming a valid collateral category like equipment can't be used as collateral at all.",
            "Assuming the debtor's own possession and use of the goods substitutes for a security agreement.",
            "Signing new paperwork from a creditor without reviewing what it actually grants.",
            "Stopping payment entirely as soon as a security-interest claim seems doubtful, without addressing the separate underlying debt.",
        ],
        difficulty=2,
        next_task_id="sim-espresso-2-perfection",
        prerequisite_task_id=None,
        business_or_personal_context="Anna's Espresso Bar; financed a commercial espresso machine six months ago.",
        time_pressure="Roastline's collections department called today threatening to \"come get\" the machine.",
        financial_stakes="$14,000 espresso machine, central to daily operations.",
        parties_involved=["Anna's Espresso Bar (you)", "Roastline Equipment Co."],
        competency_id="determine-whether-a-security-interest-attached",
        business_effect=(
            "By refusing to sign anything and asking Roastline to prove its claim first, Anna keeps full "
            "use of the espresso machine and avoids conceding any right Roastline hasn't actually earned."
        ),
        legal_effect=(
            "No security interest attaches merely from a collections call or from continued payments; "
            "attachment requires a real security agreement (or possession/control), which still doesn't "
            "exist at this point."
        ),
        rights_created_waived_or_preserved=(
            "Anna's right to dispute Roastline's claim is preserved by asking for proof rather than "
            "complying; signing without review would waive that leverage."
        ),
        evidence_created_preserved_or_lost=(
            "No new paperwork is created; the absence of any document creating a security interest "
            "remains the key evidence in Anna's favor."
        ),
    )

    step_2 = Task(
        task_id="sim-espresso-2-perfection",
        scenario=(
            "You point out to Roastline that its paperwork never actually created a security interest. "
            "To resolve the dispute and let you keep paying down the machine, Roastline has you sign a new "
            "document, titled \"Security Agreement,\" that specifically describes the espresso machine as "
            "collateral securing your remaining balance. Roastline's manager tells you, \"Good -- we're "
            "fully protected now.\" Roastline hasn't filed anything anywhere, and still has never had "
            "possession of the machine. A week later, the manager calls again: to \"lock in\" their "
            "protection, he says he's sending an employee to pick up the espresso machine for a week so "
            "Roastline can \"hold it as collateral\" before returning it -- the last step, he says, to make "
            "sure they're \"fully protected.\""
        ),
        learner_role="small-business owner (espresso bar)",
        objective="Decide how to respond to Roastline's plan to take the machine for a week.",
        facts_provided=[
            "You've now signed a document titled \"Security Agreement\" describing the machine as collateral.",
            "Roastline has not filed anything with any filing office.",
            "Roastline still has never had possession of the machine.",
            "The machine is equipment used in your business, not a consumer good.",
            "Roastline says taking the machine for a week is needed to \"finalize\" their protection.",
        ],
        options=[
            TaskOption(
                option_id="hand-over-machine",
                label="Let Roastline take the machine for the week, since they say it's necessary to finalize their protection.",
                is_correct=False,
                consequence=(
                    "You'd lose a full week of use of your central piece of equipment for a step that "
                    "doesn't durably protect Roastline anyway -- perfection by holding collateral only lasts "
                    "while Roastline actually keeps holding it, and they plan to give it back."
                ),
                plain_language_feedback=(
                    "Temporary possession that Roastline later returns wouldn't create lasting protection for "
                    "them -- that route requires actually keeping the collateral, not borrowing it for a "
                    "week. You'd give up real business use for no durable benefit to either side."
                ),
            ),
            TaskOption(
                option_id="redirect-to-filing",
                label=(
                    "Tell Roastline that if they want to be protected, they should file a financing "
                    "statement instead -- you need to keep using the machine for your business."
                ),
                is_correct=True,
                consequence=(
                    "You correctly identify the real, durable way for Roastline to perfect without "
                    "disrupting your operations, and Roastline can act on it without you giving up anything "
                    "you don't have to."
                ),
                plain_language_feedback=(
                    "Filing a financing statement is the standard way to perfect a security interest in "
                    "equipment, and it doesn't require you to give up possession at all. Attachment and "
                    "perfection are two different things -- the new agreement fixed attachment, but "
                    "perfection still requires filing (or possession/control), and filing is the option that "
                    "doesn't cost you use of the machine."
                ),
            ),
            TaskOption(
                option_id="allow-inspection-only",
                label="Offer to let a Roastline employee inspect and photograph the machine on-site, but refuse to let them remove it.",
                is_correct=False,
                consequence=(
                    "This doesn't hurt you, but it also doesn't actually perfect anything for Roastline or "
                    "resolve the real question of whether they've filed -- it's a compromise that leaves the "
                    "real issue unaddressed."
                ),
                plain_language_feedback=(
                    "On-site inspection is harmless, but it isn't possession and isn't filing -- it doesn't "
                    "satisfy either perfection method, so it doesn't actually move Roastline any closer to "
                    "being protected. It's a safe but incomplete response."
                ),
            ),
            TaskOption(
                option_id="refuse-and-threaten-stop-payment",
                label="Refuse to engage at all, and warn Roastline you'll stop payments if they send anyone to pick up the machine.",
                is_correct=False,
                consequence=(
                    "Threatening to stop payments over a possession request could itself be read as an "
                    "anticipatory default under your existing payment plan, creating a real problem "
                    "independent of the perfection question."
                ),
                plain_language_feedback=(
                    "You can decline to hand over the machine without threatening to stop paying -- your "
                    "payment obligation exists independent of whether Roastline is perfected, and "
                    "threatening default over this creates a new, avoidable risk."
                ),
            ),
        ],
        governing_sections=["8.9A-203", "8.9A-308", "8.9A-310"],
        professional_terminology={
            "perfection": "The additional step, beyond attachment, that protects a security interest against most other claimants to the same collateral.",
            "financing statement": "The document filed with a filing office to perfect a security interest by filing.",
        },
        reasoning_chain=[
            "§ 8.9A-203(b)(3)(A): the newly signed security agreement, describing the espresso machine, now satisfies the element that was missing before -- combined with value already given and your rights in the machine, the security interest attaches as of the date you sign.",
            "§ 8.9A-308(a): a security interest is perfected only once it has attached AND all applicable perfection requirements (§§ 8.9A-310 through 8.9A-316) are satisfied -- attachment alone isn't perfection.",
            "§ 8.9A-310(a): a financing statement must be filed to perfect a security interest, except in the specific situations listed in § 8.9A-310(b) -- none of which apply here, since Roastline never took possession or control of the machine.",
            "The security interest is now attached but unperfected until Roastline actually files a financing statement -- and filing, not a week of temporary possession, is the real, durable way to get there.",
        ],
        common_mistakes=[
            "Treating a signed security agreement as automatically perfecting the interest.",
            "Assuming perfection dates back to when payments began rather than when its actual requirements are met.",
            "Assuming temporary possession that will later be returned durably perfects a security interest.",
        ],
        difficulty=3,
        next_task_id="sim-espresso-3-priority",
        prerequisite_task_id="sim-espresso-1-attachment",
        business_or_personal_context="Anna's Espresso Bar; the attachment dispute with Roastline was just resolved by signing a new agreement.",
        parties_involved=["Anna's Espresso Bar (you)", "Roastline Equipment Co."],
        competency_id="perfect-a-security-interest-by-filing",
        business_effect=(
            "By redirecting Roastline to filing instead of temporary possession, Anna keeps uninterrupted "
            "use of the espresso machine for her business."
        ),
        legal_effect=(
            "Filing a financing statement is the durable way to perfect a security interest in equipment; "
            "temporary possession that Roastline later returns wouldn't create lasting protection and isn't "
            "a substitute for filing."
        ),
        rights_created_waived_or_preserved=(
            "Anna's continued use and possession of the machine is preserved; she creates no new grant of "
            "rights beyond the security agreement she already signed."
        ),
        evidence_created_preserved_or_lost=(
            "No new evidence is lost; if Roastline later files a financing statement, that filing becomes "
            "the real, public evidence of perfection."
        ),
    )

    step_3 = Task(
        task_id="sim-espresso-3-priority",
        scenario=(
            "You mention the whole dispute to a friend, who reminds you of something you'd forgotten: a "
            "year before you bought the espresso machine, you took out a small business line of credit from "
            "Riverbend Community Bank, secured by a blanket lien on \"all business equipment now owned or "
            "hereafter acquired.\" Riverbend properly filed its financing statement at that time and has "
            "kept it in place ever since. Roastline, meanwhile, just filed its own financing statement this "
            "week -- more than twenty days after you originally received the machine six months ago. "
            "Riverbend's loan officer has since noticed Roastline's new filing on equipment their own "
            "blanket lien already covers, and calls asking you to sign a short letter confirming "
            "\"Riverbend Community Bank holds first-priority security interest in all business equipment, "
            "including the espresso machine,\" so the bank can finalize a new loan against its collateral "
            "position."
        ),
        learner_role="small-business owner (espresso bar)",
        objective="Decide what to do about Riverbend's request that you sign the priority confirmation letter.",
        facts_provided=[
            "Riverbend Bank's blanket lien on \"all equipment now owned or hereafter acquired\" was filed a year before you bought the machine.",
            "Roastline just filed its financing statement this week, more than twenty days after you received the machine.",
            "The machine is equipment, not inventory or livestock.",
            "Riverbend's loan officer wants you to sign a letter confirming Riverbend has first priority in the machine.",
        ],
        hidden_or_irrelevant_facts=[
            "Which bank officer originally approved your line of credit is not relevant to who has priority in the machine.",
        ],
        options=[
            TaskOption(
                option_id="sign-without-review",
                label="Sign the confirmation letter as requested, since Riverbend is a bank and its blanket lien was filed first.",
                is_correct=False,
                consequence=(
                    "You'd sign a formal written statement about a legal conclusion -- priority -- without "
                    "actually verifying the filing dates or the purchase-money timing rule yourself, and "
                    "that signed statement could be used against you or Roastline later regardless of "
                    "whether it's accurate."
                ),
                plain_language_feedback=(
                    "Being a bank doesn't make Riverbend automatically right, and signing a written "
                    "confirmation of a legal conclusion you haven't verified creates a real, signed document "
                    "that could bind you to a mistaken analysis."
                ),
            ),
            TaskOption(
                option_id="verify-dates-before-signing",
                label=(
                    "Ask Riverbend for the actual filing dates and file numbers for both security interests, "
                    "and check the purchase-money twenty-day window yourself before signing anything."
                ),
                is_correct=True,
                consequence=(
                    "You correctly verify the real facts driving priority before putting your name on any "
                    "written confirmation, and you're prepared regardless of which creditor asks you again."
                ),
                plain_language_feedback=(
                    "Priority is decided by real, checkable facts -- filing dates and whether Roastline "
                    "perfected within the twenty-day purchase-money window -- not by which creditor asks "
                    "first or what kind of institution is asking. Verifying before signing protects you from "
                    "putting your name on the wrong conclusion."
                ),
            ),
            TaskOption(
                option_id="do-nothing-let-creditors-sort-it-out",
                label="Don't respond to Riverbend's request and assume the two creditors will sort out priority between themselves.",
                is_correct=False,
                consequence=(
                    "You're right that the actual priority ranking doesn't depend on anything you do -- but "
                    "staying silent leaves you unprepared if either creditor follows up, and doesn't give "
                    "you the real facts you'd want on hand."
                ),
                plain_language_feedback=(
                    "It's true that priority between Riverbend and Roastline is decided by their own filing "
                    "and perfection dates, not by you. But ignoring the request instead of at least "
                    "gathering the real facts leaves you exposed to being asked to sign something later "
                    "without being ready to evaluate it."
                ),
            ),
            TaskOption(
                option_id="help-roastline-fix-filing",
                label="Contact Roastline to warn them Riverbend is asserting superior priority, and offer to help Roastline correct its late filing.",
                is_correct=False,
                consequence=(
                    "You'd take on a task that isn't yours -- helping one of your own creditors improve its "
                    "legal position against another creditor -- and a late purchase-money filing can't be "
                    "fixed retroactively regardless of what you do."
                ),
                plain_language_feedback=(
                    "Fixing Roastline's missed twenty-day window isn't possible after the fact, and it isn't "
                    "your role as the debtor to manage a priority dispute between two creditors -- doing so "
                    "could also be read as taking sides in a dispute that isn't really yours to referee."
                ),
            ),
        ],
        governing_sections=["8.9A-310", "8.9A-322", "8.9A-324", "8.9A-204"],
        professional_terminology={
            "purchase-money security interest": "A security interest that secures the debt used to buy the specific collateral it covers -- eligible for special priority if perfected on time.",
            "blanket lien": "A security interest covering a broad category of a debtor's property, often including property acquired later.",
            "after-acquired property clause": "Contract language extending a security interest to collateral the debtor acquires after the agreement is signed.",
        },
        reasoning_chain=[
            "§ 8.9A-204(a): a security agreement may create or provide for a security interest in after-acquired collateral -- Riverbend's blanket lien on \"all equipment now owned or hereafter acquired\" reaches the espresso machine even though Riverbend's agreement predates the purchase.",
            "§ 8.9A-322(a)(1): conflicting perfected security interests rank by priority in time of filing or perfection -- Riverbend filed first, a year before Roastline.",
            "§ 8.9A-324(a): a perfected purchase-money security interest in goods other than inventory or livestock has priority over a conflicting security interest in the same goods only if it's perfected when the debtor receives possession of the collateral or within twenty days thereafter.",
            "Roastline filed more than twenty days after you received the machine, so it never qualified for purchase-money super-priority -- § 8.9A-322(a)(1)'s ordinary first-in-time rule controls instead, and Riverbend filed and perfected first.",
        ],
        common_mistakes=[
            "Assuming purchase-money financing always beats a prior blanket lien, regardless of timing.",
            "Assuming priority is decided by the type of creditor rather than filing/perfection dates.",
            "Assuming competing claims to the same collateral default to an even split.",
            "Signing a written confirmation of a priority conclusion without verifying the underlying filing dates.",
        ],
        difficulty=4,
        next_task_id="sim-espresso-4-default",
        prerequisite_task_id="sim-espresso-2-perfection",
        business_or_personal_context="Anna's Espresso Bar; a second, earlier-filed lender has now surfaced.",
        parties_involved=["Anna's Espresso Bar (you)", "Roastline Equipment Co.", "Riverbend Community Bank"],
        competency_id="resolve-priority-between-a-pmsi-and-an-earlier-filed-lien",
        business_effect=(
            "By verifying the real filing dates before signing anything, Anna avoids putting her name on a "
            "written statement about priority that may not hold up, while the actual ranking between "
            "Riverbend and Roastline is unaffected by anything she does."
        ),
        legal_effect=(
            "Priority between Riverbend and Roastline turns entirely on their own filing/perfection dates "
            "and the purchase-money twenty-day window -- not on the debtor's participation or agreement."
        ),
        rights_created_waived_or_preserved=(
            "By declining to sign an unverified confirmation, Anna avoids creating a written admission that "
            "could later be used against her or against whichever creditor's position it misstates."
        ),
        evidence_created_preserved_or_lost=(
            "The real filing dates and file numbers Anna requests become the actual evidence establishing "
            "which creditor has priority, rather than a signed but unverified letter."
        ),
    )

    step_4 = Task(
        task_id="sim-espresso-4-default",
        scenario=(
            "Months later, Anna's Espresso Bar has stopped making any payments to Roastline for three "
            "months and isn't returning calls. You are now the person at Roastline handling this account -- "
            "stepping into the lender's own shoes, even though Roastline's interest in the machine is "
            "subordinate to Riverbend Bank's, as you worked out in the last step. Roastline's manager asks "
            "you what the company can actually do about the machine."
        ),
        learner_role="commercial lender (Roastline Equipment Co.) -- transfer",
        objective="Decide what Roastline can actually do now that Anna's Espresso Bar has defaulted on the machine.",
        facts_provided=[
            "Anna's Espresso Bar has missed three consecutive payments and isn't responding.",
            "Roastline's security interest in the machine is perfected but subordinate to Riverbend Bank's.",
            "The machine is still in Anna's shop, in ordinary daily use.",
        ],
        hidden_or_irrelevant_facts=[
            "Roastline being subordinate in priority to Riverbend Bank doesn't change what default remedies Roastline itself may exercise against the collateral.",
        ],
        options=[
            TaskOption(
                option_id="any-means-necessary",
                label="Roastline can enter Anna's shop after hours and remove the machine by any means necessary, since Anna is in default and has no rights left.",
                is_correct=False,
                consequence="Roastline would expose itself to real liability by going beyond what self-help repossession actually permits.",
                plain_language_feedback=(
                    "Default doesn't strip the debtor of every protection. Repossession without a court order "
                    "is only allowed if it doesn't breach the peace -- forcing entry or confronting Anna doesn't qualify."
                ),
            ),
            TaskOption(
                option_id="court-only",
                label="Roastline has no real options without first getting a court judgment, since self-help repossession isn't allowed.",
                is_correct=False,
                consequence=(
                    "Roastline stays entirely safe from any breach-of-the-peace or wrongful-repossession "
                    "liability, but gives up a real, faster, equally lawful option it actually has -- a "
                    "legitimate, low-risk choice that's simply not the best one available."
                ),
                plain_language_feedback=(
                    "Judicial process is one real, safe option, but not the only one -- non-judicial "
                    "repossession is allowed too, as long as it doesn't breach the peace. Going straight to "
                    "court isn't wrong, it's just slower and more expensive than the self-help route the "
                    "statute also permits."
                ),
            ),
            TaskOption(
                option_id="public-auction-only",
                label="Roastline can take possession, but any resale of the machine must go through a public auction only -- private sales aren't allowed.",
                is_correct=False,
                consequence="Roastline would unnecessarily limit itself to one disposition method when others are equally real and available.",
                plain_language_feedback=(
                    "Disposition can be public or private, and by one or more contracts, as long as every "
                    "aspect of it is commercially reasonable -- private sales are just as real an option."
                ),
            ),
            TaskOption(
                option_id="peaceful-repossession-then-reasonable-disposition",
                label="Roastline may take possession of the machine without going to court, as long as it does so without breaching the peace, and then sell it in a commercially reasonable disposition, applying proceeds to the debt.",
                is_correct=True,
                consequence="Roastline pursues a real, bounded set of rights it actually has, without overstepping them.",
                plain_language_feedback=(
                    "This is exactly the real, bounded self-help path the statute allows: peaceful "
                    "repossession, then a commercially reasonable sale, lease, or other disposition -- public "
                    "or private."
                ),
            ),
        ],
        governing_sections=["8.9A-601", "8.9A-609", "8.9A-610"],
        professional_terminology={
            "breach of the peace": "Using force, confrontation, or unlawful entry to repossess collateral -- not allowed even after default.",
            "commercially reasonable disposition": "A sale, lease, or other disposition of collateral that is reasonable in its method, manner, time, place, and terms.",
        },
        reasoning_chain=[
            "§ 8.9A-609(a)(1),(b): after default, a secured party may take possession of the collateral either through judicial process or, without judicial process, as long as it proceeds without breach of the peace.",
            "§ 8.9A-601(a)(1),(c): these self-help rights exist alongside, not instead of, the right to sue and reduce the claim to judgment -- court process remains available, it's simply not the only real option.",
            "§ 8.9A-610(a)-(b): once Roastline has possession, it may sell, lease, license, or otherwise dispose of the machine by public or private proceedings, on any terms, as long as every aspect of the disposition is commercially reasonable.",
            "Nothing in §§ 8.9A-609 or 8.9A-610 permits breaching the peace to get the machine, or limits disposition to a public sale only -- both are real, common misreadings of a secured party's real, bounded rights.",
        ],
        common_mistakes=[
            "Assuming default eliminates every protection the debtor has, including protection against a breach of the peace.",
            "Assuming self-help repossession isn't legally available without a court order first.",
            "Assuming disposition of repossessed collateral must always be a public sale.",
        ],
        difficulty=5,
        next_task_id=None,
        prerequisite_task_id="sim-espresso-3-priority",
        business_or_personal_context="You now represent Roastline Equipment Co., the subordinate but real secured creditor in the espresso machine.",
        parties_involved=["Roastline Equipment Co. (you)", "Anna's Espresso Bar", "Riverbend Community Bank"],
        competency_id="exercise-a-secured-partys-default-remedies",
        business_effect=(
            "By repossessing peacefully and reselling commercially reasonably, Roastline recovers value "
            "from the collateral while avoiding liability for wrongful repossession."
        ),
        legal_effect=(
            "A breach of the peace during repossession, or a commercially unreasonable disposition, would "
            "expose Roastline to real damages claims from Anna, regardless of the underlying default."
        ),
        rights_created_waived_or_preserved=(
            "Anna retains a right to any surplus after the debt and expenses are satisfied, and a right to "
            "redeem before disposition -- self-help repossession doesn't erase these."
        ),
        evidence_created_preserved_or_lost=(
            "Roastline should document the peaceful repossession and the commercially reasonable "
            "disposition process, since that record is what would prove compliance if challenged later."
        ),
    )

    steps = [step_1, step_2, step_3, step_4]
    for step in steps:
        step.validate()
    return steps
