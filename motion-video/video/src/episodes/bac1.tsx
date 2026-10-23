// Bac exercise series «حلول تمارين البكالوريا: الدالة الأسية», episode 1: Bac 2026, subject 2, experimental
// sciences, exercise 1 (documents/exponentielle/bac_exp_3as.tex). One board per question part: the statement
// in a box, a «try it yourself» pause, then the solution. Colours: questions blue, working white, key facts
// blue/pink, results yellow (framed), asymptotes pink, the curve blue, monotonicity green.
import { Board, BBox, Builder, C, isolate } from '../lib/engine';
import { Pt, arrow, check, circle, dashed, path, rect, seg, wobble } from '../lib/geom';
import { RUQAA, measure } from '../lib/fonts';
import { typeset } from '../lib/math';
import { at, heading } from '../boards/util';
import { board as exBoard, frame } from './ex1';

const LIM = (to: string) => `\\lim_{x \\to ${to}}`;
const F_DEF = 'f(x) = 1 + \\frac{5 - 4e^{x}}{e^{2x} - 1}';
const F_PRIME = "f'(x) = \\frac{2e^{x}\\left(e^{x} - 2\\right)\\left(2e^{x} - 1\\right)}{\\left(e^{2x} - 1\\right)^{2}}";
const F_OTHER = 'f(x) = -4 + \\frac{1}{2}\\left(\\frac{9e^{x}}{1 + e^{x}} - \\frac{e^{x}}{1 - e^{x}}\\right)';

/** Unary signs (−∞, −3, +∞, e^{−x}) without the spacing of a binary minus. */
const fix = (s: string) =>
  s
    .replace(/(^|[([{;\]]\s*|[=<>]\s*|\\(?:to|implies|iff|approx|quad)\s*)-/g, '$1\\umin{}')
    .replace(/(^|[([{;\]]\s*|[=<>]\s*|\\(?:to|quad)\s*)\+/g, '$1\\uplus{}');

function board(id: string, chapter: string, first: string, P: boolean, W: number, H: number) {
  const b = exBoard(id, chapter, first, P, W, H);
  b.minZoom = 0.76;
  const math = b.math.bind(b);
  b.math = (src, o) => math(fix(src), o);
  return b;
}

type Part = { k: 't' | 'm'; s: string; at: number; color?: string; size?: number };
const T = (s: string, t: number, color?: string, size?: number): Part => ({ k: 't', s, at: t, color, size });
const M = (s: string, t: number, color?: string, size?: number): Part => ({ k: 'm', s: fix(s), at: t, color, size });

/** Rows written one under the other. A row may mix Arabic sentences and formulas: in an Arabic row ('rtl')
 *  the first part sits on the right; formulas stay left to right. */
function column(b: Builder, y: number, gap = b.P ? 58 : 44) {
  let cur = y;
  const dt = b.P ? 42 : 40;
  const dm = b.P ? 52 : 50;
  const row = (parts: Part[], o: { dir?: 'rtl' | 'ltr'; space?: number; x?: number } = {}): BBox => {
    const dir = o.dir ?? 'rtl';
    const maxW = b.W - (b.P ? 110 : 150);
    let k = 1;
    const dims = () =>
      parts.map((p) => {
        const size = (p.size ?? (p.k === 't' ? dt : dm)) * k;
        if (p.k === 't') return { size, w: measure(isolate(p.s), `700 ${size}px ${RUQAA}`), asc: size * 0.85 };
        const bx = typeset(p.s, size);
        return { size, w: bx.w, asc: bx.asc };
      });
    let d = dims();
    const sp = (o.space ?? 22) * (b.P ? 0.8 : 1);
    const total = () => d.reduce((a, x) => a + x.w, 0) + sp * (parts.length - 1);
    if (total() > maxW) {
      k = maxW / total();
      d = dims();
    }
    const asc = Math.max(...d.map((x) => x.asc));
    const base = cur + asc;
    const cx = o.x ?? b.W / 2;
    let x = dir === 'rtl' ? cx + total() / 2 : cx - total() / 2;
    const boxes = parts.map((p, i) => {
      const w = d[i].w;
      const left = dir === 'rtl' ? x - w : x;
      x = dir === 'rtl' ? x - w - sp : x + w + sp;
      const place = { x: left, y: base, size: d[i].size, color: p.color ?? C.white, at: p.at, align: 'l' as const, maxW: 1e5 };
      return p.k === 't' ? b.text(p.s, place) : b.math(p.s, place);
    });
    const x0 = Math.min(...boxes.map((q) => q.x));
    const y0 = Math.min(...boxes.map((q) => q.y));
    const x1 = Math.max(...boxes.map((q) => q.x + q.w));
    const y1 = Math.max(...boxes.map((q) => q.y + q.h));
    cur = y1 + gap;
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  };
  return {
    get y() {
      return cur;
    },
    skip(dy: number) {
      cur += dy;
    },
    row,
    math: (s: string, t: number, color?: string, size?: number) => row([M(s, t, color, size)]),
    text: (s: string, t: number, color?: string, size?: number) => row([T(s, t, color, size)]),
  };
}

/** A framed result with a shimmer. */
function result(b: Builder, boxes: BBox[], t: number, pad = 18) {
  frame(b, boxes, t, C.yellow, pad);
  b.sound(t + 0.3, 'shimmer', 0.3);
}

// ---------------- a table of signs / variations (as on a bac paper) ----------------

interface TabSpec {
  xs: string[];
  labels: string[]; // sign rows then the variations row
  signs: string[][]; // per sign row, 2n-1 cells: even = at a point ('', '0'), odd = on an interval ('+', '-')
  dbl: number[]; // points with a double bar (the function is not defined there)
  vals: { p: number; side?: -1 | 1; lvl: 't' | 'b'; s: string; at: number }[];
  arrows: [number, number, number][]; // value index -> value index, at
  t: { lines: number; x: number; rows: number[] };
  tw?: number;
  lw?: number;
}

function table(b: Builder, y: number, s: TabSpec) {
  const P = b.P;
  const n = s.xs.length;
  const tw = s.tw ?? (P ? 1000 : 1400);
  const tx = (b.W - tw) / 2;
  const lw = s.lw ?? (P ? 190 : 230);
  const S = P ? 38 : 40;
  const rh = [...s.signs.map(() => (P ? 72 : 68)), P ? 190 : 180];
  rh.unshift(P ? 72 : 68);
  const yR = rh.reduce((a, h) => [...a, a[a.length - 1] + h], [y]);
  const bottom = yR[yR.length - 1];
  const lines = [rect(tx, y, tw, bottom - y), seg([tx + lw, y], [tx + lw, bottom]), ...yR.slice(1, -1).map((yy) => seg([tx, yy], [tx + tw, yy]))];
  b.stroke(lines.map((p, i) => wobble(p, b.id + 'tab' + i, 1)), { at: s.t.lines, color: C.white, width: 4, dur: 1.0 });
  const pad = P ? 60 : 80;
  const px = (i: number) => tx + lw + pad + (i * (tw - lw - 2 * pad)) / (n - 1);
  const ix = (i: number) => (px(i) + px(i + 1)) / 2;
  const mid = (r: number) => (yR[r] + yR[r + 1]) / 2 + S * 0.32;
  ['x', ...s.labels].forEach((l, r) => b.math(l, { x: tx + lw / 2, y: mid(r), size: r === 0 ? S : S * 0.9, at: s.t.lines + 0.5 + r * 0.1, dur: 0.2 }));
  s.xs.forEach((v, i) => b.math(v, { x: px(i), y: mid(0), size: S, color: C.blue, at: s.t.x + i * 0.25, dur: 0.25 }));
  s.dbl.forEach((p, k) =>
    b.stroke(
      [-6, 6].map((d) => seg([px(p) + d, yR[1]], [px(p) + d, bottom])),
      { at: s.t.x + 0.1 + k * 0.1, color: C.white, width: 3, dur: 0.3 },
    ),
  );
  s.signs.forEach((cells, r) =>
    cells.forEach((c, j) => {
      if (!c) return;
      const x = j % 2 ? ix((j - 1) / 2) : px(j / 2);
      const color = c === '+' ? C.green : c === '-' ? C.pink : C.white;
      b.math(c, { x, y: mid(r + 1), size: c === '0' ? S : S * 1.15, color, at: s.t.rows[r] + j * 0.12, dur: 0.15 });
    }),
  );
  const vr = s.signs.length + 1;
  const top = yR[vr] + S * 1.05;
  const bot = yR[vr + 1] - S * 0.4;
  const off = P ? 40 : 46;
  const pos = s.vals.map((v) => {
    const w = typeset(fix(v.s), S).w;
    const x = px(v.p) + (v.side ?? 0) * (off + w / 2 - 6);
    const yy = v.lvl === 't' ? top : bot;
    b.math(v.s, { x, y: yy, size: S, color: C.yellow, at: v.at, dur: 0.3 });
    return { x, w, lvl: v.lvl };
  });
  s.arrows.forEach(([a, z, t]) => {
    const A = pos[a];
    const Z = pos[z];
    const ya = A.lvl === 't' ? top - S * 0.25 : bot - S * 0.55;
    const yz = Z.lvl === 't' ? top - S * 0.25 : bot - S * 0.55;
    b.stroke(arrow([A.x + A.w / 2 + 14, ya], [Z.x - Z.w / 2 - 14, yz], 16), { at: t, color: C.yellow, width: 4 });
  });
  return { y, h: bottom - y };
}

// ---------------- the boards ----------------

function intro(P: boolean, W: number, H: number) {
  const b = board('intro', 'مقدمة', 'السلام عليكم', P, W, H);
  const cx = W / 2;
  b.text('الأستاذ سوايسية هشام', { x: cx, y: P ? 300 : 150, size: 54, color: C.white, at: at('السلام عليكم', 'معكم') });
  const q = 'هذه هي الحلقة الأولى';
  const t = b.text('حلول تمارين البكالوريا', { x: cx, y: P ? 480 : 300, size: P ? 88 : 100, color: C.yellow, at: at(q, 'حلول') });
  b.stroke([seg([t.x + t.w + 30, t.y + t.h + 6], [t.x - 30, t.y + t.h + 14])], { at: at(q, 'البكالوريا'), color: C.yellow, width: 6 });
  b.text('الدالة الأسية: الحلقة 1', { x: cx, y: P ? 650 : 445, size: P ? 62 : 58, color: C.pink, at: at(q, 'الدالة') });
  const q2 = 'تمرين اليوم';
  b.text('بكالوريا 2026، الموضوع الثاني', { x: cx, y: P ? 810 : 575, size: P ? 54 : 52, color: C.blue, at: at(q2, 'بكالوريا') });
  b.text('شعبة العلوم التجريبية، التمرين الأول', { x: cx, y: P ? 920 : 670, size: P ? 46 : 46, color: C.blue, at: at(q2, 'شعبة') });
  b.text('أوقف الفيديو وحاول قبل رؤية الحل', { x: cx, y: P ? 1070 : 810, size: 40, color: C.white, at: at('في كل سؤال', 'أوقف') });
  return b;
}

function statement(P: boolean, W: number, H: number) {
  const q = 'نص التمرين';
  const b = board('statement', 'نص التمرين', q, P, W, H);
  const c = column(b, heading(b, 'نص التمرين', at(q)) + (P ? 10 : 20), P ? 70 : 56);
  const s1 = c.row([T('f دالة معرفة على', at(q, 'دالة'), C.blue), M('\\R^{*}', at(q, 'عدا'), C.blue), T('بـ :', at(q, 'بـ'), C.blue)]);
  const s2 = c.math(F_DEF, at(q, 'يساوي'), C.white, P ? 66 : 72);
  const l2 = 'والمنحنى سي إيف';
  const s3 = c.row([M('(C_{f})', at(l2, 'سي'), C.blue), T('تمثيلها البياني في معلم متعامد ومتجانس', at(l2, 'تمثيلها'), C.blue)]);
  frame(b, [s1, s2, s3], at(l2, 'ومتجانس') + 0.5, C.white, 34);
  return b;
}

function q1(P: boolean, W: number, H: number) {
  const q = 'السؤال الأول';
  const b = board('q1', 'السؤال 1: النهايات', q, P, W, H);
  const c = column(b, heading(b, 'السؤال 1 : النهايات', at(q)) - 20);
  const s1 = c.text('احسب النهايات التالية، ثم فسّر النتائج هندسيا :', at(q, 'احسب'), C.blue);
  const s2 = c.row(
    [M(`${LIM('-\\infty')} f(x)`, at(q, 'ناقص')), M(`${LIM('0^{+}')} f(x)`, at(q, 'اليمين')), M(`${LIM('0^{-}')} f(x)`, at(q, 'اليسار')), M(`${LIM('+\\infty')} f(x)`, at(q, 'زائد'))],
    { dir: 'ltr', space: 70 },
  );
  frame(b, [s1, s2], at(q, 'هندسيا') + 0.3);
  c.skip(24);
  const l = 'عند ناقص ما لا نهاية: e';
  c.math(`${LIM('-\\infty')} e^{x} = 0 \\quad ; \\quad ${LIM('-\\infty')} e^{2x} = 0`, at(l, 'يؤولان'), C.blue);
  c.math(`${LIM('-\\infty')} \\frac{5 - 4e^{x}}{e^{2x} - 1} = \\frac{5}{-1} = -5`, at(l, 'فالكسر'));
  const l2 = 'إذن نهاية f عند ناقص';
  const r = c.math(`${LIM('-\\infty')} f(x) = 1 - 5 = -4`, at(l2, 'تساوي'), C.yellow, P ? 56 : 54);
  result(b, [r], at(l2, 'أربعة') + 0.3);
  return b;
}

function q1b(P: boolean, W: number, H: number) {
  const q = 'عند الصفر: البسط';
  const b = board('q1b', 'السؤال 1: النهايات', q, P, W, H);
  const c = column(b, heading(b, 'النهايات عند الصفر وعند اللانهاية', at(q)) - 20);
  c.math(`${LIM('0')} \\left(5 - 4e^{x}\\right) = 1 \\quad ; \\quad ${LIM('0')} \\left(e^{2x} - 1\\right) = 0`, at(q, 'البسط'), C.blue);
  const l = 'إذا كان x موجبا';
  const r1 = c.row([M('x > 0 \\implies e^{2x} - 1 > 0 \\implies', at(l, 'فالمقام')), M(`${LIM('0^{+}')} f(x) = +\\infty`, at(l, 'والنهاية'), C.yellow)], { dir: 'ltr' });
  const r2 = c.row([M('x < 0 \\implies e^{2x} - 1 < 0 \\implies', at(l, 'فالمقام', 1)), M(`${LIM('0^{-}')} f(x) = -\\infty`, at(l, 'والنهاية', 1), C.yellow)], { dir: 'ltr' });
  b.sound(at(l, 'والنهاية', 1) + 1.0, 'shimmer', 0.3);
  void r1;
  void r2;
  c.skip(10);
  const l3 = 'عند زائد ما لا نهاية: نقسم';
  c.row([T('نقسم البسط والمقام على', at(l3, 'نقسم'), C.pink), M('e^{2x}', at(l3, 'اثنين'), C.pink)]);
  c.math(`\\frac{5 - 4e^{x}}{e^{2x} - 1} = \\frac{5e^{-2x} - 4e^{-x}}{1 - e^{-2x}} \\to \\frac{0}{1} = 0`, at('نجد خمسة e', 'خمسة'));
  const l4 = 'إذن نهاية f عند زائد';
  const r3 = c.math(`${LIM('+\\infty')} f(x) = 1`, at(l4, 'تساوي'), C.yellow, P ? 56 : 54);
  result(b, [r3], at(l4, 'واحدا') + 0.3);
  return b;
}

function q1c(P: boolean, W: number, H: number) {
  const q = 'التفسير الهندسي';
  const b = board('q1c', 'السؤال 1: التفسير الهندسي', q, P, W, H);
  const c = column(b, heading(b, 'التفسير الهندسي', at(q)) + 10, P ? 70 : 60);
  const a1 = c.row([M('y = -4', at(q, 'المستقيم'), C.pink, P ? 54 : 56), T('مستقيم مقارب أفقي بجوار', at(q, 'مقارب')), M('-\\infty', at(q, 'بجوار'))]);
  const l2 = 'والمستقيم x يساوي صفرا';
  const a2 = c.row([M('x = 0', at(l2, 'المستقيم'), C.pink, P ? 54 : 56), T('(محور التراتيب) مستقيم مقارب عمودي', at(l2, 'محور'))]);
  const l3 = 'والمستقيم y يساوي واحدا';
  const a3 = c.row([M('y = 1', at(l3, 'المستقيم'), C.pink, P ? 54 : 56), T('مستقيم مقارب أفقي بجوار', at(l3, 'مقارب')), M('+\\infty', at(l3, 'بجوار'))]);
  frame(b, [a1, a2, a3], at(l3, 'نهاية') + 0.4, C.pink, 30);
  return b;
}

function q2a(P: boolean, W: number, H: number) {
  const q = 'السؤال الثاني';
  const b = board('q2a', 'السؤال 2 أ: المشتقة', q, P, W, H);
  const c = column(b, heading(b, 'السؤال 2 أ : المشتقة', at(q)) - 20);
  const s1 = c.row([T('بيّن أنه من أجل كل x من', at(q, 'بين'), C.blue), M(': \\R^{*}', at(q, 'بين') + 0.4, C.blue)]);
  const s2 = c.math(F_PRIME, at(q, 'يساوي'), C.white, P ? 52 : 54);
  frame(b, [s1, s2], at(q, 'مربع') + 0.3);
  c.skip(24);
  const l = 'نستعمل مشتقة حاصل';
  c.math("\\left(5 - 4e^{x}\\right)' = -4e^{x} \\quad ; \\quad \\left(e^{2x} - 1\\right)' = 2e^{2x}", at(l, 'البسط'), C.blue);
  c.math("f'(x) = \\frac{-4e^{x}\\left(e^{2x} - 1\\right) - \\left(5 - 4e^{x}\\right) \\times 2e^{2x}}{\\left(e^{2x} - 1\\right)^{2}}", at('فالبسط: ناقص', 'ناقص'));
  c.math("f'(x) = \\frac{4e^{3x} - 10e^{2x} + 4e^{x}}{\\left(e^{2x} - 1\\right)^{2}}", at('بالنشر والتبسيط', 'أربعة'));
  return b;
}

function q2a2(P: boolean, W: number, H: number) {
  const q = 'نخرج اثنين';
  const b = board('q2a2', 'السؤال 2 أ: المشتقة', q, P, W, H);
  const c = column(b, heading(b, 'التحليل', at(q)) - 10, P ? 70 : 56);
  c.math("f'(x) = \\frac{2e^{x}\\left(2e^{2x} - 5e^{x} + 2\\right)}{\\left(e^{2x} - 1\\right)^{2}}", at(q, 'يبقى'));
  const l = 'ونتحقق بالنشر';
  c.math('\\left(e^{x} - 2\\right)\\left(2e^{x} - 1\\right) = 2e^{2x} - e^{x} - 4e^{x} + 2 = 2e^{2x} - 5e^{x} + 2', at(l, 'ناقص'), C.blue);
  c.skip(16);
  const l2 = 'إذن عبارة f بريم';
  const r = c.math(F_PRIME, at(l2, 'عبارة'), C.yellow, P ? 56 : 58);
  result(b, [r], at(l2, 'صحيحة'), 24);
  b.stroke(check([r.x + r.w + 60, r.y + r.h / 2], 44), { at: at(l2, 'صحيحة') + 0.5, color: C.green, width: 6 });
  return b;
}

function q2b(P: boolean, W: number, H: number) {
  const q = 'ثم: استنتج';
  const b = board('q2b', 'السؤال 2 ب: إشارة المشتقة', q, P, W, H);
  const c = column(b, heading(b, 'السؤال 2 ب : الإشارة', at(q)) - 20);
  const s = c.text('استنتج اتجاه تغيّر الدالة f ثم شكّل جدول تغيّراتها', at(q, 'استنتج'), C.blue);
  frame(b, [s], at(q, 'تغيراتها') + 0.2);
  c.skip(24);
  const l = 'بما أن اثنين e';
  c.row([M('2e^{x} > 0', at(l, 'موجب')), T('و', at(l, 'والمقام')), M('\\left(e^{2x} - 1\\right)^{2} > 0', at(l, 'مربع'))]);
  c.row([T('إشارة', at(l, 'فإشارة'), C.pink), M("f'(x)", at(l, 'بريم'), C.pink), T('هي إشارة', at(l, 'هي'), C.pink), M('\\left(e^{x} - 2\\right)\\left(2e^{x} - 1\\right)', at(l, 'الجداء'), C.pink)]);
  c.math('e^{x} - 2 > 0 \\iff e^{x} > 2 \\iff x > \\ln 2', at('أس x ناقص اثنين موجب', 'يعني'), C.blue);
  c.math('2e^{x} - 1 > 0 \\iff e^{x} > \\frac{1}{2} \\iff x > -\\ln 2', at('واثنان e أس x ناقص واحد موجب', 'يعني'), C.blue);
  c.skip(10);
  const l2 = 'القيم الحدية';
  const r1 = c.row([M('f(\\ln 2) = 0', at(l2, 'يساوي'), C.yellow), M('f(-\\ln 2) = -3', at(l2, 'يساوي', 1), C.yellow)], { dir: 'ltr', space: 90 });
  result(b, [r1], at(l2, 'ثلاثة') + 0.3);
  return b;
}

function q2b2(P: boolean, W: number, H: number) {
  const q = 'جدول الإشارة';
  const b = board('q2b2', 'السؤال 2 ب: جدول التغيرات', q, P, W, H);
  const c = column(b, heading(b, 'جدول التغيرات', at(q)) - 10, P ? 60 : 46);
  const l = 'وتتغير f';
  const tb = table(b, c.y, {
    xs: ['-\\infty', '-\\ln 2', '0', '\\ln 2', '+\\infty'],
    labels: ['e^{x} - 2', '2e^{x} - 1', "f'(x)", 'f(x)'],
    signs: [
      ['', '-', '', '-', '', '-', '0', '+', ''],
      ['', '-', '0', '+', '', '+', '', '+', ''],
      ['', '+', '0', '-', '', '-', '0', '+', ''],
    ],
    dbl: [2],
    vals: [
      { p: 0, lvl: 'b', s: '-4', at: at(l, 'أربعة') },
      { p: 1, lvl: 't', s: '-3', at: at(l, 'ثلاثة') },
      { p: 2, side: -1, lvl: 'b', s: '-\\infty', at: at(l, 'تنزل') + 0.4 },
      { p: 2, side: 1, lvl: 't', s: '+\\infty', at: at(l, 'زائد') },
      { p: 3, lvl: 'b', s: '0', at: at(l, 'الصفر') },
      { p: 4, lvl: 't', s: '1', at: at(l, 'تصعد') + 0.4 },
    ],
    arrows: [
      [0, 1, at(l, 'ثلاثة') + 0.4],
      [1, 2, at(l, 'تنزل') + 0.8],
      [3, 4, at(l, 'الصفر') + 0.4],
      [4, 5, at(l, 'تصعد') + 0.8],
    ],
    t: { lines: at(q, 'جدول') + 0.3, x: at(q, 'موجبة') - 0.6, rows: [at(q, 'موجبة') - 0.2, at(q, 'سالبة') - 0.2, at(q, 'وموجبة')] },
  });
  c.skip(tb.h + (P ? 50 : 40));
  const l3 = 'إذن f متزايدة تماما';
  const l4 = 'ومتناقصة تماما على المجال من ناقص';
  const G = C.green;
  const r1 = c.row([M('f', at(l3, 'متزايدة'), G), T('متزايدة تماما على', at(l3, 'متزايدة'), G), M(']-\\infty ; -\\ln 2]', at(l3, 'المجال'), G), T('وعلى', at(l3, 'وعلى'), G), M('[\\ln 2 ; +\\infty[', at(l3, 'المجال', 1), G)]);
  const r2 = c.row([M('f', at(l4, 'ومتناقصة'), G), T('متناقصة تماما على', at(l4, 'ومتناقصة'), G), M('[-\\ln 2 ; 0[', at(l4, 'المجال'), G), T('وعلى', at(l4, 'وعلى'), G), M(']0 ; \\ln 2]', at(l4, 'المجال', 1), G)]);
  frame(b, [r1, r2], at(l4, 'اثنين', 1) + 0.3, C.green, 20);
  return b;
}

function q3(P: boolean, W: number, H: number) {
  const q = 'السؤال الثالث';
  const b = board('q3', 'السؤال 3: مركز التناظر', q, P, W, H);
  const c = column(b, heading(b, 'السؤال 3 : مركز التناظر', at(q)) - 20);
  const s1 = c.row([T('بيّن أنه من أجل كل x من', at(q, 'بين'), C.blue), M(': \\R^{*}', at(q, 'بين') + 0.4, C.blue), M('f(-x) + f(x) = -3', at(q, 'يساوي'), C.white)]);
  const s2 = c.text('وفسّر النتيجة هندسيا، ثم ارسم المنحنى', at(q, 'وفسر'), C.blue);
  frame(b, [s1, s2], at(q, 'المنحنى') + 0.3);
  c.skip(24);
  const l = 'نضرب بسط ومقام';
  c.row([M('f(-x) = 1 + \\frac{5 - 4e^{-x}}{e^{-2x} - 1}', at(l, 'نضرب')), M('= 1 + \\frac{5e^{2x} - 4e^{x}}{1 - e^{2x}}', at(l, 'فنجد'))], { dir: 'ltr', space: 16 });
  const l2 = 'نجمع: اثنان';
  c.row([M('f(-x) + f(x) = 2 + \\frac{5 - 5e^{2x}}{e^{2x} - 1}', at(l2, 'نجمع')), M('= 2 - 5', at(l2, 'أي'))], { dir: 'ltr', space: 16 });
  const l3 = 'إذن f لناقص x زائد';
  const r = c.math('f(-x) + f(x) = -3', at(l3, 'يساوي'), C.yellow, P ? 60 : 60);
  result(b, [r], at(l3, 'ثلاثة') + 0.3, 22);
  return b;
}

/** The curve of f, drawn from the function itself. */
const f = (x: number) => 1 + (5 - 4 * Math.exp(x)) / (Math.exp(2 * x) - 1);
const LN2 = Math.log(2);

function q3b(P: boolean, W: number, H: number) {
  const q = 'هندسيا: النقطة';
  const b = board('q3b', 'السؤال 3: الرسم', q, P, W, H);
  const y0 = heading(b, 'التفسير والرسم', at(q)) - (P ? 10 : 30);
  // notes: right column (16:9) or above the graph (9:16)
  const c = column(b, y0, P ? 40 : 46);
  const nx = P ? W / 2 : W * 0.755;
  const keep = b.W;
  if (!P) b.W = W * 0.44 + 150; // so rows shrink to the note column
  const n1 = c.row([T('النقطة', at(q, 'النقطة'), C.yellow), M('\\Omega\\left(0 ; -\\frac{3}{2}\\right)', at(q, 'أوميغا'), C.yellow)], { x: nx });
  const n2 = c.row([T('مركز تناظر للمنحنى', at(q, 'مركز'), C.yellow)], { x: nx });
  result(b, [n1, n2], at(q, 'للمنحنى') + 0.2, 18);
  c.skip(P ? 0 : 10);
  const l = 'نرسم المقاربات';
  c.row([T('المقاربات :', at(l, 'المقاربات'), C.pink), M('y = 1', at(l, 'واحدا'), C.pink), M('y = -4', at(l, 'أربعة'), C.pink), M('x = 0', at(l, 'التراتيب'), C.pink)], { x: nx, space: 56 });
  const l2 = 'المنحنى يمس';
  c.row([T('يمسّ محور الفواصل في', at(l2, 'يمس')), M('(\\ln 2 ; 0)', at(l2, 'لوغاريتم'))], { x: nx });
  c.row([T('ويمرّ بالنقطة', at(l2, 'ويمر')), M('(-\\ln 2 ; -3)', at(l2, 'لوغاريتم', 1))], { x: nx });
  c.row([M('\\ln 2 \\approx 0{,}69', at(l2, 'ثلاثة'), C.blue, P ? 40 : 40)], { x: nx });
  b.W = keep;

  // the graph
  const u = P ? 98 : 88;
  const X0 = -4.6, X1 = 4.6, Y0 = -6.4, Y1 = 2.7;
  const ox = P ? W / 2 : 120 + -X0 * u;
  const oy = P ? c.y + 30 + Y1 * u : y0 + 30 + Y1 * u;
  const m = (x: number, y: number): Pt => [ox + x * u, oy - y * u];
  const tA = at(q, 'النقطة') - 0.2;
  b.stroke([...arrow(m(X0, 0), m(X1, 0), 16)], { at: tA, color: C.white, width: 3.5, dur: 0.8 });
  b.stroke([...arrow(m(0, Y0), m(0, Y1), 16)], { at: tA + 0.8, color: C.white, width: 3.5, dur: 0.8 });
  const ticks: Pt[][] = [];
  for (let i = -4; i <= 4; i++) if (i) ticks.push(seg(m(i, 0.08), m(i, -0.08), 3));
  for (let j = -6; j <= 2; j++) if (j) ticks.push(seg(m(-0.08, j), m(0.08, j), 3));
  b.stroke(ticks, { at: tA + 1.6, color: C.white, width: 2.5, dur: 0.6, sound: false });
  const ts = P ? 26 : 24;
  [-4, -3, -2, -1, 1, 2, 3, 4].forEach((i, k) => {
    if (i === 1) return; // ln 2 sits near 1
    b.math(String(i).replace('-', '-'), { x: m(i, 0)[0], y: m(i, 0)[1] + ts * 1.25, size: ts, color: C.white, at: tA + 2.2 + k * 0.05, dur: 0.1 });
  });
  [-6, -5, -3, -2, -1, 2].forEach((j, k) => b.math(String(j), { x: m(0, j)[0] - 14, y: m(0, j)[1] + ts * 0.35, size: ts, align: 'r', color: C.white, at: tA + 2.6 + k * 0.05, dur: 0.1 }));
  b.math('O', { x: m(0, 0)[0] - 12, y: m(0, 0)[1] + ts * 1.2, size: ts, align: 'r', at: tA + 2.9, dur: 0.1 });
  // Ω
  const om = m(0, -1.5);
  b.stroke([circle(om, 7)], { at: at(q, 'أوميغا') + 0.6, color: C.yellow, width: 7, dur: 0.3 });
  b.math('\\Omega', { x: om[0] + 16, y: om[1] + 12, size: 34, align: 'l', color: C.yellow, at: at(q, 'أوميغا') + 0.9, dur: 0.2 });
  // asymptotes
  b.stroke(dashed(m(X0, 1), m(X1, 1)), { at: at(l, 'واحدا') + 0.3, color: C.pink, width: 3.5, dur: 0.8 });
  b.math('y = 1', { x: m(-3.4, 1)[0], y: m(-3.4, 1)[1] - 14, size: 30, color: C.pink, at: at(l, 'واحدا') + 1.0, dur: 0.2 });
  b.stroke(dashed(m(X0, -4), m(X1, -4)), { at: at(l, 'أربعة') + 0.3, color: C.pink, width: 3.5, dur: 0.8 });
  b.math('y = -4', { x: m(-3.3, -4)[0], y: m(-3.3, -4)[1] + 38, size: 30, color: C.pink, at: at(l, 'أربعة') + 1.0, dur: 0.2 });
  b.stroke(dashed(m(0, Y0), m(0, Y1)), { at: at(l, 'التراتيب') + 0.3, color: C.pink, width: 3, dur: 0.6, sound: false });
  // special points
  const A = m(LN2, 0);
  b.stroke([circle(A, 6)], { at: at(l2, 'لوغاريتم') + 0.3, color: C.white, width: 6, dur: 0.25 });
  b.math('\\ln 2', { x: A[0] + 6, y: A[1] - 18, size: 28, color: C.white, at: at(l2, 'لوغاريتم') + 0.6, dur: 0.2 });
  const Bp = m(-LN2, -3);
  b.stroke([circle(Bp, 6)], { at: at(l2, 'لوغاريتم', 1) + 0.3, color: C.white, width: 6, dur: 0.25 });
  b.stroke(dashed(m(-LN2, 0), Bp, 8, 8), { at: at(l2, 'لوغاريتم', 1) + 0.6, color: C.white, width: 2.5, dur: 0.4, sound: false });
  b.stroke(dashed(m(0, -3), Bp, 8, 8), { at: at(l2, 'لوغاريتم', 1) + 1.0, color: C.white, width: 2.5, dur: 0.3, sound: false });
  b.math('-\\ln 2', { x: m(-LN2, 0)[0] - 4, y: m(-LN2, 0)[1] - 16, size: 26, align: 'r', color: C.white, at: at(l2, 'لوغاريتم', 1) + 1.3, dur: 0.2 });
  // the two branches: from the function, cut where they leave the picture
  const edge = (a: number, z: number, lim: number) => {
    // f(a) inside, f(z) outside: bisection for the x where f = lim
    for (let i = 0; i < 60; i++) {
      const mid = (a + z) / 2;
      if ((f(mid) - lim) * (f(a) - lim) > 0) a = mid;
      else z = mid;
    }
    return a;
  };
  const left = edge(-1, -1e-9, Y0);
  const right = edge(1, 1e-9, Y1);
  const branch = (a: number, z: number) => path(Array.from({ length: 241 }, (_, i) => { const x = a + ((z - a) * i) / 240; return m(x, f(x)); }), 4);
  const lb = 'ثم نرسم الفرعين';
  b.stroke([branch(X0, left)], { at: at(lb, 'نرسم'), color: C.blue, width: 6, dur: 2.2 });
  b.stroke([branch(X1, right)], { at: at(lb, 'متناظران') - 0.3, color: C.blue, width: 6, dur: 2.2 });
  b.math('(C_{f})', { x: m(-2.4, -2.5)[0], y: m(-2.4, -2.5)[1], size: 34, color: C.blue, at: at(lb, 'أوميغا'), dur: 0.3 });
  return b;
}

function q4(P: boolean, W: number, H: number) {
  const q = 'السؤال الرابع';
  const b = board('q4', 'السؤال 4: كتابة أخرى', q, P, W, H);
  const c = column(b, heading(b, 'السؤال 4 : كتابة أخرى لـ f', at(q)) - 20);
  const s1 = c.row([T('تحقّق أنه من أجل كل x من', at(q, 'تحقق'), C.blue), M(': \\R^{*}', at(q, 'تحقق') + 0.4, C.blue)]);
  const s2 = c.math(F_OTHER, at(q, 'يساوي'), C.white, P ? 50 : 54);
  frame(b, [s1, s2], at(q, 'ناقص', 2) + 1.2);
  c.skip(24);
  const l = 'نوحد المقامين';
  c.math('\\left(1 + e^{x}\\right)\\left(1 - e^{x}\\right) = 1 - e^{2x}', at(l, 'يساوي'), C.blue);
  const l2 = 'فيصبح الفرق';
  c.math('\\frac{9e^{x}}{1 + e^{x}} - \\frac{e^{x}}{1 - e^{x}} = \\frac{9e^{x}\\left(1 - e^{x}\\right) - e^{x}\\left(1 + e^{x}\\right)}{1 - e^{2x}}', at(l2, 'فيصبح'));
  c.math('= \\frac{8e^{x} - 10e^{2x}}{1 - e^{2x}}', at(l2, 'ثمانية'));
  return b;
}

function q4b(P: boolean, W: number, H: number) {
  const q = 'نضرب في النصف';
  const b = board('q4b', 'السؤال 4: التحقق', q, P, W, H);
  const c = column(b, heading(b, 'التحقق', at(q)) - 10, P ? 64 : 52);
  c.math('-4 + \\frac{4e^{x} - 5e^{2x}}{1 - e^{2x}} = \\frac{-e^{2x} + 4e^{x} - 4}{1 - e^{2x}} = \\frac{e^{2x} - 4e^{x} + 4}{e^{2x} - 1}', at(q, 'فنجد'));
  const l = 'ومن جهة أخرى';
  c.math('f(x) = \\frac{e^{2x} - 1 + 5 - 4e^{x}}{e^{2x} - 1} = \\frac{e^{2x} - 4e^{x} + 4}{e^{2x} - 1}', at(l, 'بتوحيد'), C.blue);
  c.skip(14);
  const l2 = 'إذن المساواة محققة';
  const r = c.math(F_OTHER, at(l2, 'المساواة'), C.yellow, P ? 52 : 56);
  result(b, [r], at(l2, 'محققة'), 22);
  b.stroke(check([r.x + r.w + 60, r.y + r.h / 2], 44), { at: at(l2, 'محققة') + 0.5, color: C.green, width: 6 });
  return b;
}

function q5(P: boolean, W: number, H: number) {
  const q = 'السؤال الخامس';
  const b = board('q5', 'السؤال 5: الدالة g', q, P, W, H);
  const c = column(b, heading(b, 'السؤال 5 : الدالة g', at(q)) - 20, P ? 52 : 40);
  const s1 = c.row([M('g', at(q, 'دالة'), C.blue), T('الدالة المعرفة على', at(q, 'معرفة'), C.blue), M(']1 ; +\\infty[', at(q, 'المجال'), C.blue), T('بـ :', at(q, 'بـ'), C.blue), M('g(x) = f(\\ln x)', at(q, 'يساوي'))]);
  const l = 'تحقق أن g';
  const s2 = c.row([T('تحقّق أن :', at(l, 'تحقق'), C.blue), M('g(x) = \\frac{(x - 2)^{2}}{x^{2} - 1}', at(l, 'يساوي'))]);
  const s3 = c.text('ثم حدّد اتجاه تغيّر g وشكّل جدول تغيّراتها', at(l, 'حدد'), C.blue);
  frame(b, [s1, s2, s3], at(l, 'تغيراتها') + 0.3);
  c.skip(24);
  c.math('e^{\\ln x} = x \\quad ; \\quad e^{2\\ln x} = x^{2}', at('لأن e أس لوغاريتم', 'يساوي'), C.blue);
  c.math('g(x) = 1 + \\frac{5 - 4x}{x^{2} - 1} = \\frac{x^{2} - 4x + 4}{x^{2} - 1}', at('نجد: g لـ x', 'يساوي'));
  const l3 = 'وهو x ناقص اثنين';
  const r = c.math('g(x) = \\frac{(x - 2)^{2}}{x^{2} - 1}', at(l3, 'وهو'), C.yellow, P ? 58 : 58);
  result(b, [r], at(l3, 'واحد') + 0.3, 20);
  return b;
}

function q5b(P: boolean, W: number, H: number) {
  const q = 'اتجاه التغير: g بريم';
  const b = board('q5b', 'السؤال 5: اتجاه تغير g', q, P, W, H);
  const c = column(b, heading(b, 'اتجاه تغيّر g', at(q)) - 10, P ? 64 : 52);
  c.math("g'(x) = \\frac{1}{x} \\times f'(\\ln x)", at(q, 'يساوي'));
  c.row([T('إشارة', at(q, 'وإشارته'), C.pink), M("g'(x)", at(q, 'وإشارته') + 0.3, C.pink), T('هي إشارة', at(q, 'إشارة'), C.pink), M("f'(\\ln x)", at(q, 'بريم', 1), C.pink)]);
  c.math("1 < x < 2 \\implies 0 < \\ln x < \\ln 2 \\implies g'(x) < 0", at('إذا كان x بين', 'بين'), C.blue);
  c.math("x > 2 \\implies \\ln x > \\ln 2 \\implies g'(x) > 0", at('وإذا كان x أكبر', 'أكبر'), C.blue);
  return b;
}

function q5c(P: boolean, W: number, H: number) {
  const q = 'النهايات: عند الواحد';
  const b = board('q5c', 'السؤال 5: جدول تغيرات g', q, P, W, H);
  const c = column(b, heading(b, 'جدول تغيّرات g', at(q)) - 10, P ? 60 : 50);
  c.row(
    [M(`${LIM('1^{+}')} g(x) = +\\infty`, at(q, 'الواحد'), C.blue), M(`${LIM('+\\infty')} g(x) = 1`, at(q, 'وعند'), C.blue), M('g(2) = 0', at(q, 'لاثنين'), C.blue)],
    { dir: 'ltr', space: 60 },
  );
  const tb = table(b, c.y + 10, {
    xs: ['1', '2', '+\\infty'],
    labels: ["g'(x)", 'g(x)'],
    signs: [['', '-', '0', '+', '']],
    dbl: [0],
    vals: [
      { p: 0, side: 1, lvl: 't', s: '+\\infty', at: at(q, 'الواحد') + 0.6 },
      { p: 1, lvl: 'b', s: '0', at: at(q, 'لاثنين') + 0.4 },
      { p: 2, lvl: 't', s: '1', at: at(q, 'وعند') + 0.6 },
    ],
    arrows: [
      [0, 1, at(q, 'لاثنين') + 0.8],
      [1, 2, at(q, 'لاثنين') + 1.4],
    ],
    tw: P ? 900 : 1000,
    lw: P ? 180 : 200,
    t: { lines: at(q, 'النهايات') - 0.6, x: at(q, 'النهايات') - 0.2, rows: [at(q, 'النهايات')] },
  });
  c.skip(tb.h + (P ? 50 : 40));
  const l = 'إذن g متناقصة';
  const G = C.green;
  const r1 = c.row([M('g', at(l, 'متناقصة'), G), T('متناقصة تماما على', at(l, 'متناقصة'), G), M(']1 ; 2]', at(l, 'المجال'), G)]);
  const r2 = c.row([M('g', at(l, 'ومتزايدة'), G), T('متزايدة تماما على', at(l, 'ومتزايدة'), G), M('[2 ; +\\infty[', at(l, 'المجال', 1), G)]);
  frame(b, [r1, r2], at(l, 'نهاية') + 0.4, C.green, 20);
  return b;
}

function outro(P: boolean, W: number, H: number) {
  const q = 'الخلاصة: عند الصفر';
  const b = board('outro', 'خلاصة', q, P, W, H);
  const c = column(b, heading(b, 'خلاصة', at(q)) - 10, P ? 56 : 42);
  c.text('عند الصفر: ندرس إشارة المقام', at(q, 'ندرس'), C.yellow);
  c.row([M('e^{x} > 0', at(q, 'موجب'), C.pink), T('لا يغيّر إشارة المشتقة', at(q, 'يغير'), C.pink)]);
  const l = 'وإذا كان f لناقص x';
  c.row([T('إذا كان', at(l, 'كان'), C.blue), M('f(-x) + f(x) = 2b', at(l, 'يساوي'), C.blue), T('فإن', at(l, 'فالنقطة'), C.blue), M('\\Omega(0 ; b)', at(l, 'فالنقطة') + 0.3, C.blue), T('مركز تناظر', at(l, 'مركز'), C.blue)]);
  c.skip(26);
  c.text('الحلقة القادمة : تمرين آخر من البكالوريا', at('في الحلقة القادمة', 'تمرين'), C.white, 42);
  const nm = c.text('الأستاذ سوايسية هشام', at('كنتم مع الأستاذ', 'الأستاذ'), C.yellow, P ? 64 : 60);
  b.stroke([seg([nm.x + nm.w + 20, nm.y + nm.h + 4], [nm.x - 20, nm.y + nm.h + 10])], { at: at('كنتم مع الأستاذ', 'الأستاذ') + 1.0, color: C.yellow, width: 5 });
  b.sound(at('كنتم مع الأستاذ', 'بالتوفيق') + 0.5, 'swell', 0.3, 3);
  return b;
}

const ALL = [intro, statement, q1, q1b, q1c, q2a, q2a2, q2b, q2b2, q3, q3b, q4, q4b, q5, q5b, q5c, outro];

export function buildBac1(P: boolean, W: number, H: number): Board[] {
  const gap = W * 0.3;
  const bs = ALL.map((fn) => fn(P, W, H));
  // writes due after the camera leaves (a frame drawn on the last word) are pulled back so they are seen
  bs.forEach((b, i) => {
    if (i + 1 >= bs.length) return;
    const lim = bs[i + 1].from - 0.85;
    for (const it of b.items) {
      if (it.t1 <= lim) continue;
      const d = Math.min(it.t1 - it.t0, 0.6);
      it.t0 = Math.min(it.t0, lim - d);
      it.t1 = it.t0 + d;
    }
  });
  return bs.map((b, i) => b.build(-i * (W + gap), 0, i + 1 < bs.length ? bs[i + 1].from - 0.8 : Infinity));
}
