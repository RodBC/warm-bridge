/** Portraits: session CDN → http photo → unavatar for real /in/ → initials. */

const PALETTE = [
  ["#05072e", "#00a3e0"],
  ["#0a0f3d", "#7dd3fc"],
  ["#007bc0", "#e0f2fe"],
  ["#023e8a", "#90e0ef"],
  ["#1b4332", "#95d5b2"],
  ["#7f1d1d", "#fecaca"],
  ["#3730a3", "#c7d2fe"],
  ["#44403c", "#e7e5e4"],
];

const FAKE_URL_RE = /demo-warmbridge|example\.invalid|acme-example|-mock(?:\/|$)/i;

function usablePhoto(url?: string | null): string | null {
  const u = (url || "").trim();
  if (!u) return null;
  if (u.includes("example.invalid")) return null;
  // Local portrait assets are offline fixtures — prefer CDN/unavatar when available.
  if (u.startsWith("/portraits/")) return null;
  if (u.startsWith("https://") || u.startsWith("http://") || u.startsWith("data:")) return u;
  return null;
}

export function hashName(name: string): number {
  let h = 0;
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) | 0;
  return Math.abs(h);
}

export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export function avatarColors(name: string): { bg: string; fg: string } {
  const [bg, fg] = PALETTE[hashName(name) % PALETTE.length];
  return { bg, fg };
}

export function linkedinSlug(url?: string | null): string | null {
  if (!url) return null;
  const m = url.match(/linkedin\.com\/in\/([^/?#]+)/i);
  return m ? decodeURIComponent(m[1]).replace(/\/$/, "").toLowerCase() : null;
}

export function isRealLinkedInProfileUrl(url?: string | null): boolean {
  const raw = (url || "").trim();
  if (!raw) return false;
  if (FAKE_URL_RE.test(raw)) return false;
  return /linkedin\.com\/(in|pub)\//i.test(raw);
}

export function avatarDataUrl(name: string, size = 128): string {
  const { bg, fg } = avatarColors(name);
  const text = initials(name);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <rect width="${size}" height="${size}" fill="${bg}"/>
  <text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle"
    fill="${fg}" font-family="Noto Sans,system-ui,sans-serif" font-weight="700"
    font-size="${size * 0.32}">${text}</text>
</svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

export type AvatarInput = {
  name: string;
  photo?: string | null;
  avatar_url?: string | null;
  linkedin_url?: string | null;
  linkedin?: string | null;
};

export function liveLinkedInAvatar(slug: string): string {
  return `https://unavatar.io/linkedin/${encodeURIComponent(slug)}`;
}

/**
 * Priority: session avatar_url → photo http(s) → unavatar (any real /in/ slug) → initials.
 * Never uses /portraits/*.png in the happy path.
 */
export function resolvePortrait(input: AvatarInput): string {
  const session = usablePhoto(input.avatar_url);
  if (session) return session;

  const photo = usablePhoto(input.photo);
  if (photo) return photo;

  const li = (input.linkedin_url || input.linkedin || "").trim();
  const slug = linkedinSlug(li);
  if (slug && isRealLinkedInProfileUrl(li)) {
    return liveLinkedInAvatar(slug);
  }

  // Name fallbacks for investigator / target when URL missing on the node
  const key = (input.name || "").trim().toLowerCase();
  if (key === "rodrigo castro") return liveLinkedInAvatar("rodrigo-castro-536b85209");
  if (key === "sabrina coelho godoy") {
    return liveLinkedInAvatar("sabrina-coelho-godoy-98094917b");
  }

  return avatarDataUrl(input.name || "?");
}

/**
 * Profile URL for the pin LinkedIn button.
 * Returns null for fake/absent URLs — UI must hide the button (never people search).
 */
export function boardLinkedInHref(input: {
  name: string;
  linkedin_url?: string | null;
}): string | null {
  const raw = (input.linkedin_url || "").trim();
  if (isRealLinkedInProfileUrl(raw)) {
    return raw.startsWith("http") ? raw : `https://${raw.replace(/^\/+/, "")}`;
  }
  const key = (input.name || "").trim().toLowerCase();
  if (key === "rodrigo castro") {
    return "https://www.linkedin.com/in/rodrigo-castro-536b85209/";
  }
  if (key === "sabrina coelho godoy") {
    return "https://www.linkedin.com/in/sabrina-coelho-godoy-98094917b/";
  }
  return null;
}
