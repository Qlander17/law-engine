"""Law Engine -- Syntax Engine foundation + II (Live Run 1.37 Mission 21;
expanded Live Run 1.38 Mission 19).

A real, extensible grammatical/structural analysis tool for legal text --
identifies modal verbs, conjunctions/disjunctions, negations, defined-term
usage, conditionals, exceptions, cross-references, incorporated
definitions, and the small operative terms ("is", "and", "or", "shall",
"may", "must", "means", "includes") Mission 19 specifically called out.
Useful for genuinely mainstream purposes: statutory interpretation,
spotting ambiguous "and"/"or" scope, flagging where a term looks like it's
being used as a defined term without actually being defined,
distinguishing mandatory ("shall"/"must") from permissive ("may")
language -- all real, standard tools of legal drafting/interpretation,
applicable to any statute (including the real UCC sections already
ingested).

Real, disclosed scope decision: this module analyzes grammatical
STRUCTURE via word/phrase-pattern matching, not a real parser -- it does
NOT identify subject/predicate/object (that requires real POS tagging/
dependency parsing, which this deterministic, no-ML-dependency module
does not attempt). An earlier draft of this docstring claimed
subject/predicate/object identification that was never actually
implemented; that claim is removed here rather than carried forward.

Real, disclosed scope decision (confirmed with the Chairman, Live Run
1.37): this module analyzes grammatical STRUCTURE only. It does not
implement, assert, or output "David-Wynn: Miller / CSSCPSG-style"
constructions as a legally effective technique, and it is never wired to
any wizard or workflow that would present its output as a courtroom
tactic. Per this run's own instruction ("do not assert Miller's system as
authoritative"), MILLER_STYLE remains a real, selectable analysis MODE for
future research/comparison -- e.g., studying how that framework parses a
sentence differently from standard grammar -- not a default, not a
recommendation, and not connected to any real legal advice or filing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

MODAL_VERBS = ("shall", "may", "must", "will", "should", "can", "might")
CONJUNCTIONS = ("and",)
DISJUNCTIONS = ("or",)
NEGATIONS = ("not", "no", "never", "none", "n't")

# Mission 19's own explicit callout list of small, easy-to-skim-past
# operative terms. Distinct from MODAL_VERBS/CONJUNCTIONS/etc. above --
# this is a flat surface for "which of these known-important small words
# appear here", independent of which specific category each belongs to.
OPERATIVE_TERMS = ("is", "and", "or", "shall", "may", "must", "means", "includes")

# Terms that, when they appear right after a candidate term, signal THIS
# sentence is a definition of that term (not just a use of it).
DEFINITIONAL_MARKERS = ("means", "includes")

CONDITIONAL_MARKERS = ("if", "unless", "provided that", "when", "where", "except as provided")
EXCEPTION_MARKERS = ("except", "unless", "other than", "notwithstanding", "save as provided")

# Real, deterministic cross-reference patterns -- statutory section
# citations and same-document scope references. Intentionally narrow
# (exact patterns, not a general NER model) so every match is explainable.
_CROSS_REFERENCE_PATTERNS = (
    re.compile(r"§+\s?\d[\w.\-]*"),
    re.compile(r"\bSection\s+\d[\w.\-]*", re.IGNORECASE),
    re.compile(r"\bsubsection\s+\([a-zA-Z0-9]+\)", re.IGNORECASE),
    re.compile(r"\bthis\s+(article|chapter|title|section|subsection)\b", re.IGNORECASE),
)

# "As defined in ...", "has the meaning set forth in ...", "within the
# meaning of ..." -- a definition borrowed from elsewhere rather than
# given inline. Distinct from DEFINITIONAL_MARKERS, which flags an
# inline definition being made right here.
_INCORPORATED_DEFINITION_PATTERN = re.compile(
    r"(as defined in [^,.;]+|has the meaning (?:set forth|given) in [^,.;]+|within the meaning of [^,.;]+)",
    re.IGNORECASE,
)

# Quoted terms ("merchant", 'goods') are the standard statutory-drafting
# signal for "this is a defined term". A quoted term that ISN'T in the
# caller's known_defined_terms list is a real, actionable flag: either
# the term is defined somewhere this analysis wasn't told about, or the
# statute is using quotation marks for emphasis rather than definition --
# either way, worth surfacing rather than silently ignoring.
_QUOTED_TERM_PATTERN = re.compile(r'["“]([a-zA-Z][a-zA-Z \-]*)["”]')


class AnalysisMode(str, Enum):
    """Real, distinct analysis modes (Mission 21). Only STANDARD_LANGUAGE
    and STATUTORY_LEGAL are implemented with real logic this run;
    HISTORICAL_GRAMMAR, MILLER_STYLE, and COURT_CONSTRUCTION_COMPARISON are
    named/reserved for future work, not implemented, and never silently
    treated as equivalent to a real, standard grammatical analysis."""

    STANDARD_LANGUAGE_PARSE = "STANDARD_LANGUAGE_PARSE"
    STATUTORY_LEGAL_PARSE = "STATUTORY_LEGAL_PARSE"
    HISTORICAL_GRAMMAR = "HISTORICAL_GRAMMAR"
    MILLER_STYLE_ANALYSIS = "MILLER_STYLE_ANALYSIS"
    COURT_CONSTRUCTION_COMPARISON = "COURT_CONSTRUCTION_COMPARISON"


_UNIMPLEMENTED_MODES = (
    AnalysisMode.HISTORICAL_GRAMMAR,
    AnalysisMode.MILLER_STYLE_ANALYSIS,
    AnalysisMode.COURT_CONSTRUCTION_COMPARISON,
)


class SyntaxEngineError(Exception):
    """Raised for real, unrecoverable syntax-analysis errors."""


@dataclass
class SentenceAnalysis:
    text: str
    mode: AnalysisMode
    modal_verbs_found: list[str] = field(default_factory=list)
    has_conjunction: bool = False
    has_disjunction: bool = False
    has_negation: bool = False
    defined_terms_used: list[str] = field(default_factory=list)
    is_mandatory: bool = False
    is_permissive: bool = False
    # Mission 19 additions below.
    operative_terms_found: list[str] = field(default_factory=list)
    has_conditional: bool = False
    conditional_markers_found: list[str] = field(default_factory=list)
    has_exception: bool = False
    exception_markers_found: list[str] = field(default_factory=list)
    cross_references: list[str] = field(default_factory=list)
    incorporated_definitions: list[str] = field(default_factory=list)
    is_definitional_sentence: bool = False
    potentially_undefined_terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "mode": self.mode.value,
            "modal_verbs_found": self.modal_verbs_found,
            "has_conjunction": self.has_conjunction,
            "has_disjunction": self.has_disjunction,
            "has_negation": self.has_negation,
            "defined_terms_used": self.defined_terms_used,
            "is_mandatory": self.is_mandatory,
            "is_permissive": self.is_permissive,
            "operative_terms_found": self.operative_terms_found,
            "has_conditional": self.has_conditional,
            "conditional_markers_found": self.conditional_markers_found,
            "has_exception": self.has_exception,
            "exception_markers_found": self.exception_markers_found,
            "cross_references": self.cross_references,
            "incorporated_definitions": self.incorporated_definitions,
            "is_definitional_sentence": self.is_definitional_sentence,
            "potentially_undefined_terms": self.potentially_undefined_terms,
        }


def _find_words(text: str, words: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [w for w in words if re.search(rf"\b{re.escape(w)}\b", lowered)]


def analyze_sentence(
    text: str,
    *,
    mode: AnalysisMode = AnalysisMode.STATUTORY_LEGAL_PARSE,
    known_defined_terms: list[str] | None = None,
) -> SentenceAnalysis:
    """Real, deterministic structural analysis -- no model call, fully
    reviewable. Raises for the explicitly-reserved-not-implemented modes
    rather than silently returning an empty/misleading result."""
    if mode in _UNIMPLEMENTED_MODES:
        raise SyntaxEngineError(
            f"{mode.value} is a real, reserved analysis mode for future "
            "research, not implemented this run -- see this module's own "
            "docstring for why (Live Run 1.37, Mission 21 scope decision)."
        )
    if not text.strip():
        raise SyntaxEngineError("text must be real, non-empty text to analyze.")

    modals = _find_words(text, MODAL_VERBS)
    defined_terms = known_defined_terms or []
    used_terms = [t for t in defined_terms if re.search(rf"\b{re.escape(t)}\b", text.lower())]

    conditional_markers = _find_words(text, CONDITIONAL_MARKERS)
    exception_markers = _find_words(text, EXCEPTION_MARKERS)
    cross_references = [
        m.group(0) for pattern in _CROSS_REFERENCE_PATTERNS for m in pattern.finditer(text)
    ]
    incorporated_definitions = [m.group(0) for m in _INCORPORATED_DEFINITION_PATTERN.finditer(text)]

    definitional_hits = _find_words(text, DEFINITIONAL_MARKERS)
    quoted_terms = [m.group(1).strip() for m in _QUOTED_TERM_PATTERN.finditer(text)]
    known_lower = {t.lower() for t in defined_terms}
    potentially_undefined = [t for t in quoted_terms if t.lower() not in known_lower]

    return SentenceAnalysis(
        text=text,
        mode=mode,
        modal_verbs_found=modals,
        has_conjunction=bool(_find_words(text, CONJUNCTIONS)),
        has_disjunction=bool(_find_words(text, DISJUNCTIONS)),
        has_negation=bool(_find_words(text, NEGATIONS)),
        defined_terms_used=used_terms,
        is_mandatory=any(m in modals for m in ("shall", "must")),
        is_permissive="may" in modals,
        operative_terms_found=_find_words(text, OPERATIVE_TERMS),
        has_conditional=bool(conditional_markers),
        conditional_markers_found=conditional_markers,
        has_exception=bool(exception_markers),
        exception_markers_found=exception_markers,
        cross_references=cross_references,
        incorporated_definitions=incorporated_definitions,
        is_definitional_sentence=bool(definitional_hits) and bool(quoted_terms),
        potentially_undefined_terms=potentially_undefined,
    )
