// Real transaction-state-transition tests for the interactive lifecycle
// runner (Live Run 1.39, Mission 19) -- not trivial render snapshots.
// Exercises the actual state machine: selecting a choice, seeing
// correct/incorrect feedback with its real citation, revealing a
// changed-fact variant, and advancing to the next stage.

import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import LifecycleRunner from "./LifecycleRunner";
import type { TransactionLifecycle } from "@/types/lifecycle";

const FIXTURE: TransactionLifecycle = {
  lifecycle_id: "fixture-v1",
  title: "Fixture Lifecycle",
  stages: [
    {
      stage_id: "stage-one",
      title: "First stage",
      facts: "Some facts about stage one.",
      question: "Is the correct answer correct?",
      choices: [
        {
          label: "Yes, this is correct",
          is_correct: true,
          outcome: "Because the rule says so.",
          section_id: "8.2-999",
          citation: "Va. Code Ann. § 8.2-999",
        },
        {
          label: "No, this is wrong",
          is_correct: false,
          outcome: "Because the rule says otherwise.",
          section_id: "8.2-999",
          citation: "Va. Code Ann. § 8.2-999",
        },
      ],
      explanation: "Explanation text.",
      section_id: "8.2-999",
      citation: "Va. Code Ann. § 8.2-999",
      changed_fact_variants: [
        {
          changed_fact: "What if a fact changed?",
          effect: "The outcome would differ.",
          section_id: "8.2-998",
          citation: "Va. Code Ann. § 8.2-998",
        },
      ],
    },
    {
      stage_id: "stage-two",
      title: "Second stage",
      facts: "Some facts about stage two.",
      question: "Final question?",
      choices: [
        {
          label: "Final correct answer",
          is_correct: true,
          outcome: "Final outcome.",
          section_id: "8.2-997",
          citation: "Va. Code Ann. § 8.2-997",
        },
      ],
      explanation: "Final explanation.",
      section_id: "8.2-997",
      citation: "Va. Code Ann. § 8.2-997",
      changed_fact_variants: [],
    },
  ],
};

describe("LifecycleRunner", () => {
  it("shows the first stage's facts and question before any answer is selected", () => {
    render(<LifecycleRunner lifecycle={FIXTURE} />);
    expect(screen.getByText("Some facts about stage one.")).toBeInTheDocument();
    expect(screen.getByText("Is the correct answer correct?")).toBeInTheDocument();
    expect(screen.queryByText("Because the rule says so.")).not.toBeInTheDocument();
  });

  it("reveals correct feedback and its citation when the correct choice is selected", () => {
    render(<LifecycleRunner lifecycle={FIXTURE} />);
    fireEvent.click(screen.getByText("Yes, this is correct"));
    expect(screen.getByText("Correct.")).toBeInTheDocument();
    expect(screen.getByText("Because the rule says so.")).toBeInTheDocument();
    expect(screen.getByText(/Va\. Code Ann\. § 8\.2-999/)).toBeInTheDocument();
  });

  it("reveals incorrect feedback when a wrong choice is selected", () => {
    render(<LifecycleRunner lifecycle={FIXTURE} />);
    fireEvent.click(screen.getByText("No, this is wrong"));
    expect(screen.getByText("Not correct.")).toBeInTheDocument();
    expect(screen.getByText("Because the rule says otherwise.")).toBeInTheDocument();
  });

  it("disables all choices after one is selected, so the answer can't be changed", () => {
    render(<LifecycleRunner lifecycle={FIXTURE} />);
    fireEvent.click(screen.getByText("Yes, this is correct"));
    expect(screen.getByText("No, this is wrong").closest("button")).toBeDisabled();
    expect(screen.getByText("Yes, this is correct").closest("button")).toBeDisabled();
  });

  it("reveals a changed-fact variant only after the toggle is clicked", () => {
    render(<LifecycleRunner lifecycle={FIXTURE} />);
    fireEvent.click(screen.getByText("Yes, this is correct"));
    expect(screen.queryByText("What if a fact changed?")).not.toBeInTheDocument();
    fireEvent.click(screen.getByText("Show what-if variant"));
    expect(screen.getByText("What if a fact changed?")).toBeInTheDocument();
    expect(screen.getByText("The outcome would differ.")).toBeInTheDocument();
  });

  it("advances to the next stage and resets selection state", () => {
    render(<LifecycleRunner lifecycle={FIXTURE} />);
    fireEvent.click(screen.getByText("Yes, this is correct"));
    fireEvent.click(screen.getByText(/Next stage/));

    expect(screen.getByText("Some facts about stage two.")).toBeInTheDocument();
    expect(screen.queryByText("Because the rule says so.")).not.toBeInTheDocument();
    expect(screen.getByText("Final correct answer").closest("button")).not.toBeDisabled();
  });

  it("shows an end-of-lifecycle message on the last stage instead of a next-stage button", () => {
    render(<LifecycleRunner lifecycle={FIXTURE} />);
    fireEvent.click(screen.getByText("Yes, this is correct"));
    fireEvent.click(screen.getByText(/Next stage/));
    fireEvent.click(screen.getByText("Final correct answer"));

    expect(screen.getByText("End of this lifecycle.")).toBeInTheDocument();
    expect(screen.queryByText(/Next stage/)).not.toBeInTheDocument();
  });

  // Live Run 1.48 regression guard: the real, Chairman-observed bug was
  // answer buttons carrying an explicit light background with NO explicit
  // text color, so a dark-mode browser's own default (light) button text
  // rendered invisible against it until the button became disabled. Every
  // answer button must always carry the shared, explicit-color class --
  // never fall back to an unstyled <button> with only a background set.
  it("every answer button always has an explicit, readable text-color class -- before and after selection", () => {
    render(<LifecycleRunner lifecycle={FIXTURE} />);
    const yesButton = screen.getByText("Yes, this is correct").closest("button")!;
    const noButton = screen.getByText("No, this is wrong").closest("button")!;

    expect(yesButton.className).toMatch(/answerButton/);
    expect(noButton.className).toMatch(/answerButton/);

    fireEvent.click(yesButton);

    // The chosen, correct button gets the correct-state class (still an
    // explicit, readable color); the unchosen button reverts to the plain
    // answerButton class -- never becomes a bare, uncolored <button>.
    expect(yesButton.className).toMatch(/answerButtonCorrect/);
    expect(noButton.className).toMatch(/answerButton/);
    expect(noButton.className).not.toMatch(/answerButtonCorrect|answerButtonIncorrect/);
  });

  it("marks the chosen wrong answer with the incorrect-state class, not the correct-state class", () => {
    render(<LifecycleRunner lifecycle={FIXTURE} />);
    const noButton = screen.getByText("No, this is wrong").closest("button")!;
    fireEvent.click(noButton);
    expect(noButton.className).toMatch(/answerButtonIncorrect/);
    expect(noButton.className).not.toMatch(/answerButtonCorrect/);
  });
});
