// Exercise series, episode 3: limits and indeterminate forms (famous limits only, no ln).
import { Board, C } from '../lib/engine';
import { seg } from '../lib/geom';
import { at, heading } from '../boards/util';
import { board, column, frame } from './ex1';

const LIM_P = '\\lim_{x \\to +\\infty}';
const LIM_M = '\\lim_{x \\to -\\infty}';
const LIM_0 = '\\lim_{x \\to 0}';

function intro(P: boolean, W: number, H: number) {
  const b = board('intro', 'مقدمة', 'السلام عليكم', P, W, H);
  const cx = W / 2;
  b.text('الأستاذ سوايسية هشام', { x: cx, y: P ? 300 : 150, size: 54, color: C.white, at: at('السلام عليكم', 'معكم') });
  const t = b.text('تمارين محلولة', { x: cx, y: P ? 470 : 290, size: P ? 100 : 100, color: C.yellow, at: at('هذه هي الحلقة', 'التمارين') });
  b.stroke([seg([t.x + t.w + 30, t.y + t.h + 6], [t.x - 30, t.y + t.h + 14])], { at: at('هذه هي الحلقة', 'المحلولة'), color: C.yellow, width: 6 });
  b.text('الدالة الأسية: الحلقة 3', { x: cx, y: P ? 640 : 430, size: P ? 62 : 58, color: C.pink, at: at('هذه هي الحلقة', 'الدالة') });
  b.text('حساب النهايات وإزالة حالات عدم التعيين', { x: cx, y: P ? 790 : 550, size: P ? 48 : 50, color: C.blue, at: at('موضوعنا اليوم', 'حساب') });
  const q = 'سنستعمل النهايات الشهيرة';
  const S = P ? 52 : 50;
  const rows = P
    ? [
        b.math(`${LIM_P} \\frac{e^{x}}{x^{n}} = +\\infty`, { x: cx, y: 990, size: S, color: C.yellow, at: at(q, 'أس') }),
        b.math(`${LIM_M} x^{n} e^{x} = 0`, { x: cx, y: 1150, size: S, color: C.yellow, at: at(q, 'في') }),
        b.math(`${LIM_0} \\frac{e^{x} - 1}{x} = 1`, { x: cx, y: 1310, size: S, color: C.yellow, at: at(q, 'ناقص') }),
      ]
    : [
        b.math(`${LIM_P} \\frac{e^{x}}{x^{n}} = +\\infty`, { x: W * 0.8, y: 730, size: S, color: C.yellow, at: at(q, 'أس') }),
        b.math(`${LIM_M} x^{n} e^{x} = 0`, { x: W * 0.5, y: 730, size: S, color: C.yellow, at: at(q, 'في') }),
        b.math(`${LIM_0} \\frac{e^{x} - 1}{x} = 1`, { x: W * 0.2, y: 730, size: S, color: C.yellow, at: at(q, 'ناقص') }),
      ];
  frame(b, rows, at(q, 'واحد', 1) + 0.5, C.yellow, 30);
  return b;
}

function ex1(P: boolean, W: number, H: number) {
  const q = 'التمرين الأول';
  const b = board('ex1', 'التمرين 1', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 1', at(q)) - 20);
  const s1 = c.text('احسب :', at(q, 'احسب'), { color: C.blue });
  const s2 = c.math(`${LIM_P} x^{2} e^{-x}`, at(q, 'نهاية'), { size: P ? 62 : 60 });
  frame(b, [s1, s2], at(q, 'نهاية', 1) + 0.4);
  c.skip(16);
  c.text('حالة عدم تعيين : ∞ × 0', at('هذه حالة عدم تعيين', 'حالة'), { color: C.pink });
  c.math('x^{2} e^{-x} = \\frac{x^{2}}{e^{x}} = \\frac{1}{\\frac{e^{x}}{x^{2}}}', at('هذه حالة عدم تعيين', 'نكتب'));
  c.math(`${LIM_P} \\frac{e^{x}}{x^{2}} = +\\infty`, at('وبما أن e أس x على x مربع', 'يؤول'), { color: C.blue });
  const r = c.math(`${LIM_P} x^{2} e^{-x} = 0`, at('وبما أن e أس x على x مربع', 'مقلوبه'), { color: C.yellow, size: P ? 58 : 58 });
  frame(b, [r], at('وبما أن e أس x على x مربع', 'الصفر') + 0.3, C.yellow, 20);
  b.sound(at('وبما أن e أس x على x مربع', 'الصفر') + 0.7, 'shimmer', 0.3);
  return b;
}

function ex2(P: boolean, W: number, H: number) {
  const q = 'التمرين الثاني';
  const b = board('ex2', 'التمرين 2', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 2', at(q)) - 20);
  const s1 = c.text('احسب :', at(q, 'احسب'), { color: C.blue });
  const s2 = c.math(`${LIM_M} \\left(x^{2} + 2x\\right) e^{x}`, at(q, 'نهاية'), { size: P ? 60 : 60 });
  frame(b, [s1, s2], at(q, 'نهاية', 1) + 0.4);
  c.skip(16);
  c.math('\\left(x^{2} + 2x\\right) e^{x} = x^{2} e^{x} + 2x e^{x}', at('ننشر', 'مربع'), { color: C.blue });
  c.math(`${LIM_M} x^{2} e^{x} = 0 \\quad ; \\quad ${LIM_M} x e^{x} = 0`, at('كل منهما يؤول', 'منهما'), { size: P ? 44 : 50 });
  const r = c.math(`${LIM_M} \\left(x^{2} + 2x\\right) e^{x} = 0`, at('كل منهما يؤول', 'إذن'), { color: C.yellow, size: P ? 56 : 58 });
  frame(b, [r], at('كل منهما يؤول', 'صفرا') + 0.3, C.yellow, 20);
  b.sound(at('كل منهما يؤول', 'صفرا') + 0.7, 'shimmer', 0.3);
  return b;
}

function ex3(P: boolean, W: number, H: number) {
  const q = 'التمرين الثالث';
  const b = board('ex3', 'التمرين 3', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 3', at(q)) - 20, P ? 60 : 40);
  const s1 = c.math('f(x) = \\frac{e^{2x} - e^{x} + 1}{e^{2x} + 3}', at(q, 'نهاية'), { size: P ? 58 : 58 });
  const s2 = c.text('احسب نهاية f عند +∞ ثم عند −∞', at(q, 'زائد'), { color: C.blue });
  frame(b, [s1, s2], at(q, 'ناقص') + 0.6);
  c.skip(36);
  c.math('f(x) = \\frac{1 - e^{-x} + e^{-2x}}{1 + 3e^{-2x}}', at('عند زائد ما لا نهاية: حالة', 'فنقسم'), { size: P ? 50 : 50 });
  const r1 = c.math(`${LIM_P} f(x) = 1`, at('فتؤول e أس ناقص x', 'والنهاية'), { color: C.yellow, size: P ? 54 : 54 });
  c.math(`${LIM_M} e^{2x} = ${LIM_M} e^{x} = 0`, at('عند ناقص ما لا نهاية: e أس', 'يؤولان'), { color: C.blue, size: P ? 46 : 50 });
  const r2 = c.math(`${LIM_M} f(x) = \\frac{1}{3}`, at('فالنهاية تساوي واحدا على ثلاثة', 'تساوي'), { color: C.yellow, size: P ? 54 : 54 });
  frame(b, [r1], at('فتؤول e أس ناقص x', 'واحدا') + 0.3, C.yellow, 18);
  frame(b, [r2], at('فالنهاية تساوي واحدا على ثلاثة', 'ثلاثة') + 0.3, C.yellow, 18);
  b.sound(at('فالنهاية تساوي واحدا على ثلاثة', 'ثلاثة') + 0.7, 'shimmer', 0.3);
  return b;
}

function ex4(P: boolean, W: number, H: number) {
  const q = 'التمرين الرابع';
  const b = board('ex4', 'التمرين 4', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 4', at(q)) - 20, P ? 64 : 44);
  const s1 = c.text('احسب :', at(q, 'احسب'), { color: C.blue });
  const s2 = c.math(`${LIM_0} \\frac{e^{2x} - e^{x}}{x}`, at(q, 'نهاية'), { size: P ? 62 : 60 });
  frame(b, [s1, s2], at(q, 'الصفر') + 0.4);
  c.skip(10);
  c.text('حالة عدم تعيين : 0/0', at('حالة عدم تعيين: صفر على صفر', 'حالة'), { color: C.pink });
  c.math('\\frac{e^{2x} - e^{x}}{x} = \\frac{e^{2x} - 1}{x} - \\frac{e^{x} - 1}{x}', at('حالة عدم تعيين: صفر على صفر', 'نضيف'), { size: P ? 48 : 52 });
  c.math('\\frac{e^{2x} - 1}{x} = 2 \\times \\frac{e^{2x} - 1}{2x} \\to 2', at('الكسر الأول يكتب', 'اثنين'), { color: C.blue, size: P ? 48 : 52 });
  const r = c.math(`${LIM_0} \\frac{e^{2x} - e^{x}}{x} = 2 - 1 = 1`, at('والكسر الثاني يؤول', 'إذن'), { color: C.yellow, size: P ? 52 : 56 });
  frame(b, [r], at('والكسر الثاني يؤول', 'واحدا') + 0.3, C.yellow, 20);
  b.sound(at('والكسر الثاني يؤول', 'واحدا') + 0.7, 'shimmer', 0.3);
  return b;
}

function ex5(P: boolean, W: number, H: number) {
  const q = 'التمرين الخامس';
  const b = board('ex5', 'التمرين 5', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 5', at(q)) - 20);
  const s1 = c.text('احسب :', at(q, 'احسب'), { color: C.blue });
  const s2 = c.math(`${LIM_P} \\left(e^{x} - x^{3}\\right)`, at(q, 'نهاية'), { size: P ? 62 : 60 });
  frame(b, [s1, s2], at(q, 'نهاية', 1) + 0.4);
  c.skip(16);
  c.text('حالة عدم تعيين : ∞ − ∞', at('حالة عدم تعيين: ما لا نهاية ناقص', 'حالة'), { color: C.pink });
  c.math('e^{x} - x^{3} = x^{3}\\left(\\frac{e^{x}}{x^{3}} - 1\\right)', at('حالة عدم تعيين: ما لا نهاية ناقص', 'نخرج'), { size: P ? 54 : 56 });
  const r = c.math(`${LIM_P} \\left(e^{x} - x^{3}\\right) = +\\infty`, at('فنجد x مكعب في', 'وهذا'), { color: C.yellow, size: P ? 56 : 58 });
  frame(b, [r], at('فنجد x مكعب في', 'نهاية') + 0.3, C.yellow, 20);
  b.sound(at('فنجد x مكعب في', 'نهاية') + 0.7, 'shimmer', 0.3);
  return b;
}

function ex6(P: boolean, W: number, H: number) {
  const q = 'التمرين السادس';
  const b = board('ex6', 'التمرين 6', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 6', at(q)) - 20);
  const s1 = c.text('احسب :', at(q, 'احسب'), { color: C.blue });
  const s2 = c.math(`${LIM_P} x\\left(e^{\\frac{1}{x}} - 1\\right)`, at(q, 'نهاية'), { size: P ? 62 : 60 });
  frame(b, [s1, s2], at(q, 'نهاية', 1) + 0.4);
  c.skip(16);
  c.math('X = \\frac{1}{x} \\quad ; \\quad x \\to +\\infty \\implies X \\to 0', at('نغير المتغير', 'نضع'), { color: C.blue, size: P ? 48 : 52 });
  c.math('x\\left(e^{\\frac{1}{x}} - 1\\right) = \\frac{e^{X} - 1}{X}', at('وتصبح العبارة', 'العبارة'), { size: P ? 56 : 56 });
  const r = c.math(`${LIM_P} x\\left(e^{\\frac{1}{x}} - 1\\right) = \\lim_{X \\to 0} \\frac{e^{X} - 1}{X} = 1`, at('وتصبح العبارة', 'شهيرة'), { color: C.yellow, size: P ? 46 : 52 });
  frame(b, [r], at('وتصبح العبارة', 'واحدا') + 0.3, C.yellow, 20);
  b.sound(at('وتصبح العبارة', 'واحدا') + 0.7, 'shimmer', 0.3);
  return b;
}

function outro(P: boolean, W: number, H: number) {
  const q = 'الخلاصة: حدد نوع';
  const b = board('outro', 'خلاصة', q, P, W, H);
  const c = column(b, heading(b, 'خلاصة', at(q)) - 10, P ? 60 : 44);
  c.text('حدّد نوع حالة عدم التعيين', at(q, 'حدد'), { color: C.yellow });
  c.text('أخرج الحد الغالب، أو اقسم عليه', at(q, 'أخرج'), { color: C.pink });
  c.text('أو غيّر المتغير لتصل إلى نهاية شهيرة', at(q, 'غير'), { color: C.blue });
  c.skip(30);
  c.text('الحلقة القادمة : دراسة دالة كاملة', at('في الحلقة القادمة', 'القادمة'), { color: C.white, size: 42 });
  const nm = c.text('الأستاذ سوايسية هشام', at('كنتم مع الأستاذ', 'الأستاذ'), { color: C.yellow, size: P ? 64 : 60 });
  b.stroke([seg([nm.x + nm.w + 20, nm.y + nm.h + 4], [nm.x - 20, nm.y + nm.h + 10])], { at: at('كنتم مع الأستاذ', 'الأستاذ') + 1.0, color: C.yellow, width: 5 });
  b.sound(at('كنتم مع الأستاذ', 'بالتوفيق') + 0.5, 'swell', 0.3, 3);
  return b;
}

const ALL = [intro, ex1, ex2, ex3, ex4, ex5, ex6, outro];

export function buildEx3(P: boolean, W: number, H: number): Board[] {
  const gap = W * 0.3;
  const bs = ALL.map((f) => f(P, W, H));
  return bs.map((b, i) => b.build(-i * (W + gap), 0, i + 1 < bs.length ? bs[i + 1].from - 0.8 : Infinity));
}
