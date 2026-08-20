/** Browser-first case memory (Casos). Survives refresh; no server PII. */

import type { ReachStatus } from "./outcomes";
import type { TargetFields } from "./storage";

const CASES_KEY = "warm-bridge-cases-v1";
const MAX_CASES = 12;

export type CaseSource = "demo" | "live";

export type WarmCase = {
  id: string;
  target: TargetFields;
  proof_line: string;
  top_bridge: string;
  mutual_count: number;
  source: CaseSource;
  updatedAt: string;
  sellerLinkedin?: string;
  lastOutcome?: ReachStatus;
};

function caseId(target: TargetFields): string {
  const key = (target.linkedin || target.name || "unknown").trim().toLowerCase();
  return `c_${key.replace(/[^a-z0-9]+/g, "_").slice(0, 80)}`;
}

export function loadCases(): WarmCase[] {
  try {
    const raw = localStorage.getItem(CASES_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((c): c is WarmCase => {
        if (!c || typeof c !== "object") return false;
        const row = c as WarmCase;
        return (
          typeof row.id === "string" &&
          typeof row.updatedAt === "string" &&
          row.target &&
          typeof row.target.name === "string"
        );
      })
      .slice(0, MAX_CASES);
  } catch {
    return [];
  }
}

export function saveCases(cases: WarmCase[]): WarmCase[] {
  const trimmed = cases.slice(0, MAX_CASES);
  localStorage.setItem(CASES_KEY, JSON.stringify(trimmed));
  return trimmed;
}

export function clearCases(): void {
  localStorage.removeItem(CASES_KEY);
}

export type UpsertCaseInput = {
  target: TargetFields;
  proof_line: string;
  top_bridge: string;
  mutual_count: number;
  source: CaseSource;
  sellerLinkedin?: string;
  lastOutcome?: ReachStatus;
};

/** Upsert by LinkedIn URL / name; newest first. */
export function upsertCase(input: UpsertCaseInput): WarmCase[] {
  const id = caseId(input.target);
  const prev = loadCases().filter((c) => c.id !== id);
  const row: WarmCase = {
    id,
    target: {
      name: input.target.name.trim(),
      company: input.target.company.trim(),
      title: input.target.title.trim(),
      linkedin: input.target.linkedin.trim(),
    },
    proof_line: input.proof_line.slice(0, 280),
    top_bridge: input.top_bridge.slice(0, 120),
    mutual_count: input.mutual_count,
    source: input.source,
    updatedAt: new Date().toISOString(),
    ...(input.sellerLinkedin?.trim()
      ? { sellerLinkedin: input.sellerLinkedin.trim() }
      : {}),
    ...(input.lastOutcome ? { lastOutcome: input.lastOutcome } : {}),
  };
  return saveCases([row, ...prev]);
}

export function touchCaseOutcome(
  targetName: string,
  status: ReachStatus,
): WarmCase[] {
  const name = targetName.trim().toLowerCase();
  const next = loadCases().map((c) => {
    if (c.target.name.trim().toLowerCase() !== name) return c;
    return { ...c, lastOutcome: status, updatedAt: new Date().toISOString() };
  });
  return saveCases(next);
}
