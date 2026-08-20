import type { Bridge, TutorAdvice } from "./api";
import type { ReachEvent } from "./outcomes";
import { recentFavorAsk } from "./outcomes";

export function tutorLevelLabel(level: string, locale: string): string {
  const pt: Record<string, string> = { yes: "Sim", soft: "Leve", no: "Ainda não" };
  const en: Record<string, string> = { yes: "Yes", soft: "Soft", no: "Not yet" };
  const map = locale === "en" ? en : pt;
  return map[level] || level;
}

const FAVOR_DAYS = 14;

/** Soft/no if this bridge was asked recently (sent / intro_landed). */
export function applyFavorBank(
  advice: TutorAdvice,
  bridgeId: string,
  outcomes: ReachEvent[],
  locale: string,
): TutorAdvice & { favor_cooldown?: boolean } {
  const hit = recentFavorAsk(bridgeId, outcomes, FAVOR_DAYS);
  if (!hit) return advice;
  const en = locale === "en";
  const when = hit.at.slice(0, 10);
  return {
    ...advice,
    level: advice.level === "no" ? "no" : "soft",
    can_ask: false,
    favor_cooldown: true,
    headline: en
      ? `Cooldown — you already asked ${hit.bridgeName} recently (${when}).`
      : `Já pediu recentemente a ${hit.bridgeName} (${when}).`,
    headline_pt: `Já pediu recentemente a ${hit.bridgeName} (${when}).`,
    headline_en: `Cooldown — you already asked ${hit.bridgeName} recently (${when}).`,
    bullets: en
      ? [
          "Wait before asking the same bridge again.",
          "Pick another path or mark status if this ask already landed.",
        ]
      : [
          "Espere antes de pedir de novo à mesma ponte.",
          "Escolha outro caminho ou atualize o status se o pedido já andou.",
        ],
    bullets_pt: [
      "Espere antes de pedir de novo à mesma ponte.",
      "Escolha outro caminho ou atualize o status se o pedido já andou.",
    ],
    bullets_en: [
      "Wait before asking the same bridge again.",
      "Pick another path or mark status if this ask already landed.",
    ],
  };
}

/** Client fallback when API omits tutor (older server). */
export function fallbackTutor(bridge: Bridge, locale: string): TutorAdvice {
  const s = (bridge.strength || "unknown").toLowerCase();
  const m = bridge.mode || "ask_permission";
  const isDirect = bridge.bucket === "direct";

  if (isDirect) {
    return pack(
      "yes",
      true,
      locale,
      "Você já tem o alvo na rede — pode abordar direto.",
      "Target is already in your graph — reach out directly.",
      ["Não precisa pedir intro a ninguém.", "Tom curto no WhatsApp ou LinkedIn."],
      ["No bridge intro needed.", "Keep it short on WhatsApp or LinkedIn."],
    );
  }
  if (s === "low") {
    return pack(
      "no",
      false,
      locale,
      "Ainda não peça intro dura — relação fraca ou fria.",
      "Don't ask for a hard intro yet — weak or cold tie.",
      ["Prefira mapa ou permissão leve.", "Reaqueça antes de citar o alvo."],
      ["Prefer intel or soft permission.", "Re-warm before naming the target."],
    );
  }
  if (m === "ask_intro" && s === "high") {
    return pack(
      "yes",
      true,
      locale,
      "Sim — confiança alta e caminho claro para intro.",
      "Yes — high trust and a clear path for an intro.",
      ["Peça intro curta com texto pronto.", "Dê saída fácil se não for o momento."],
      ["Ask for a short intro with forwardable text.", "Give an easy out."],
    );
  }
  return pack(
    "soft",
    m !== "ask_intro",
    locale,
    "Pedido leve — mapa, permissão ou encaminhar.",
    "Soft ask — intel, permission, or forward.",
    ["Confirme quem decide antes de pedir ponte.", "Cite o alvo só se a relação aguentar."],
    ["Confirm who decides first.", "Name the target only if the tie can handle it."],
  );
}

export function bridgeTutor(
  bridge: Bridge,
  locale: string,
  outcomes: ReachEvent[] = [],
): TutorAdvice & { favor_cooldown?: boolean } {
  const base = bridge.tutor ?? fallbackTutor(bridge, locale);
  return applyFavorBank(base, bridge.contact_id, outcomes, locale);
}

function pack(
  level: string,
  canAsk: boolean,
  locale: string,
  headlinePt: string,
  headlineEn: string,
  bulletsPt: string[],
  bulletsEn: string[],
): TutorAdvice {
  const en = locale === "en";
  return {
    level,
    can_ask: canAsk,
    headline: en ? headlineEn : headlinePt,
    headline_pt: headlinePt,
    headline_en: headlineEn,
    bullets: en ? bulletsEn : bulletsPt,
    bullets_pt: bulletsPt,
    bullets_en: bulletsEn,
  };
}
