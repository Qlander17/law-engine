// Law Engine -- real, typed lifecycle API route (Live Run 1.38, Mission
// 17). GET /api/lifecycle?id=<lifecycle_id> returns the real,
// Python-produced TransactionLifecycle JSON -- same
// Python-owns-the-data/TypeScript-only-reads boundary as /api/search.

import { NextRequest, NextResponse } from "next/server";
import { getLifecycle } from "@/lib/lawEngineData";
import type { TransactionLifecycle } from "@/types/lifecycle";

export interface LifecycleResponse {
  lifecycle: TransactionLifecycle | null;
  error?: string;
}

export async function GET(request: NextRequest): Promise<NextResponse<LifecycleResponse>> {
  const id = request.nextUrl.searchParams.get("id") ?? "consumer-goods-purchase-v1";
  try {
    const lifecycle = await getLifecycle(id);
    return NextResponse.json({ lifecycle });
  } catch {
    return NextResponse.json({ lifecycle: null, error: `No lifecycle found for id "${id}".` }, { status: 404 });
  }
}
