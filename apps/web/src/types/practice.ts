// Law Engine -- typed practice-items model (Live Run 1.45, Mission
// 5/V1). Mirrors services/learning.py's MultipleChoiceQuestion and
// services/document_intelligence.py's DocumentIdentificationExercise
// 1:1, same Python-owns-the-data boundary as the rest of this app.

export interface MultipleChoiceQuestion {
  item_id: string;
  type: string;
  prompt: string;
  correct_choice: string;
  why_correct: string;
  incorrect_choices: Record<string, string>;
  citation: string;
  section_id: string;
}

export interface DocumentIdentificationChoice {
  family: string;
  label: string;
  is_correct: boolean;
  explanation: string;
}

export interface DocumentMetaphor {
  metaphor: string;
  explanation: string;
}

export interface DocumentIdentificationExercise {
  exercise_id: string;
  title: string;
  hypothetical: string;
  observed_features: string[];
  choices: DocumentIdentificationChoice[];
  plain_language_summary: string;
  metaphor: DocumentMetaphor | null;
}

export interface PracticeSet {
  mcqs: MultipleChoiceQuestion[];
  document_identification_exercise: DocumentIdentificationExercise;
}
