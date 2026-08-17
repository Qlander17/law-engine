// Law Engine -- real search API route (Live Run 1.37, Mission 19).
// A real, typed API contract: GET /api/search?q=<query> returns the real,
// matching StatuteSection records -- never a synthesized answer, only the
// actual statutory text plus its citation. Deterministic, same logic
// shape as the Python retrieval.search() (services/retrieval.py), kept
// as a thin, separate implementation here per the "clean Python<->
// TypeScript boundary" instruction (Mission 20) -- Python owns the
// authoritative ingestion; this route only searches the already-ingested,
// already-normalized JSON.

import { NextRequest, NextResponse } from "next/server";
import { searchSections } from "@/lib/lawEngineData";
import type { StatuteSection } from "@/types/statute";

export interface SearchResponse {
  query: string;
  results: StatuteSection[];
}

export async function GET(request: NextRequest): Promise<NextResponse<SearchResponse>> {
  const query = request.nextUrl.searchParams.get("q") ?? "";
  const results = await searchSections(query);
  return NextResponse.json({ query, results });
}
