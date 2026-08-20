/** UI contract smoke for Lead Police pins — run with: npx tsx web/src/avatar.contract.test.ts */
import {
  boardLinkedInHref,
  isRealLinkedInProfileUrl,
  resolvePortrait,
} from "./avatar";

function assert(cond: unknown, msg: string) {
  if (!cond) throw new Error(msg);
}

const fake = boardLinkedInHref({
  name: "Ana Ribeiro",
  linkedin_url: "https://www.linkedin.com/in/ana-ribeiro-demo-warmbridge",
});
assert(fake === null, "fake demo-warmbridge must not yield LI href");

const searchLeak = boardLinkedInHref({ name: "Someone Unknown", linkedin_url: "" });
assert(searchLeak === null, "missing URL must not fall back to people search");
assert(
  searchLeak === null || !String(searchLeak).includes("/search/results"),
  "boardLinkedInHref never returns /search/results",
);

const real = boardLinkedInHref({
  name: "Rodrigo Castro",
  linkedin_url: "https://www.linkedin.com/in/rodrigo-castro-536b85209/",
});
assert(real?.includes("/in/rodrigo-castro"), "real slug must open profile");

const bridge = boardLinkedInHref({
  name: "Beatris Avelino",
  linkedin_url: "https://www.linkedin.com/in/beatris-avelino-09077720/",
});
assert(bridge?.includes("/in/beatris-avelino"), "demo bridge must open real LI");

assert(!isRealLinkedInProfileUrl("https://www.linkedin.com/in/x-mock"), "*-mock is fake");

const cdn = resolvePortrait({
  name: "X",
  avatar_url: "https://media.licdn.com/dms/image/test.jpg",
});
assert(cdn.includes("media.licdn.com"), "CDN avatar_url wins");

const unavatar = resolvePortrait({
  name: "Cintia Monteiro",
  linkedin_url: "https://www.linkedin.com/in/cintia-monteiro-45a31a73/",
});
assert(unavatar.includes("unavatar.io/linkedin/cintia-monteiro"), "real slug → unavatar");

const noPortrait = resolvePortrait({
  name: "Someone Else",
  photo: "/portraits/ana.png",
});
assert(!noPortrait.includes("/portraits/"), "local portraits not in happy path");
assert(noPortrait.startsWith("data:image"), "falls back to initials");

console.log("avatar.contract.test.ts OK");
