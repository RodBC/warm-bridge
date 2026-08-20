import { useEffect, useRef, useState } from "react";
import {
  Alert,
  AppBar,
  Avatar,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  Chip,
  Collapse,
  Container,
  Divider,
  Grid,
  IconButton,
  Link,
  MenuItem,
  Paper,
  Stack,
  Tab,
  Tabs,
  TextField,
  Toolbar,
  Tooltip,
  Typography,
} from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import LinkedInIcon from "@mui/icons-material/LinkedIn";
import HistoryIcon from "@mui/icons-material/History";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import SearchIcon from "@mui/icons-material/Search";
import ClearIcon from "@mui/icons-material/Clear";
import AddIcon from "@mui/icons-material/Add";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutlineOutlined";
import ChatIcon from "@mui/icons-material/Chat";
import { motion } from "framer-motion";
import {
  findAccount,
  findBridges,
  importNetwork,
  researchTarget,
  linkedInMap,
  linkedInSessionAccount,
  linkedInSessionStatus,
  linkedinProfileUrl,
  loadExampleAccount,
  loadExampleNetwork,
  loadExampleSeller,
  uploadSellerYaml,
  whatsAppUrl,
  type AccountFindResult,
  type AccountTargetResult,
  type Bridge,
  type FindResult,
  type InsightPack,
  type LinkedInSessionStatus,
  type Network,
  type Seller,
} from "./api";
import {
  loadCases,
  touchCaseOutcome,
  upsertCase,
  type WarmCase,
} from "./cases";
import {
  CHIP_STATUSES,
  STATUS_LABEL_PT,
  clearOutcomes,
  formatReachWhen,
  loadOutcomes,
  logReach,
  recentFavorAsk,
  type ReachEvent,
  type ReachStatus,
} from "./outcomes";
import {
  clearSession,
  defaultSellerLinkedin,
  defaultTarget,
  loadSession,
  newTargetId,
  saveSession,
  type AccountTargetRow,
  type WorkspaceMode,
} from "./storage";
import { SpiderBoard } from "./SpiderBoard";
import { resolvePortrait } from "./avatar";
import { bridgeTutor, tutorLevelLabel } from "./tutor";

function confidenceLabel(c: string) {
  if (c === "high") return "Alta";
  if (c === "medium") return "Média";
  if (c === "low") return "Baixa";
  if (c === "direct") return "Direto";
  return c;
}

function modeLabel(m: string) {
  const map: Record<string, string> = {
    ask_intro: "Pedir intro",
    peer_forward: "Encaminhar texto",
    ask_intel: "Pedir mapa",
    ask_permission: "Permissão leve",
    direct: "Abordar direto",
  };
  return map[m] || m;
}

function bandColor(c: string): "success" | "warning" | "default" | "info" {
  if (c === "high") return "success";
  if (c === "medium") return "warning";
  if (c === "direct") return "info";
  return "default";
}

function applyFindResult(
  data: FindResult,
  setResult: (r: FindResult) => void,
  setSelected: (b: Bridge | null) => void,
  setStatus: (s: string) => void,
  opts?: { selectFirst?: boolean },
) {
  setResult(data);
  if (opts?.selectFirst === false) {
    setSelected(null);
  } else {
    const first = data.bridges[0] || data.direct[0] || null;
    setSelected(first);
  }
  setStatus(data.proof_line);
}

const fade = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.35 },
};

export default function App() {
  const [seller, setSeller] = useState<Seller | null>(null);
  const [sellerLabel, setSellerLabel] = useState("Pronto para mapear");
  const [network, setNetwork] = useState<Network | null>(null);
  const [networkPaste, setNetworkPaste] = useState("");
  const [workspaceMode, setWorkspaceMode] = useState<WorkspaceMode>("single");
  const [targetName, setTargetName] = useState("");
  const [targetCompany, setTargetCompany] = useState("");
  const [targetTitle, setTargetTitle] = useState("");
  const [targetLinkedin, setTargetLinkedin] = useState("");
  const [sellerLinkedin, setSellerLinkedin] = useState("");
  const [sellerPhoto, setSellerPhoto] = useState<string | undefined>();
  const [targetPhoto, setTargetPhoto] = useState<string | undefined>();
  const [accountCompany, setAccountCompany] = useState("");
  const [accountTargets, setAccountTargets] = useState<AccountTargetRow[]>([
    { id: newTargetId(), name: "", title: "" },
  ]);
  const [accountResult, setAccountResult] = useState<AccountFindResult | null>(null);
  const [activeAccountTargetId, setActiveAccountTargetId] = useState<string | null>(null);
  const [locale, setLocale] = useState("pt");
  const [result, setResult] = useState<FindResult | null>(null);
  const [selected, setSelected] = useState<Bridge | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState(
    "Cole o LinkedIn do alvo e clique Mapear — sessão LinkedIn automática.",
  );
  const [copied, setCopied] = useState(false);
  const [restored, setRestored] = useState(false);
  const [isDemo, setIsDemo] = useState(false);
  const [insight, setInsight] = useState<InsightPack | null>(null);
  const [outcomes, setOutcomes] = useState<ReachEvent[]>([]);
  const [cases, setCases] = useState<WarmCase[]>([]);
  const [sessionStatus, setSessionStatus] = useState<LinkedInSessionStatus | null>(null);
  const [sessionStatusOpen, setSessionStatusOpen] = useState(false);
  const [legacyImportOpen, setLegacyImportOpen] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const askRef = useRef<HTMLElement>(null);

  useEffect(() => {
    setOutcomes(loadOutcomes());
    setCases(loadCases());
  }, []);

  useEffect(() => {
    void linkedInSessionStatus()
      .then((st) => {
        setSessionStatus(st);
        const acct = st.account;
        if (acct?.configured && acct.linkedin_url && !sellerLinkedin.trim()) {
          setSellerLinkedin(acct.linkedin_url);
        }
      })
      .catch(() => setSessionStatus(null));
    void linkedInSessionAccount()
      .then((acct) => {
        if (acct.configured && acct.linkedin_url) {
          setSellerLinkedin((prev) => prev.trim() || acct.linkedin_url || "");
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    const session = loadSession();
    if (session?.network?.contacts?.length) {
      setNetwork(session.network);
      if (session.seller) {
        setSeller(session.seller);
        const name = (session.seller.identity as { name?: string } | undefined)?.name;
        setSellerLabel(name ? `Sessão: ${name}` : "Sessão restaurada");
      }
      if (session.target) {
        setTargetName(session.target.name);
        setTargetCompany(session.target.company);
        setTargetTitle(session.target.title);
        if (session.target.linkedin) setTargetLinkedin(session.target.linkedin);
      }
      if (session.sellerLinkedin) setSellerLinkedin(session.sellerLinkedin);
      else if (session.seller) {
        const li = (session.seller.identity as { linkedin?: string } | undefined)?.linkedin;
        if (li) setSellerLinkedin(li.startsWith("http") ? li : `https://${li}`);
      }
      if (session.account) {
        setAccountCompany(session.account.company);
        setAccountTargets(session.account.targets);
      }
      if (session.mode) setWorkspaceMode(session.mode);
      if (session.accountResult) setAccountResult(session.accountResult);
      if (session.activeAccountTargetId) {
        setActiveAccountTargetId(session.activeAccountTargetId);
        const row = session.accountResult?.targets.find(
          (t) => t.id === session.activeAccountTargetId,
        );
        if (row) applyFindResult(row.find, setResult, setSelected, setStatus);
      }
      if (session.locale) setLocale(session.locale);
      setStatus(`${session.network.contacts.length} contatos restaurados do navegador`);
      setRestored(true);
      if (!session.accountResult && !session.activeAccountTargetId) {
        const t = session.target ?? defaultTarget();
        void findBridges({
          target: {
            name: t.name,
            company: t.company,
            title: t.title,
            linkedin: t.linkedin,
          },
          network: session.network,
          seller: session.seller,
          locale: session.locale || "pt",
          top_k: 8,
          with_approaches: true,
        })
          .then((data) =>
            applyFindResult(data, setResult, setSelected, setStatus, {
              selectFirst: false,
            }),
          )
          .catch(() => {});
      }
      return;
    }
    setSellerLabel("Pronto para investigar");
    setStatus("Importe Connections.csv ou cole contatos — depois investigue o alvo.");
  }, []);

  useEffect(() => {
    if (!network && !seller && !sellerLinkedin && !targetName) return;
    saveSession({
      network,
      seller,
      sellerLinkedin,
      mode: workspaceMode,
      target: {
        name: targetName,
        company: targetCompany,
        title: targetTitle,
        linkedin: targetLinkedin,
      },
      account: { company: accountCompany, targets: accountTargets },
      accountResult,
      activeAccountTargetId,
      locale,
    });
  }, [
    network,
    seller,
    sellerLinkedin,
    workspaceMode,
    targetName,
    targetCompany,
    targetTitle,
    targetLinkedin,
    accountCompany,
    accountTargets,
    accountResult,
    activeAccountTargetId,
    locale,
  ]);

  useEffect(() => {
    if (selected && askRef.current) {
      askRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [selected?.contact_id]);

  async function onUploadSeller(file: File | null) {
    if (!file) return;
    setError("");
    try {
      const s = await uploadSellerYaml(file);
      setSeller(s);
      const name = (s.identity as { name?: string } | undefined)?.name;
      setSellerLabel(name ? `Carregado: ${name}` : file.name);
      const li = (s.identity as { linkedin?: string } | undefined)?.linkedin;
      if (li) setSellerLinkedin(li.startsWith("http") ? li : `https://${li}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  function patchSellerLinkedin(url: string) {
    setSellerLinkedin(url);
    setSeller((prev) => {
      if (!prev) return prev;
      const identity = { ...((prev.identity as object) || {}), linkedin: url };
      return { ...prev, identity };
    });
  }

  async function onImport() {
    setError("");
    setBusy(true);
    try {
      const data = await importNetwork(networkPaste, network);
      setNetwork(data.network);
      setNetworkPaste("");
      setIsDemo(false);
      setStatus(`${data.added} importados (${data.import_kind}) · total ${data.total}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onMapear(demo = false) {
    if (!targetLinkedin.trim() && !demo) {
      setError("Cole o LinkedIn do alvo (linkedin.com/in/…).");
      return;
    }
    await onLinkedInMap(demo);
  }

  function rememberCase(opts: {
    target: { name: string; company: string; title: string; linkedin: string };
    find: FindResult;
    mutual_count: number;
    source: "demo" | "live";
    sellerLinkedin?: string;
  }) {
    const top = opts.find.bridges[0] || opts.find.direct[0];
    setCases(
      upsertCase({
        target: {
          name: opts.target.name || opts.find.target.name,
          company: opts.target.company || opts.find.target.company,
          title: opts.target.title || opts.find.target.title,
          linkedin: opts.target.linkedin,
        },
        proof_line: opts.find.proof_line,
        top_bridge: top?.name || "",
        mutual_count: opts.mutual_count,
        source: opts.source,
        sellerLinkedin: opts.sellerLinkedin || sellerLinkedin || undefined,
      }),
    );
  }

  async function runLinkedInMap(opts: {
    demo?: boolean;
    sellerLi: string;
    target: { name: string; company: string; title: string; linkedin: string };
    sellerOverride?: Seller | null;
  }): Promise<boolean> {
    const data = await linkedInMap(
      {
        seller_linkedin: opts.sellerLi,
        target: opts.target,
        seller: opts.sellerOverride !== undefined ? opts.sellerOverride : seller,
        locale,
        top_k: 8,
        with_approaches: true,
        enrich: !opts.demo,
      },
      { demo: opts.demo },
    );
    setNetwork(data.network);
    setIsDemo(false);
    if (data.seller) {
      setSeller(data.seller);
      const name = (data.seller.identity as { name?: string } | undefined)?.name;
      setSellerLabel(name ? `Sessão: ${name}` : "Sessão LinkedIn");
    }
    if (data.meta.seller_avatar_url) setSellerPhoto(data.meta.seller_avatar_url);
    if (data.meta.target_avatar_url) setTargetPhoto(data.meta.target_avatar_url);
    if (data.meta.target_title) setTargetTitle((prev) => prev.trim() || data.meta.target_title || "");
    if (data.meta.target_company) {
      setTargetCompany((prev) => prev.trim() || data.meta.target_company || "");
    }
    applyFindResult(data.find, setResult, setSelected, setStatus, {
      selectFirst: false,
    });
    try {
      const insightPack = await researchTarget({
        target: {
          name: opts.target.name || data.find.target.name,
          company: opts.target.company || data.find.target.company,
          title: opts.target.title || data.find.target.title,
          linkedin: opts.target.linkedin,
        },
      });
      setInsight(insightPack);
    } catch {
      setInsight(null);
    }
    const mockNote = data.meta.mock ? " · modo simulado (CI)" : "";
    const n = data.meta.mutual_count;
    if (!data.meta.mock && n === 0) {
      setStatus(
        "0 mutuals observados — confira login no perfil Camoufox (painel Sessão LinkedIn).",
      );
      setSessionStatusOpen(true);
      void linkedInSessionStatus().then(setSessionStatus).catch(() => {});
    } else {
      setStatus(`${data.find.proof_line} · ${n} mutuals${mockNote}`);
    }
    rememberCase({
      target: opts.target,
      find: data.find,
      mutual_count: n,
      source: opts.demo || data.meta.mock ? "demo" : "live",
      sellerLinkedin: opts.sellerLi,
    });
    return true;
  }

  async function onLinkedInMap(demo = false) {
    setError("");
    setBusy(true);
    setCopied(false);
    setAccountResult(null);
    setActiveAccountTargetId(null);
    try {
      const sellerLi = sellerLinkedin.trim() || defaultSellerLinkedin();
      const t = {
        name: targetName.trim() || defaultTarget().name,
        company: targetCompany,
        title: targetTitle,
        linkedin: targetLinkedin.trim() || defaultTarget().linkedin,
      };
      if (!sellerLinkedin.trim()) setSellerLinkedin(sellerLi);
      if (!targetName.trim()) setTargetName(t.name);
      if (!targetLinkedin.trim()) setTargetLinkedin(t.linkedin);
      await runLinkedInMap({ demo, sellerLi, target: t });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      if (/sessão|chrome|selenium|painel/i.test(msg)) {
        setSessionStatusOpen(true);
        void linkedInSessionStatus().then(setSessionStatus).catch(() => {});
      }
    } finally {
      setBusy(false);
    }
  }

  async function openCase(c: WarmCase) {
    setError("");
    setWorkspaceMode("single");
    setTargetName(c.target.name);
    setTargetCompany(c.target.company);
    setTargetTitle(c.target.title);
    setTargetLinkedin(c.target.linkedin);
    if (c.sellerLinkedin) setSellerLinkedin(c.sellerLinkedin);
    if (!network?.contacts?.length) {
      setStatus(`Caso ${c.target.name} — mapeie ou abra a demo para ter rede.`);
      return;
    }
    setBusy(true);
    try {
      const data = await findBridges({
        target: {
          name: c.target.name,
          company: c.target.company,
          title: c.target.title,
          linkedin: c.target.linkedin,
        },
        network,
        seller,
        locale,
        top_k: 8,
        with_approaches: true,
      });
      applyFindResult(data, setResult, setSelected, setStatus);
      setStatus(c.proof_line || data.proof_line);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function loadDemo() {
    setError("");
    setBusy(true);
    setCopied(false);
    setAccountResult(null);
    setActiveAccountTargetId(null);
    try {
      const [s, n, a] = await Promise.all([
        loadExampleSeller(),
        loadExampleNetwork(),
        loadExampleAccount(),
      ]);
      setSeller(s);
      setNetwork(n);
      setAccountCompany(a.company);
      setAccountTargets(a.targets);
      const idnLocal = s.identity as
        | { name?: string; linkedin?: string; role?: string; company?: string }
        | undefined;
      setSellerLabel(idnLocal?.name ? `Demo: ${idnLocal.name}` : "Demo aberta");
      const li = idnLocal?.linkedin;
      const sellerLi = li
        ? li.startsWith("http")
          ? li
          : `https://${li}`
        : defaultSellerLinkedin();
      setSellerLinkedin(sellerLi);
      setSellerPhoto(undefined);
      const t = defaultTarget();
      setTargetName(t.name);
      setTargetCompany(t.company);
      setTargetTitle(t.title);
      setTargetLinkedin(t.linkedin);
      setTargetPhoto(undefined);
      setIsDemo(true);
      setWorkspaceMode("single");
      const data = await findBridges({
        target: {
          name: t.name,
          company: t.company,
          title: t.title,
          linkedin: t.linkedin,
        },
        network: n,
        seller: s,
        locale: "pt",
        top_k: 8,
        with_approaches: true,
      });
      applyFindResult(data, setResult, setSelected, setStatus, { selectFirst: false });
      setStatus(
        `${n.contacts?.length ?? 0} pontes · demo offline com perfis LinkedIn reais · Mapear usa sessão Chrome`,
      );
      rememberCase({
        target: t,
        find: data,
        mutual_count: n.contacts?.length ?? 0,
        source: "demo",
        sellerLinkedin: sellerLi,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStatus("API offline — rode: npm run dev");
    } finally {
      setBusy(false);
    }
  }

  async function onFindAccount() {
    setError("");
    setBusy(true);
    setCopied(false);
    const valid = accountTargets.filter((t) => t.name.trim());
    if (!valid.length) {
      setError("Adicione pelo menos um tomador com nome.");
      setBusy(false);
      return;
    }
    try {
      const data = await findAccount({
        company: accountCompany,
        targets: valid,
        network,
        seller,
        locale,
        top_k: 8,
        with_approaches: true,
      });
      setAccountResult(data);
      const first = data.targets.find((t) => t.has_path) || data.targets[0];
      if (first) selectAccountTarget(first, data);
      else {
        setResult(null);
        setSelected(null);
      }
      setStatus(data.summary_line);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  function selectAccountTarget(row: AccountTargetResult, data?: AccountFindResult) {
    setActiveAccountTargetId(row.id);
    applyFindResult(row.find, setResult, setSelected, setStatus);
    if (data) setAccountResult(data);
  }

  function addAccountTarget() {
    setAccountTargets((prev) => [...prev, { id: newTargetId(), name: "", title: "" }]);
  }

  function updateAccountTarget(id: string, patch: Partial<AccountTargetRow>) {
    setAccountTargets((prev) => prev.map((t) => (t.id === id ? { ...t, ...patch } : t)));
  }

  function removeAccountTarget(id: string) {
    setAccountTargets((prev) => prev.filter((t) => t.id !== id));
  }

  async function copyMessage(text: string) {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    recordReach("copied");
    setStatus("Mensagem copiada — cole no WhatsApp / LinkedIn");
    window.setTimeout(() => setCopied(false), 2200);
  }

  function recordReach(status: ReachStatus) {
    if (!selected || !result) return;
    const next = logReach({
      status,
      targetName: result.target.name,
      bridgeId: selected.contact_id,
      bridgeName: selected.name,
      ...(workspaceMode === "account" && accountCompany.trim()
        ? { accountCompany: accountCompany.trim() }
        : {}),
    });
    setOutcomes(next);
    setCases(touchCaseOutcome(result.target.name, status));
  }

  function onOpenWhatsApp() {
    recordReach("copied");
  }

  function clearReachHistory() {
    clearOutcomes();
    setOutcomes([]);
  }

  function resetSession() {
    clearSession();
    setResult(null);
    setSelected(null);
    setAccountResult(null);
    setActiveAccountTargetId(null);
    setNetwork(null);
    setSeller(null);
    setSellerPhoto(undefined);
    setTargetPhoto(undefined);
    setRestored(false);
    setIsDemo(false);
    setInsight(null);
    setWorkspaceMode("single");
    setAccountCompany("");
    setAccountTargets([{ id: newTargetId(), name: "", title: "" }]);
    setTargetName("");
    setTargetCompany("");
    setTargetTitle("");
    setTargetLinkedin("");
    setSellerLinkedin("");
    setSellerLabel("Pronto para investigar");
    setStatus("Importe Connections.csv ou cole contatos — depois investigue o alvo.");
    setError("");
  }

  const sellerName =
    (seller?.identity as { name?: string } | undefined)?.name || "você";
  const idn = seller?.identity as
    | { role?: string; company?: string; headline?: string }
    | undefined;
  const sellerRole = idn?.role || "";
  const sellerCompany = idn?.company || "";
  const sellerHeadline =
    idn?.headline ||
    (sellerRole && sellerCompany
      ? `${sellerRole} - ${sellerCompany}`
      : sellerRole || sellerCompany || "");
  const sellerPinTitle = sellerRole || sellerHeadline;
  const sellerPinCompany = sellerRole ? sellerCompany : "";
  const tutor = selected ? bridgeTutor(selected, locale, outcomes) : null;
  const favorHit = selected
    ? recentFavorAsk(selected.contact_id, outcomes, 14)
    : null;
  const waLink =
    selected?.message && selected.phone ? whatsAppUrl(selected.phone, selected.message) : null;
  const bridgeLinkedin = selected?.linkedin_url
    ? linkedinProfileUrl(selected.linkedin_url)
    : null;
  const latestForSelected = selected
    ? outcomes.find((e) => e.bridgeId === selected.contact_id)
    : null;
  const sessionSeverity = sessionStatus?.severity ?? "yellow";
  const sessionAlertSeverity =
    sessionSeverity === "ready"
      ? "success"
      : sessionSeverity === "blocked"
        ? "error"
        : "warning";

  const stepNetwork = (network?.contacts?.length ?? 0) > 0;
  const stepTarget =
    workspaceMode === "account"
      ? accountTargets.some((t) => t.name.trim())
      : Boolean(targetName.trim());
  const stepBridges = Boolean(result || accountResult);
  const stepAsk = Boolean(selected?.message);

  const steps = [
    { label: "Rede", on: stepNetwork },
    { label: "Alvo", on: stepTarget },
    { label: "Pontes", on: stepBridges },
    { label: "Pedir", on: stepAsk },
  ];

  return (
    <Box sx={{ pb: 6 }}>
      <AppBar position="sticky" color="transparent">
        <Toolbar sx={{ gap: 2, flexWrap: "wrap", py: 1 }}>
          <Box sx={{ flex: "1 1 200px" }}>
            <Typography variant="overline" sx={{ color: "primary.light", display: "block" }}>
              Warm Bridge · você envia
            </Typography>
            <Typography
              variant="h1"
              sx={{ fontSize: { xs: "1.6rem", md: "2rem" }, color: "#fff", lineHeight: 1 }}
            >
              Lead{" "}
              <Box component="span" sx={{ color: "primary.light" }}>
                Police
              </Box>
            </Typography>
            <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.65)", mt: 0.5 }}>
              Caminhos quentes da sua rede até o tomador.
            </Typography>
          </Box>
          <Stack direction="row" spacing={0.75} useFlexGap sx={{ flexWrap: "wrap" }}>
            {steps.map((s) => (
              <Chip
                key={s.label}
                size="small"
                label={s.label}
                color={s.on ? "primary" : "default"}
                variant={s.on ? "filled" : "outlined"}
                sx={{
                  color: s.on ? undefined : "rgba(255,255,255,0.7)",
                  borderColor: "rgba(255,255,255,0.25)",
                }}
              />
            ))}
          </Stack>
          <Tooltip title="Histórico de alcance">
            <IconButton color="inherit" onClick={() => setHistoryOpen((o) => !o)}>
              <HistoryIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
        {cases.length > 0 && (
          <Box
            sx={{
              px: 2,
              pb: 1.5,
              display: "flex",
              gap: 1,
              overflowX: "auto",
              alignItems: "center",
              borderTop: "1px solid rgba(255,255,255,0.08)",
            }}
          >
            <Typography
              variant="caption"
              sx={{ color: "rgba(255,255,255,0.55)", whiteSpace: "nowrap", mr: 0.5 }}
            >
              Casos recentes
            </Typography>
            {cases.map((c) => (
              <Chip
                key={c.id}
                size="small"
                clickable
                onClick={() => void openCase(c)}
                label={`${c.target.name}${c.top_bridge ? ` · ${c.top_bridge}` : ""}`}
                color={c.source === "live" ? "primary" : "default"}
                variant={c.source === "live" ? "filled" : "outlined"}
                sx={{
                  color: "#fff",
                  borderColor: "rgba(255,255,255,0.28)",
                  maxWidth: 280,
                }}
              />
            ))}
          </Box>
        )}
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 3 }}>
        <Collapse in={historyOpen}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center", mb: 1 }}>
              <Typography variant="h3">Dossiê</Typography>
              {outcomes.length > 0 && (
                <Button size="small" onClick={clearReachHistory}>
                  Limpar
                </Button>
              )}
            </Stack>
            {outcomes.length === 0 ? (
              <Typography color="text.secondary">Ainda vazio — marque status após enviar.</Typography>
            ) : (
              <Stack spacing={1}>
                {outcomes.map((ev) => (
                  <Stack
                    key={ev.id}
                    direction={{ xs: "column", sm: "row" }}
                    spacing={1}
                    sx={{ alignItems: { sm: "baseline" } }}
                  >
                    <Chip size="small" label={STATUS_LABEL_PT[ev.status]} color="primary" />
                    <Typography variant="body2" sx={{ flex: 1 }}>
                      {ev.bridgeName} → {ev.targetName}
                      {ev.accountCompany ? ` · ${ev.accountCompany}` : ""}
                    </Typography>
                    <Typography variant="caption">{formatReachWhen(ev.at)}</Typography>
                  </Stack>
                ))}
              </Stack>
            )}
          </Paper>
        </Collapse>

        {(network || result) && (
          <Box component={motion.div} {...fade}>
            <SpiderBoard
              sellerName={sellerName}
              sellerTitle={sellerPinTitle}
              sellerCompany={sellerPinCompany}
              sellerLinkedin={sellerLinkedin}
              sellerPhoto={sellerPhoto}
              targetPhoto={targetPhoto}
              networkContacts={network?.contacts ?? []}
              result={
                workspaceMode === "account" && accountResult && !activeAccountTargetId
                  ? null
                  : result
              }
              selectedId={selected?.contact_id ?? null}
              onSelectBridge={setSelected}
              targetLinkedin={targetLinkedin}
            />
          </Box>
        )}

        <Grid container spacing={2} sx={{ alignItems: "flex-start" }}>
          <Grid size={{ xs: 12, md: 5 }}>
            <Card>
              <CardContent>
                <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center", mb: 1.5 }}>
                  <Typography variant="overline" color="text.secondary">
                    Briefing
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    {(restored || isDemo || network) && (
                      <Button size="small" startIcon={<ClearIcon />} onClick={resetSession}>
                        Limpar
                      </Button>
                    )}
                  </Stack>
                </Stack>

                {isDemo && (
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    Modo demo (eval) — não é sua rede real. Produção = sessão LinkedIn automática.
                  </Alert>
                )}

                <Alert severity={sessionAlertSeverity} sx={{ mb: 2 }}>
                  <Typography sx={{ fontWeight: 700 }}>Sessão LinkedIn</Typography>
                  <Typography variant="body2">
                    {sessionStatus?.ready
                      ? "Camoufox pronto — mutuals ao vivo via scrape."
                      : sessionStatus?.account?.configured
                        ? "Conta configurada — sessão headless na subida."
                        : "Cole no chat: email LinkedIn + senha + Gmail App Password."}
                  </Typography>
                  <Button
                    size="small"
                    sx={{ mt: 1 }}
                    onClick={() => setSessionStatusOpen((o) => !o)}
                  >
                    {sessionStatusOpen ? "Ocultar detalhes" : "Detalhes sessão"}
                  </Button>
                  <Collapse in={sessionStatusOpen}>
                    <Box sx={{ mt: 1 }}>
                      {(sessionStatus?.hints || []).slice(0, 5).map((h) => (
                        <Typography key={h} variant="caption" sx={{ display: "block" }}>
                          · {h}
                        </Typography>
                      ))}
                    </Box>
                  </Collapse>
                </Alert>

                <Button size="small" onClick={() => setLegacyImportOpen((o) => !o)} sx={{ mb: 1 }}>
                  Legado · CSV import (deprecated)
                </Button>
                <Collapse in={legacyImportOpen}>
                  <Stack spacing={1.5} sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Fallback offline — produção usa scrape LinkedIn (mutuals).
                    </Typography>
                    <TextField
                      multiline
                      minRows={3}
                      fullWidth
                      value={networkPaste}
                      onChange={(e) => setNetworkPaste(e.target.value)}
                      placeholder="Connections.csv, celular ou cartões…"
                    />
                    <Stack direction="row" spacing={1} useFlexGap sx={{ flexWrap: "wrap" }}>
                      <Button
                        variant="outlined"
                        size="small"
                        disabled={busy || !networkPaste.trim()}
                        onClick={() => void onImport()}
                      >
                        Importar · {network?.contacts?.length ?? 0}
                      </Button>
                    </Stack>
                  </Stack>
                </Collapse>

                <Divider sx={{ mb: 2 }} />

                <Tabs
                  value={workspaceMode}
                  onChange={(_, v: WorkspaceMode) => setWorkspaceMode(v)}
                  sx={{ mb: 2, minHeight: 40 }}
                >
                  <Tab value="single" label="Alvo único" />
                  <Tab value="account" label="Conta" />
                </Tabs>

                <Typography variant="caption" color="text.secondary" sx={{ display: "block", mb: 0.5 }}>
                  2 · Alvo · {sellerLabel}
                </Typography>

                {workspaceMode === "single" ? (
                  <Stack spacing={1.5}>
                    <TextField
                      label="LinkedIn do alvo"
                      fullWidth
                      required
                      value={targetLinkedin}
                      onChange={(e) => setTargetLinkedin(e.target.value)}
                      placeholder="https://www.linkedin.com/in/…"
                    />
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
                      <TextField
                        label="Nome (opcional — preenchido no scrape)"
                        fullWidth
                        value={targetName}
                        onChange={(e) => setTargetName(e.target.value)}
                      />
                      <TextField
                        label="Empresa"
                        fullWidth
                        value={targetCompany}
                        onChange={(e) => setTargetCompany(e.target.value)}
                      />
                    </Stack>
                    <TextField
                      label="Cargo"
                      fullWidth
                      value={targetTitle}
                      onChange={(e) => setTargetTitle(e.target.value)}
                    />
                    <TextField
                      select
                      label="Idioma"
                      value={locale}
                      onChange={(e) => setLocale(e.target.value)}
                      sx={{ maxWidth: 140 }}
                    >
                      <MenuItem value="pt">PT</MenuItem>
                      <MenuItem value="en">EN</MenuItem>
                    </TextField>
                    <Button
                      variant="contained"
                      size="large"
                      fullWidth
                      startIcon={<LinkedInIcon />}
                      disabled={busy || !targetLinkedin.trim()}
                      onClick={() => void onMapear()}
                    >
                      {busy ? "Mapeando…" : "Mapear"}
                    </Button>
                    <Typography variant="caption" color="text.secondary">
                      Mutuals observados + enrich + pesquisa pública citada — zero CSV.
                    </Typography>
                  </Stack>
                ) : (
                  <Stack spacing={1.5}>
                    <TextField
                      label="Empresa / conta"
                      fullWidth
                      value={accountCompany}
                      onChange={(e) => setAccountCompany(e.target.value)}
                    />
                    {accountTargets.map((t) => (
                      <Stack key={t.id} direction="row" spacing={1} sx={{ alignItems: "center" }}>
                        <TextField
                          label="Nome"
                          fullWidth
                          value={t.name}
                          onChange={(e) => updateAccountTarget(t.id, { name: e.target.value })}
                        />
                        <TextField
                          label="Cargo"
                          fullWidth
                          value={t.title}
                          onChange={(e) => updateAccountTarget(t.id, { title: e.target.value })}
                        />
                        <IconButton
                          aria-label="Remover"
                          disabled={accountTargets.length <= 1}
                          onClick={() => removeAccountTarget(t.id)}
                        >
                          <DeleteOutlineIcon />
                        </IconButton>
                      </Stack>
                    ))}
                    <Stack direction="row" spacing={1}>
                      <Button size="small" startIcon={<AddIcon />} onClick={addAccountTarget}>
                        Alvo
                      </Button>
                      <Button
                        size="small"
                        onClick={() =>
                          loadExampleAccount().then((a) => {
                            setAccountCompany(a.company);
                            setAccountTargets(a.targets);
                          })
                        }
                      >
                        Exemplo 3S
                      </Button>
                    </Stack>
                    <Button
                      variant="contained"
                      fullWidth
                      disabled={busy || !accountCompany.trim() || !network}
                      onClick={() => void onFindAccount()}
                    >
                      Mapear conta inteira
                    </Button>
                  </Stack>
                )}

                <Divider sx={{ my: 2 }} />
                <Button size="small" onClick={() => setAdvancedOpen((o) => !o)}>
                  Avançado · demo eval / seller YAML
                </Button>
                <Collapse in={advancedOpen}>
                  <Stack spacing={1.5} sx={{ mt: 1.5 }}>
                    <Button component="label" size="small">
                      Seller YAML · {sellerLabel}
                      <input
                        type="file"
                        hidden
                        accept=".yaml,.yml,.json"
                        onChange={(e) => void onUploadSeller(e.target.files?.[0] ?? null)}
                      />
                    </Button>
                    <TextField
                      label="Seu LinkedIn (auto de secrets se vazio)"
                      fullWidth
                      value={sellerLinkedin}
                      onChange={(e) => patchSellerLinkedin(e.target.value)}
                      placeholder="https://www.linkedin.com/in/…"
                    />
                    <Button
                      size="small"
                      startIcon={<PlayArrowIcon />}
                      disabled={busy}
                      onClick={() => void loadDemo()}
                    >
                      Demo eval (dev)
                    </Button>
                  </Stack>
                </Collapse>

                {insight && (
                  <Paper sx={{ mt: 2, p: 1.5 }}>
                    <Typography variant="overline">Insights públicos</Typography>
                    {insight.empty ? (
                      <Typography variant="body2" color="text.secondary">
                        {insight.note}
                      </Typography>
                    ) : (
                      <Stack spacing={1} sx={{ mt: 1 }}>
                        {insight.items.slice(0, 5).map((item) => (
                          <Box key={item.url}>
                            <Link href={item.url} target="_blank" rel="noreferrer" variant="body2">
                              {item.title}
                            </Link>
                            {item.snippet && (
                              <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>
                                {item.snippet}
                              </Typography>
                            )}
                          </Box>
                        ))}
                      </Stack>
                    )}
                  </Paper>
                )}

                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                  </Alert>
                )}
                {status && !error && (
                  <Alert severity="success" sx={{ mt: 2 }} icon={false}>
                    <Typography variant="body2" sx={{ fontFamily: "IBM Plex Mono, monospace" }}>
                      {status}
                    </Typography>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 12, md: 7 }}>
            <Card>
              <CardContent>
                {!result && !accountResult && (
                  <Box sx={{ py: 3 }}>
                    <Typography variant="h2" gutterBottom>
                      {network ? "Caso montado" : "Comece aqui"}
                    </Typography>
                    <Typography color="text.secondary" sx={{ mb: 2 }}>
                      {network
                        ? "Clique uma ponte no quadro ou na lista — o pedido abre abaixo."
                        : "Importe Connections.csv no Briefing e clique Investigar."}
                    </Typography>
                  </Box>
                )}

                {accountResult && workspaceMode === "account" && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="overline">Suspeitos · {accountResult.company}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {accountResult.summary_line}
                    </Typography>
                    <Stack spacing={1}>
                      {accountResult.targets.map((row) => (
                        <Card
                          key={row.id}
                          variant="outlined"
                          sx={{
                            borderColor:
                              activeAccountTargetId === row.id ? "primary.main" : "divider",
                            boxShadow:
                              activeAccountTargetId === row.id
                                ? "inset 0 0 0 1px #007bc0"
                                : undefined,
                          }}
                        >
                          <CardActionArea onClick={() => selectAccountTarget(row)}>
                            <CardContent sx={{ py: 1.5, "&:last-child": { pb: 1.5 } }}>
                              <Stack direction="row" sx={{ justifyContent: "space-between" }}>
                                <Typography sx={{ fontWeight: 700 }}>{row.name}</Typography>
                                <Chip
                                  size="small"
                                  label={
                                    row.has_path
                                      ? confidenceLabel(row.top_confidence || "medium")
                                      : "Sem ponte"
                                  }
                                  color={bandColor(row.top_confidence || "low")}
                                />
                              </Stack>
                              <Typography variant="body2" color="text.secondary">
                                {row.proof_line}
                              </Typography>
                            </CardContent>
                          </CardActionArea>
                        </Card>
                      ))}
                    </Stack>
                  </Box>
                )}

                {result && (
                  <>
                    <Stack
                      direction={{ xs: "column", sm: "row" }}
                      sx={{ justifyContent: "space-between", mb: 1.5, gap: 1 }}
                    >
                      <Typography variant="h3">Lista do caso</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {selected
                          ? "Pedido abaixo · clique outra ponte para trocar"
                          : "Clique no pin ou na lista"}
                      </Typography>
                    </Stack>
                    {result.direct.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="overline">Já na sua rede</Typography>
                        {result.direct.map((b) => (
                          <BridgeCard
                            key={b.contact_id}
                            bridge={b}
                            selected={selected?.contact_id === b.contact_id}
                            onSelect={() => setSelected(b)}
                          />
                        ))}
                      </Box>
                    )}
                    {result.bridges.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="overline">Pontes quentes</Typography>
                        {result.bridges.map((b) => (
                          <BridgeCard
                            key={b.contact_id}
                            bridge={b}
                            selected={selected?.contact_id === b.contact_id}
                            onSelect={() => setSelected(b)}
                          />
                        ))}
                      </Box>
                    )}

                    {selected?.message && (
                      <Paper
                        ref={askRef as React.RefObject<HTMLDivElement>}
                        sx={{
                          mt: 2,
                          p: 2,
                          bgcolor: "#05072e",
                          color: "#fff",
                          borderTop: "3px solid",
                          borderColor: "primary.light",
                        }}
                      >
                        {tutor && (
                          <Alert
                            severity={
                              tutor.level === "yes"
                                ? "success"
                                : tutor.level === "soft"
                                  ? "warning"
                                  : "error"
                            }
                            sx={{ mb: 2, bgcolor: "rgba(255,255,255,0.06)" }}
                          >
                            <Stack direction="row" spacing={1} sx={{ alignItems: "center", mb: 0.5 }}>
                              <Typography sx={{ fontWeight: 700 }}>
                                Posso pedir intro? · {tutorLevelLabel(tutor.level, locale)}
                              </Typography>
                              {favorHit && (
                                <Chip
                                  size="small"
                                  color="warning"
                                  label="já pediu recentemente"
                                  sx={{ height: 22 }}
                                />
                              )}
                            </Stack>
                            <Typography variant="body2">{tutor.headline}</Typography>
                            <Box component="ul" sx={{ m: 0, pl: 2 }}>
                              {tutor.bullets.map((x) => (
                                <li key={x}>
                                  <Typography variant="body2">{x}</Typography>
                                </li>
                              ))}
                            </Box>
                          </Alert>
                        )}
                        <Stack direction="row" sx={{ justifyContent: "space-between", mb: 1 }}>
                          <Box>
                            <Typography variant="overline" sx={{ color: "rgba(255,255,255,0.55)" }}>
                              {modeLabel(selected.mode)}
                            </Typography>
                            <Typography sx={{ color: "primary.light", fontWeight: 600 }}>
                              {selected.path_label}
                            </Typography>
                          </Box>
                          <Chip
                            size="small"
                            label={confidenceLabel(selected.confidence)}
                            color={bandColor(selected.confidence)}
                          />
                        </Stack>
                        <Paper
                          sx={{
                            p: 1.5,
                            mb: 1.5,
                            bgcolor: "rgba(255,255,255,0.06)",
                            color: "inherit",
                            fontFamily: "IBM Plex Mono, monospace",
                            fontSize: "0.85rem",
                            whiteSpace: "pre-wrap",
                          }}
                        >
                          {selected.message}
                        </Paper>
                        <Stack direction="row" useFlexGap sx={{ flexWrap: "wrap", gap: 1, mb: 1.5 }}>
                          <Button
                            variant="contained"
                            startIcon={<ContentCopyIcon />}
                            color={copied ? "success" : "primary"}
                            onClick={() => void copyMessage(selected.message || "")}
                          >
                            {copied ? "Copiado" : "Copiar"}
                          </Button>
                          {waLink ? (
                            <Button
                              variant="outlined"
                              href={waLink}
                              target="_blank"
                              rel="noreferrer"
                              startIcon={<ChatIcon />}
                              onClick={onOpenWhatsApp}
                              sx={{ color: "#fff", borderColor: "rgba(255,255,255,0.35)" }}
                            >
                              WhatsApp
                            </Button>
                          ) : null}
                          {bridgeLinkedin ? (
                            <Button
                              variant="outlined"
                              href={bridgeLinkedin}
                              target="_blank"
                              rel="noreferrer"
                              startIcon={<LinkedInIcon />}
                              sx={{ color: "#fff", borderColor: "rgba(255,255,255,0.35)" }}
                            >
                              LinkedIn
                            </Button>
                          ) : null}
                        </Stack>
                        <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.55)" }}>
                          Status do alcance
                        </Typography>
                        <Stack direction="row" useFlexGap sx={{ flexWrap: "wrap", gap: 0.75, mt: 0.5 }}>
                          {CHIP_STATUSES.map((st) => (
                            <Chip
                              key={st}
                              size="small"
                              label={STATUS_LABEL_PT[st]}
                              onClick={() => recordReach(st)}
                              color={latestForSelected?.status === st ? "primary" : "default"}
                              variant={latestForSelected?.status === st ? "filled" : "outlined"}
                              sx={{
                                color: "#fff",
                                borderColor: "rgba(255,255,255,0.3)",
                              }}
                            />
                          ))}
                        </Stack>
                      </Paper>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Stack
          direction="row"
          useFlexGap
          sx={{ justifyContent: "space-between", mt: 4, flexWrap: "wrap", gap: 1, color: "text.secondary" }}
        >
          <Typography variant="caption">Lead Police · Warm Bridge</Typography>
          <Typography variant="caption">
            Craft:{" "}
            <Link href="https://rwd-dashboard.solutions.iqvia.com/public" target="_blank" rel="noreferrer">
              RWD Connect
            </Link>{" "}
            · MUI
          </Typography>
        </Stack>
      </Container>
    </Box>
  );
}

function BridgeCard({
  bridge,
  selected,
  onSelect,
}: {
  bridge: Bridge;
  selected: boolean;
  onSelect: () => void;
}) {
  const src = resolvePortrait({
    name: bridge.name,
    photo: bridge.photo,
    avatar_url: bridge.avatar_url,
    linkedin_url: bridge.linkedin_url,
  });
  return (
    <Card
      variant="outlined"
      sx={{
        mb: 1,
        borderColor: selected ? "primary.main" : "divider",
        boxShadow: selected ? "inset 0 0 0 1px #007bc0" : undefined,
        transition: "transform 0.2s, box-shadow 0.2s",
        "&:hover": { transform: "translateY(-1px)" },
      }}
    >
      <CardActionArea onClick={onSelect}>
        <CardContent sx={{ py: 1.25, "&:last-child": { pb: 1.25 } }}>
          <Stack direction="row" spacing={1.25} sx={{ alignItems: "center" }}>
            <Avatar src={src} alt="" sx={{ width: 40, height: 40 }} />
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Stack direction="row" sx={{ justifyContent: "space-between", gap: 1 }}>
                <Typography noWrap sx={{ fontWeight: 700 }}>
                  {bridge.name}
                </Typography>
                <Chip
                  size="small"
                  label={confidenceLabel(bridge.confidence)}
                  color={bandColor(bridge.confidence)}
                />
              </Stack>
              <Typography variant="body2" color="text.secondary" noWrap>
                {[bridge.title, bridge.company].filter(Boolean).join(" · ")}
              </Typography>
            </Box>
          </Stack>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
