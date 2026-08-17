// Law Engine -- Task Ladder types (Live Run 1.48). Mirrors
// services/tasks.py's Task/TaskOption 1:1, same Python-owns-the-data
// boundary as every other type in this directory.

export interface TaskOption {
  option_id: string;
  label: string;
  is_correct: boolean;
  consequence: string;
  plain_language_feedback: string;
}

export interface Task {
  task_id: string;
  scenario: string;
  learner_role: string;
  objective: string;
  facts_provided: string[];
  options: TaskOption[];
  governing_sections: string[];
  governing_citations: string[];
  professional_terminology: Record<string, string>;
  reasoning_chain: string[];
  common_mistakes: string[];
  documents_provided: string[];
  hidden_or_irrelevant_facts: string[];
  difficulty: number;
  next_task_id: string | null;
  prerequisite_task_id: string | null;
}

export interface TaskLadder {
  ladder_id: string;
  title: string;
  tasks: Task[];
}
