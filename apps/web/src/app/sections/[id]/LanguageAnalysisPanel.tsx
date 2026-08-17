"use client";

// Law Engine -- "Analyze Language" panel (Live Run 1.38, Mission 20).
// PLAIN LANGUAGE / SYNTAX / DEFINED TERMS / CROSS REFERENCES views over
// one section's real paragraphs and their precomputed SentenceAnalysis
// records (services/syntax_analysis_export.py). AUTHORITY and
// VERIFICATION STATUS views from Mission 20's suggested list are not
// included here -- SourceManifest tracks those per source DOCUMENT, not
// per individual section, in this codebase's current data model (see
// services/models.py); showing them here would mean fabricating a
// section-level value the system doesn't actually have. That's a real,
// disclosed gap, not an oversight.

import { useState } from "react";
import type { StatuteSection } from "@/types/statute";
import type { SentenceAnalysis } from "@/types/syntaxAnalysis";

type View = "PLAIN_LANGUAGE" | "SYNTAX" | "DEFINED_TERMS" | "CROSS_REFERENCES";

interface Props {
  section: StatuteSection;
  analysis: SentenceAnalysis[];
}

const VIEWS: { key: View; label: string }[] = [
  { key: "PLAIN_LANGUAGE", label: "Plain language" },
  { key: "SYNTAX", label: "Syntax" },
  { key: "DEFINED_TERMS", label: "Defined terms" },
  { key: "CROSS_REFERENCES", label: "Cross references" },
];

export default function LanguageAnalysisPanel({ section, analysis }: Props) {
  const [open, setOpen] = useState(false);
  const [view, setView] = useState<View>("PLAIN_LANGUAGE");

  return (
    <div style={{ marginTop: "1.5rem", borderTop: "1px solid #ddd", paddingTop: "1rem" }}>
      <button onClick={() => setOpen((o) => !o)}>{open ? "Hide" : "Analyze language"}</button>
      {open && (
        <div style={{ marginTop: "0.75rem" }}>
          <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem" }}>
            {VIEWS.map((v) => (
              <button
                key={v.key}
                onClick={() => setView(v.key)}
                style={{ fontWeight: view === v.key ? 700 : 400 }}
              >
                {v.label}
              </button>
            ))}
          </div>

          {view === "PLAIN_LANGUAGE" &&
            section.paragraphs.map((p, i) => <p key={i}>{p}</p>)}

          {view === "SYNTAX" &&
            analysis.map((a, i) => (
              <div key={i} style={{ marginBottom: "1rem", fontSize: "0.9rem" }}>
                <p>{a.text}</p>
                <ul style={{ color: "#555", paddingLeft: "1.25rem" }}>
                  {a.operative_terms_found.length > 0 && <li>Operative terms: {a.operative_terms_found.join(", ")}</li>}
                  {a.is_mandatory && <li>Mandatory (shall/must)</li>}
                  {a.is_permissive && <li>Permissive (may)</li>}
                  {a.has_conditional && <li>Conditional: {a.conditional_markers_found.join(", ")}</li>}
                  {a.has_exception && <li>Exception: {a.exception_markers_found.join(", ")}</li>}
                  {a.has_negation && <li>Negation present</li>}
                  {a.is_definitional_sentence && <li>Defines a term inline</li>}
                  {a.incorporated_definitions.length > 0 && <li>Incorporated definition: {a.incorporated_definitions.join("; ")}</li>}
                  {a.potentially_undefined_terms.length > 0 && (
                    <li>Quoted but not in this section&apos;s known defined terms: {a.potentially_undefined_terms.join(", ")}</li>
                  )}
                </ul>
              </div>
            ))}

          {view === "DEFINED_TERMS" &&
            (section.defined_terms.length > 0 ? (
              <ul>
                {section.defined_terms.map((t) => (
                  <li key={t}>{t}</li>
                ))}
              </ul>
            ) : (
              <p>No defined terms recorded for this section.</p>
            ))}

          {view === "CROSS_REFERENCES" &&
            (section.cross_references.length > 0 ? (
              <ul>
                {section.cross_references.map((r) => (
                  <li key={r}>§ {r}</li>
                ))}
              </ul>
            ) : (
              <p>No cross-references recorded for this section.</p>
            ))}
        </div>
      )}
    </div>
  );
}
