// Law Engine -- /learn/tasks (Live Run 1.48). Server Component: loads
// the real, precomputed Task Ladder JSON, hands it to the interactive
// client component -- same pattern as ../practice/page.tsx.

import Link from "next/link";
import { getTaskLadder } from "@/lib/lawEngineData";
import TaskRunner from "./TaskRunner";

export default async function TasksPage() {
  const ladder = await getTaskLadder();

  return (
    <div>
      <p style={{ maxWidth: 760, margin: "1rem auto 0", padding: "0 1rem", fontFamily: "system-ui, sans-serif" }}>
        <Link href="/learn">&larr; Learn</Link>
      </p>
      <TaskRunner ladder={ladder} />
    </div>
  );
}
