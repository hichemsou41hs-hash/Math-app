// A tiny chalkboard typesetter: a LaTeX-like string -> SVG elements laid out with measured glyphs.
// Supported: ^{} _{} \frac{}{} \lim_{} \left( \right) \text{arabic} and the symbols in SYMBOLS.
import React from 'react';
import { HAND, NASKH, SYM, measure } from './fonts';

type El = (x: number, y: number, key: string) => React.ReactNode;
export interface Box { w: number; asc: number; desc: number; draw: El[] }

const SYMBOLS: Record<string, string> = {
  infty: '∞', to: '→', R: 'ℝ', times: '×', cdot: '·', le: '≤', ge: '≥', iff: '⟺', approx: '≈', ne: '≠',
  Delta: 'Δ', in: '∈', forall: '∀', mapsto: '↦', implies: '⟹', quad: ' ', pm: '±', lt: '<', gt: '>',
};
const REL = new Set(['=', '<', '>', '≤', '≥', '⟺', '≈', '≠', '→', '∈', '↦', '⟹', '+', '−', '×', '·', '±']);
const SYMFONT = new Set(['Δ', '∞', 'ℝ', '⟺', '≤', '≥', '≈', '≠', '∈', '∀', '↦', '⟹', '→', '−', '×', '·', '±']);

function glyph(s: string, size: number, font: string, weight = 400): Box {
  const css = `${weight} ${size}px ${font}`;
  const w = measure(s, css);
  const arabic = /[؀-ۿ]/.test(s);
  return {
    w,
    asc: size * 0.78,
    desc: size * (arabic ? 0.35 : 0.22),
    draw: [
      (x, y, key) => (
        <text key={key} x={arabic ? x + w : x} y={y} style={{ font: css }} direction={arabic ? 'rtl' : 'ltr'} textAnchor="start">
          {s}
        </text>
      ),
    ],
  };
}

function shift(b: Box, dx: number, dy: number): El[] {
  return b.draw.map((d) => (x: number, y: number, key: string) => d(x + dx, y + dy, key));
}

function row(items: Box[]): Box {
  let x = 0;
  let asc = 0;
  let desc = 0;
  const draw: El[] = [];
  for (const b of items) {
    draw.push(...shift(b, x, 0));
    x += b.w;
    asc = Math.max(asc, b.asc);
    desc = Math.max(desc, b.desc);
  }
  return { w: x, asc, desc, draw };
}

const space = (w: number): Box => ({ w, asc: 0, desc: 0, draw: [] });

type Tok = { k: 'cmd' | 'ch' | 'open' | 'close' | 'sup' | 'sub'; v: string };
function tokenize(src: string): Tok[] {
  const out: Tok[] = [];
  for (let i = 0; i < src.length; i++) {
    const c = src[i];
    if (c === '\\') {
      let j = i + 1;
      while (j < src.length && /[a-zA-Z]/.test(src[j])) j++;
      if (j === i + 1) j++;
      out.push({ k: 'cmd', v: src.slice(i + 1, j) });
      i = j - 1;
    } else if (c === '{') out.push({ k: 'open', v: c });
    else if (c === '}') out.push({ k: 'close', v: c });
    else if (c === '^') out.push({ k: 'sup', v: c });
    else if (c === '_') out.push({ k: 'sub', v: c });
    else out.push({ k: 'ch', v: c });
  }
  return out;
}

export function typeset(src: string, size: number, weight = 400): Box {
  const toks = tokenize(src);
  let p = 0;

  const atomText = (s: string, sz: number): Box => {
    if (s === ' ') return space(sz * 0.25);
    if (s === '-') s = '−';
    const font = SYMFONT.has(s) ? SYM : HAND;
    const g = glyph(s, sz, font, SYMFONT.has(s) ? 400 : weight);
    if (REL.has(s)) return row([space(sz * 0.18), g, space(sz * 0.18)]);
    if (s === ',' || s === ';') return row([g, space(sz * 0.15)]);
    if (s === "'") return row([space(sz * 0.1), g, space(sz * 0.04)]);
    return g;
  };

  const group = (sz: number): Box => {
    if (toks[p]?.k === 'open') {
      p++;
      const b = seq(sz, true);
      p++; // close
      return b;
    }
    return one(sz);
  };

  const scripts = (base: Box, sz: number): Box => {
    let b = base;
    while (toks[p] && (toks[p].k === 'sup' || toks[p].k === 'sub')) {
      const up = toks[p].k === 'sup';
      p++;
      const s = group(sz * 0.62);
      const dy = up ? -Math.max(sz * 0.42, b.asc - s.asc * 0.55) : sz * 0.22;
      b = {
        w: b.w + s.w + sz * 0.04,
        asc: Math.max(b.asc, s.asc - dy),
        desc: Math.max(b.desc, s.desc + dy),
        draw: [...b.draw, ...shift(s, b.w + sz * 0.04, dy)],
      };
    }
    return b;
  };

  const one = (sz: number): Box => {
    const t = toks[p++];
    if (!t) return space(0);
    if (t.k === 'ch' && t.v === ',' && toks[p]?.k === 'ch' && /\d/.test(toks[p].v)) return glyph(',', sz, HAND, weight);
    if (t.k === 'ch') return scripts(atomText(t.v, sz), sz);
    if (t.k === 'open') {
      p--;
      return scripts(group(sz), sz);
    }
    if (t.k !== 'cmd') return space(0);
    const c = t.v;
    if (c === 'frac') {
      const n = group(sz * 0.9);
      const d = group(sz * 0.9);
      const w = Math.max(n.w, d.w) + sz * 0.3;
      const axis = -sz * 0.3;
      const th = Math.max(2, sz * 0.055);
      const nb = axis - th - sz * 0.12 - n.desc;
      const db = axis + th + sz * 0.12 + d.asc;
      return scripts(
        {
          w: w + sz * 0.1,
          asc: -nb + n.asc,
          desc: db + d.desc,
          draw: [
            ...shift(n, (w - n.w) / 2 + sz * 0.05, nb),
            ...shift(d, (w - d.w) / 2 + sz * 0.05, db),
            (x, y, key) => <rect key={key} x={x + sz * 0.05} y={y + axis - th / 2} width={w} height={th} rx={th / 2} />,
          ],
        },
        sz,
      );
    }
    if (c === 'lim') {
      const l = glyph('lim', sz, HAND, weight);
      let under: Box = space(0);
      if (toks[p]?.k === 'sub') {
        p++;
        under = group(sz * 0.55);
      }
      const w = Math.max(l.w, under.w);
      const ub = l.desc + sz * 0.1 + under.asc;
      return {
        w: w + sz * 0.2,
        asc: l.asc,
        desc: ub + under.desc,
        draw: [...shift(l, (w - l.w) / 2, 0), ...shift(under, (w - under.w) / 2, ub)],
      };
    }
    if (c === 'text') {
      p++; // open
      let s = '';
      while (toks[p] && toks[p].k !== 'close') s += toks[p++].v;
      p++;
      return glyph(s, sz * 0.95, NASKH, 700);
    }
    if (c === 'left' || c === 'right') return space(0); // handled in seq
    if (c === ',') return space(sz * 0.2);
    if (c === ';') return space(sz * 0.35);
    if (SYMBOLS[c]) return scripts(atomText(SYMBOLS[c], sz), sz);
    return atomText(c, sz);
  };

  const seq = (sz: number, inGroup = false): Box => {
    const items: Box[] = [];
    while (p < toks.length) {
      const t = toks[p];
      if (inGroup && t.k === 'close') break;
      if (t.k === 'cmd' && t.v === 'right') break;
      if (t.k === 'cmd' && t.v === 'left') {
        p++;
        const open = toks[p++].v;
        const inner = seq(sz);
        p++; // \right
        const close = toks[p++].v;
        items.push(scripts(fence(open, close, inner, sz), sz));
        continue;
      }
      items.push(one(sz));
    }
    return row(items);
  };

  return seq(size);
}

/** Brackets stretched to the height of their content. */
function fence(open: string, close: string, inner: Box, sz: number): Box {
  const h = inner.asc + inner.desc;
  const k = Math.max(1, h / (sz * 1.05));
  const mk = (ch: string): Box => {
    const g = glyph(ch, sz, HAND);
    const mid = (inner.desc - inner.asc) / 2; // centre of content relative to baseline
    const gmid = (g.desc - g.asc) / 2;
    return {
      w: g.w * (k > 1.3 ? 1.15 : 1),
      asc: inner.asc + sz * 0.05,
      desc: inner.desc + sz * 0.05,
      draw: g.draw.map((d) => (x: number, y: number, key: string) => (
        <g key={key} transform={`translate(${x} ${y + mid}) scale(1 ${k}) translate(${-x} ${-(y + gmid)})`}>{d(x, y, 'g')}</g>
      )),
    };
  };
  return row([mk(open), space(sz * 0.04), inner, space(sz * 0.04), mk(close)]);
}
