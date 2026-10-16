// Chapter 3: derivative, limits, table of variations, graph.
import { C } from '../lib/engine';
import { Pt, arrow, check, circle, dashed, fn, rect, seg, wobble } from '../lib/geom';
import { at, board, heading } from './util';

export function deriv(P: boolean, W: number, H: number) {
  const b = board('deriv', 'المشتقة واتجاه التغير', 'المشتقة: e أس x برايم', P, W, H);
  const y0 = heading(b, 'المشتقة واتجاه التغير', at('المشتقة: e أس x برايم'));
  const cx = W / 2;
  b.text('الدالة الأسية قابلة للاشتقاق على ℝ ، ومن أجل كل x من ℝ :', { x: cx, y: y0, size: P ? 40 : 42, color: C.white, at: at('المشتقة: e أس x برايم', 'برايم') - 0.4, maxW: W - 140 });
  const d = b.math("\\left(e^{x}\\right)' = e^{x}", { x: cx, y: y0 + (P ? 190 : 160), size: P ? 96 : 100, color: C.yellow, at: at('المشتقة: e أس x برايم', 'تساوي') });
  b.stroke([rect(d.x - 40, d.y - 30, d.w + 80, d.h + 60)], { at: at('المشتقة: e أس x برايم', 'أس', 1) + 0.3, color: C.yellow, width: 5 });
  b.sound(at('المشتقة: e أس x برايم', 'أس', 1) + 0.6, 'shimmer', 0.3);

  const y1 = d.y + d.h + (P ? 160 : 110);
  b.math('e^{x} > 0', { x: P ? cx : W * 0.75, y: y1, size: P ? 70 : 66, color: C.white, at: at('وبما أنو', 'موجب') });
  const m = b.text('الدالة الأسية متزايدة تماما على ℝ', { x: P ? cx : W * 0.36, y: P ? y1 + 120 : y1 - 30, size: P ? 54 : 52, color: C.green, at: at('وبما أنو', 'متزايدة'), maxW: P ? W - 140 : W * 0.6 });
  if (!P) b.stroke(arrow([W * 0.64, y1 - 18], [W * 0.62 - 10, y1 - 18], 14), { at: at('وبما أنو', 'الدالة'), color: C.white, width: 4 });
  b.stroke(arrow([m.x - 60, m.y + m.h], [m.x - 20, m.y], 16), { at: at('وبما أنو', 'تماما', 1) + 0.2, color: C.green, width: 5 });

  const y2 = (P ? y1 + 330 : y1 + 210);
  b.text('إذا كانت u دالة قابلة للاشتقاق على مجال I :', { x: cx, y: y2 - (P ? 60 : 50), size: P ? 40 : 40, color: C.white, at: at('وإذا عندنا دالة u'), maxW: W - 140 });
  const eu = b.math("\\left(e^{u}\\right)' = u' \\times e^{u}", { x: cx, y: y2 + (P ? 90 : 70), size: P ? 82 : 80, color: C.pink, at: at('وإذا عندنا دالة u', 'برايم') - 0.4 });
  b.focus(at('وإذا عندنا دالة u', 'المشتقة'), { x: eu.x, y: y2 - 100, w: eu.w, h: eu.h + 160 }, 1.5, 1);
  return b;
}

export function limits(P: boolean, W: number, H: number) {
  const b = board('limits', 'النهايات وجدول التغيرات', 'النهايات: لما x يروح', P, W, H);
  const y0 = heading(b, 'النهايات', at('النهايات: لما x يروح'));
  const S = P ? 64 : 64;
  const l1 = b.math('\\lim_{x \\to +\\infty} e^{x} = +\\infty', { x: P ? W / 2 : W * 0.73, y: y0 + 60, size: S, color: C.yellow, at: at('النهايات: لما x يروح', 'يروح', 1) - 0.3 });
  const l2 = b.math('\\lim_{x \\to -\\infty} e^{x} = 0', { x: P ? W / 2 : W * 0.27, y: P ? y0 + 230 : y0 + 60, size: S, color: C.yellow, at: at('ولما x يروح لناقص', 'أس') });
  const ya = Math.max(l1.y + l1.h, l2.y + l2.h) + (P ? 70 : 60);
  b.text('المستقيم ذو المعادلة y = 0 مقارب أفقي عند −∞', { x: W / 2, y: ya, size: P ? 42 : 44, color: C.pink, at: at('معناها المستقيم اللي معادلتو', 'مستقيم', 1), maxW: W - 140 });

  // the table of variations, laid out left to right as in the Algerian textbook
  const tw = P ? 940 : 1100;
  const tx = (W - tw) / 2;
  const ty = ya + (P ? 140 : 110);
  const lw = P ? 170 : 180;
  const rh = [P ? 95 : 85, P ? 95 : 85, P ? 210 : 190];
  const yR = [ty, ty + rh[0], ty + rh[0] + rh[1], ty + rh[0] + rh[1] + rh[2]];
  const t0 = at('نجمعو كلش', 'جدول');
  b.stroke(
    [rect(tx, ty, tw, yR[3] - ty), seg([tx, yR[1]], [tx + tw, yR[1]]), seg([tx, yR[2]], [tx + tw, yR[2]]), seg([tx + lw, ty], [tx + lw, yR[3]])].map((p, i) => wobble(p, 'vt' + i, 1)),
    { at: t0 - 0.6, color: C.white, width: 4, dur: 1.0 },
  );
  const S2 = P ? 46 : 44;
  const mid = (i: number) => (yR[i] + yR[i + 1]) / 2 + S2 * 0.32;
  b.math('x', { x: tx + lw / 2, y: mid(0), size: S2, at: t0 + 0.5 });
  b.math("f'(x)", { x: tx + lw / 2, y: mid(1), size: S2, at: t0 + 0.6 });
  b.math('f(x)', { x: tx + lw / 2, y: mid(2), size: S2, at: t0 + 0.7 });
  b.math('-\\infty', { x: tx + lw + 70, y: mid(0), size: S2, color: C.blue, at: t0 + 0.8 });
  b.math('+\\infty', { x: tx + tw - 70, y: mid(0), size: S2, color: C.blue, at: t0 + 0.9 });
  b.math('+', { x: tx + lw + (tw - lw) / 2, y: mid(1), size: S2 * 1.2, color: C.green, at: at('نجمعو كلش', 'موجبة') });
  b.math('0', { x: tx + lw + 70, y: yR[3] - 30, size: S2, color: C.yellow, at: at('نجمعو كلش', 'تطلع') });
  b.math('+\\infty', { x: tx + tw - 70, y: yR[2] + 62, size: S2, color: C.yellow, at: at('نجمعو كلش', 'نهاية') - 0.3 });
  b.stroke(arrow([tx + lw + 120, yR[3] - 50], [tx + tw - 130, yR[2] + 50], 22), { at: at('نجمعو كلش', 'لزائد'), color: C.yellow, width: 5 });

  return b;
}

export function curve(P: boolean, W: number, H: number) {
  const b = board('curve', 'التمثيل البياني', 'ضرك نرسمو المنحنى', P, W, H);
  heading(b, 'التمثيل البياني', at('ضرك نرسمو المنحنى'), P ? 180 : 110);
  // the frame: orthonormal, unit u
  const u = P ? 124 : 112;
  const [xmin, xmax, ymin, ymax] = [-4.6, 2.3, -0.7, 6.4];
  const ox = P ? W / 2 + 1.0 * u : W * 0.43 + 0.6 * u; // origin on the board
  const oy = P ? 300 + ymax * u : 205 + ymax * u;
  const M = (x: number, y: number): Pt => [ox + x * u, oy - y * u];
  const t0 = at('ضرك نرسمو المنحنى', 'نرسمو');
  b.stroke(arrow(M(xmin, 0), M(xmax, 0), 18), { at: t0 - 0.3, color: C.white, width: 4, dur: 0.45 });
  b.stroke(arrow(M(0, ymin), M(0, ymax), 18), { at: t0 + 0.2, color: C.white, width: 4, dur: 0.45 });
  const ticks = [];
  for (let i = -4; i <= 2; i++) if (i) ticks.push(seg(M(i, -0.06), M(i, 0.06), 3));
  for (let j = 1; j <= 6; j++) ticks.push(seg(M(-0.06, j), M(0.06, j), 3));
  b.stroke(ticks, { at: t0 + 0.7, color: C.white, width: 3, dur: 0.3, sound: false });
  b.math('O', { x: ox - 26, y: oy + 38, size: 34, at: t0 + 1.0, dur: 0.12 });
  b.math('x', { x: M(xmax, 0)[0] - 10, y: oy + 44, size: 36, at: t0 + 1.15, dur: 0.12 });
  b.math('y', { x: ox - 30, y: M(0, ymax)[1] + 20, size: 36, at: t0 + 1.3, dur: 0.12 });

  // the curve, drawn from the left
  const xr = Math.log(ymax - 0.05);
  const cv = fn(Math.exp, xmin, xr, M, 220);
  b.stroke([cv], { at: t0 + 1.45, color: C.yellow, width: 6, dur: 1.6 });
  b.math('(C_{f})', { x: M(xr, 0)[0] + 70, y: M(0, ymax - 0.3)[1], size: 42, color: C.yellow, at: t0 + 3.1, dur: 0.3 });

  // the two points
  const tA = at('ضرك نرسمو المنحنى', 'صفر');
  b.stroke([circle(M(0, 1), 7)], { at: tA, color: C.pink, width: 5, dur: 0.3 });
  b.math('A(0;1)', { x: M(0, 1)[0] - 18, y: M(0, 1)[1] - 22, size: 36, color: C.pink, at: tA + 0.3, align: 'r' });
  const tB = at('ضرك نرسمو المنحنى', 'واحد', 1);
  const E = Math.E;
  b.stroke([...dashed(M(1, 0), M(1, E)), ...dashed(M(0, E), M(1, E))], { at: tB, color: C.blue, width: 3, dur: 0.6 });
  b.stroke([circle(M(1, E), 7)], { at: tB + 0.6, color: C.blue, width: 5, dur: 0.3 });
  b.math('B(1;e)', { x: M(1, E)[0] + 22, y: M(1, E)[1] + 12, size: 36, color: C.blue, at: tB + 0.9, align: 'l' });
  b.math('e', { x: ox - 30, y: M(0, E)[1] + 12, size: 36, color: C.blue, at: tB + 1.3 });
  b.math('1', { x: M(1, 0)[0], y: oy + 44, size: 34, color: C.blue, at: tB + 1.4 });

  // the tangent at 0: y = x + 1, and the curve stays above it
  const tT = at('المماس عند صفر', 'معادلتو');
  b.stroke([seg(M(-1.7, -0.7), M(2.1, 3.1))], { at: tT, color: C.pink, width: 4, dur: 1.0 });
  const tl = b.math('(T): y = x + 1', { x: P ? M(-1.2, 0)[0] : M(-1.9, 0)[0], y: P ? M(0, 2.3)[1] : M(0, 1.6)[1], size: 40, color: C.pink, at: tT + 0.9, align: 'r' });
  b.text('المنحنى فوق المماس', { x: tl.x + tl.w / 2, y: tl.y - 40, size: 32, color: C.pink, at: at('المماس عند صفر', 'فوقو') });

  // the asymptote on the left
  const tY = at('وعلى اليسار المنحنى', 'يقرب');
  b.stroke(arrow(M(-2.4, 0.55), M(-4.1, 0.2), 14), { at: tY, color: C.green, width: 4 });
  b.math('y = 0', { x: M(-3.4, 0)[0], y: M(0, 1.15)[1], size: 38, color: C.green, at: tY + 0.5 });
  b.text('مقارب أفقي عند −∞', { x: M(-3.3, 0)[0], y: M(0, 0.7)[1] + 40 + (P ? 60 : 50), size: 32, color: C.green, at: tY + 0.9 });
  b.stroke(check([M(-1.5, 0)[0], oy + 90], 36), { at: at('وعلى اليسار المنحنى', 'يلمسو'), color: C.green, width: 6 });
  b.focus(tY - 0.4, { x: M(-4.6, 0)[0], y: M(0, 2)[1], w: 3.6 * u, h: 2.6 * u }, 1.3, 1);
  b.home(at('وعلى اليسار المنحنى', 'يلمسو') + 0.6);
  return b;
}
