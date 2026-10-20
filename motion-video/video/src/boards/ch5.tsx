// Chapter 5: equations, sign studies, and the closing board.
import { C, Builder } from '../lib/engine';
import { check, rect, seg, wobble } from '../lib/geom';
import { at, board, heading } from './util';

export function equations(P: boolean, W: number, H: number) {
  const b = board('equations', 'حل المعادلات', 'نحلو المعادلات', P, W, H);
  const y0 = heading(b, 'حل المعادلات', at('نحلو المعادلات'));
  const r = b.math('e^{a} = e^{b} \\iff a = b', { x: W / 2, y: y0 + 40, size: P ? 66 : 62, color: C.pink, at: at('نحلو المعادلات', 'القاعدة') + 0.3 });
  b.stroke([rect(r.x - 30, r.y - 22, r.w + 60, r.h + 44)], { at: at('نحلو المعادلات', 'معناها') + 0.4, color: C.pink, width: 4 });
  const S = P ? 54 : 52;
  const col = (i: number) => (P ? W / 2 : i === 0 ? W * 0.74 : W * 0.26);
  const top = r.y + r.h + (P ? 120 : 110);
  const gap = P ? 125 : 118;
  // (1)
  const e1: [string, number, string][] = [
    ['e^{2x-1} = 1', at('المعادلة الأولى', 'يساوي'), C.white],
    ['e^{2x-1} = e^{0}', at('المعادلة الأولى', 'والواحد') + 0.4, C.white],
    ['2x - 1 = 0', at('إذن اثنين x', 'يساوي'), C.white],
    ['x = \\frac{1}{2} \\quad ; \\quad S = \\left\\{ \\frac{1}{2} \\right\\}', at('إذن اثنين x', 'نص') - 0.3, C.yellow],
  ];
  b.text('المعادلة 1', { x: col(0), y: top - 10, size: 40, color: C.orange, at: at('المعادلة الأولى') });
  e1.forEach(([src, t, c], i) => b.math(src, { x: col(0), y: top + 100 + i * gap, size: i === 3 ? S * 0.95 : S, color: c, at: t, maxW: P ? W - 140 : W * 0.44 }));
  // (2)
  const t2 = P ? top + 100 + 4 * gap + 40 : top;
  const e2: [string, number, string][] = [
    ['e^{x^{2}} = e^{x+2}', at('المعادلة الثانية', 'يساوي'), C.white],
    ['x^{2} = x + 2', at('الحلول: ناقص'), C.white],
    ['x^{2} - x - 2 = 0', at('الحلول: ناقص', 'زايد') + 0.2, C.white],
    ['S = \\left\\{ -1 \\; ; \\; 2 \\right\\}', at('الحلول: ناقص', 'الحلول'), C.yellow],
  ];
  b.text('المعادلة 2', { x: col(1), y: t2 - 10, size: 40, color: C.orange, at: at('المعادلة الثانية') });
  e2.forEach(([src, t, c], i) => b.math(src, { x: col(1), y: t2 + 100 + i * gap, size: S, color: c, at: t, maxW: P ? W - 140 : W * 0.44 }));
  return b;
}

export function equations2(P: boolean, W: number, H: number) {
  const b = board('equations2', 'حل المعادلات', 'المعادلة الثالثة', P, W, H);
  const y0 = heading(b, 'المعادلة 3', at('المعادلة الثالثة'));
  const S = P ? 52 : 54;
  const x = W / 2;
  const L: [string, number, string][] = [
    ['e^{2x} - (e + 1)e^{x} + e = 0', at('المعادلة الثالثة', 'ضرب'), C.white],
    ['X = e^{x} \\quad ; \\quad X > 0', at('مع X موجب', 'نحطو') + 0.3, C.blue],
    ['X^{2} - (e + 1)X + e = 0', at('مع X موجب', 'تولي'), C.white],
    ['X = 1 \\quad \\text{أو} \\quad X = e', at('ولا X يساوي e', 'الحلول') + 0.3, C.white],
    ['e^{x} = 1 \\implies x = 0 \\quad ; \\quad e^{x} = e \\implies x = 1', at('ولا X يساوي e', 'إذن'), C.white],
    ['S = \\left\\{ 0 \\; ; \\; 1 \\right\\}', at('ولا X يساوي e', 'واحد', 1) + 0.3, C.yellow],
  ];
  let y = y0 + 60;
  L.forEach(([src, t, c], i) => {
    const bx = b.math(src, { x, y, size: S, color: c, at: t, maxW: W - 150 });
    if (i === 5) b.stroke([rect(bx.x - 26, bx.y - 20, bx.w + 52, bx.h + 40)], { at: t + 0.8, color: C.yellow, width: 4 });
    y = bx.y + bx.h + (P ? 110 : 70);
    if (i === 2) {
      const d = b.math('\\Delta = (e - 1)^{2} > 0', P ? { x, y: y - 20, size: 40, color: C.blue, at: at('مع X موجب', 'الثانية') + 0.5 } : { x: bx.x + bx.w + 60, y: bx.y + bx.h * 0.75, size: 40, color: C.blue, at: at('مع X موجب', 'الثانية') + 0.5, align: 'l' });
      if (P) y = d.y + d.h + 100;
    }
  });
  b.sound(at('ولا X يساوي e', 'واحد', 1) + 1, 'shimmer', 0.3);
  return b;
}

/** A sign table (Algerian layout: labels on the left, values left to right). cells: 2k-1 entries for k points. */
export function signTable(b: Builder, o: { y: number; xs: string[]; rows: { label: string; cells: string[]; t: number; color?: string; times?: number[] }[]; t0: number; labelW?: number; rowH?: number; size?: number; width?: number }) {
  const tw = o.width ?? (b.P ? 980 : 1150);
  const tx = (b.W - tw) / 2;
  const lw = o.labelW ?? (b.P ? 300 : 320);
  const rh = o.rowH ?? (b.P ? 100 : 92);
  const n = o.rows.length + 1;
  const S = o.size ?? 44;
  const k = o.xs.length;
  const px = (i: number) => tx + lw + 60 + (i * (tw - lw - 120)) / (k - 1);
  const ix = (i: number) => (px(i) + px(i + 1)) / 2;
  const lines = [rect(tx, o.y, tw, rh * n), seg([tx + lw, o.y], [tx + lw, o.y + rh * n])];
  for (let r = 1; r < n; r++) lines.push(seg([tx, o.y + rh * r], [tx + tw, o.y + rh * r]));
  b.stroke(lines.map((p, i) => wobble(p, 'st' + o.y + i, 1)), { at: o.t0, color: C.white, width: 4, dur: 1.0 });
  const mid = (r: number) => o.y + rh * r + rh / 2 + S * 0.32;
  b.math('x', { x: tx + lw / 2, y: mid(0), size: S, at: o.t0 + 1.0 });
  o.xs.forEach((v, i) => b.math(v, { x: px(i), y: mid(0), size: S, color: C.blue, at: o.t0 + 1.1 + i * 0.15 }));
  o.rows.forEach((row, r) => {
    b.math(row.label, { x: tx + lw / 2, y: mid(r + 1), size: S * 0.9, at: row.t, maxW: lw - 30, color: row.color ?? C.white });
    row.cells.forEach((c, j) => {
      if (!c) return;
      const x = j % 2 === 0 ? px(j / 2) : ix((j - 1) / 2);
      const col = c === '+' ? C.green : c === '-' ? C.pink : C.white;
      b.math(c, { x, y: mid(r + 1), size: S * (c === '+' || c === '-' ? 1.15 : 1), color: col, at: row.times?.[j] ?? row.t + 0.5 + j * 0.12, dur: 0.25 });
    });
    // vertical guides under each zero
    row.cells.forEach((c, j) => {
      if (c === '0' && j % 2 === 0) b.stroke([seg([px(j / 2), o.y + rh * (r + 1) + 6], [px(j / 2), o.y + rh * (r + 1) + 18])], { at: row.t + 0.4, color: C.white, width: 2, dur: 0.1, sound: false });
    });
  });
  return { x: tx, y: o.y, w: tw, h: rh * n };
}

export function sign1(P: boolean, W: number, H: number) {
  const b = board('sign', 'دراسة الإشارة', 'وأخيرا دراسة الإشارة', P, W, H);
  const y0 = heading(b, 'دراسة الإشارة', at('وأخيرا دراسة الإشارة'));
  const k = b.math('e^{x} > 0', { x: W / 2, y: y0 + 40, size: P ? 74 : 70, color: C.yellow, at: at('وأخيرا دراسة الإشارة', 'السر') });
  b.text('دائما', { x: k.x - 40, y: k.y + k.h * 0.78, size: 48, color: C.yellow, at: at('وأخيرا دراسة الإشارة', 'ديما'), align: 'r' });
  b.stroke([rect(k.x - 200, k.y - 24, k.w + 230, k.h + 48)], { at: at('وأخيرا دراسة الإشارة', 'موجب'), color: C.yellow, width: 4 });
  const y1 = k.y + k.h + (P ? 140 : 110);
  b.text('إشارة (x − 2)eˣ هي إشارة (x − 2)', { x: W / 2, y: y1, size: P ? 46 : 46, color: C.white, at: at('إذن إشارة', 'ضرب'), maxW: W - 140 });
  signTable(b, {
    y: y1 + (P ? 70 : 60),
    t0: at('إذن إشارة', 'هي') - 0.2,
    xs: ['-\\infty', '2', '+\\infty'],
    rows: [{ label: '(x - 2)e^{x}', cells: ['', '-', '0', '+', ''], t: at('إذن إشارة', 'برك') - 0.3 }],
  });
  const y2 = y1 + (P ? 380 : 300);
  b.math('e^{x} - 1 > 0 \\iff x > 0', { x: P ? W / 2 : W * 0.73, y: y2, size: P ? 54 : 52, color: C.green, at: at('موجبة كي x موجب', 'موجبة') });
  b.math('e^{x} - 1 < 0 \\iff x < 0', { x: P ? W / 2 : W * 0.27, y: P ? y2 + 130 : y2, size: P ? 54 : 52, color: C.pink, at: at('موجبة كي x موجب', 'وسالبة') });
  b.text('لأن e⁰ = 1 والدالة الأسية متزايدة تماما', { x: W / 2, y: (P ? y2 + 250 : y2 + 110), size: 34, color: C.white, at: at('موجبة كي x موجب', 'وسالبة') + 1.2, maxW: W - 160 });
  return b;
}

export function sign2(P: boolean, W: number, H: number) {
  const b = board('sign2', 'دراسة الإشارة', 'نديرو جدول الإشارة', P, W, H);
  const q = 'نديرو جدول الإشارة';
  const y0 = heading(b, 'مثال', at(q));
  b.math('f(x) = (x - 1)\\left(e^{x} - 1\\right)', { x: W / 2, y: y0 + 50, size: P ? 62 : 64, color: C.yellow, at: at(q, 'ناقص') - 0.2 });
  const t0 = at(q, 'أس');
  const r = 'موجبة قبل الصفر';
  const tp = at(r, 'موجبة');
  const tm = at(r, 'سالبة');
  const tq = at(r, 'وموجبة');
  const tb = signTable(b, {
    y: y0 + (P ? 170 : 150),
    t0,
    labelW: P ? 330 : 360,
    xs: ['-\\infty', '0', '1', '+\\infty'],
    rows: [
      { label: 'x - 1', cells: ['', '-', '', '-', '0', '+', ''], t: at(q, 'نديرو') - 0.4 },
      { label: 'e^{x} - 1', cells: ['', '-', '0', '+', '', '+', ''], t: at(q, 'جدول') },
      { label: 'f(x)', cells: ['', '+', '0', '-', '0', '+', ''], t: tp - 0.5, color: C.yellow, times: [0, tp, tm - 0.3, tm, tq - 0.3, tq, 0] },
    ],
  });
  void tb.h;
  b.stroke(check([tb.x + tb.w + (P ? -40 : 50), tb.y + tb.h - 50], 46), { at: tq + 0.6, color: C.green, width: 6 });
  b.sound(tq + 0.8, 'shimmer', 0.3);
  return b;
}

export function outro(P: boolean, W: number, H: number) {
  const b = board('outro', 'خلاصة', 'نلخصو', P, W, H);
  const y0 = heading(b, 'خلاصة', at('نلخصو'));
  const S = P ? 58 : 54;
  const items: [string, number, string][] = [
    ['e^{x} > 0', at('نلخصو', 'موجب'), C.yellow],
    ["\\left(e^{x}\\right)' = e^{x}", at('نلخصو', 'روحها'), C.pink],
    ['', at('نلخصو', 'متزايدة'), C.green],
    ['\\lim_{x \\to -\\infty} e^{x} = 0 \\quad ; \\quad \\lim_{x \\to +\\infty} e^{x} = +\\infty', at('نلخصو', 'لزائد') - 0.5, C.blue],
  ];
  let y = y0 + 40;
  items.forEach(([src, t, c], i) => {
    if (i === 2) {
      b.text('الدالة الأسية متزايدة تماما على ℝ', { x: W / 2, y: y - S * 0.3, size: S * 0.85, color: c, at: t, maxW: W - 160 });
      y += P ? 130 : 105;
      return;
    }
    const bx = b.math(src, { x: W / 2, y, size: S, color: c, at: t, maxW: W - 160 });
    y = bx.y + bx.h + (P ? 110 : 80);
  });
  const yl = y + (P ? 60 : 30);
  b.text('أعجبك الدرس؟ اضغط إعجاب واشترك وشارك', { x: W / 2, y: yl, size: P ? 44 : 44, color: C.white, at: at('إذا عجبكم الدرس'), maxW: W - 160 });
  const nm = b.text('الأستاذ سوايسية هشام', { x: W / 2, y: yl + (P ? 150 : 115), size: P ? 70 : 64, color: C.yellow, at: at('كنتم مع الأستاذ', 'الأستاذ') });
  b.stroke([seg([nm.x + nm.w + 20, nm.y + nm.h + 4], [nm.x - 20, nm.y + nm.h + 10])], { at: at('كنتم مع الأستاذ', 'الأستاذ') + 1.2, color: C.yellow, width: 5 });
  b.text('بالتوفيق في البكالوريا', { x: W / 2, y: yl + (P ? 270 : 210), size: P ? 54 : 50, color: C.pink, at: at('كنتم مع الأستاذ', 'بالتوفيق') });
  b.sound(at('كنتم مع الأستاذ', 'بالتوفيق') + 1.4, 'swell', 0.3, 3);
  return b;
}
