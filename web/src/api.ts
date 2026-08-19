export type Seller = Record<string, unknown>;
export type Network = { contacts: ContactNode[]; import_kind?: string };

export type ContactNode = {
  id?: string;
  name: string;
  company?: string;
  title?: string;
  strength?: string;
  notes?: string;
  phone?: string;
  linkedin_url?: string;
  sources?: string[];
};

export type TutorAdvice = {
  level: string;
  can_ask: boolean;
  headline: string;
  headline_pt: string;
  headline_en: string;
  bullets: string[];
  bullets_pt: string[];
  bullets_en: string[];
};

export type Bridge = {
  contact_id: string;
  name: string;
  score: number;
  types: string[];
  strength: string;
  mode: string;
  confidence: string;
  bucket: string;
  path_label: string;
  why: string[];
  title: string;
  company: string;
  phone: string;
  linkedin_url: string;
  message?: string;
  tutor?: TutorAdvice;
};

export type FindResult = {
  target: { name: string; company: string; title: string };
  locale: string;
  resolution: {
    status: string;
    contact_id: string | null;
    contact_name: string | null;
    score: number;
    rationale: string;
  };
  counts: { network: number; bridges: number; direct: number };
  bridges: Bridge[];
  direct: Bridge[];
  proof_line: string;
  note: string;
};

export type AccountTargetInput = {
  id: string;
  name: string;
  title: string;
};

export type AccountTargetResult = {
  id: string;
  name: string;
  title: string;
  company: string;
  has_path: boolean;
  proof_line: string;
  top_bridge_name: string | null;
  top_confidence: string | null;
  bridge_count: number;
  direct_count: number;
  find: FindResult;
};

export type AccountFindResult = {
  company: string;
  locale: string;
  summary_line: string;
  with_path: number;
  total_targets: number;
  targets: AccountTargetResult[];
};

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export function loadExampleSeller() {
  return api<Seller>("/api/example-seller");
}

export function loadExampleNetwork() {
  return api<Network>("/api/example-network");
}

export function loadExampleAccount() {
  return api<{ company: string; targets: AccountTargetInput[] }>("/api/example-account");
}

export function importNetwork(text: string, existing: Network | null) {
  return api<{
    import_kind: string;
    added: number;
    total: number;
    network: Network;
    note: string;
  }>("/api/import-network", {
    method: "POST",
    body: JSON.stringify({ text, existing }),
  });
}

export function findBridges(body: {
  target: { name: string; company: string; title: string };
  network: Network | null;
  seller: Seller | null;
  locale: string;
  top_k?: number;
  with_approaches?: boolean;
}) {
  return api<FindResult>("/api/find", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function findAccount(body: {
  company: string;
  targets: AccountTargetInput[];
  network: Network | null;
  seller: Seller | null;
  locale: string;
  top_k?: number;
  with_approaches?: boolean;
}) {
  return api<AccountFindResult>("/api/find-account", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function uploadSellerYaml(file: File): Promise<Seller> {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch("/api/upload-seller", { method: "POST", body: fd });
  if (!res.ok) throw new Error(await res.text());
  const data = (await res.json()) as { seller: Seller };
  return data.seller;
}

/** wa.me deep link — user still sends manually. */
export function whatsAppUrl(phone: string, text: string): string | null {
  const digits = phone.replace(/\D/g, "");
  if (digits.length < 10) return null;
  return `https://wa.me/${digits}?text=${encodeURIComponent(text)}`;
}

/** Echo/validate reach events — client remains source of truth. */
export function postOutcomes(body: {
  events: Array<{
    id?: string;
    at?: string;
    accountCompany?: string;
    targetName: string;
    bridgeId: string;
    bridgeName: string;
    status: string;
    note?: string;
  }>;
}) {
  return api<{ ok: boolean; events: unknown[]; note: string }>("/api/outcomes", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
