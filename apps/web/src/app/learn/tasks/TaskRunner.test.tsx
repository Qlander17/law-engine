// Real interaction tests for the Task Ladder runner (Live Run 1.48).

import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import TaskRunner from "./TaskRunner";
import type { TaskLadder } from "@/types/task";

const LADDER: TaskLadder = {
  ladder_id: "fixture-ladder",
  title: "Fixture Ladder",
  tasks: [
    {
      task_id: "fixture-t1",
      scenario: "Fixture scenario one.",
      learner_role: "ordinary consumer",
      objective: "Fixture objective one.",
      facts_provided: ["Fact one."],
      options: [
        { option_id: "right", label: "Right answer", is_correct: true, consequence: "Good outcome.", plain_language_feedback: "Correct because fixture." },
        { option_id: "wrong", label: "Wrong answer", is_correct: false, consequence: "Bad outcome.", plain_language_feedback: "Wrong because fixture." },
      ],
      governing_sections: ["8.2-102"],
      governing_citations: ["Va. Code Ann. § 8.2-102"],
      professional_terminology: { goods: "A fixture gloss." },
      reasoning_chain: ["Step one."],
      common_mistakes: ["A common mistake."],
      documents_provided: [],
      hidden_or_irrelevant_facts: [],
      difficulty: 1,
      next_task_id: "fixture-t2",
      prerequisite_task_id: null,
    },
    {
      task_id: "fixture-t2",
      scenario: "Fixture scenario two.",
      learner_role: "small-business buyer",
      objective: "Fixture objective two.",
      facts_provided: [],
      options: [
        { option_id: "a", label: "Option A", is_correct: true, consequence: "Consequence A.", plain_language_feedback: "Feedback A." },
        { option_id: "b", label: "Option B", is_correct: false, consequence: "Consequence B.", plain_language_feedback: "Feedback B." },
      ],
      governing_sections: ["8.2-104"],
      governing_citations: ["Va. Code Ann. § 8.2-104"],
      professional_terminology: {},
      reasoning_chain: [],
      common_mistakes: [],
      documents_provided: [],
      hidden_or_irrelevant_facts: [],
      difficulty: 2,
      next_task_id: null,
      prerequisite_task_id: "fixture-t1",
    },
  ],
};

describe("TaskRunner", () => {
  it("shows the first task's scenario, role, and objective before any interaction", () => {
    render(<TaskRunner ladder={LADDER} />);
    expect(screen.getByText("Fixture scenario one.")).toBeInTheDocument();
    expect(screen.getByText(/ordinary consumer/)).toBeInTheDocument();
    expect(screen.getByText("Fixture objective one.")).toBeInTheDocument();
  });

  it("does not reveal feedback, terminology, or authority until an option is chosen", () => {
    render(<TaskRunner ladder={LADDER} />);
    expect(screen.queryByText("Correct because fixture.")).not.toBeInTheDocument();
    expect(screen.queryByText(/Va\. Code Ann\. § 8\.2-102/)).not.toBeInTheDocument();
  });

  it("choosing an option reveals consequence, feedback, terminology, and real governing authority", () => {
    render(<TaskRunner ladder={LADDER} />);
    fireEvent.click(screen.getByText("Right answer"));

    expect(screen.getByText("Good outcome.")).toBeInTheDocument();
    expect(screen.getByText("Correct because fixture.")).toBeInTheDocument();
    expect(screen.getByText(/A fixture gloss\./)).toBeInTheDocument();
    expect(screen.getByText(/Va\. Code Ann\. § 8\.2-102/)).toBeInTheDocument();
    expect(screen.getByText("Step one.")).toBeInTheDocument();
    expect(screen.getByText("A common mistake.")).toBeInTheDocument();
  });

  it("both options carry the shared, readable answer-button class before and after selection", () => {
    render(<TaskRunner ladder={LADDER} />);
    const right = screen.getByText("Right answer").closest("button")!;
    const wrong = screen.getByText("Wrong answer").closest("button")!;
    expect(right.className).toMatch(/answerButton/);
    fireEvent.click(right);
    expect(right.className).toMatch(/answerButtonCorrect/);
    expect(wrong.className).not.toMatch(/answerButtonCorrect|answerButtonIncorrect/);
  });

  it("advances to the next task and resets selection state", () => {
    render(<TaskRunner ladder={LADDER} />);
    fireEvent.click(screen.getByText("Right answer"));
    fireEvent.click(screen.getByText(/Next task/));

    expect(screen.getByText("Fixture scenario two.")).toBeInTheDocument();
    expect(screen.queryByText("Good outcome.")).not.toBeInTheDocument();
  });

  it("shows an end-of-ladder message on the last task instead of a next-task button", () => {
    render(<TaskRunner ladder={LADDER} />);
    fireEvent.click(screen.getByText("Right answer"));
    fireEvent.click(screen.getByText(/Next task/));
    fireEvent.click(screen.getByText("Option A"));

    expect(screen.getByText("End of this task ladder.")).toBeInTheDocument();
    expect(screen.queryByText(/Next task/)).not.toBeInTheDocument();
  });
});
