"use client";

// Law Engine -- interactive lifecycle runner (Live Run 1.38, Mission
// 17-18). Real client-side state: current stage, selected choice,
// correct/incorrect feedback, why-correct/why-wrong explanation, source
// citation, and a revealable changed-fact variant per stage. No network
// round trip per answer -- the whole lifecycle was already loaded
// server-side (see page.tsx) since it's small, static, per-run data.

import { useState } from "react";
import type { LifecycleChoice, TransactionLifecycle } from "@/types/lifecycle";

interface Props {
  lifecycle: TransactionLifecycle;
}

export default function LifecycleRunner({ lifecycle }: Props) {
  const [stageIndex, setStageIndex] = useState(0);
  const [selected, setSelected] = useState<LifecycleChoice | null>(null);
  const [showVariant, setShowVariant] = useState(false);

  const stage = lifecycle.stages[stageIndex];
  const isLastStage = stageIndex === lifecycle.stages.length - 1;

  function selectChoice(choice: LifecycleChoice) {
    setSelected(choice);
  }

  function nextStage() {
    setStageIndex((i) => Math.min(i + 1, lifecycle.stages.length - 1));
    setSelected(null);
    setShowVariant(false);
  }

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "2rem 1rem", fontFamily: "system-ui, sans-serif" }}>
      <h1>{lifecycle.title}</h1>
      <p style={{ color: "#555" }}>
        Stage {stageIndex + 1} of {lifecycle.stages.length}: {stage.title}
      </p>

      <p>{stage.facts}</p>
      <p style={{ fontWeight: 600 }}>{stage.question}</p>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {stage.choices.map((choice) => {
          const isChosen = selected?.label === choice.label;
          const bg = !selected ? "#fff" : isChosen ? (choice.is_correct ? "#e6f4ea" : "#fdecea") : "#fff";
          return (
            <button
              key={choice.label}
              onClick={() => selectChoice(choice)}
              disabled={selected !== null}
              style={{
                textAlign: "left",
                padding: "0.75rem",
                border: "1px solid #ccc",
                borderRadius: 6,
                background: bg,
                cursor: selected ? "default" : "pointer",
              }}
            >
              {choice.label}
            </button>
          );
        })}
      </div>

      {selected && (
        <div style={{ marginTop: "1rem", padding: "0.75rem", border: "1px solid #ccc", borderRadius: 6 }}>
          <p style={{ fontWeight: 600, color: selected.is_correct ? "#1a7431" : "#a12622" }}>
            {selected.is_correct ? "Correct." : "Not correct."}
          </p>
          <p>{selected.outcome}</p>
          <p style={{ color: "#555", fontSize: "0.9rem" }}>Source: {selected.citation}</p>

          {stage.changed_fact_variants.length > 0 && (
            <div style={{ marginTop: "0.75rem" }}>
              <button onClick={() => setShowVariant((v) => !v)} style={{ fontSize: "0.9rem" }}>
                {showVariant ? "Hide" : "Show"} what-if variant
              </button>
              {showVariant &&
                stage.changed_fact_variants.map((variant) => (
                  <div key={variant.changed_fact} style={{ marginTop: "0.5rem", paddingLeft: "0.75rem", borderLeft: "3px solid #ccc" }}>
                    <p style={{ fontStyle: "italic" }}>{variant.changed_fact}</p>
                    <p>{variant.effect}</p>
                    <p style={{ color: "#555", fontSize: "0.9rem" }}>Source: {variant.citation}</p>
                  </div>
                ))}
            </div>
          )}

          {!isLastStage && (
            <button onClick={nextStage} style={{ marginTop: "1rem" }}>
              Next stage &rarr;
            </button>
          )}
          {isLastStage && <p style={{ marginTop: "1rem", fontWeight: 600 }}>End of this lifecycle.</p>}
        </div>
      )}
    </div>
  );
}
