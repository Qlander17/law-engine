// Law Engine -- /learn/practice (Live Run 1.45, Mission 5/V1).
// Server Component: loads the real, precomputed practice-item JSON,
// hands it to the interactive client component -- same pattern as
// ../page.tsx / LifecycleRunner.tsx.

import Link from "next/link";
import { getPracticeSet } from "@/lib/lawEngineData";
import PracticeRunner from "./PracticeRunner";

export default async function PracticePage() {
  const practice = await getPracticeSet();

  return (
    <div>
      <p style={{ maxWidth: 760, margin: "1rem auto 0", padding: "0 1rem", fontFamily: "system-ui, sans-serif" }}>
        <Link href="/learn">&larr; Learn</Link>
      </p>
      <PracticeRunner mcqs={practice.mcqs} exercise={practice.document_identification_exercise} />
    </div>
  );
}
