// Chapter 4: famous limits and how to lift indeterminate forms.
import { C, Builder } from '../lib/engine';
import { rect, seg } from '../lib/geom';
import { at, board, heading } from './util';

export function famous(P: boolean, W: number, H: number) {
  const b = board('famous', 'النهايات الشهيرة', 'نجيو للنهايات الشهيرة', P, W, H);
  const y0 = heading(b, 'النهايات الشهيرة', at('نجيو للنهايات الشهيرة'));
  const S = P ? 70 : 66;
  const gap = P ? 230 : 190;
  const rows: [string, number, string][] = [
    ['\\lim_{x \\to 0} \\frac{e^{x} - 1}{x} = 1', at('نهاية e أس x ناقص واحد', 'على') - 0.3, C.yellow],
    ['\\lim_{x \\to +\\infty} \\frac{e^{x}}{x} = +\\infty', at('نهاية e أس x على x', 'يروح') - 0.2, C.blue],
    ['\\lim_{x \\to -\\infty} x e^{x} = 0', at('ونهاية x ضرب e أس x', 'يروح') - 0.2, C.pink],
  ];
  const xs = P ? [W / 2, W / 2, W / 2] : [W / 2, W / 2, W / 2];
  const boxes = rows.map(([src, t, color], i) => b.math(src, { x: xs[i], y: y0 + 120 + i * gap, size: S, color, at: t }));
  const big = boxes.reduce((a, x) => ({ x: Math.min(a.x, x.x), w: Math.max(a.w, x.w) }), { x: W, w: 0 });
  b.stroke([rect(big.x - 50, boxes[0].y - 40, big.w + 100, boxes[2].y + boxes[2].h - boxes[0].y + 80)], { at: at('والقاعدة: في ما لا نهاية') - 0.6, color: C.white, width: 4, dur: 0.9 });
  const yr = boxes[2].y + boxes[2].h + (P ? 140 : 110);
  b.text('في اللانهاية، الدالة الأسية «تتغلب» على x', { x: W / 2, y: yr, size: P ? 50 : 52, color: C.green, at: at('والقاعدة: في ما لا نهاية', 'الأسية'), maxW: W - 140 });
  b.sound(at('والقاعدة: في ما لا نهاية', 'تغلب'), 'shimmer', 0.3);
  b.focus(at('نهاية e أس x ناقص واحد'), { ...boxes[0] }, 2.0, 1.0);
  b.home(at('نهاية e أس x على x') - 0.2);
  return b;
}

/** One worked limit: the limit, the indeterminate form, the trick, the result. */
function example(b: Builder, o: { x: number; y: number; maxW: number; title: string; tTitle: number; lim: string; tLim: number; form: string; tForm: number; steps: [string, number][]; result: string; tRes: number }) {
  const S = b.P ? 54 : 50;
  b.text(o.title, { x: o.x, y: o.y, size: b.P ? 46 : 44, color: C.orange, at: o.tTitle, maxW: o.maxW });
  let y = o.y + (b.P ? 120 : 105);
  const lim = b.math(o.lim, { x: o.x, y, size: S * 1.05, color: C.white, at: o.tLim, maxW: o.maxW });
  y = lim.y + lim.h + (b.P ? 70 : 60);
  const f = b.math(o.form, { x: o.x + 60, y, size: S * 0.8, color: C.pink, at: o.tForm, maxW: o.maxW - 200 });
  b.text('حالة عدم تعيين', { x: f.x - 30, y: y - S * 0.35, size: b.P ? 34 : 32, color: C.pink, at: o.tForm + 0.4, align: 'r' });
  y = f.y + f.h + (b.P ? 80 : 70);
  for (const [src, t] of o.steps) {
    const s = b.math(src, { x: o.x, y, size: S, color: C.white, at: t, maxW: o.maxW });
    y = s.y + s.h + (b.P ? 75 : 65);
  }
  const r = b.math(o.result, { x: o.x, y: y + 6, size: S * 1.05, color: C.yellow, at: o.tRes, maxW: o.maxW });
  b.stroke([rect(r.x - 26, r.y - 20, r.w + 52, r.h + 40)], { at: o.tRes + 0.9, color: C.yellow, width: 4 });
  return y;
}

export function indet1(P: boolean, W: number, H: number) {
  const b = board('indet', 'إزالة حالات عدم التعيين', 'ضرك كيفاش نزيلو', P, W, H);
  const y0 = heading(b, 'إزالة حالات عدم التعيين', at('ضرك كيفاش نزيلو'));
  const colW = P ? W - 140 : W * 0.44;
  example(b, {
    x: P ? W / 2 : W * 0.74,
    y: y0,
    maxW: colW,
    title: 'المثال 1',
    tTitle: at('ضرك كيفاش نزيلو', 'المثال'),
    lim: '\\lim_{x \\to +\\infty} \\left(e^{x} - x\\right)',
    tLim: at('ضرك كيفاش نزيلو', 'نهاية'),
    form: '\\infty - \\infty',
    tForm: at('هنا عندنا ما لا نهاية'),
    steps: [["e^{x} - x = x\\left(\\frac{e^{x}}{x} - 1\\right)", at('هنا عندنا ما لا نهاية', 'نخرجو')]],
    result: '\\lim_{x \\to +\\infty} \\left(e^{x} - x\\right) = +\\infty',
    tRes: at('والنتيجة زائد', 'والنتيجة'),
  });
  const x2 = P ? W / 2 : W * 0.26;
  const yy = P ? y0 + 760 : y0;
  example(b, {
    x: x2,
    y: yy,
    maxW: colW,
    title: 'المثال 2',
    tTitle: at('المثال الثاني'),
    lim: '\\lim_{x \\to +\\infty} \\frac{e^{x} + 1}{e^{x} - 1}',
    tLim: at('المثال الثاني', 'أس'),
    form: '\\frac{\\infty}{\\infty}',
    tForm: at('المثال الثاني', 'نهاية') + 0.2,
    steps: [
      ['\\frac{e^{x} + 1}{e^{x} - 1} = \\frac{1 + e^{-x}}{1 - e^{-x}}', at('نقسمو البسط والمقام', 'على')],
      ['\\lim_{x \\to +\\infty} e^{-x} = 0', at('نقسمو البسط والمقام', 'للصفر') - 0.6],
    ],
    result: '\\lim_{x \\to +\\infty} \\frac{e^{x} + 1}{e^{x} - 1} = 1',
    tRes: at('نقسمو البسط والمقام', 'تساوي'),
  });
  return b;
}

export function indet2(P: boolean, W: number, H: number) {
  const b = board('indet2', 'إزالة حالات عدم التعيين', 'المثال الثالث', P, W, H);
  const y0 = heading(b, 'إزالة حالات عدم التعيين', at('المثال الثالث'));
  const x = W / 2;
  const S = P ? 56 : 54;
  b.text('المثال 3', { x, y: y0, size: 46, color: C.orange, at: at('المثال الثالث') + 0.2 });
  const lim = b.math('\\lim_{x \\to 0} \\frac{e^{2x} - 1}{x}', { x, y: y0 + 130, size: S * 1.1, color: C.white, at: at('المثال الثالث', 'أس') });
  const f = b.math('\\frac{0}{0}', { x: x + 40, y: lim.y + lim.h + 70, size: S * 0.8, color: C.pink, at: at('المثال الثالث', 'يروح') });
  b.text('حالة عدم تعيين', { x: f.x - 30, y: f.y + f.h * 0.2, size: 34, color: C.pink, at: at('المثال الثالث', 'للصفر'), align: 'r' });
  const s1 = b.math('\\frac{e^{2x} - 1}{x} = 2 \\times \\frac{e^{2x} - 1}{2x}', { x, y: f.y + f.h + 110, size: S, color: C.white, at: at('نضربو ونقسمو', 'ونقسمو') });
  const s2 = b.math('X = 2x \\quad ; \\quad x \\to 0 \\implies X \\to 0', { x, y: s1.y + s1.h + 90, size: S * 0.85, color: C.blue, at: at('نضربو ونقسمو', 'ونحطو') });
  const s3 = b.math('\\lim_{X \\to 0} \\frac{e^{X} - 1}{X} = 1', { x, y: s2.y + s2.h + 110, size: S * 0.85, color: C.blue, at: at('نضربو ونقسمو', 'يساوي') + 0.6 });
  const r = b.math('\\lim_{x \\to 0} \\frac{e^{2x} - 1}{x} = 2 \\times 1 = 2', { x, y: s3.y + s3.h + 130, size: S * 1.05, color: C.yellow, at: at('نضربو ونقسمو', 'تساوي') });
  b.stroke([rect(r.x - 26, r.y - 20, r.w + 52, r.h + 40)], { at: at('نضربو ونقسمو', 'تساوي') + 1.4, color: C.yellow, width: 4 });
  b.sound(at('نضربو ونقسمو', 'تساوي') + 1.5, 'shimmer', 0.3);

  void seg;
  return b;
}
