// Law Engine -- typed syntax-analysis model (Live Run 1.38, Mission 20).
// Mirrors SentenceAnalysis.to_dict() in services/syntax_engine.py.

export interface SentenceAnalysis {
  text: string;
  mode: string;
  modal_verbs_found: string[];
  has_conjunction: boolean;
  has_disjunction: boolean;
  has_negation: boolean;
  defined_terms_used: string[];
  is_mandatory: boolean;
  is_permissive: boolean;
  operative_terms_found: string[];
  has_conditional: boolean;
  conditional_markers_found: string[];
  has_exception: boolean;
  exception_markers_found: string[];
  cross_references: string[];
  incorporated_definitions: string[];
  is_definitional_sentence: boolean;
  potentially_undefined_terms: string[];
}

export type SyntaxAnalysisMap = Record<string, SentenceAnalysis[]>;
