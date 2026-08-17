// Law Engine -- typed transaction-lifecycle model (Live Run 1.38, Mission
// 17-18). Mirrors law-engine/services/transaction_lifecycle.py's
// dataclasses 1:1, same Python-owns-the-data / TypeScript-only-types-it
// boundary as types/statute.ts.

export interface LifecycleChoice {
  label: string;
  is_correct: boolean;
  outcome: string;
  section_id: string;
  citation: string;
}

export interface ChangedFactVariant {
  changed_fact: string;
  effect: string;
  section_id: string;
  citation: string;
}

export interface LifecycleStage {
  stage_id: string;
  title: string;
  facts: string;
  question: string;
  choices: LifecycleChoice[];
  explanation: string;
  section_id: string;
  citation: string;
  changed_fact_variants: ChangedFactVariant[];
}

export interface TransactionLifecycle {
  lifecycle_id: string;
  title: string;
  stages: LifecycleStage[];
}
