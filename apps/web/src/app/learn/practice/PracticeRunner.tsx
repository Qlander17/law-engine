"use client";

// Law Engine -- interactive practice runner (Live Run 1.45, Mission
// 5/V1). Real client-side state, matching the same pattern as
// ../LifecycleRunner.tsx: the real Article 2 MCQ set plus the real
// Document Identification exercise, both already tested and
// citation-grounded server-side (services/learning.py,
// services/document_intelligence.py) -- this component only adds the
// interactive answer/feedback loop, never invents content.

import { useState } from "react";
import type { MultipleChoiceQuestion, DocumentIdentificationExercise } from "@/types/practice";
import styles from "../AnswerButton.module.css";

function answerButtonClassName(chosen: boolean, isChosen: boolean, isCorrectChoice: boolean): string {
  if (!chosen || !isChosen) return styles.answerButton;
  return `${styles.answerButton} ${isCorrectChoice ? styles.answerButtonCorrect : styles.answerButtonIncorrect}`;
}

interface Props {
  mcqs: MultipleChoiceQuestion[];
  exercise: DocumentIdentificationExercise;
}

function McqItem({ mcq }: { mcq: MultipleChoiceQuestion }) {
  const [chosen, setChosen] = useState<string | null>(null);
  const isCorrect = chosen === mcq.correct_choice;
  const explanation = chosen === null ? null : chosen === mcq.correct_choice ? mcq.why_correct : mcq.incorrect_choices[chosen];

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 6, padding: "1rem", marginBottom: "1rem" }}>
      <p style={{ fontWeight: 600 }}>{mcq.prompt}</p>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {[mcq.correct_choice, ...Object.keys(mcq.incorrect_choices)].map((choice) => {
          const isChosen = chosen === choice;
          return (
            <button
              key={choice}
              onClick={() => setChosen(choice)}
              disabled={chosen !== null}
              className={answerButtonClassName(chosen !== null, isChosen, choice === mcq.correct_choice)}
            >
              {choice}
            </button>
          );
        })}
      </div>
      {chosen && (
        <div style={{ marginTop: "0.75rem" }}>
          <p style={{ fontWeight: 600, color: isCorrect ? "#1a7431" : "#a12622" }}>{isCorrect ? "Correct." : "Not correct."}</p>
          <p>{explanation}</p>
          <p style={{ color: "#555", fontSize: "0.9rem" }}>Source: {mcq.citation}</p>
        </div>
      )}
    </div>
  );
}

function DocumentExercise({ exercise }: { exercise: DocumentIdentificationExercise }) {
  const [chosen, setChosen] = useState<string | null>(null);
  const chosenChoice = exercise.choices.find((c) => c.family === chosen) ?? null;

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 6, padding: "1rem" }}>
      <h3 style={{ marginTop: 0 }}>{exercise.title}</h3>
      <p>{exercise.hypothetical}</p>
      <ul>
        {exercise.observed_features.map((f) => (
          <li key={f}>{f}</li>
        ))}
      </ul>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {exercise.choices.map((choice) => {
          const isChosen = chosen === choice.family;
          return (
            <button
              key={choice.family}
              onClick={() => setChosen(choice.family)}
              disabled={chosen !== null}
              className={answerButtonClassName(chosen !== null, isChosen, choice.is_correct)}
            >
              {choice.label}
            </button>
          );
        })}
      </div>
      {chosenChoice && (
        <div style={{ marginTop: "0.75rem" }}>
          <p style={{ fontWeight: 600, color: chosenChoice.is_correct ? "#1a7431" : "#a12622" }}>
            {chosenChoice.is_correct ? "Correct." : "Not correct."}
          </p>
          <p>{chosenChoice.explanation}</p>
          {exercise.metaphor && <p style={{ color: "#555", fontStyle: "italic" }}>{exercise.metaphor.metaphor} — {exercise.metaphor.explanation}</p>}
        </div>
      )}
    </div>
  );
}

export default function PracticeRunner({ mcqs, exercise }: Props) {
  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "2rem 1rem", fontFamily: "system-ui, sans-serif" }}>
      <h1>Practice: Article 2</h1>
      <h2>Multiple choice</h2>
      {mcqs.map((mcq) => (
        <McqItem key={mcq.item_id} mcq={mcq} />
      ))}
      <h2>Document identification</h2>
      <DocumentExercise exercise={exercise} />
    </div>
  );
}
