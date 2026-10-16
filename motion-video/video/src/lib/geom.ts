// Point lists for chalk strokes. Every shape is a list of polylines drawn one after the other.
import { random } from 'remotion';

export type Pt = [number, number];
export type Poly = Pt[];

export function seg(a: Pt, b: Pt, step = 6): Poly {
  const n = Math.max(2, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / step));
  return Array.from({ length: n + 1 }, (_, i) => [a[0] + ((b[0] - a[0]) * i) / n, a[1] + ((b[1] - a[1]) * i) / n] as Pt);
}

export function path(pts: Pt[], step = 6): Poly {
  const out: Poly = [];
  for (let i = 0; i < pts.length - 1; i++) out.push(...seg(pts[i], pts[i + 1], step).slice(i ? 1 : 0));
  return out;
}

export function rect(x: number, y: number, w: number, h: number): Poly {
  return path([[x + w, y], [x, y], [x, y + h], [x + w, y + h], [x + w, y - 2]]);
}

export function circle(c: Pt, r: number, from = -Math.PI / 2, sweep = Math.PI * 2.05): Poly {
  const n = Math.max(12, Math.ceil((r * sweep) / 5));
  return Array.from({ length: n + 1 }, (_, i) => {
    const a = from - (sweep * i) / n;
    return [c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)] as Pt;
  });
}

/** Sample y = f(x) between x0 and x1 and map it to the board with `map`. */
export function fn(f: (x: number) => number, x0: number, x1: number, map: (x: number, y: number) => Pt, n = 160): Poly {
  return Array.from({ length: n + 1 }, (_, i) => {
    const x = x0 + ((x1 - x0) * i) / n;
    return map(x, f(x));
  });
}

export function arrowHead(tip: Pt, from: Pt, size = 18): Poly[] {
  const a = Math.atan2(tip[1] - from[1], tip[0] - from[0]);
  const l: Pt = [tip[0] - size * Math.cos(a - 0.45), tip[1] - size * Math.sin(a - 0.45)];
  const r: Pt = [tip[0] - size * Math.cos(a + 0.45), tip[1] - size * Math.sin(a + 0.45)];
  return [seg(l, tip, 4), seg(tip, r, 4)];
}

export function arrow(a: Pt, b: Pt, head = 18): Poly[] {
  return [seg(a, b), ...arrowHead(b, a, head)];
}

export function dashed(a: Pt, b: Pt, dash = 14, gap = 10): Poly[] {
  const L = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const out: Poly[] = [];
  for (let s = 0; s < L; s += dash + gap) {
    const e = Math.min(L, s + dash);
    out.push(seg([a[0] + ((b[0] - a[0]) * s) / L, a[1] + ((b[1] - a[1]) * s) / L], [a[0] + ((b[0] - a[0]) * e) / L, a[1] + ((b[1] - a[1]) * e) / L], 4));
  }
  return out;
}

export function check(c: Pt, s = 40): Poly[] {
  return [path([[c[0] - s * 0.5, c[1]], [c[0] - s * 0.15, c[1] + s * 0.35], [c[0] + s * 0.55, c[1] - s * 0.45]], 4)];
}

/** Hand wobble: a smooth deterministic offset so ruler-straight lines look drawn. */
export function wobble(p: Poly, seed: string, amp = 1.4): Poly {
  const a = random(seed + 'a') * 6.28;
  const b = random(seed + 'b') * 6.28;
  return p.map(([x, y], i) => [x + amp * Math.sin(i * 0.21 + a), y + amp * Math.sin(i * 0.17 + b)] as Pt);
}

export function length(p: Poly) {
  let L = 0;
  for (let i = 1; i < p.length; i++) L += Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]);
  return L;
}

/** The first `k` (0..1) of a polyline by length, and the point where it ends. */
export function cut(p: Poly, k: number): { pts: Poly; tip: Pt } {
  if (k >= 1) return { pts: p, tip: p[p.length - 1] };
  const target = length(p) * Math.max(0, k);
  let L = 0;
  for (let i = 1; i < p.length; i++) {
    const d = Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]);
    if (L + d >= target) {
      const u = d ? (target - L) / d : 0;
      const tip: Pt = [p[i - 1][0] + (p[i][0] - p[i - 1][0]) * u, p[i - 1][1] + (p[i][1] - p[i - 1][1]) * u];
      return { pts: [...p.slice(0, i), tip], tip };
    }
    L += d;
  }
  return { pts: p, tip: p[p.length - 1] };
}
