// Law Engine -- /learn vertical slice (Live Run 1.38, Mission 17;
// multi-lifecycle picker added Live Run 1.39, Mission 15/18).
// Server Component: loads the real Python-produced lifecycle JSON,
// hands it to the interactive client component. Real career evidence,
// not a placeholder -- typed data model, typed API contract
// (api/lifecycle/route.ts), interactive state, source citations.

import Link from "next/link";
import { getLifecycle } from "@/lib/lawEngineData";
import LifecycleRunner from "./LifecycleRunner";

const LIFECYCLES = [
  { id: "consumer-goods-purchase-v1", label: "Consumer goods purchase (Article 2 only)" },
  { id: "equipment-purchase-on-credit-v1", label: "Equipment purchase on credit (Article 2 → Article 9)" },
];

export default async function LearnPage({
  searchParams,
}: {
  searchParams: { lifecycle?: string };
}) {
  const requestedId = searchParams.lifecycle ?? LIFECYCLES[0].id;
  const known = LIFECYCLES.some((l) => l.id === requestedId);
  const lifecycleId = known ? requestedId : LIFECYCLES[0].id;
  const lifecycle = await getLifecycle(lifecycleId);

  return (
    <div>
      <nav style={{ maxWidth: 760, margin: "1rem auto 0", padding: "0 1rem", fontFamily: "system-ui, sans-serif" }}>
        <p style={{ marginBottom: "0.5rem" }}>
          <Link href="/">&larr; All sections</Link>
          {" · "}
          <Link href="/learn/orientation">UCC orientation</Link>
          {" · "}
          <Link href="/learn/practice">Practice</Link>
          {" · "}
          <Link href="/learn/tasks">Task Ladder</Link>
        </p>
        <p style={{ fontSize: "0.9rem", color: "#555" }}>
          {LIFECYCLES.map((l, i) => (
            <span key={l.id}>
              {i > 0 && " | "}
              <Link
                href={`/learn?lifecycle=${l.id}`}
                style={{ fontWeight: l.id === lifecycleId ? 700 : 400 }}
              >
                {l.label}
              </Link>
            </span>
          ))}
        </p>
      </nav>
      <LifecycleRunner lifecycle={lifecycle} key={lifecycleId} />
    </div>
  );
}
