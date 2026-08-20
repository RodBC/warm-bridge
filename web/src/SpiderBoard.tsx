import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import { resolvePortrait, boardLinkedInHref } from "./avatar";
import type { Bridge, ContactNode, FindResult } from "./api";

export type BoardNodeRole = "you" | "target" | "bridge" | "direct" | "contact";

export type BoardNode = {
  id: string;
  name: string;
  company?: string;
  title?: string;
  photo?: string;
  linkedin_url?: string;
  role: BoardNodeRole;
  bridge?: Bridge;
  x: number;
  y: number;
};

export type BoardEdge = {
  id: string;
  from: string;
  to: string;
  kind: "path" | "soft" | "cluster";
};

type Props = {
  sellerName: string;
  sellerTitle?: string;
  sellerCompany?: string;
  sellerLinkedin?: string;
  sellerPhoto?: string;
  targetPhoto?: string;
  networkContacts: ContactNode[];
  result: FindResult | null;
  selectedId: string | null;
  onSelectBridge: (b: Bridge) => void;
  targetLinkedin?: string;
};

const W = 1180;
const H = 680;
const PIN_W = 168;
const MARGIN = 90;
const POS_KEY = "warm-bridge-pin-positions-v2";

type PosMap = Record<string, { x: number; y: number }>;

function loadPositions(): PosMap {
  try {
    const raw = localStorage.getItem(POS_KEY);
    if (!raw) return {};
    return JSON.parse(raw) as PosMap;
  } catch {
    return {};
  }
}

function savePositions(map: PosMap) {
  try {
    localStorage.setItem(POS_KEY, JSON.stringify(map));
  } catch {
    /* ignore */
  }
}

function yarnPath(x1: number, y1: number, x2: number, y2: number, wobble: number): string {
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.hypot(dx, dy) || 1;
  const nx = -dy / len;
  const ny = dx / len;
  const cx = mx + nx * wobble;
  const cy = my + ny * wobble;
  return `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`;
}

/** Scatter slots — investigation board, not a single column */
function scatterSlots(count: number): { x: number; y: number }[] {
  const slots = [
    { x: 340, y: 140 },
    { x: 520, y: 110 },
    { x: 700, y: 150 },
    { x: 380, y: 320 },
    { x: 560, y: 300 },
    { x: 740, y: 340 },
    { x: 300, y: 500 },
    { x: 500, y: 520 },
    { x: 680, y: 500 },
    { x: 860, y: 280 },
  ];
  return slots.slice(0, Math.max(count, 0));
}

function layoutBoard(
  sellerName: string,
  sellerTitle: string | undefined,
  sellerCompany: string | undefined,
  sellerLinkedin: string | undefined,
  sellerPhoto: string | undefined,
  contacts: ContactNode[],
  result: FindResult | null,
  targetLinkedin?: string,
  targetPhoto?: string,
): { nodes: BoardNode[]; edges: BoardEdge[] } {
  const nodes: BoardNode[] = [];
  const edges: BoardEdge[] = [];

  const youId = "you";
  nodes.push({
    id: youId,
    name: sellerName,
    title: sellerTitle || undefined,
    company: sellerCompany || undefined,
    photo: sellerPhoto,
    linkedin_url: sellerLinkedin,
    role: "you",
    x: MARGIN + 10,
    y: H / 2,
  });

  if (!result) {
    const ring = contacts.slice(0, 9);
    const slots = scatterSlots(ring.length);
    ring.forEach((c, i) => {
      const id = c.id || `n_${i}`;
      const slot = slots[i] || { x: 500, y: 300 };
      nodes.push({
        id,
        name: c.name,
        company: c.company,
        title: c.title,
        photo: c.photo || c.avatar_url,
        linkedin_url: c.linkedin_url,
        role: "contact",
        x: slot.x,
        y: slot.y,
      });
      edges.push({ id: `e_${id}`, from: youId, to: id, kind: "soft" });
    });
    // Cluster soft edges: same company
    for (let i = 0; i < ring.length; i++) {
      for (let j = i + 1; j < ring.length; j++) {
        const a = ring[i];
        const b = ring[j];
        const ca = (a.company || "").toLowerCase();
        const cb = (b.company || "").toLowerCase();
        if (ca && ca === cb) {
          edges.push({
            id: `cl_${a.id}_${b.id}`,
            from: a.id || `n_${i}`,
            to: b.id || `n_${j}`,
            kind: "cluster",
          });
        }
      }
    }
    return { nodes, edges };
  }

  const targetId = "target";
  nodes.push({
    id: targetId,
    name: result.target.name,
    company: result.target.company,
    title: result.target.title,
    photo: targetPhoto,
    linkedin_url: targetLinkedin,
    role: "target",
    x: W - MARGIN - 10,
    y: H / 2,
  });

  const pathBridges = result.bridges.slice(0, 8);
  const directs = result.direct.slice(0, 2);
  const slots = scatterSlots(pathBridges.length + directs.length);

  pathBridges.forEach((b, i) => {
    const slot = slots[i] || { x: 500, y: 300 };
    nodes.push({
      id: b.contact_id,
      name: b.name,
      company: b.company,
      title: b.title,
      photo: b.photo || b.avatar_url,
      linkedin_url: b.linkedin_url,
      role: "bridge",
      bridge: b,
      x: slot.x,
      y: slot.y,
    });
    edges.push({ id: `yb_${b.contact_id}`, from: youId, to: b.contact_id, kind: "path" });
    edges.push({ id: `bt_${b.contact_id}`, from: b.contact_id, to: targetId, kind: "path" });
  });

  directs.forEach((b, i) => {
    const slot = slots[pathBridges.length + i] || { x: 860, y: 160 };
    nodes.push({
      id: b.contact_id,
      name: b.name,
      company: b.company,
      title: b.title,
      photo: b.photo || b.avatar_url,
      linkedin_url: b.linkedin_url,
      role: "direct",
      bridge: b,
      x: slot.x,
      y: Math.min(slot.y, MARGIN + 80),
    });
    edges.push({ id: `yd_${b.contact_id}`, from: youId, to: b.contact_id, kind: "soft" });
    edges.push({ id: `dt_${b.contact_id}`, from: b.contact_id, to: targetId, kind: "path" });
  });

  // Multi-links: same employer among bridges
  for (let i = 0; i < pathBridges.length; i++) {
    for (let j = i + 1; j < pathBridges.length; j++) {
      const a = pathBridges[i];
      const b = pathBridges[j];
      const ca = (a.company || "").toLowerCase();
      const cb = (b.company || "").toLowerCase();
      if (ca && ca === cb) {
        edges.push({
          id: `cl_${a.contact_id}_${b.contact_id}`,
          from: a.contact_id,
          to: b.contact_id,
          kind: "cluster",
        });
      }
    }
  }

  if (pathBridges.length === 0 && directs.length === 0) {
    edges.push({ id: "cold", from: youId, to: targetId, kind: "soft" });
  }

  return { nodes, edges };
}

function PersonPin({
  node,
  selected,
  onSelect,
  onDragStart,
}: {
  node: BoardNode;
  selected: boolean;
  onSelect?: () => void;
  onDragStart: (id: string, e: ReactPointerEvent) => void;
}) {
  const companyLine =
    node.title && node.company
      ? `${node.title} - ${node.company}`
      : node.title || node.company || "";
  const src = resolvePortrait({
    name: node.name,
    photo: node.photo,
    avatar_url: node.photo,
    linkedin_url: node.linkedin_url,
  });
  const liHref = boardLinkedInHref({
    name: node.name,
    linkedin_url: node.linkedin_url,
  });

  return (
    <div
      role={node.bridge ? "button" : undefined}
      tabIndex={node.bridge ? 0 : undefined}
      className={`person-pin role-${node.role} ${selected ? "selected" : ""} ${
        node.bridge ? "clickable" : ""
      }`}
      style={{ left: node.x, top: node.y, width: PIN_W }}
      onPointerDown={(e) => {
        if ((e.target as HTMLElement).closest("a.pin-linkedin")) return;
        onDragStart(node.id, e);
      }}
      onKeyDown={(e) => {
        if ((e.key === "Enter" || e.key === " ") && onSelect) {
          e.preventDefault();
          onSelect();
        }
      }}
      title={`${node.name}${companyLine ? ` — ${companyLine}` : ""} · arraste para mover`}
      aria-pressed={node.bridge ? selected : undefined}
    >
      <span className="pin-tack" aria-hidden />
      <img
        className="pin-photo"
        src={src}
        alt=""
        width={72}
        height={72}
        draggable={false}
        referrerPolicy="no-referrer"
        onError={(e) => {
          e.currentTarget.src = resolvePortrait({ name: node.name });
        }}
      />
      <span className="pin-body">
        <span className="pin-role-tag">
          {node.role === "you"
            ? "Você"
            : node.role === "target"
              ? "Alvo"
              : node.role === "direct"
                ? "Direto"
                : node.role === "bridge"
                  ? "Ponte"
                  : "Rede"}
        </span>
        <span className="pin-name">{node.name}</span>
        {companyLine ? <span className="pin-meta">{companyLine}</span> : null}
      </span>
      {liHref ? (
        <a
          className="pin-linkedin"
          href={liHref}
          target="_blank"
          rel="noreferrer"
          title={`Abrir LinkedIn · ${node.name}`}
          aria-label={`Abrir LinkedIn de ${node.name}`}
          onPointerDown={(e) => e.stopPropagation()}
          onClick={(e) => e.stopPropagation()}
        >
          <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden>
            <path
              fill="currentColor"
              d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.23 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.22.79 24 1.77 24h20.45c.98 0 1.78-.78 1.78-1.73V1.73C24 .77 23.2 0 22.23 0z"
            />
          </svg>
          <span>LinkedIn</span>
        </a>
      ) : null}
    </div>
  );
}

export function SpiderBoard({
  sellerName,
  sellerTitle,
  sellerCompany,
  sellerLinkedin,
  sellerPhoto,
  targetPhoto,
  networkContacts,
  result,
  selectedId,
  onSelectBridge,
  targetLinkedin,
}: Props) {
  const base = useMemo(
    () =>
      layoutBoard(
        sellerName,
        sellerTitle,
        sellerCompany,
        sellerLinkedin,
        sellerPhoto,
        networkContacts,
        result,
        targetLinkedin,
        targetPhoto,
      ),
    [
      sellerName,
      sellerTitle,
      sellerCompany,
      sellerLinkedin,
      sellerPhoto,
      networkContacts,
      result,
      targetLinkedin,
      targetPhoto,
    ],
  );

  const [overrides, setOverrides] = useState<PosMap>(() => loadPositions());
  const dragRef = useRef<{
    id: string;
    ox: number;
    oy: number;
    sx: number;
    sy: number;
    moved: boolean;
  } | null>(null);
  const corkRef = useRef<HTMLDivElement>(null);

  const nodes = useMemo(() => {
    return base.nodes.map((n) => {
      const o = overrides[n.id];
      return o ? { ...n, x: o.x, y: o.y } : n;
    });
  }, [base.nodes, overrides]);

  const byId = useMemo(() => {
    const m = new Map<string, BoardNode>();
    nodes.forEach((n) => m.set(n.id, n));
    return m;
  }, [nodes]);

  const onDragStart = useCallback((id: string, e: ReactPointerEvent) => {
    e.preventDefault();
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
    const node = byId.get(id);
    if (!node) return;
    dragRef.current = {
      id,
      ox: e.clientX,
      oy: e.clientY,
      sx: node.x,
      sy: node.y,
      moved: false,
    };
  }, [byId]);

  useEffect(() => {
    const onMove = (e: PointerEvent) => {
      const d = dragRef.current;
      if (!d || !corkRef.current) return;
      const dx = e.clientX - d.ox;
      const dy = e.clientY - d.oy;
      if (Math.hypot(dx, dy) > 4) d.moved = true;
      const rect = corkRef.current.getBoundingClientRect();
      const scaleX = W / rect.width;
      const scaleY = H / rect.height;
      let x = d.sx + dx * scaleX;
      let y = d.sy + dy * scaleY;
      x = Math.max(MARGIN - 20, Math.min(W - MARGIN + 20, x));
      y = Math.max(MARGIN - 20, Math.min(H - MARGIN + 20, y));
      setOverrides((prev) => {
        const next = { ...prev, [d.id]: { x, y } };
        return next;
      });
    };
    const onUp = (e: PointerEvent) => {
      const d = dragRef.current;
      if (!d) return;
      dragRef.current = null;
      setOverrides((prev) => {
        savePositions(prev);
        return prev;
      });
      if (!d.moved) {
        const node = byId.get(d.id);
        if (node?.bridge) onSelectBridge(node.bridge);
      }
      void e;
    };
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
  }, [byId, onSelectBridge]);

  const modeLabel = result
    ? `Caso: ${result.target.name}`
    : networkContacts.length
      ? "Rede mapeada"
      : "Quadro vazio — mapeie ou abra a demonstração";

  return (
    <section className="spider-board" aria-label="Quadro Lead Police">
      <header className="board-ribbon">
        <div>
          <p className="board-kicker">Lead Police · quadro de evidências</p>
          <h2 className="board-title">{modeLabel}</h2>
        </div>
        {result && <p className="board-proof">{result.proof_line}</p>}
      </header>

      <div className="board-stage">
        <div
          className="board-cork"
          ref={corkRef}
          style={{ width: W, height: H, minWidth: W, minHeight: H }}
        >
          <svg
            className="yarn-layer"
            viewBox={`0 0 ${W} ${H}`}
            width={W}
            height={H}
            aria-hidden
          >
            <defs>
              <filter id="yarn-shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0.5" dy="1.2" stdDeviation="1.2" floodOpacity="0.35" />
              </filter>
            </defs>
            {base.edges.map((e, i) => {
              const a = byId.get(e.from);
              const b = byId.get(e.to);
              if (!a || !b) return null;
              const wobble = ((i % 5) - 2) * 16 + (e.kind === "path" ? 12 : 6);
              const hot =
                selectedId && (e.from === selectedId || e.to === selectedId);
              return (
                <path
                  key={e.id}
                  d={yarnPath(a.x, a.y, b.x, b.y, wobble)}
                  className={`yarn ${e.kind} ${hot ? "hot" : ""}`}
                  filter="url(#yarn-shadow)"
                  fill="none"
                />
              );
            })}
          </svg>

          {nodes.map((n) => (
            <PersonPin
              key={n.id}
              node={n}
              selected={selectedId === n.id}
              onSelect={n.bridge ? () => onSelectBridge(n.bridge!) : undefined}
              onDragStart={onDragStart}
            />
          ))}
        </div>
      </div>

      <p className="board-legend">
        <span className="leg path" /> caminho ao alvo
        <span className="leg soft" /> ligação
        <span className="leg cluster" /> mesmo empregador
        <span className="hint-drag">Arraste os pins para reorganizar</span>
      </p>
    </section>
  );
}
