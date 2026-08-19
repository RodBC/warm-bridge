/** Browser-first reach / outcome history. No invented replies. */

export type ReachStatus =
  | "copied"
  | "sent"
  | "bridge_replied"
  | "intro_landed"
  | "no_reply"
  | "dead";

export type ReachEvent = {
  id: string;
  at: string;
  accountCompany?: string;
  targetName: string;
  bridgeId: string;
  bridgeName: string;
  status: ReachStatus;
  note?: string;
};

export const ALLOWED_STATUSES: readonly ReachStatus[] = [
  "copied",
  "sent",
  "bridge_replied",
  "intro_landed",
  "no_reply",
  "dead",
] as const;

/** Ask-dock chips (copied is auto-logged on Copiar / WhatsApp). */
export const CHIP_STATUSES: readonly ReachStatus[] = [
  "sent",
  "bridge_replied",
  "intro_landed",
  "no_reply",
] as const;

export const STATUS_LABEL_PT: Record<ReachStatus, string> = {
  copied: "Copiado",
  sent: "Enviei",
  bridge_replied: "Respondeu",
  intro_landed: "Intro feita",
  no_reply: "Sem resposta",
  dead: "Encerrado",
};

const HISTORY_KEY = "warm-bridge-outcomes-v1";
const MAX_HISTORY = 20;

function newId(): string {
  return `r_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

export function loadOutcomes(): ReachEvent[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((e): e is ReachEvent => {
        if (!e || typeof e !== "object") return false;
        const ev = e as ReachEvent;
        return (
          typeof ev.id === "string" &&
          typeof ev.at === "string" &&
          typeof ev.targetName === "string" &&
          typeof ev.bridgeId === "string" &&
          typeof ev.bridgeName === "string" &&
          ALLOWED_STATUSES.includes(ev.status)
        );
      })
      .slice(0, MAX_HISTORY);
  } catch {
    return [];
  }
}

export function saveOutcomes(events: ReachEvent[]): ReachEvent[] {
  const trimmed = events.slice(0, MAX_HISTORY);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmed));
  return trimmed;
}

export function clearOutcomes(): void {
  localStorage.removeItem(HISTORY_KEY);
}

export type LogReachInput = {
  targetName: string;
  bridgeId: string;
  bridgeName: string;
  status: ReachStatus;
  accountCompany?: string;
  note?: string;
};

/** Prepend a reach event; keep last 20. */
export function logReach(input: LogReachInput): ReachEvent[] {
  const event: ReachEvent = {
    id: newId(),
    at: new Date().toISOString(),
    targetName: input.targetName.trim(),
    bridgeId: input.bridgeId,
    bridgeName: input.bridgeName.trim(),
    status: input.status,
    ...(input.accountCompany?.trim()
      ? { accountCompany: input.accountCompany.trim() }
      : {}),
    ...(input.note?.trim() ? { note: input.note.trim().slice(0, 500) } : {}),
  };
  const next = [event, ...loadOutcomes()].slice(0, MAX_HISTORY);
  return saveOutcomes(next);
}

export function formatReachWhen(iso: string): string {
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleString("pt-BR", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}
