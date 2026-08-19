import type { AccountFindResult, Network, Seller } from "./api";

const KEY_V2 = "warm-bridge-session-v2";
const KEY_V1 = "warm-bridge-session-v1";

export type TargetFields = {
  name: string;
  company: string;
  title: string;
};

export type AccountTargetRow = {
  id: string;
  name: string;
  title: string;
};

export type AccountFields = {
  company: string;
  targets: AccountTargetRow[];
};

export type WorkspaceMode = "single" | "account";

export type SessionData = {
  network: Network | null;
  seller: Seller | null;
  mode: WorkspaceMode;
  target: TargetFields;
  account: AccountFields;
  accountResult: AccountFindResult | null;
  activeAccountTargetId: string | null;
  locale: string;
  savedAt: string;
};

const DEFAULT_TARGET: TargetFields = {
  name: "Marina Costa",
  company: "Acme Saúde",
  title: "Diretora de Compras",
};

const DEFAULT_ACCOUNT: AccountFields = {
  company: "Acme Saúde",
  targets: [
    { id: "t_marina", name: "Marina Costa", title: "Diretora de Compras" },
    { id: "t_farmacia", name: "Paulo Almeida", title: "Gerente de Farmácia" },
    { id: "t_clinico", name: "Ricardo Mendes", title: "Diretor Clínico" },
  ],
};

export function defaultTarget(): TargetFields {
  return { ...DEFAULT_TARGET };
}

export function defaultAccount(): AccountFields {
  return {
    company: DEFAULT_ACCOUNT.company,
    targets: DEFAULT_ACCOUNT.targets.map((t) => ({ ...t })),
  };
}

function migrateV1(): SessionData | null {
  try {
    const raw = localStorage.getItem(KEY_V1);
    if (!raw) return null;
    const v1 = JSON.parse(raw) as Partial<SessionData>;
    return {
      network: v1.network ?? null,
      seller: v1.seller ?? null,
      mode: "single",
      target: v1.target ?? defaultTarget(),
      account: defaultAccount(),
      accountResult: null,
      activeAccountTargetId: null,
      locale: v1.locale ?? "pt",
      savedAt: new Date().toISOString(),
    };
  } catch {
    return null;
  }
}

export function loadSession(): SessionData | null {
  try {
    const raw = localStorage.getItem(KEY_V2);
    if (raw) {
      const data = JSON.parse(raw) as SessionData;
      if (data && typeof data === "object") return data;
    }
    return migrateV1();
  } catch {
    return null;
  }
}

export function saveSession(partial: Partial<SessionData>): SessionData {
  const prev = loadSession();
  const next: SessionData = {
    network: partial.network !== undefined ? partial.network : prev?.network ?? null,
    seller: partial.seller !== undefined ? partial.seller : prev?.seller ?? null,
    mode: partial.mode ?? prev?.mode ?? "single",
    target: partial.target ?? prev?.target ?? defaultTarget(),
    account: partial.account ?? prev?.account ?? defaultAccount(),
    accountResult:
      partial.accountResult !== undefined
        ? partial.accountResult
        : prev?.accountResult ?? null,
    activeAccountTargetId:
      partial.activeAccountTargetId !== undefined
        ? partial.activeAccountTargetId
        : prev?.activeAccountTargetId ?? null,
    locale: partial.locale ?? prev?.locale ?? "pt",
    savedAt: new Date().toISOString(),
  };
  localStorage.setItem(KEY_V2, JSON.stringify(next));
  return next;
}

export function clearSession(): void {
  localStorage.removeItem(KEY_V2);
  localStorage.removeItem(KEY_V1);
}

export function newTargetId(): string {
  return `t_${Date.now().toString(36)}`;
}
