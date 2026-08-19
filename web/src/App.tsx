import { useEffect, useRef, useState } from "react";
import {
  findAccount,
  findBridges,
  importNetwork,
  loadExampleAccount,
  loadExampleNetwork,
  loadExampleSeller,
  uploadSellerYaml,
  whatsAppUrl,
  type AccountFindResult,
  type AccountTargetResult,
  type Bridge,
  type FindResult,
  type Network,
  type Seller,
} from "./api";
import {
  CHIP_STATUSES,
  STATUS_LABEL_PT,
  clearOutcomes,
  formatReachWhen,
  loadOutcomes,
  logReach,
  type ReachEvent,
  type ReachStatus,
} from "./outcomes";
import {
  clearSession,
  defaultAccount,
  loadSession,
  newTargetId,
  saveSession,
  type AccountTargetRow,
  type WorkspaceMode,
} from "./storage";
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

function tutorClass(level: string) {
  if (level === "yes") return "tutor-yes";
  if (level === "soft") return "tutor-soft";
  return "tutor-no";
}

function applyFindResult(
  data: FindResult,
  setResult: (r: FindResult) => void,
  setSelected: (b: Bridge | null) => void,
  setStatus: (s: string) => void,
) {
  setResult(data);
  const first = data.bridges[0] || data.direct[0] || null;
  setSelected(first);
  setStatus(data.proof_line);
}

export default function App() {
  const [seller, setSeller] = useState<Seller | null>(null);
  const [sellerLabel, setSellerLabel] = useState("Carregando…");
  const [network, setNetwork] = useState<Network | null>(null);
  const [networkPaste, setNetworkPaste] = useState("");
  const [workspaceMode, setWorkspaceMode] = useState<WorkspaceMode>("single");
  const [targetName, setTargetName] = useState("Marina Costa");
  const [targetCompany, setTargetCompany] = useState("Acme Saúde");
  const [targetTitle, setTargetTitle] = useState("Diretora de Compras");
  const [accountCompany, setAccountCompany] = useState(defaultAccount().company);
  const [accountTargets, setAccountTargets] = useState<AccountTargetRow[]>(
    defaultAccount().targets,
  );
  const [accountResult, setAccountResult] = useState<AccountFindResult | null>(null);
  const [activeAccountTargetId, setActiveAccountTargetId] = useState<string | null>(null);
  const [locale, setLocale] = useState("pt");
  const [result, setResult] = useState<FindResult | null>(null);
  const [selected, setSelected] = useState<Bridge | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [copied, setCopied] = useState(false);
  const [restored, setRestored] = useState(false);
  const [outcomes, setOutcomes] = useState<ReachEvent[]>([]);
  const [historyOpen, setHistoryOpen] = useState(false);
  const askRef = useRef<HTMLElement>(null);

  useEffect(() => {
    setOutcomes(loadOutcomes());
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
      return;
    }

    Promise.all([loadExampleSeller(), loadExampleNetwork(), loadExampleAccount()])
      .then(([s, n, a]) => {
        setSeller(s);
        setNetwork(n);
        setAccountCompany(a.company);
        setAccountTargets(a.targets);
        const name = (s.identity as { name?: string } | undefined)?.name;
        setSellerLabel(name ? `Exemplo: ${name}` : "Seller de exemplo");
        setStatus(`${n.contacts?.length ?? 0} contatos no grafo de exemplo`);
      })
      .catch(() => setStatus("API offline — rode: warm-bridge serve"));
  }, []);

  useEffect(() => {
    if (!network && !seller) return;
    saveSession({
      network,
      seller,
      mode: workspaceMode,
      target: { name: targetName, company: targetCompany, title: targetTitle },
      account: { company: accountCompany, targets: accountTargets },
      accountResult,
      activeAccountTargetId,
      locale,
    });
  }, [
    network,
    seller,
    workspaceMode,
    targetName,
    targetCompany,
    targetTitle,
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
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  async function onImport() {
    setError("");
    setBusy(true);
    try {
      const data = await importNetwork(networkPaste, network);
      setNetwork(data.network);
      setNetworkPaste("");
      setStatus(`${data.added} importados (${data.import_kind}) · total ${data.total}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onFind() {
    setError("");
    setBusy(true);
    setCopied(false);
    setAccountResult(null);
    setActiveAccountTargetId(null);
    try {
      const data = await findBridges({
        target: { name: targetName, company: targetCompany, title: targetTitle },
        network,
        seller,
        locale,
        top_k: 8,
        with_approaches: true,
      });
      applyFindResult(data, setResult, setSelected, setStatus);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
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
      if (first) {
        selectAccountTarget(first, data);
      } else {
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
    setAccountTargets((prev) => [
      ...prev,
      { id: newTargetId(), name: "", title: "" },
    ]);
  }

  function updateAccountTarget(id: string, patch: Partial<AccountTargetRow>) {
    setAccountTargets((prev) =>
      prev.map((t) => (t.id === id ? { ...t, ...patch } : t)),
    );
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
    setRestored(false);
    setWorkspaceMode("single");
    const acct = defaultAccount();
    setAccountCompany(acct.company);
    setAccountTargets(acct.targets);
    loadExampleSeller()
      .then((s) => {
        setSeller(s);
        const name = (s.identity as { name?: string } | undefined)?.name;
        setSellerLabel(name ? `Exemplo: ${name}` : "Seller de exemplo");
      })
      .catch(() => {});
    Promise.all([loadExampleNetwork(), loadExampleAccount()])
      .then(([n, a]) => {
        setNetwork(n);
        setAccountCompany(a.company);
        setAccountTargets(a.targets);
        setStatus("Sessão limpa — exemplos recarregados");
      })
      .catch(() => {});
  }

  const sellerName =
    (seller?.identity as { name?: string } | undefined)?.name || "você";
  const tutor = selected ? bridgeTutor(selected, locale) : null;
  const waLink =
    selected?.message && selected.phone
      ? whatsAppUrl(selected.phone, selected.message)
      : null;
  const latestForSelected = selected
    ? outcomes.find((e) => e.bridgeId === selected.contact_id)
    : null;

  const stepNetwork = (network?.contacts?.length ?? 0) > 0;
  const stepTarget =
    workspaceMode === "account"
      ? accountTargets.some((t) => t.name.trim())
      : Boolean(targetName.trim());
  const stepBridges = Boolean(result || accountResult);
  const stepAsk = Boolean(selected?.message);

  const heroLine =
    workspaceMode === "account" && accountResult && !activeAccountTargetId
      ? accountResult.summary_line
      : result?.proof_line;

  return (
    <div className="app">
      <header className="site-header">
        <div className="brand-block">
          <p className="brand">Warm Bridge</p>
          <p className="tagline">Chegue no tomador pela ponte certa.</p>
        </div>
        <nav className="steps" aria-label="Progresso">
          <span className={`step ${stepNetwork ? "on" : ""}`}>Rede</span>
          <span className={`step ${stepTarget ? "on" : ""}`}>Alvo</span>
          <span className={`step ${stepBridges ? "on" : ""}`}>Pontes</span>
          <span className={`step ${stepAsk ? "on" : ""}`}>Pedir</span>
        </nav>
        <button
          type="button"
          className={`btn ghost sm history-toggle ${historyOpen ? "on" : ""}`}
          onClick={() => setHistoryOpen((o) => !o)}
        >
          Histórico{outcomes.length ? ` (${outcomes.length})` : ""}
        </button>
      </header>

      {historyOpen && (
        <section className="history-panel animate-in" aria-label="Histórico de alcance">
          <div className="history-head">
            <h2>Histórico</h2>
            <p>Últimos alcances neste navegador — você marca o status.</p>
            {outcomes.length > 0 && (
              <button type="button" className="btn ghost sm" onClick={clearReachHistory}>
                Limpar histórico
              </button>
            )}
          </div>
          {outcomes.length === 0 ? (
            <p className="history-empty">
              Ainda vazio. Copie uma mensagem ou marque Enviei / Intro feita no painel Pedir.
            </p>
          ) : (
            <ul className="history-list">
              {outcomes.map((ev) => (
                <li key={ev.id}>
                  <span className="history-status">{STATUS_LABEL_PT[ev.status]}</span>
                  <span className="history-who">
                    {ev.bridgeName} → {ev.targetName}
                    {ev.accountCompany ? ` · ${ev.accountCompany}` : ""}
                  </span>
                  <time dateTime={ev.at}>{formatReachWhen(ev.at)}</time>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {heroLine && (
        <section className="proof-hero animate-in" key={heroLine}>
          <p className="proof-kicker">
            {workspaceMode === "account" ? "Conta mapeada" : "Melhor caminho"}
          </p>
          <p className="proof-line">{heroLine}</p>
          {result && (
            <p className="proof-meta">
              {result.counts.bridges} pontes · {result.counts.direct} direto · alvo{" "}
              {result.resolution.status}
              {workspaceMode === "account" && result.target.name
                ? ` · ${result.target.name}`
                : ""}
            </p>
          )}
        </section>
      )}

      <main className={`workspace ${result ? "has-result" : ""}`}>
        <section className="setup">
          <div className="setup-head">
            <h2>Preparar</h2>
            {restored && (
              <button type="button" className="btn ghost sm" onClick={resetSession}>
                Limpar sessão
              </button>
            )}
          </div>

          <div className="mode-toggle" role="tablist" aria-label="Modo de trabalho">
            <button
              type="button"
              role="tab"
              aria-selected={workspaceMode === "single"}
              className={`mode-btn ${workspaceMode === "single" ? "on" : ""}`}
              onClick={() => setWorkspaceMode("single")}
            >
              Alvo único
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={workspaceMode === "account"}
              className={`mode-btn ${workspaceMode === "account" ? "on" : ""}`}
              onClick={() => setWorkspaceMode("account")}
            >
              Conta · vários alvos
            </button>
          </div>

          <details className="fold" open={!result}>
            <summary>Rede · {network?.contacts?.length ?? 0} contatos</summary>
            <p className="hint">
              Cole <code>Connections.csv</code>, CSV do celular ou cartões. Dados ficam no
              navegador — sem scraper.
            </p>
            <textarea
              value={networkPaste}
              onChange={(e) => setNetworkPaste(e.target.value)}
              placeholder="Cole CSV do LinkedIn ou contatos aqui…"
            />
            <div className="row">
              <button
                type="button"
                className="btn secondary"
                disabled={busy || !networkPaste.trim()}
                onClick={onImport}
              >
                Importar / mesclar
              </button>
              <button
                type="button"
                className="btn ghost"
                onClick={() =>
                  loadExampleNetwork().then((n) => {
                    setNetwork(n);
                    setStatus("Rede de exemplo carregada");
                  })
                }
              >
                Exemplo
              </button>
            </div>
          </details>

          <details className="fold seller-fold">
            <summary>Vendedor · {sellerLabel}</summary>
            <input
              type="file"
              accept=".yaml,.yml,.json"
              onChange={(e) => onUploadSeller(e.target.files?.[0] ?? null)}
            />
          </details>

          {workspaceMode === "single" ? (
            <div className="target-block">
              <h3>Tomador de decisão</h3>
              <div className="target-grid">
                <label>
                  Nome
                  <input value={targetName} onChange={(e) => setTargetName(e.target.value)} />
                </label>
                <label>
                  Empresa
                  <input
                    value={targetCompany}
                    onChange={(e) => setTargetCompany(e.target.value)}
                  />
                </label>
                <label>
                  Cargo
                  <input value={targetTitle} onChange={(e) => setTargetTitle(e.target.value)} />
                </label>
                <label>
                  Idioma
                  <select value={locale} onChange={(e) => setLocale(e.target.value)}>
                    <option value="pt">PT · WhatsApp</option>
                    <option value="en">EN</option>
                  </select>
                </label>
              </div>
              <button
                type="button"
                className="btn primary wide"
                disabled={busy || !targetName.trim() || !network}
                onClick={onFind}
              >
                {busy ? "Mapeando pontes…" : "Achar pontes + pedidos"}
              </button>
            </div>
          ) : (
            <div className="target-block account-block">
              <h3>Conta · tomadores</h3>
              <label>
                Empresa / conta
                <input
                  value={accountCompany}
                  onChange={(e) => setAccountCompany(e.target.value)}
                />
              </label>
              <label>
                Idioma
                <select value={locale} onChange={(e) => setLocale(e.target.value)}>
                  <option value="pt">PT · WhatsApp</option>
                  <option value="en">EN</option>
                </select>
              </label>
              <div className="account-roster-edit">
                {accountTargets.map((t) => (
                  <div key={t.id} className="account-row">
                    <input
                      placeholder="Nome"
                      value={t.name}
                      onChange={(e) => updateAccountTarget(t.id, { name: e.target.value })}
                    />
                    <input
                      placeholder="Cargo"
                      value={t.title}
                      onChange={(e) => updateAccountTarget(t.id, { title: e.target.value })}
                    />
                    <button
                      type="button"
                      className="btn ghost sm"
                      aria-label="Remover alvo"
                      onClick={() => removeAccountTarget(t.id)}
                      disabled={accountTargets.length <= 1}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
              <div className="row">
                <button type="button" className="btn ghost sm" onClick={addAccountTarget}>
                  + Alvo
                </button>
                <button
                  type="button"
                  className="btn ghost sm"
                  onClick={() =>
                    loadExampleAccount().then((a) => {
                      setAccountCompany(a.company);
                      setAccountTargets(a.targets);
                    })
                  }
                >
                  Exemplo Acme
                </button>
              </div>
              <button
                type="button"
                className="btn primary wide"
                disabled={busy || !accountCompany.trim() || !network}
                onClick={onFindAccount}
              >
                {busy ? "Mapeando conta…" : "Mapear conta inteira"}
              </button>
            </div>
          )}

          {error && <p className="flash err">{error}</p>}
          {status && !error && <p className="flash ok">{status}</p>}
        </section>

        <section className="results">
          {!result && !accountResult && (
            <div className="empty">
              <h2>Prova do caminho</h2>
              <p>
                Quando {sellerName} nomear um alvo ou conta, mostramos a melhor ponte com
                motivos concretos — não um score mágico.
              </p>
            </div>
          )}

          {accountResult && workspaceMode === "account" && (
            <div className="bucket account-roster">
              <h3>Alvos em {accountResult.company}</h3>
              <p className="hint">{accountResult.summary_line}</p>
              {accountResult.targets.map((row) => (
                <button
                  key={row.id}
                  type="button"
                  className={`account-target-card ${
                    activeAccountTargetId === row.id ? "selected" : ""
                  } ${row.has_path ? "" : "no-path"}`}
                  onClick={() => selectAccountTarget(row)}
                >
                  <div className="bridge-top">
                    <strong>
                      {row.name}
                      {row.title ? ` · ${row.title}` : ""}
                    </strong>
                    <span className={`band ${row.has_path ? row.top_confidence || "medium" : "low"}`}>
                      {row.has_path ? confidenceLabel(row.top_confidence || "medium") : "Sem ponte"}
                    </span>
                  </div>
                  <p className="meta account-proof">{row.proof_line}</p>
                  {row.top_bridge_name && (
                    <p className="meta">via {row.top_bridge_name}</p>
                  )}
                </button>
              ))}
            </div>
          )}

          {result && (
            <>
              {result.direct.length > 0 && (
                <div className="bucket">
                  <h3>Já na sua rede</h3>
                  {result.direct.map((b) => (
                    <BridgeCard
                      key={b.contact_id}
                      bridge={b}
                      selected={selected?.contact_id === b.contact_id}
                      onSelect={() => setSelected(b)}
                    />
                  ))}
                </div>
              )}

              <div className="bucket">
                <h3>Pontes quentes</h3>
                {result.bridges.length === 0 && (
                  <p className="hint">
                    Nenhuma ponte forte. Enriqueça notas, marque strength=high no celular,
                    ou importe mais gente da empresa alvo.
                  </p>
                )}
                {result.bridges.map((b) => (
                  <BridgeCard
                    key={b.contact_id}
                    bridge={b}
                    selected={selected?.contact_id === b.contact_id}
                    onSelect={() => setSelected(b)}
                  />
                ))}
              </div>
            </>
          )}
        </section>
      </main>

      {selected && tutor && (
        <aside className="ask-dock animate-in" ref={askRef}>
          <div className={`tutor ${tutorClass(tutor.level)}`}>
            <div className="tutor-head">
              <span className="tutor-q">Posso pedir intro?</span>
              <span className={`tutor-badge ${tutorClass(tutor.level)}`}>
                {tutorLevelLabel(tutor.level, locale)}
              </span>
            </div>
            <p className="tutor-headline">{tutor.headline}</p>
            <ul className="tutor-bullets">
              {tutor.bullets.map((b) => (
                <li key={b}>{b}</li>
              ))}
            </ul>
          </div>

          <div className="ask-body">
            <header className="ask-head">
              <div>
                <p className="ask-mode">{modeLabel(selected.mode)}</p>
                <p className="ask-path">{selected.path_label}</p>
              </div>
              <span className={`band ${selected.confidence}`}>
                {confidenceLabel(selected.confidence)}
              </span>
            </header>
            <pre className="ask-message">{selected.message || "Sem mensagem gerada."}</pre>
            <div className="ask-actions">
              <button
                type="button"
                className={`btn primary ${copied ? "copied" : ""}`}
                disabled={!selected.message}
                onClick={() => selected.message && copyMessage(selected.message)}
              >
                {copied ? "Copiado ✓" : "Copiar mensagem"}
              </button>
              {waLink && (
                <a
                  className="btn wa"
                  href={waLink}
                  target="_blank"
                  rel="noreferrer"
                  onClick={onOpenWhatsApp}
                >
                  Abrir WhatsApp
                </a>
              )}
              {selected.linkedin_url && (
                <a
                  className="btn ghost"
                  href={selected.linkedin_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  LinkedIn
                </a>
              )}
            </div>
            <div className="outcome-chips" role="group" aria-label="Status do alcance">
              <span className="outcome-label">Status</span>
              {CHIP_STATUSES.map((st) => (
                <button
                  key={st}
                  type="button"
                  className={`chip ${latestForSelected?.status === st ? "on" : ""}`}
                  onClick={() => {
                    recordReach(st);
                    setStatus(`${STATUS_LABEL_PT[st]} · ${selected.name}`);
                  }}
                >
                  {STATUS_LABEL_PT[st]}
                </button>
              ))}
            </div>
            {latestForSelected && (
              <p className="outcome-latest">
                Último: {STATUS_LABEL_PT[latestForSelected.status]} ·{" "}
                {formatReachWhen(latestForSelected.at)}
              </p>
            )}
            {result && <p className="ask-note">{result.note}</p>}
          </div>
        </aside>
      )}

      <footer className="site-footer">
        <span>Você envia · nós achamos a ponte</span>
        <code>warm-bridge serve</code>
      </footer>
    </div>
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
  return (
    <button
      type="button"
      className={`bridge-card ${selected ? "selected" : ""}`}
      onClick={onSelect}
    >
      <div className="bridge-top">
        <strong>{bridge.path_label}</strong>
        <span className={`band ${bridge.confidence}`}>
          {confidenceLabel(bridge.confidence)}
        </span>
      </div>
      <p className="meta">
        {bridge.title || "Sem cargo"}
        {bridge.company ? ` · ${bridge.company}` : ""} · {modeLabel(bridge.mode)}
      </p>
      <ul className="why">
        {bridge.why.slice(0, 3).map((w) => (
          <li key={w}>{w}</li>
        ))}
      </ul>
    </button>
  );
}
