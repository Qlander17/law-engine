// Real interaction/regression tests for the practice runner (Live Run
// 1.48) -- previously had zero test coverage. Covers the actual MCQ and
// document-identification state transitions, plus the button-readability
// regression guard for the Chairman-reported dark-mode visibility bug
// (see AnswerButton.module.css and LifecycleRunner.test.tsx's own
// version of this same guard).

import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import PracticeRunner from "./PracticeRunner";
import type { MultipleChoiceQuestion, DocumentIdentificationExercise } from "@/types/practice";

const MCQS: MultipleChoiceQuestion[] = [
  {
    item_id: "fixture-mcq-1",
    type: "multiple_choice",
    prompt: "Fixture question?",
    correct_choice: "Right answer",
    why_correct: "Because the fixture says so.",
    incorrect_choices: { "Wrong answer": "Because the fixture says otherwise." },
    citation: "Va. Code Ann. § 8.2-999",
    section_id: "8.2-999",
  },
];

const EXERCISE: DocumentIdentificationExercise = {
  exercise_id: "fixture-doc-id-1",
  title: "Fixture document",
  hypothetical: "A fixture hypothetical.",
  observed_features: ["Feature one"],
  choices: [
    { family: "bill_of_lading", label: "Bill of Lading", is_correct: true, explanation: "Correct explanation." },
    { family: "invoice", label: "Invoice", is_correct: false, explanation: "Incorrect explanation." },
  ],
  plain_language_summary: "A fixture summary.",
  metaphor: null,
};

describe("PracticeRunner MCQ", () => {
  it("every answer button has an explicit, readable text-color class before selection", () => {
    render(<PracticeRunner mcqs={MCQS} exercise={EXERCISE} />);
    const rightButton = screen.getByText("Right answer").closest("button")!;
    const wrongButton = screen.getByText("Wrong answer").closest("button")!;
    expect(rightButton.className).toMatch(/answerButton/);
    expect(wrongButton.className).toMatch(/answerButton/);
  });

  it("marks the chosen correct answer with the correct-state class and shows the real citation", () => {
    render(<PracticeRunner mcqs={MCQS} exercise={EXERCISE} />);
    const rightButton = screen.getByText("Right answer").closest("button")!;
    fireEvent.click(rightButton);

    expect(rightButton.className).toMatch(/answerButtonCorrect/);
    expect(screen.getByText("Correct.")).toBeInTheDocument();
    expect(screen.getByText("Because the fixture says so.")).toBeInTheDocument();
    expect(screen.getByText(/8\.2-999/)).toBeInTheDocument();
  });

  it("marks a chosen wrong answer with the incorrect-state class, not the correct-state class", () => {
    render(<PracticeRunner mcqs={MCQS} exercise={EXERCISE} />);
    const wrongButton = screen.getByText("Wrong answer").closest("button")!;
    fireEvent.click(wrongButton);

    expect(wrongButton.className).toMatch(/answerButtonIncorrect/);
    expect(wrongButton.className).not.toMatch(/answerButtonCorrect/);
    expect(screen.getByText("Not correct.")).toBeInTheDocument();
  });

  it("disables both choices once one is selected", () => {
    render(<PracticeRunner mcqs={MCQS} exercise={EXERCISE} />);
    fireEvent.click(screen.getByText("Right answer"));
    expect(screen.getByText("Right answer").closest("button")).toBeDisabled();
    expect(screen.getByText("Wrong answer").closest("button")).toBeDisabled();
  });
});

describe("PracticeRunner document identification exercise", () => {
  it("shows the real hypothetical and observed features", () => {
    render(<PracticeRunner mcqs={MCQS} exercise={EXERCISE} />);
    expect(screen.getByText("A fixture hypothetical.")).toBeInTheDocument();
    expect(screen.getByText("Feature one")).toBeInTheDocument();
  });

  it("selecting the correct document family shows correct feedback with the correct-state class", () => {
    render(<PracticeRunner mcqs={MCQS} exercise={EXERCISE} />);
    const button = screen.getByText("Bill of Lading").closest("button")!;
    fireEvent.click(button);
    expect(button.className).toMatch(/answerButtonCorrect/);
    expect(screen.getByText("Correct explanation.")).toBeInTheDocument();
  });

  it("selecting the wrong document family shows the incorrect-state class and explanation", () => {
    render(<PracticeRunner mcqs={MCQS} exercise={EXERCISE} />);
    const button = screen.getByText("Invoice").closest("button")!;
    fireEvent.click(button);
    expect(button.className).toMatch(/answerButtonIncorrect/);
    expect(screen.getByText("Incorrect explanation.")).toBeInTheDocument();
  });
});
