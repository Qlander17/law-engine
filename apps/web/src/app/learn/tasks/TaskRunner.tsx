"use client";

// Law Engine -- Task Ladder runner (Live Run 1.48). Real implementation
// of the Task-First pedagogical cycle
// (docs/task-first-pedagogy-and-task-ladder-architecture.md): the
// learner reads the scenario/role/facts, DOES something (picks an
// option) before seeing any explanation, then observes the consequence,
// gets plain-language feedback, sees professional terminology and the
// real governing authority, and can advance to the next task. Reuses
// AnswerButton.module.css for the option buttons -- same shared,
// explicit-color styling as LifecycleRunner/PracticeRunner (Live Run
// 1.48's own dark-mode readability fix), not a new, parallel style.

import { useState } from "react";
import type { Task, TaskLadder } from "@/types/task";
import styles from "../AnswerButton.module.css";

interface Props {
  ladder: TaskLadder;
}

function answerButtonClassName(chosen: boolean, isChosen: boolean, isCorrectChoice: boolean): string {
  if (!chosen || !isChosen) return styles.answerButton;
  return `${styles.answerButton} ${isCorrectChoice ? styles.answerButtonCorrect : styles.answerButtonIncorrect}`;
}

function TaskView({ task, onAdvance, hasNext }: { task: Task; onAdvance: () => void; hasNext: boolean }) {
  const [chosenId, setChosenId] = useState<string | null>(null);
  const chosen = task.options.find((o) => o.option_id === chosenId) ?? null;

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 6, padding: "1.25rem", marginBottom: "1rem" }}>
      <p style={{ color: "#555", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.03em" }}>
        Your role: {task.learner_role} &middot; Difficulty {task.difficulty}
      </p>
      <h2 style={{ marginTop: "0.25rem" }}>{task.objective}</h2>
      <p>{task.scenario}</p>

      {task.facts_provided.length > 0 && (
        <div style={{ marginTop: "0.75rem" }}>
          <p style={{ fontWeight: 600 }}>Facts</p>
          <ul>
            {task.facts_provided.map((f) => (
              <li key={f}>{f}</li>
            ))}
          </ul>
        </div>
      )}

      {task.documents_provided.length > 0 && (
        <div style={{ marginTop: "0.5rem" }}>
          <p style={{ fontWeight: 600 }}>Documents</p>
          <ul>
            {task.documents_provided.map((d) => (
              <li key={d}>{d}</li>
            ))}
          </ul>
        </div>
      )}

      <p style={{ fontWeight: 600, marginTop: "1rem" }}>What do you do?</p>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {task.options.map((option) => (
          <button
            key={option.option_id}
            onClick={() => setChosenId(option.option_id)}
            disabled={chosenId !== null}
            className={answerButtonClassName(chosenId !== null, chosenId === option.option_id, option.is_correct)}
          >
            {option.label}
          </button>
        ))}
      </div>

      {chosen && (
        <div style={{ marginTop: "1rem", padding: "0.75rem", border: "1px solid #ccc", borderRadius: 6 }}>
          <p style={{ fontWeight: 600, color: chosen.is_correct ? "#14532d" : "#7f1d1d" }}>
            {chosen.is_correct ? "Correct." : "Not quite."}
          </p>
          <p style={{ marginTop: "0.5rem" }}>
            <strong>What happens:</strong> {chosen.consequence}
          </p>
          <p style={{ marginTop: "0.5rem" }}>{chosen.plain_language_feedback}</p>

          {Object.keys(task.professional_terminology).length > 0 && (
            <div style={{ marginTop: "0.75rem" }}>
              <p style={{ fontWeight: 600 }}>Terminology</p>
              <ul>
                {Object.entries(task.professional_terminology).map(([term, gloss]) => (
                  <li key={term}>
                    <strong>{term}</strong> &mdash; {gloss}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div style={{ marginTop: "0.75rem" }}>
            <p style={{ fontWeight: 600 }}>Governing authority</p>
            <p style={{ color: "#555" }}>{task.governing_citations.join("; ")}</p>
            {task.reasoning_chain.length > 0 && (
              <ol>
                {task.reasoning_chain.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            )}
          </div>

          {task.common_mistakes.length > 0 && (
            <div style={{ marginTop: "0.75rem" }}>
              <p style={{ fontWeight: 600 }}>Common mistakes</p>
              <ul>
                {task.common_mistakes.map((m) => (
                  <li key={m}>{m}</li>
                ))}
              </ul>
            </div>
          )}

          {hasNext && (
            <button onClick={onAdvance} style={{ marginTop: "1rem" }}>
              Next task &rarr;
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default function TaskRunner({ ladder }: Props) {
  const [taskIndex, setTaskIndex] = useState(0);
  const task = ladder.tasks[taskIndex];
  const isLastTask = taskIndex === ladder.tasks.length - 1;

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "2rem 1rem", fontFamily: "system-ui, sans-serif" }}>
      <h1>{ladder.title}</h1>
      <p style={{ color: "#555" }}>
        Task {taskIndex + 1} of {ladder.tasks.length}
      </p>

      <TaskView
        key={task.task_id}
        task={task}
        hasNext={!isLastTask}
        onAdvance={() => setTaskIndex((i) => Math.min(i + 1, ladder.tasks.length - 1))}
      />

      {isLastTask && (
        <p style={{ marginTop: "1rem", fontStyle: "italic" }}>
          End of this task ladder.
        </p>
      )}
    </div>
  );
}
