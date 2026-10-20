// Exercise series, episode 4: a full function study (limits, derivative, table of variations, tangent).
import { Board, Builder, C } from '../lib/engine';
import { arrow, rect, seg, wobble } from '../lib/geom';
import { at, heading } from '../boards/util';
import { board, column, frame } from './ex1';

const LIM_P = '\\lim_{x \\to +\\infty}';
const LIM_M = '\\lim_{x \\to -\\infty}';

function intro(P: boolean, W: number, H: number) {
  const b = board('intro', 'مقدمة', 'السلام عليكم', P, W, H);
  const cx = W / 2;
  b.text('الأستاذ سوايسية هشام', { x: cx, y: P ? 300 : 150, size: 54, color: C.white, at: at('السلام عليكم', 'معكم') });
  const t = b.text('تمارين محلولة', { x: cx, y: P ? 470 : 290, size: 100, color: C.yellow, at: at('هذه هي الحلقة', 'التمارين') });
  b.stroke([seg([t.x + t.w + 30, t.y + t.h + 6], [t.x - 30, t.y + t.h + 14])], { at: at('هذه هي الحلقة', 'المحلولة'), color: C.yellow, width: 6 });
  b.text('الدالة الأسية: الحلقة 4', { x: cx, y: P ? 640 : 430, size: P ? 62 : 58, color: C.pink, at: at('هذه هي الحلقة', 'الدالة') });
  b.text('دراسة دالة كاملة', { x: cx, y: P ? 790 : 550, size: P ? 56 : 54, color: C.blue, at: at('موضوعنا اليوم', 'دراسة') });
  const q = 'تذكير: مشتقة e أس u';
  const r1 = b.math("\\left(e^{u}\\right)' = u'e^{u}", { x: P ? cx : W * 0.68, y: P ? 990 : 740, size: P ? 60 : 56, color: C.yellow, at: at(q, 'هي') });
  const r2 = b.math("(uv)' = u'v + uv'", { x: P ? cx : W * 0.32, y: P ? 1130 : 740, size: P ? 60 : 56, color: C.yellow, at: at(q, 'الجداء') + 0.3 });
  frame(b, [r1, r2], at(q, 'زائد') + 1.2, C.yellow, 30);
  return b;
}

function ex1(P: boolean, W: number, H: number) {
  const q = 'التمرين الأول';
  const b = board('ex1', 'التمرين 1', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 1', at(q)) - 20, P ? 60 : 40);
  const s1 = c.text('f الدالة المعرفة على ℝ بـ :', at(q, 'الدالة'), { color: C.blue });
  const s2 = c.math('f(x) = \\left(x^{2} - 3\\right)e^{x}', at(q, 'يساوي'), { size: P ? 62 : 60 });
  const s3 = c.text('احسب النهايتين، ثم f′(x)، ثم جدول التغيرات، والمماس عند 0', at('احسب نهايتي f'), { color: C.blue, size: P ? 36 : 36 });
  frame(b, [s1, s2, s3], at('احسب نهايتي f', 'الصفر') + 0.4);
  c.skip(10);
  c.math(`${LIM_M} x^{2}e^{x} = 0 \\quad ; \\quad ${LIM_M} 3e^{x} = 0`, at('عند ناقص ما لا نهاية: ننشر', 'فنجد'), { color: C.blue, size: P ? 44 : 48 });
  const l1 = c.math(`${LIM_M} f(x) = 0`, at('إذن نهاية f عند ناقص', 'تساوي'), { color: C.yellow, size: P ? 54 : 52 });
  c.text('y = 0 مستقيم مقارب أفقي عند −∞', at('إذن نهاية f عند ناقص', 'والمستقيم'), { color: C.pink, size: P ? 38 : 36 });
  const l2 = c.math(`${LIM_P} f(x) = +\\infty`, at('وعند زائد ما لا نهاية', 'فالنهاية'), { color: C.yellow, size: P ? 54 : 52 });
  frame(b, [l1], at('إذن نهاية f عند ناقص', 'أفقي') + 0.3, C.yellow, 16);
  frame(b, [l2], at('وعند زائد ما لا نهاية', 'فالنهاية') + 1.4, C.yellow, 16);
  return b;
}

function deriv(P: boolean, W: number, H: number) {
  const q = 'المشتقة: f بريم';
  const b = board('deriv', 'التمرين 1: المشتقة', q, P, W, H);
  const c = column(b, heading(b, 'المشتقة', at(q)) - 10, P ? 80 : 60);
  c.math("f'(x) = 2xe^{x} + \\left(x^{2} - 3\\right)e^{x}", at(q, 'يساوي'), { size: P ? 54 : 58 });
  c.math("f'(x) = \\left(x^{2} + 2x - 3\\right)e^{x}", at('نخرج e أس x عاملا', 'مربع'), { size: P ? 56 : 58 });
  const r = c.math("f'(x) = (x + 3)(x - 1)e^{x}", at('وبالتحليل', 'زائد'), { color: C.yellow, size: P ? 62 : 62 });
  frame(b, [r], at('وبالتحليل', 'ضرب', 1) + 0.6, C.yellow, 22);
  b.sound(at('وبالتحليل', 'ضرب', 1) + 0.9, 'shimmer', 0.3);
  return b;
}

/** The table of variations of f: x, f'(x) and the arrows of f. */
function variations(b: Builder, y: number, t: { lines: number; x: number; sign: number[]; max: number; min: number; ends: number }) {
  const tw = b.P ? 960 : 1100;
  const tx = (b.W - tw) / 2;
  const lw = b.P ? 160 : 180;
  const rh = [b.P ? 80 : 70, b.P ? 80 : 70, b.P ? 210 : 180];
  const yR = [y, y + rh[0], y + rh[0] + rh[1], y + rh[0] + rh[1] + rh[2]];
  const S = b.P ? 42 : 40;
  b.stroke(
    [rect(tx, y, tw, yR[3] - y), seg([tx, yR[1]], [tx + tw, yR[1]]), seg([tx, yR[2]], [tx + tw, yR[2]]), seg([tx + lw, y], [tx + lw, yR[3]])].map((p, i) => wobble(p, 'var' + i, 1)),
    { at: t.lines, color: C.white, width: 4, dur: 1.0 },
  );
  const px = (i: number) => tx + lw + 70 + (i * (tw - lw - 140)) / 3;
  const ix = (i: number) => (px(i) + px(i + 1)) / 2;
  const mid = (r: number) => (yR[r] + yR[r + 1]) / 2 + S * 0.32;
  b.math('x', { x: tx + lw / 2, y: mid(0), size: S, at: t.lines + 0.6, dur: 0.15 });
  b.math("f'(x)", { x: tx + lw / 2, y: mid(1), size: S, at: t.lines + 0.7, dur: 0.15 });
  b.math('f(x)', { x: tx + lw / 2, y: mid(2), size: S, at: t.lines + 0.8, dur: 0.15 });
  ['-\\infty', '-3', '1', '+\\infty'].forEach((v, i) => b.math(v, { x: px(i), y: mid(0), size: S, color: C.blue, at: t.x + i * 0.2, dur: 0.2 }));
  ['+', '-', '+'].forEach((s, i) => b.math(s, { x: ix(i), y: mid(1), size: S * 1.15, color: s === '+' ? C.green : C.pink, at: t.sign[i], dur: 0.2 }));
  [1, 2].forEach((i) => b.math('0', { x: px(i), y: mid(1), size: S, at: t.sign[i] - 0.2, dur: 0.15 }));
  const top = yR[2] + S * 1.0;
  const bot = yR[3] - S * 0.35;
  b.math('0', { x: px(0), y: bot, size: S, color: C.yellow, at: t.max - 0.6, dur: 0.15 });
  b.math('6e^{-3}', { x: px(1), y: top, size: S, color: C.yellow, at: t.max, dur: 0.3 });
  b.math('-2e', { x: px(2), y: bot, size: S, color: C.yellow, at: t.min, dur: 0.3 });
  b.math('+\\infty', { x: px(3), y: top, size: S, color: C.yellow, at: t.ends, dur: 0.3 });
  const up = (a: number, z: number) => arrow([px(a) + 50, bot - S * 0.5], [px(z) - 60, top - S * 0.2], 16);
  const down = (a: number, z: number) => arrow([px(a) + 60, top - S * 0.2], [px(z) - 50, bot - S * 0.5], 16);
  b.stroke(up(0, 1), { at: t.max + 0.4, color: C.yellow, width: 4 });
  b.stroke(down(1, 2), { at: t.min + 0.4, color: C.yellow, width: 4 });
  b.stroke(up(2, 3), { at: t.ends + 0.4, color: C.yellow, width: 4 });
  return { y, h: yR[3] - y };
}

function table(P: boolean, W: number, H: number) {
  const q = 'وبما أن e أس x موجب، فإشارة';
  const b = board('table', 'التمرين 1: جدول التغيرات', q, P, W, H);
  const c = column(b, heading(b, 'جدول التغيرات', at(q)) - 10, P ? 60 : 40);
  c.text('eˣ > 0 : إشارة f′(x) هي إشارة (x + 3)(x − 1)', at(q, 'فإشارة'), { color: C.pink, size: P ? 40 : 40 });
  const ls = 'المشتقة موجبة قبل';
  const tb = variations(b, c.y + 10, {
    lines: at(q, 'تنعدم') - 0.4,
    x: at(q, 'ثلاثة'),
    sign: [at(ls, 'موجبة'), at(ls, 'سالبة'), at(ls, 'وموجبة')],
    max: at('القيمة الحدية العظمى', 'يساوي'),
    min: at('والقيمة الحدية الصغرى', 'يساوي'),
    ends: at('والقيمة الحدية الصغرى', 'اثنين') + 0.6,
  });
  c.skip(tb.h + 30);
  c.math('f(-3) = 6e^{-3} \\quad ; \\quad f(1) = -2e', at('والقيمة الحدية الصغرى', 'الصغرى'), { color: C.blue, size: P ? 46 : 46 });
  return b;
}

function tangent(P: boolean, W: number, H: number) {
  const q = 'المماس عند الصفر: f للصفر';
  const b = board('tangent', 'التمرين 1: المماس', q, P, W, H);
  const c = column(b, heading(b, 'المماس عند 0', at(q)) - 10, P ? 80 : 60);
  c.math("f(0) = -3 \\quad ; \\quad f'(0) = -3", at(q, 'للصفر'), { color: C.blue, size: P ? 54 : 56 });
  c.math("y = f'(0)(x - 0) + f(0)", at('إذن معادلة المماس', 'معادلة'), { size: P ? 54 : 56 });
  const r = c.math('(T) : y = -3x - 3', at('إذن معادلة المماس', 'يساوي'), { color: C.yellow, size: P ? 64 : 64 });
  frame(b, [r], at('إذن معادلة المماس', 'ثلاثة', 1) + 0.3, C.yellow, 22);
  b.sound(at('إذن معادلة المماس', 'ثلاثة', 1) + 0.7, 'shimmer', 0.3);
  return b;
}

function ex2(P: boolean, W: number, H: number) {
  const q = 'التمرين الثاني';
  const b = board('ex2', 'التمرين 2', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 2', at(q)) - 20, P ? 60 : 38);
  const s1 = c.math('g(x) = e^{-x^{2} + 2x}', at(q, 'الدالة'), { size: P ? 64 : 62 });
  const s2 = c.text('احسب g′(x) وادرس اتجاه تغير g', at(q, 'احسب'), { color: C.blue });
  frame(b, [s1, s2], at(q, 'تغيرها') + 0.4);
  c.skip(10);
  c.math("u(x) = -x^{2} + 2x \\quad ; \\quad u'(x) = -2x + 2", at('نستعمل قاعدة e أس u', 'هنا'), { color: C.blue, size: P ? 46 : 50 });
  c.math("g'(x) = (-2x + 2)e^{-x^{2} + 2x}", at('إذن g بريم', 'يساوي'), { size: P ? 54 : 56 });
  c.math("x < 1 \\implies g'(x) > 0 \\quad ; \\quad x > 1 \\implies g'(x) < 0", at('إشارتها إشارة ناقص', 'موجبة'), { color: C.blue, size: P ? 42 : 46 });
  const r1 = c.text('g متزايدة على ]−∞ ; 1] ومتناقصة على [1 ; +∞[', at('إذن g متزايدة', 'متزايدة'), { color: C.green, size: P ? 40 : 40 });
  const r2 = c.math('g(1) = e^{-1 + 2} = e', at('إذن g متزايدة', 'العظمى'), { color: C.yellow, size: P ? 56 : 54 });
  frame(b, [r1, r2], at('إذن g متزايدة', 'يساوي') + 0.4, C.yellow, 18);
  return b;
}

function ex3(P: boolean, W: number, H: number) {
  const q = 'التمرين الثالث';
  const b = board('ex3', 'التمرين 3', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 3', at(q)) - 20, P ? 64 : 44);
  const s1 = c.math('k(x) = \\frac{e^{x} - 1}{e^{x} + 1}', at(q, 'الدالة'), { size: P ? 62 : 60 });
  const s2 = c.text('بيّن أن k متزايدة تماما على ℝ', at(q, 'بين'), { color: C.blue });
  frame(b, [s1, s2], at(q, 'R') + 0.6);
  c.skip(34);
  c.math("\\left(\\frac{u}{v}\\right)' = \\frac{u'v - uv'}{v^{2}}", at('نشتق حاصل القسمة', 'بريم'), { color: C.blue, size: P ? 54 : 54 });
  c.math('e^{x}\\left(e^{x} + 1\\right) - e^{x}\\left(e^{x} - 1\\right) = 2e^{x}', at('في البسط', 'ضرب'), { size: P ? 46 : 52 });
  c.skip(18);
  const r = c.math("k'(x) = \\frac{2e^{x}}{\\left(e^{x} + 1\\right)^{2}} > 0", at('إذن k بريم', 'يساوي'), { color: C.yellow, size: P ? 58 : 58 });
  frame(b, [r], at('إذن k بريم', 'موجب') + 0.3, C.yellow, 20);
  c.text('k متزايدة تماما على ℝ', at('إذن k بريم', 'فالدالة'), { color: C.green });
  b.sound(at('إذن k بريم', 'فالدالة') + 0.8, 'shimmer', 0.3);
  return b;
}

function outro(P: boolean, W: number, H: number) {
  const q = 'الخلاصة: نحسب النهايات';
  const b = board('outro', 'خلاصة', q, P, W, H);
  const c = column(b, heading(b, 'خلاصة', at(q)) - 10, P ? 60 : 44);
  c.text('احسب النهايات أولًا', at(q, 'نحسب'), { color: C.yellow });
  c.text('اشتق، ثم أخرج eˣ عاملًا مشتركًا', at(q, 'نشتق'), { color: C.pink });
  c.text('eˣ > 0 لا يغيّر الإشارة', at(q, 'لأنه'), { color: C.blue });
  c.skip(30);
  c.text('الحلقة الأخيرة : دراسة الإشارة والدوال المساعدة', at('في الحلقة الأخيرة', 'الأخيرة'), { color: C.white, size: 42 });
  const nm = c.text('الأستاذ سوايسية هشام', at('كنتم مع الأستاذ', 'الأستاذ'), { color: C.yellow, size: P ? 64 : 60 });
  b.stroke([seg([nm.x + nm.w + 20, nm.y + nm.h + 4], [nm.x - 20, nm.y + nm.h + 10])], { at: at('كنتم مع الأستاذ', 'الأستاذ') + 1.0, color: C.yellow, width: 5 });
  b.sound(at('كنتم مع الأستاذ', 'بالتوفيق') + 0.5, 'swell', 0.3, 3);
  return b;
}

const ALL = [intro, ex1, deriv, table, tangent, ex2, ex3, outro];

export function buildEx4(P: boolean, W: number, H: number): Board[] {
  const gap = W * 0.3;
  const bs = ALL.map((f) => f(P, W, H));
  return bs.map((b, i) => b.build(-i * (W + gap), 0, i + 1 < bs.length ? bs[i + 1].from - 0.8 : Infinity));
}
