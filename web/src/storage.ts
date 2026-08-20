import type { AccountFindResult, Network, Seller } from "./api";

const KEY_V8 = "warm-bridge-session-v8"
const KEY_V7 = "warm-bridge-session-v7";
const KEY_V6 = "warm-bridge-session-v6";
const KEY_V5 = "warm-bridge-session-v5";
const KEY_V4 = "warm-bridge-session-v4";
const KEY_V3 = "warm-bridge-session-v3";
const KEY_V2 = "warm-bridge-session-v2";
const KEY_V1 = "warm-bridge-session-v1";

export type TargetFields = {
  name: string;
  company: string;
  title: string;
  linkedin: string;
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
  sellerLinkedin: string;
  mode: WorkspaceMode;
  target: TargetFields;
  account: AccountFields;
  accountResult: AccountFindResult | null;
  activeAccountTargetId: string | null;
  locale: string;
  savedAt: string;
};

/** Lead Police default case — Rodrigo → Sabrina */
const DEFAULT_TARGET: TargetFields = {
  name: "Sabrina Coelho Godoy",
  company: "3S Checkout",
  title: "Analista de Recursos Humanos Pleno",
  linkedin: "https://www.linkedin.com/in/sabrina-coelho-godoy-98094917b/",
};

const DEFAULT_SELLER_LINKEDIN =
  "https://www.linkedin.com/in/rodrigo-castro-536b85209/";

const DEFAULT_ACCOUNT: AccountFields = {
  company: "3S Checkout",
  targets: [
    {
      id: "t_sabrina",
      name: "Sabrina Coelho Godoy",
      title: "Analista de Recursos Humanos Pleno",
    },
    {
      id: "t_cintia",
      name: "Cintia Monteiro",
      title: "Analista de Departamento Pessoal",
    },
  ],
};

export function defaultTarget(): TargetFields {
  return { ...DEFAULT_TARGET };
}

export function defaultSellerLinkedin(): string {
  return DEFAULT_SELLER_LINKEDIN;
}

export function defaultAccount(): AccountFields {
  return {
    company: DEFAULT_ACCOUNT.company,
    targets: DEFAULT_ACCOUNT.targets.map((t) => ({ ...t })),
  };
}

export function loadSession(): SessionData | null {
  try {
    const raw = localStorage.getItem(KEY_V8);
    if (!raw) return null;
    const data = JSON.parse(raw) as SessionData;
    if (data && typeof data === "object" && data.network?.contacts?.length) {
      return {
        ...data,
        sellerLinkedin: data.sellerLinkedin || "",
        target: {
          name: data.target?.name || "",
          company: data.target?.company || "",
          title: data.target?.title || "",
          linkedin: data.target?.linkedin || "",
        },
      };
    }
    return null;
  } catch {
    return null;
  }
}

export function saveSession(partial: Partial<SessionData>): SessionData {
  const prev = loadSession();
  const next: SessionData = {
    network: partial.network !== undefined ? partial.network : prev?.network ?? null,
    seller: partial.seller !== undefined ? partial.seller : prev?.seller ?? null,
    sellerLinkedin: partial.sellerLinkedin ?? prev?.sellerLinkedin ?? "",
    mode: partial.mode ?? prev?.mode ?? "single",
    target: partial.target ?? prev?.target ?? {
      name: "",
      company: "",
      title: "",
      linkedin: "",
    },
    account: partial.account ?? prev?.account ?? {
      company: "",
      targets: [{ id: newTargetId(), name: "", title: "" }],
    },
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
  localStorage.setItem(KEY_V8, JSON.stringify(next));
  return next;
}

export function clearSession(): void {
  localStorage.removeItem(KEY_V8);
  localStorage.removeItem(KEY_V7);
  localStorage.removeItem(KEY_V6);
  localStorage.removeItem(KEY_V5);
  localStorage.removeItem(KEY_V4);
  localStorage.removeItem(KEY_V3);
  localStorage.removeItem(KEY_V2);
  localStorage.removeItem(KEY_V1);
}

export function newTargetId(): string {
  return `t_${Date.now().toString(36)}`;
}
