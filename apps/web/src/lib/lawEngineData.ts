// Law Engine -- server-side data loader (Live Run 1.37, Mission 19-20).
// Reads the real, Python-produced normalized JSON directly from the
// filesystem -- this app never re-implements ingestion/normalization in
// TypeScript; that stays Python's real responsibility
// (law-engine/services/ingestion.py). Server Components only, never
// bundled to the client (real file-path reads on disk).

import "server-only";
import { promises as fs } from "fs";
import path from "path";
import type { SourceManifest, StatuteSection, StatuteSectionMap } from "@/types/statute";
import type { TransactionLifecycle } from "@/types/lifecycle";
import type { SentenceAnalysis, SyntaxAnalysisMap } from "@/types/syntaxAnalysis";
import type { UccOrientation } from "@/types/orientation";
import type { PracticeSet } from "@/types/practice";
import type { TaskLadder } from "@/types/task";

const LAW_ENGINE_ROOT = path.resolve(process.cwd(), "..", "..");
const NORMALIZED_UCC_DIR = path.join(LAW_ENGINE_ROOT, "library", "normalized", "ucc");
const MANIFEST_DIR = path.join(LAW_ENGINE_ROOT, "library", "manifests");
const LIFECYCLES_DIR = path.join(LAW_ENGINE_ROOT, "library", "normalized", "lifecycles");
const SYNTAX_ANALYSIS_PATH = path.join(
  LAW_ENGINE_ROOT,
  "library",
  "normalized",
  "syntax-analysis",
  "article-2-sections-analysis.json"
);
const ORIENTATION_PATH = path.join(
  LAW_ENGINE_ROOT,
  "library",
  "normalized",
  "orientation",
  "ucc-orientation.json"
);

// Live Run 1.45, Mission 5/V1 -- real UCC orientation content
// (services/ucc_orientation.py, precomputed via
// services/ucc_orientation_export.py), previously invisible to any
// real user despite being fully built and tested.
export async function getOrientation(): Promise<UccOrientation> {
  const raw = await fs.readFile(ORIENTATION_PATH, "utf-8");
  return JSON.parse(raw) as UccOrientation;
}

const PRACTICE_PATH = path.join(
  LAW_ENGINE_ROOT,
  "library",
  "normalized",
  "practice",
  "article-2-practice.json"
);

// Live Run 1.45, Mission 5/V1 -- the real Article 2 MCQ set
// (services/learning.py) and Document Identification exercise
// (services/document_intelligence.py), previously invisible to any
// real user despite being tested and citation-grounded.
export async function getPracticeSet(): Promise<PracticeSet> {
  const raw = await fs.readFile(PRACTICE_PATH, "utf-8");
  return JSON.parse(raw) as PracticeSet;
}

const TASKS_DIR = path.join(LAW_ENGINE_ROOT, "library", "normalized", "tasks");

// Live Run 1.48 -- the first real Task Ladder (services/tasks.py),
// implementing the Task-First pedagogy Live Run 1.47B designed but
// deliberately did not build. Live Run 1.49 -- parameterized by file
// name so the real mini-simulation (services/simulations.py) can be
// read the same way, no second data-access function needed.
export async function getTaskLadder(fileName = "article-2-consumer-to-operator-ladder.json"): Promise<TaskLadder> {
  const raw = await fs.readFile(path.join(TASKS_DIR, fileName), "utf-8");
  return JSON.parse(raw) as TaskLadder;
}

// Live Run 1.45 -- real, disclosed fix for a real, live bug found by
// the Live Run 1.44 UCC completion map: this used to hardcode
// "article-2-sections.json" alone, so a real visitor to the home page
// (and search) could never see or find any Article 9 section, despite
// Article 9 being fully ingested and real. Mirrors
// services/retrieval.py's own load_sections() fix (Live Run 1.39),
// which already merges every real "*-sections.json" file in the same
// directory on the Python side -- this brings the TypeScript reader up
// to the same, already-established pattern rather than inventing a
// different one.
export async function getAllSections(): Promise<StatuteSectionMap> {
  const files = (await fs.readdir(NORMALIZED_UCC_DIR)).filter((f) => f.endsWith("-sections.json"));
  const merged: StatuteSectionMap = {};
  for (const file of files) {
    const raw = await fs.readFile(path.join(NORMALIZED_UCC_DIR, file), "utf-8");
    Object.assign(merged, JSON.parse(raw) as StatuteSectionMap);
  }
  return merged;
}

export async function getSection(sectionId: string): Promise<StatuteSection | null> {
  const sections = await getAllSections();
  return sections[sectionId] ?? null;
}

// Real, disclosed fix, same run: there are now two real, distinct
// source manifests (Article 2, Article 9) -- returning only one
// silently hid Article 9's own provenance/licensing record from any
// visitor. Returns every real manifest found, not a single hardcoded
// one, so a future third Article needs no code change here either.
export async function getAllManifests(): Promise<SourceManifest[]> {
  const files = (await fs.readdir(MANIFEST_DIR)).filter((f) => f.endsWith(".json"));
  const manifests: SourceManifest[] = [];
  for (const file of files) {
    const raw = await fs.readFile(path.join(MANIFEST_DIR, file), "utf-8");
    manifests.push(JSON.parse(raw) as SourceManifest);
  }
  return manifests;
}

export async function getLifecycle(lifecycleId: string): Promise<TransactionLifecycle> {
  const filePath = path.join(LIFECYCLES_DIR, `${lifecycleId}.json`);
  const raw = await fs.readFile(filePath, "utf-8");
  return JSON.parse(raw) as TransactionLifecycle;
}

export async function getSyntaxAnalysis(sectionId: string): Promise<SentenceAnalysis[]> {
  const raw = await fs.readFile(SYNTAX_ANALYSIS_PATH, "utf-8");
  const all = JSON.parse(raw) as SyntaxAnalysisMap;
  return all[sectionId] ?? [];
}

export async function searchSections(query: string): Promise<StatuteSection[]> {
  const terms = query
    .toLowerCase()
    .split(/\s+/)
    .filter((t) => t.length > 0);
  if (terms.length === 0) return [];
  const sections = await getAllSections();
  return Object.values(sections).filter((section) => {
    const haystack = [section.title, ...section.paragraphs, ...section.topics, ...section.defined_terms]
      .join(" ")
      .toLowerCase();
    return terms.some((term) => haystack.includes(term));
  });
}
