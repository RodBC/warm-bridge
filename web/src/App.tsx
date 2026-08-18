import { useEffect, useState } from "react";
import {
  findBridges,
  importNetwork,
  loadExampleNetwork,
  loadExampleSeller,
  uploadSellerYaml,
  type Bridge,
  type FindResult,
  type Network,
  type Seller,
} from "./api";

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

export default function App() {
  const [seller, setSeller] = useState<Seller | null>(null);
  const [sellerLabel, setSellerLabel] = useState("Carregando vendedor…");
  const [network, setNetwork] = useState<Network | null>(null);
  const [networkPaste, setNetworkPaste] = useState("");
  const [targetName, setTargetName] = useState("Marina Costa");
  const [targetCompany, setTargetCompany] = useState("Acme Saúde");
  const [targetTitle, setTargetTitle] = useState("Diretora de Compras");
  const [locale, setLocale] = useState("pt");
  const [result, setResult] = useState<FindResult | null>(null);
  const [selected, setSelected] = useState<Bridge | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    Promise.all([loadExampleSeller(), loadExampleNetwork()])
      .then(([s, n]) => {
        setSeller(s);
        setNetwork(n);
        const name = (s.identity as { name?: string } | undefined)?.name;
        setSellerLabel(name ? `Exemplo: ${name}` : "Seller de exemplo");
        setStatus(`${n.contacts?.length ?? 0} contatos no grafo de exemplo`);
      })
      .catch(() => {
        setStatus("API offline — rode: warm-bridge serve");
      });
  }, []);

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
    try {
      const data = await findBridges({
        target: { name: targetName, company: targetCompany, title: targetTitle },
        network,
        seller,
        locale,
        top_k: 8,
        with_approaches: true,
      });
      setResult(data);
      const first = data.bridges[0] || data.direct[0] || null;
      setSelected(first);
      setStatus(data.proof_line);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function copyMessage(text: string) {
    await navigator.clipboard.writeText(text);
    setStatus("Mensagem copiada — cole no WhatsApp / LinkedIn");
  }

  const sellerName =
    (seller?.identity as { name?: string } | undefined)?.name || "você";

  return (
    <div className="app">
      <header className="hero">
        <p className="eyebrow">Warm Bridge</p>
        <h1>Chegue no tomador pela ponte certa.</h1>
        <p className="lede">
          Importe sua rede, nomeie o alvo, veja o caminho mais quente e copie o
          pedido. Você manda — a gente não queima sua relação.
        </p>
        <div className="steps">
          <span className={`pill ${network ? "on" : ""}`}>1 Rede</span>
          <span className={`pill ${targetName ? "on" : ""}`}>2 Alvo</span>
          <span className={`pill ${result ? "on" : ""}`}>3 Pontes</span>
          <span className={`pill ${selected?.message ? "on" : ""}`}>4 Pedir</span>
        </div>
      </header>

      <div className="notice">
        LinkedIn: use o export oficial <code>Connections.csv</code> ou cole
        contatos. Sem scraper. O moat é ranking + pedido que preserva a rede —
        o mesmo racional de “quem abordar” da healthtech, com os <em>seus</em>{" "}
        dados.
      </div>

      <div className="layout">
        <section className="panel inputs">
          <h2>Quem vende</h2>
          <p className="hint">{sellerLabel}</p>
          <div className="row">
            <input
              type="file"
              accept=".yaml,.yml,.json"
              onChange={(e) => onUploadSeller(e.target.files?.[0] ?? null)}
            />
            <button
              type="button"
              className="btn ghost"
              onClick={() =>
                loadExampleSeller().then((s) => {
                  setSeller(s);
                  setSellerLabel("Exemplo recarregado");
                })
              }
            >
              Usar exemplo
            </button>
          </div>

          <h2>Rede (import)</h2>
          <p className="hint">
            Cole Connections.csv, CSV do celular (<code>name,phone,company,notes,strength</code>)
            ou cartões separados por linha em branco. Grafo atual:{" "}
            <strong>{network?.contacts?.length ?? 0}</strong> contatos.
          </p>
          <textarea
            value={networkPaste}
            onChange={(e) => setNetworkPaste(e.target.value)}
            placeholder={`Ana Ribeiro\nCoordenadora de Suprimentos | Acme Saúde\nColega de hospital; ainda fala com compras.\n\nou cole o CSV do LinkedIn…`}
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
              Rede exemplo
            </button>
          </div>

          <h2>Alvo (tomador)</h2>
          <label>
            Nome
            <input value={targetName} onChange={(e) => setTargetName(e.target.value)} />
          </label>
          <label>
            Empresa / conta
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
            Idioma do pedido
            <select value={locale} onChange={(e) => setLocale(e.target.value)}>
              <option value="pt">Português (WhatsApp)</option>
              <option value="en">English</option>
            </select>
          </label>

          <button
            type="button"
            className="btn primary"
            disabled={busy || !targetName.trim() || !network}
            onClick={onFind}
          >
            {busy ? "Mapeando pontes…" : "Achar pontes + pedidos"}
          </button>

          {error && <p className="flash err">{error}</p>}
          {status && !error && <p className="flash ok">{status}</p>}
        </section>

        <section className="panel outputs">
          {!result && (
            <div className="empty">
              <h2>Prova do caminho</h2>
              <p>
                Quando {sellerName} nomear um alvo, mostramos a melhor ponte
                com motivos concretos — não um “score mágico”.
              </p>
            </div>
          )}

          {result && (
            <>
              <div className="proof">
                <p className="proof-kicker">Melhor caminho</p>
                <p className="proof-line">{result.proof_line}</p>
                <p className="meta">
                  Resolução do alvo: <strong>{result.resolution.status}</strong>
                  {result.resolution.contact_name
                    ? ` · ${result.resolution.contact_name}`
                    : ""}
                  {" · "}
                  {result.counts.bridges} pontes · {result.counts.direct} direto
                </p>
              </div>

              {result.direct.length > 0 && (
                <div className="bucket">
                  <h3>Já na sua rede</h3>
                  {result.direct.map((b) => (
                    <button
                      key={b.contact_id}
                      type="button"
                      className={`bridge-card ${selected?.contact_id === b.contact_id ? "selected" : ""}`}
                      onClick={() => setSelected(b)}
                    >
                      <div className="bridge-top">
                        <strong>{b.path_label}</strong>
                        <span className="band">{confidenceLabel(b.confidence)}</span>
                      </div>
                      <p className="meta">{modeLabel(b.mode)}</p>
                    </button>
                  ))}
                </div>
              )}

              <div className="bucket">
                <h3>Pontes quentes</h3>
                {result.bridges.length === 0 && (
                  <p className="hint">
                    Nenhuma ponte forte. Enriqueça notas (“conhece Marina”),
                    marque strength=high no celular, ou importe mais gente da
                    empresa alvo.
                  </p>
                )}
                {result.bridges.map((b) => (
                  <button
                    key={b.contact_id}
                    type="button"
                    className={`bridge-card ${selected?.contact_id === b.contact_id ? "selected" : ""}`}
                    onClick={() => setSelected(b)}
                  >
                    <div className="bridge-top">
                      <strong>{b.path_label}</strong>
                      <span className={`band ${b.confidence}`}>
                        {confidenceLabel(b.confidence)}
                      </span>
                    </div>
                    <p className="meta">
                      {b.title || "Sem cargo"}
                      {b.company ? ` · ${b.company}` : ""} · {modeLabel(b.mode)}
                    </p>
                    <ul className="why">
                      {b.why.slice(0, 3).map((w) => (
                        <li key={w}>{w}</li>
                      ))}
                    </ul>
                  </button>
                ))}
              </div>

              {selected && (
                <article className="ask">
                  <header>
                    <h3>Pedido · {modeLabel(selected.mode)}</h3>
                    <span className="band">{confidenceLabel(selected.confidence)}</span>
                  </header>
                  <p className="path">{selected.path_label}</p>
                  <ul className="why">
                    {selected.why.map((w) => (
                      <li key={w}>{w}</li>
                    ))}
                  </ul>
                  <pre>{selected.message || "Sem mensagem gerada."}</pre>
                  <div className="row">
                    <button
                      type="button"
                      className="btn primary"
                      disabled={!selected.message}
                      onClick={() => selected.message && copyMessage(selected.message)}
                    >
                      Copiar pra WhatsApp
                    </button>
                    {selected.linkedin_url && (
                      <a href={selected.linkedin_url} target="_blank" rel="noreferrer">
                        Abrir LinkedIn
                      </a>
                    )}
                  </div>
                  <p className="hint">{result.note}</p>
                </article>
              )}
            </>
          )}
        </section>
      </div>

      <footer>
        API: <code>warm-bridge serve</code> · UI: <code>cd web && npm run dev</code>{" "}
        · <code>docs/ARCHITECTURE.md</code>
      </footer>
    </div>
  );
}
