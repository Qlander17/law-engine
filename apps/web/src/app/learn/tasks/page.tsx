// Law Engine -- /learn/tasks (Live Run 1.48; ladder picker added Live
// Run 1.49). Server Component: loads the real, precomputed Task Ladder
// JSON, hands it to the interactive client component -- same pattern as
// ../practice/page.tsx and ../page.tsx's own lifecycle picker.

import Link from "next/link";
import { getTaskLadder } from "@/lib/lawEngineData";
import TaskRunner from "./TaskRunner";

const LADDERS = [
  { file: "article-2-consumer-to-operator-ladder.json", label: "Article 2: Consumer to Operator (4 tasks)" },
  { file: "riverside-bistro-simulation.json", label: "Riverside Bistro: A Real-World Simulation (3 steps)" },
  { file: "espresso-bar-financing-simulation.json", label: "Anna's Espresso Bar: A Secured Transactions Simulation (4 steps)" },
  { file: "freelance-note-simulation.json", label: "Jamie's Freelance Note: A Negotiable Instruments Simulation (4 steps)" },
];

export default async function TasksPage({
  searchParams,
}: {
  searchParams: Promise<{ ladder?: string }>;
}) {
  const resolvedSearchParams = await searchParams;
  const requestedFile = resolvedSearchParams.ladder ?? LADDERS[0].file;
  const known = LADDERS.some((l) => l.file === requestedFile);
  const ladderFile = known ? requestedFile : LADDERS[0].file;
  const ladder = await getTaskLadder(ladderFile);

  return (
    <div>
      <nav style={{ maxWidth: 760, margin: "1rem auto 0", padding: "0 1rem", fontFamily: "system-ui, sans-serif" }}>
        <p style={{ marginBottom: "0.5rem" }}>
          <Link href="/learn">&larr; Learn</Link>
        </p>
        <p style={{ fontSize: "0.9rem", color: "#555" }}>
          {LADDERS.map((l, i) => (
            <span key={l.file}>
              {i > 0 && " | "}
              <Link href={`/learn/tasks?ladder=${l.file}`} style={{ fontWeight: l.file === ladderFile ? 700 : 400 }}>
                {l.label}
              </Link>
            </span>
          ))}
        </p>
      </nav>
      <TaskRunner ladder={ladder} key={ladderFile} />
    </div>
  );
}
