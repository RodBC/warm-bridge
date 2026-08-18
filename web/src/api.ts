export type Seller = Record<string, unknown>;
export type Network = { contacts: ContactNode[]; import_kind?: string };

export type ContactNode = {
  id?: string;
  name: string;
  company?: string;
  title?: string;
  strength?: string;
  notes?: string;
  sources?: string[];
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

export async function uploadSellerYaml(file: File): Promise<Seller> {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch("/api/upload-seller", { method: "POST", body: fd });
  if (!res.ok) throw new Error(await res.text());
  const data = (await res.json()) as { seller: Seller };
  return data.seller;
}
