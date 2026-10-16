// The chalkboard engine: boards are lists of timed chalk "writes" (text, formulas, strokes).
// One chalk visits every write in order, a camera travels over one long board, and every frame is a pure
// function of the time (AGENTS.md rule 5).
import React from 'react';
import { Easing, interpolate, random } from 'remotion';
import { getStroke } from 'perfect-freehand';
import { RUQAA, measure } from './fonts';
import { Box, typeset } from './math';
import { Poly, Pt, cut, length } from './geom';

export const C = {
  white: '#F3F1E7',
  yellow: '#F6E07A',
  pink: '#F4A9BC',
  blue: '#9AD3F0',
  green: '#A9E6A2',
  orange: '#F7BE84',
  board: '#35564B',
};

export interface BBox { x: number; y: number; w: number; h: number }
export interface Item {
  id: string;
  t0: number;
  t1: number;
  color: string;
  sound: 'chalk' | 'line' | null;
  bbox: BBox;
  draw: (k: number) => React.ReactNode;
  tip: (k: number) => Pt;
}
export interface Cam { t: number; x: number; y: number; z: number; dur: number }
export interface Sfx { t: number; src: string; vol: number; dur: number }
export interface Board {
  id: string;
  chapter: string;
  from: number;
  W: number;
  H: number;
  ox: number;
  oy: number;
  items: Item[];
  cams: Cam[];
  sfx: Sfx[];
}

type Align = 'c' | 'r' | 'l';
interface Place { x: number; y: number; size?: number; color?: string; at: number; align?: Align; weight?: number; dur?: number; maxW?: number }

/** Wrap every Latin/maths run of an Arabic sentence in a left-to-right isolate, so «(x − 2)eˣ» keeps its order. */
export function isolate(s: string) {
  if (!/[\u0600-\u06FF]/.test(s)) return s;
  return s.replace(/[A-Za-z0-9(ℝ∞−+=<>²ˣ⁰⁻ΔIe][A-Za-z0-9()ℝ∞−+=<>²ˣ⁰⁻Δ;,.\s]*[A-Za-z0-9)ℝ∞²ˣ⁰]|[A-Za-z0-9ℝ∞]/g, (m) => '\u202A' + m + '\u202C');
}

const clamp = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v));

function placeBox(w: number, asc: number, desc: number, o: Place): BBox {
  const al = o.align ?? 'c';
  const x = al === 'c' ? o.x - w / 2 : al === 'r' ? o.x - w : o.x;
  return { x, y: o.y - asc, w, h: asc + desc };
}

const strokeCache = new Map<string, string>();

function outline(p: Poly, width: number, seed: number, done: boolean): string {
  if (p.length < 2) return '';
  const pts = p.map(([x, y], i) => [x, y, 0.55 + 0.18 * Math.sin(i * 0.31 + seed) + 0.1 * Math.sin(i * 0.083 + seed * 2)]);
  const o = getStroke(pts, { size: width, thinning: 0.35, smoothing: 0.6, streamline: 0.25, simulatePressure: false, last: done });
  if (!o.length) return '';
  let d = `M${o[0][0].toFixed(1)},${o[0][1].toFixed(1)}`;
  for (let i = 1; i < o.length; i++) d += `L${o[i][0].toFixed(1)},${o[i][1].toFixed(1)}`;
  return d + 'Z';
}

/** Builds one board. Positions are board-local pixels; times are video seconds. */
export class Builder {
  items: Item[] = [];
  cams: Cam[] = [];
  sfx: Sfx[] = [];
  private n = 0;
  constructor(
    public id: string,
    public chapter: string,
    public from: number,
    public P: boolean,
    public W: number,
    public H: number,
  ) {}

  /** A scale for sizes: portrait boards are narrower. */
  get s() {
    return this.P ? 0.78 : 1;
  }

  /** Arabic text written right to left. */
  text(str: string, o: Place): BBox {
    str = isolate(str);
    const weight = o.weight ?? 700;
    let size = o.size ?? 48;
    const mw = o.maxW ?? this.W - 140;
    const w0 = measure(str, `${weight} ${size}px ${RUQAA}`);
    if (w0 > mw) size = (size * mw) / w0;
    const font = `${weight} ${size}px ${RUQAA}`;
    const w = measure(str, font);
    const box = placeBox(w, size * 0.85, size * 0.45, o);
    const color = o.color ?? C.white;
    const id = `${this.id}-${this.n++}`;
    const dur = o.dur ?? clamp(str.length * 0.04 + 0.2, 0.3, 1.8);
    const base = box.y + size * 0.85;
    const content = (
      <text x={box.x + w} y={base} direction="rtl" style={{ font }}>
        {str}
      </text>
    );
    this.items.push({
      id,
      t0: o.at,
      t1: o.at + dur,
      color,
      sound: 'chalk',
      bbox: box,
      draw: (k) => chalkGroup(id, color, size, box, k, 'rtl', content),
      tip: (k) => [box.x + w * (1 - k), base - size * 0.3 + size * 0.18 * Math.sin(k * (w / (size * 0.32)) * Math.PI)],
    });
    return box;
  }

  /** A formula written left to right. */
  math(src: string, o: Place): BBox {
    let size = o.size ?? 56;
    let b: Box = typeset(src, size, o.weight ?? 400);
    const mw = o.maxW ?? this.W - 140;
    if (b.w > mw) {
      size = (size * mw) / b.w;
      b = typeset(src, size, o.weight ?? 400);
    }
    const box = placeBox(b.w, b.asc, b.desc, o);
    const color = o.color ?? C.white;
    const id = `${this.id}-${this.n++}`;
    const dur = o.dur ?? clamp(b.w / (size * 7) + 0.15, 0.25, 1.8);
    const base = box.y + b.asc;
    const content = <>{b.draw.map((d, i) => d(box.x, base, String(i)))}</>;
    this.items.push({
      id,
      t0: o.at,
      t1: o.at + dur,
      color,
      sound: 'chalk',
      bbox: box,
      draw: (k) => chalkGroup(id, color, size, box, k, 'ltr', content),
      tip: (k) => [box.x + b.w * k, base - size * 0.3 + size * 0.2 * Math.sin(k * (b.w / (size * 0.3)) * Math.PI)],
    });
    return box;
  }

  /** Chalk lines: polylines drawn one after the other. */
  stroke(polys: Poly[], o: { at: number; color?: string; width?: number; speed?: number; dur?: number; sound?: boolean }): BBox {
    const color = o.color ?? C.white;
    const width = (o.width ?? 6) * (this.P ? 0.9 : 1);
    const id = `${this.id}-${this.n++}`;
    const lens = polys.map(length);
    const total = lens.reduce((a, b) => a + b, 0) || 1;
    const dur = o.dur ?? clamp(total / (o.speed ?? 950), 0.2, 2.0);
    const xs = polys.flat().map((p) => p[0]);
    const ys = polys.flat().map((p) => p[1]);
    const box = { x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) };
    const seed = random(id) * 10;
    const at = (k: number) => {
      // which polyline and how much of it
      let rem = k * total;
      const parts: { p: Poly; done: boolean }[] = [];
      let tip: Pt = polys[0][0];
      for (let i = 0; i < polys.length; i++) {
        if (rem <= 0) break;
        const f = Math.min(1, rem / (lens[i] || 1));
        const c = cut(polys[i], f);
        parts.push({ p: c.pts, done: f >= 1 });
        tip = c.tip;
        rem -= lens[i];
      }
      return { parts, tip };
    };
    this.items.push({
      id,
      t0: o.at,
      t1: o.at + dur,
      color,
      sound: o.sound === false ? null : 'line',
      bbox: box,
      tip: (k) => at(k).tip,
      draw: (k) => {
        if (k <= 0) return null;
        const { parts } = at(k);
        return (
          <g key={id}>
            {parts.map(({ p, done }, i) => {
              const key = `${id}-${i}`;
              let d = done ? strokeCache.get(key) : undefined;
              let halo = done ? strokeCache.get(key + 'h') : undefined;
              if (!d || !halo) {
                d = outline(p, width, seed + i, done);
                halo = outline(p, width * 2.8, seed + i, done);
                if (done) {
                  strokeCache.set(key, d);
                  strokeCache.set(key + 'h', halo);
                }
              }
              return (
                <g key={i}>
                  <path d={halo} fill={color} opacity={0.12} />
                  <path d={d} fill={color} opacity={0.93} />
                </g>
              );
            })}
          </g>
        );
      },
    });
    return box;
  }

  /** Move the camera to look at (x, y) with zoom z, starting at time t. */
  cam(t: number, x: number, y: number, z = 1, dur = 1.1) {
    this.cams.push({ t, x, y, z, dur });
  }

  /** Back to the default framing (the whole written area, see fit()). */
  home(t: number, dur = 1.1) {
    this.cams.push({ t, x: NaN, y: NaN, z: NaN, dur });
  }

  /** The framing that shows everything written on the board, as large as it fits (zoom 1 to 1.3). */
  fit(): { x: number; y: number; z: number } {
    if (!this.items.length) return { x: this.W / 2, y: this.H / 2, z: 1 };
    const x0 = Math.min(...this.items.map((i) => i.bbox.x));
    const y0 = Math.min(...this.items.map((i) => i.bbox.y));
    const x1 = Math.max(...this.items.map((i) => i.bbox.x + i.bbox.w));
    const y1 = Math.max(...this.items.map((i) => i.bbox.y + i.bbox.h));
    const availW = this.W * 0.9;
    const availH = this.H - (this.P ? 330 : 230); // room for the chapter tag and the nameplate
    const z = clamp(Math.min(availW / (x1 - x0), availH / (y1 - y0)), 1, 1.3);
    const cy = (y1 - y0) * z <= availH ? (y0 + y1) / 2 : y0 + availH / 2 / z;
    // centre a little above the middle so the nameplate never covers the last line
    return { x: (x0 + x1) / 2, y: cy + (this.P ? 20 : 12) / z, z };
  }

  /** Zoom on a box. */
  focus(t: number, b: BBox, pad = 1.6, dur = 1.1) {
    const z = clamp(Math.min(this.W / (b.w * pad), this.H / (b.h * pad * 1.4)), 1, 1.6);
    this.cam(t, b.x + b.w / 2, b.y + b.h / 2, z, dur);
  }

  sound(t: number, src: string, vol = 0.35, dur = 2) {
    this.sfx.push({ t, src, vol, dur });
  }

  /** `limit`: when the camera leaves this board. If the writes would run past it, they get faster. */
  build(ox: number, oy: number, limit = Infinity): Board {
    // one chalk: writes never overlap; a later write waits for the one before it
    const its = [...this.items].sort((a, b) => a.t0 - b.t0);
    const orig = its.map((x) => [x.t0, x.t1 - x.t0]);
    for (let s = 1; ; s *= 0.85) {
      its.forEach((x, i) => {
        x.t0 = orig[i][0];
        x.t1 = x.t0 + Math.max(0.12, orig[i][1] * s);
      });
      for (let i = 1; i < its.length; i++) {
        const prev = its[i - 1];
        const cur = its[i];
        if (cur.t0 < prev.t1 + 0.06) {
          const d = cur.t1 - cur.t0;
          if (prev.t1 - prev.t0 > 0.6 && cur.t0 - 0.06 > prev.t0 + 0.6) prev.t1 = cur.t0 - 0.06;
          else {
            cur.t0 = prev.t1 + 0.06;
            cur.t1 = cur.t0 + d;
          }
        }
      }
      if (!its.length || its[its.length - 1].t1 <= limit || s < 0.3) break;
    }
    const f = this.fit();
    const cams = [{ t: -1, ...f, dur: 0.01 }, ...this.cams.map((c) => (Number.isNaN(c.x) ? { ...c, ...f } : c))].sort((a, b) => a.t - b.t);
    return { id: this.id, chapter: this.chapter, from: this.from, W: this.W, H: this.H, ox, oy, items: its, cams, sfx: this.sfx };
  }
}

function chalkGroup(id: string, color: string, size: number, box: BBox, k: number, dir: 'rtl' | 'ltr', content: React.ReactNode) {
  if (k <= 0) return null;
  const pad = size * 0.6;
  const w = box.w + pad * 2;
  const rw = w * k;
  const rx = dir === 'ltr' ? box.x - pad : box.x - pad + w - rw;
  const clip = k < 1 ? `url(#clip-${id})` : undefined;
  return (
    <g key={id}>
      {k < 1 ? (
        <clipPath id={`clip-${id}`}>
          <rect x={rx} y={box.y - pad} width={rw} height={box.h + pad * 2} />
        </clipPath>
      ) : null}
      <g clipPath={clip}>
        <g fill={color} stroke={color} strokeWidth={size * 0.13} opacity={0.13} strokeLinejoin="round">
          {content}
        </g>
        <g fill={color} opacity={0.95}>
          {content}
        </g>
      </g>
    </g>
  );
}

// ---------------- the timeline over all boards ----------------

export interface Timeline {
  boards: Board[];
  items: (Item & { b: Board })[];
  W: number;
  H: number;
  end: number;
}

export function timeline(boards: Board[], W: number, H: number, end: number): Timeline {
  const items = boards.flatMap((b) => b.items.map((it) => ({ ...it, b })));
  return { boards, items, W, H, end };
}

export const ease = Easing.inOut(Easing.cubic);

export function boardAt(tl: Timeline, t: number): number {
  let i = 0;
  for (let j = 0; j < tl.boards.length; j++) if (tl.boards[j].from - 0.7 <= t) i = j;
  return i;
}

/** The camera in world coordinates at time t. */
export function camera(tl: Timeline, t: number): { x: number; y: number; z: number } {
  const local = (b: Board, t: number) => {
    let cur = { x: b.W / 2, y: b.H / 2, z: 1 };
    for (const c of b.cams) {
      if (t < c.t) break;
      const k = ease(clamp((t - c.t) / c.dur, 0, 1));
      cur = { x: cur.x + (c.x - cur.x) * k, y: cur.y + (c.y - cur.y) * k, z: cur.z + (c.z - cur.z) * k };
    }
    return { x: cur.x + b.ox, y: cur.y + b.oy, z: cur.z };
  };
  const i = boardAt(tl, t);
  const b = tl.boards[i];
  const here = local(b, t);
  if (i === 0) return here;
  const a = b.from - 0.7;
  const e = b.from + 0.5;
  if (t >= e) return here;
  const prev = local(tl.boards[i - 1], a);
  const k = ease(clamp((t - a) / (e - a), 0, 1));
  const dip = 1 - 0.18 * Math.sin(Math.PI * k);
  return { x: prev.x + (here.x - prev.x) * k, y: prev.y + (here.y - prev.y) * k, z: (prev.z + (here.z - prev.z) * k) * dip };
}

export function toScreen(tl: Timeline, cam: { x: number; y: number; z: number }, p: Pt): Pt {
  return [(p[0] - cam.x) * cam.z + tl.W / 2, (p[1] - cam.y) * cam.z + tl.H / 2];
}
export function toWorld(tl: Timeline, cam: { x: number; y: number; z: number }, p: Pt): Pt {
  return [(p[0] - tl.W / 2) / cam.z + cam.x, (p[1] - tl.H / 2) / cam.z + cam.y];
}

export function progress(it: Item, t: number) {
  return interpolate(t, [it.t0, it.t1], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
}

/** Where the chalk is (world), whether it is drawing, how high it is lifted (0..1) and its colour. */
export function chalkState(tl: Timeline, t: number, tray: Pt): { p: Pt; lift: number; color: string; drawing: boolean } {
  const its = tl.items;
  const world = (it: Item & { b: Board }, k: number): Pt => {
    const p = it.tip(k);
    return [p[0] + it.b.ox, p[1] + it.b.oy];
  };
  let prev = -1;
  for (let i = 0; i < its.length; i++) {
    if (its[i].t0 <= t) prev = i;
    else break;
  }
  if (prev >= 0 && t <= its[prev].t1) {
    return { p: world(its[prev], progress(its[prev], t)), lift: 0, color: its[prev].color, drawing: true };
  }
  const next = prev + 1 < its.length ? its[prev + 1] : null;
  const rest = (p: Pt): Pt => [p[0] + 26, p[1] + 34];
  const from: { p: Pt; t: number; color: string } = prev >= 0 ? { p: world(its[prev], 1), t: its[prev].t1, color: its[prev].color } : { p: tray, t: -1, color: C.white };
  if (!next) {
    // back to the tray at the end
    const k = ease(clamp((t - from.t - 1.2) / 1.2, 0, 1));
    const r = rest(from.p);
    const p: Pt = [r[0] + (tray[0] - r[0]) * k, r[1] + (tray[1] - r[1]) * k];
    return { p, lift: clamp(Math.min((t - from.t) / 0.3, 1 - k), 0, 1), color: from.color, drawing: false };
  }
  const to = world(next, 0);
  const dist = Math.hypot(to[0] - from.p[0], to[1] - from.p[1]);
  const travel = clamp(dist / 1600, 0.3, 0.85);
  const ts = Math.max(from.t + 0.05, next.t0 - travel);
  const lift = clamp(Math.min((t - from.t) / 0.25, (next.t0 - t) / 0.15), 0, 1);
  if (t < ts) {
    const k = ease(clamp((t - from.t) / 0.3, 0, 1));
    const r = rest(from.p);
    return { p: [from.p[0] + (r[0] - from.p[0]) * k, from.p[1] + (r[1] - from.p[1]) * k], lift, color: from.color, drawing: false };
  }
  const k = ease(clamp((t - ts) / (next.t0 - ts), 0, 1));
  const r = from.t < 0 ? from.p : rest(from.p);
  const p: Pt = [r[0] + (to[0] - r[0]) * k, r[1] + (to[1] - r[1]) * k - Math.sin(Math.PI * k) * Math.min(80, dist * 0.15)];
  return { p, lift, color: k < 0.5 ? from.color : next.color, drawing: false };
}
