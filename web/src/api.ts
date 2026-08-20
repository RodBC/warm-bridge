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
  photo?: string;
  avatar_url?: string;
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
  photo?: string;
  avatar_url?: string;
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
  insight?: InsightPack;
};

export type InsightItem = {
  title: string;
  url: string;
  snippet: string;
  kind: string;
  domain?: string;
};

export type InsightPack = {
  target: { name: string; company: string; title: string; linkedin_url?: string };
  queries: string[];
  items: InsightItem[];
  count: number;
  empty: boolean;
  hook_line_pt?: string;
  hook_line_en?: string;
  source: string;
  note: string;
};

export type InvestigateResult = {
  find: FindResult;
  insight: InsightPack | null;
  network: Network;
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
    let detail = text || res.statusText;
    try {
      const parsed = JSON.parse(text) as { detail?: unknown };
      if (typeof parsed.detail === "string") detail = parsed.detail;
    } catch {
      /* keep raw */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export type LinkedInSessionStatus = {
  ready: boolean;
  blockers: string[];
  hints: string[];
  severity: "ready" | "mock" | "blocked" | "yellow";
  account?: {
    configured?: boolean;
    email?: string;
    linkedin_url?: string;
    path?: string;
    has_gmail_otp?: boolean;
    has_totp?: boolean;
  };
  checks: {
    backend?: string;
    camoufox_importable?: boolean;
    camoufox_version?: string | null;
    selenium_importable: boolean;
    selenium_version?: string | null;
    chrome_binary?: string | null;
    chrome_binary_configured?: boolean;
    profile_dir?: string | null;
    profile_dir_exists?: boolean;
    user_data_dir?: string | null;
    user_data_dir_exists: boolean;
    linkedin_session_yaml: boolean;
    mock_mode: boolean;
    profile_directory?: string | null;
    burner_secrets_present?: boolean;
  };
};

export function linkedInSessionStatus() {
  return api<LinkedInSessionStatus>("/api/linkedin-session/status");
}

export function linkedInSessionEnsure() {
  return api<{ status: string; [key: string]: unknown }>("/api/linkedin-session/ensure", {
    method: "POST",
  });
}

export function linkedInSessionAccount() {
  return api<{
    configured: boolean;
    email?: string;
    linkedin_url?: string;
    path?: string;
    has_gmail_otp?: boolean;
    has_totp?: boolean;
  }>("/api/linkedin-session/account");
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
  target: { name: string; company: string; title: string; linkedin?: string; linkedin_url?: string };
  network: Network | null;
  seller: Seller | null;
  locale: string;
  top_k?: number;
  with_approaches?: boolean;
  with_research?: boolean;
}) {
  return api<FindResult>("/api/find", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function researchTarget(body: {
  target: { name: string; company: string; title: string; linkedin?: string; linkedin_url?: string };
}) {
  return api<InsightPack>("/api/research", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function investigate(body: {
  target: { name: string; company: string; title: string; linkedin?: string; linkedin_url?: string };
  network: Network | null;
  seller: Seller | null;
  locale: string;
  top_k?: number;
  with_approaches?: boolean;
  with_research?: boolean;
}) {
  return api<InvestigateResult>("/api/investigate", {
    method: "POST",
    body: JSON.stringify({ ...body, with_research: body.with_research !== false }),
  });
}

export type LinkedInMapResult = {
  network: Network;
  find: FindResult;
  seller?: Seller;
  meta: {
    source: string;
    mutual_count: number;
    mock: boolean;
    enriched?: boolean;
    enrich_cap?: number;
    target_avatar_url?: string;
    seller_avatar_url?: string;
    target_title?: string;
    target_company?: string;
    target_headline?: string;
    seller_title?: string;
    seller_company?: string;
    seller_headline?: string;
  };
};

/** Selenium session map → network + find. Pass demo=true for offline mock. */
export function linkedInMap(
  body: {
    seller_linkedin: string;
    target: { name: string; company: string; title: string; linkedin?: string; linkedin_url?: string };
    seller?: Seller | null;
    locale: string;
    top_k?: number;
    with_approaches?: boolean;
    enrich?: boolean;
  },
  opts?: { demo?: boolean },
) {
  const q = opts?.demo ? "?demo=1" : "";
  return api<LinkedInMapResult>(`/api/linkedin-map${q}`, {
    method: "POST",
    body: JSON.stringify({
      ...body,
      enrich: opts?.demo ? false : body.enrich !== false,
    }),
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

/** Normalize to digits for wa.me; BR mobiles without country get 55. */
export function normalizeWaPhone(phone: string): string | null {
  let digits = phone.replace(/\D/g, "");
  if (digits.length < 10) return null;
  // Brazilian local mobile 11 digits → add country
  if (digits.length === 10 || digits.length === 11) {
    digits = `55${digits}`;
  }
  if (digits.length < 12 || digits.length > 15) return null;
  return digits;
}

/** wa.me deep link — user still sends manually. Keeps text short for URL limits. */
export function whatsAppUrl(phone: string, text: string): string | null {
  const digits = normalizeWaPhone(phone);
  if (!digits) return null;
  const clipped = text.length > 900 ? `${text.slice(0, 880).trim()}…` : text;
  return `https://wa.me/${digits}?text=${encodeURIComponent(clipped)}`;
}

export function linkedinProfileUrl(value: string | null | undefined): string | null {
  const raw = (value || "").trim();
  if (!raw) return null;
  if (/linkedin\.com\/(in|pub)\//i.test(raw)) {
    return raw.startsWith("http") ? raw : `https://${raw.replace(/^\/+/, "")}`;
  }
  if (/^[a-z0-9\-_%]{2,100}$/i.test(raw) && raw.includes("-")) {
    return `https://www.linkedin.com/in/${raw}`;
  }
  return null;
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
