// Exercise series, episode 2: equations, systems and inequalities (no ln: every equation ends on a power of e).
import { Board, Builder, C } from '../lib/engine';
import { path, seg } from '../lib/geom';
import { at, heading } from '../boards/util';
import { board, column, frame } from './ex1';

function intro(P: boolean, W: number, H: number) {
  const b = board('intro', 'مقدمة', 'السلام عليكم', P, W, H);
  const cx = W / 2;
  b.text('الأستاذ سوايسية هشام', { x: cx, y: P ? 330 : 170, size: 56, color: C.white, at: at('السلام عليكم', 'معكم') });
  const t = b.text('تمارين محلولة', { x: cx, y: P ? 510 : 320, size: P ? 104 : 106, color: C.yellow, at: at('هذه هي الحلقة', 'التمارين') });
  b.stroke([seg([t.x + t.w + 30, t.y + t.h + 6], [t.x - 30, t.y + t.h + 14])], { at: at('هذه هي الحلقة', 'المحلولة'), color: C.yellow, width: 6 });
  b.text('الدالة الأسية: الحلقة 2', { x: cx, y: P ? 690 : 470, size: P ? 64 : 60, color: C.pink, at: at('هذه هي الحلقة', 'الدالة') });
  b.text('حل المعادلات والجمل والمتراجحات', { x: cx, y: P ? 850 : 600, size: P ? 52 : 54, color: C.blue, at: at('موضوعنا اليوم', 'حل') });
  const q = 'القاعدتان الأساسيتان';
  const r1 = b.math('e^{a} = e^{b} \\iff a = b', { x: cx, y: P ? 1040 : 760, size: P ? 60 : 58, color: C.yellow, at: at(q, 'يساوي') - 0.3 });
  const r2 = b.math('e^{a} < e^{b} \\iff a < b', { x: cx, y: P ? 1160 : 860, size: P ? 60 : 58, color: C.yellow, at: at(q, 'أصغر') - 0.3 });
  frame(b, [r1, r2], at(q, 'أصغر', 1) + 0.3, C.yellow);
  return b;
}

/** A curly brace in front of a system of two equations (drawn left of the rows, as in the textbook). */
function brace(b: Builder, x: number, y0: number, y1: number, t: number) {
  const m = (y0 + y1) / 2;
  const w = 16;
  b.stroke([path([[x + w, y0], [x, y0 + w], [x, m - w], [x - w, m], [x, m + w], [x, y1 - w], [x + w, y1]], 4)], { at: t, color: C.white, width: 4 });
}

function ex1(P: boolean, W: number, H: number) {
  const q = 'التمرين الأول';
  const b = board('ex1', 'التمرين 1', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 1', at(q)) - 20);
  const s1 = c.text('حُلّ في ℝ المعادلة :', at(q, 'حل'), { color: C.blue });
  const s2 = c.math('e^{x} + e^{-x} = e + \\frac{1}{e}', at(q, 'المعادلة'), { size: P ? 62 : 60 });
  frame(b, [s1, s2], at(q, 'التالية') + 0.5);
  c.skip(16);
  c.math('X = e^{x} \\quad ; \\quad X > 0 \\quad ; \\quad e^{-x} = \\frac{1}{X}', at('نضع X يساوي e أس x، مع'), { color: C.blue, size: P ? 46 : 48 });
  c.math('X + \\frac{1}{X} = e + \\frac{1}{e} \\implies X^{2} - \\left(e + \\frac{1}{e}\\right)X + 1 = 0', at('نضرب الطرفين في'), { size: P ? 42 : 46 });
  c.math('(X - e)\\left(X - \\frac{1}{e}\\right) = 0', at('وهي تكتب', 'ناقص'), { size: P ? 50 : 50 });
  c.math('e^{x} = e \\implies x = 1 \\quad ; \\quad e^{x} = e^{-1} \\implies x = -1', at('إذن e أس x يساوي e، أي'), { color: C.blue, size: P ? 44 : 48 });
  const r = c.math('S = \\{ -1 \\; ; \\; 1 \\}', at('إذن e أس x يساوي e، أي', 'ناقص', 1), { color: C.yellow, size: P ? 60 : 58 });
  frame(b, [r], at('إذن e أس x يساوي e، أي', 'واحد', 2) + 0.4, C.yellow, 20);
  b.sound(at('إذن e أس x يساوي e، أي', 'واحد', 2) + 0.8, 'shimmer', 0.3);
  return b;
}

function ex2(P: boolean, W: number, H: number) {
  const q = 'التمرين الثاني';
  const b = board('ex2', 'التمرين 2', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 2', at(q)) - 20);
  const s1 = c.text('حُلّ في ℝ المعادلة :', at(q, 'حل'), { color: C.blue });
  const s2 = c.math('e^{x^{2}} = \\left(e^{x}\\right)^{2} \\times e^{3}', at(q, 'المعادلة'), { size: P ? 62 : 60 });
  frame(b, [s1, s2], at(q, 'التالية') + 0.5);
  c.skip(16);
  c.math('\\left(e^{x}\\right)^{2} \\times e^{3} = e^{2x + 3}', at('نكتب الطرف الثاني', 'أس'), { color: C.blue });
  c.math('x^{2} = 2x + 3 \\iff x^{2} - 2x - 3 = 0', at('إذن x مربع يساوي', 'يساوي'));
  c.math('(x - 3)(x + 1) = 0', at('بالتحليل', 'ناقص'));
  const r = c.math('S = \\{ -1 \\; ; \\; 3 \\}', at('بالتحليل', 'فالحلان'), { color: C.yellow, size: P ? 60 : 58 });
  frame(b, [r], at('بالتحليل', 'واحد') + 0.4, C.yellow, 20);
  b.sound(at('بالتحليل', 'واحد') + 0.8, 'shimmer', 0.3);
  return b;
}

function ex3(P: boolean, W: number, H: number) {
  const q = 'التمرين الثالث';
  const b = board('ex3', 'التمرين 3', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 3', at(q)) - 20, P ? 56 : 30);
  const s1 = c.text('حُلّ في ℝ² الجملة :', at(q, 'حل'), { color: C.blue });
  const e1 = c.math('e^{x} \\times e^{y} = e^{5}', at(q, 'الجملة'), { size: P ? 58 : 56 });
  const e2 = c.math('\\frac{e^{x}}{e^{y}} = e', at(q, 'التالية'), { size: P ? 58 : 56 });
  const bx = Math.min(e1.x, e2.x) - 40;
  brace(b, bx, e1.y - 6, e2.y + e2.h + 6, at(q, 'التالية') + 0.6);
  frame(b, [s1, e1, e2, { x: bx - 24, y: e1.y, w: 1, h: 1 }], at(q, 'التالية') + 1.0, C.white, 30);
  c.skip(30);
  c.math('x + y = 5 \\quad ; \\quad x - y = 1', at('المعادلة الأولى تعطي', 'يساوي'), { color: C.blue });
  c.math('2x = 6 \\implies x = 3 \\quad ; \\quad y = 2', at('بالجمع', 'اثنان'));
  const r = c.math('(x \\, ; \\, y) = (3 \\, ; \\, 2)', at('بالجمع', 'ثلاثة'), { color: C.yellow, size: P ? 60 : 58 });
  frame(b, [r], at('بالجمع', 'اثنين') + 0.4, C.yellow, 20);
  b.sound(at('بالجمع', 'اثنين') + 0.8, 'shimmer', 0.3);
  return b;
}

function ex4(P: boolean, W: number, H: number) {
  const q = 'التمرين الرابع';
  const b = board('ex4', 'التمرين 4', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 4', at(q)) - 20, P ? 64 : 44);
  const s1 = c.text('حُلّ في ℝ المتراجحة :', at(q, 'حل'), { color: C.blue });
  const s2 = c.math('e^{2x} - e^{x+1} - e^{x} + e \\le 0', at(q, 'المتراجحة'), { size: P ? 58 : 58 });
  frame(b, [s1, s2], at(q, 'التالية') + 0.5);
  c.skip(16);
  c.math('e^{x+1} = e \\times e^{x}', at('نلاحظ أن e أس x زائد', 'يساوي'), { color: C.blue });
  c.math('\\left(e^{x} - e\\right)\\left(e^{x} - 1\\right) \\le 0', at('نجد: e أس x ناقص e', 'ناقص'));
  c.math('1 \\le e^{x} \\le e', at('الجداء سالب عندما', 'بين'), { color: C.blue });
  c.math('e^{0} \\le e^{x} \\le e^{1} \\iff 0 \\le x \\le 1', at('أي e أس صفر أصغر', 'أصغر'));
  const r = c.math('S = [0 \\, ; \\, 1]', at('أي e أس صفر أصغر', 'محصور'), { color: C.yellow, size: P ? 60 : 58 });
  frame(b, [r], at('أي e أس صفر أصغر', 'وواحد') + 0.3, C.yellow, 20);
  b.sound(at('أي e أس صفر أصغر', 'وواحد') + 0.7, 'shimmer', 0.3);
  return b;
}

function ex5(P: boolean, W: number, H: number) {
  const q = 'التمرين الخامس';
  const b = board('ex5', 'التمرين 5', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 5', at(q)) - 20);
  const s1 = c.text('حُلّ في ℝ المتراجحة :', at(q, 'حل'), { color: C.blue });
  const s2 = c.math('e^{x^{2} - 3x} < e^{-2}', at(q, 'المتراجحة'), { size: P ? 64 : 62 });
  frame(b, [s1, s2], at(q, 'التالية') + 0.5);
  c.skip(16);
  c.math('x^{2} - 3x < -2', at('الدالة الأسية متزايدة تماما', 'فنقارن'), { color: C.blue });
  c.math('x^{2} - 3x + 2 < 0 \\iff (x - 1)(x - 2) < 0', at('أي x مربع ناقص ثلاثة', 'أصغر'));
  const r = c.math('S = ]1 \\, ; \\, 2[', at('كثير الحدود سالب', 'مجموعة'), { color: C.yellow, size: P ? 62 : 60 });
  frame(b, [r], at('كثير الحدود سالب', 'اثنين') + 0.4, C.yellow, 20);
  b.sound(at('كثير الحدود سالب', 'اثنين') + 0.8, 'shimmer', 0.3);
  return b;
}

function outro(P: boolean, W: number, H: number) {
  const q = 'الخلاصة: اكتب الطرفين';
  const b = board('outro', 'خلاصة', q, P, W, H);
  const c = column(b, heading(b, 'خلاصة', at(q)) - 10, P ? 60 : 44);
  c.text('اكتب الطرفين بنفس الأساس e', at(q, 'اكتب'), { color: C.yellow });
  c.text('تغيير المتغير : X = eˣ', at(q, 'واستعمل'), { color: C.pink });
  c.text('ولا تنسَ : X > 0', at(q, 'تنس'), { color: C.blue });
  c.skip(30);
  c.text('الحلقة القادمة : حساب النهايات وإزالة حالات عدم التعيين', at('في الحلقة القادمة', 'القادمة'), { color: C.white, size: 40 });
  const nm = c.text('الأستاذ سوايسية هشام', at('كنتم مع الأستاذ', 'الأستاذ'), { color: C.yellow, size: P ? 64 : 60 });
  b.stroke([seg([nm.x + nm.w + 20, nm.y + nm.h + 4], [nm.x - 20, nm.y + nm.h + 10])], { at: at('كنتم مع الأستاذ', 'الأستاذ') + 1.0, color: C.yellow, width: 5 });
  b.sound(at('كنتم مع الأستاذ', 'بالتوفيق') + 0.5, 'swell', 0.3, 3);
  return b;
}

const ALL = [intro, ex1, ex2, ex3, ex4, ex5, outro];

export function buildEx2(P: boolean, W: number, H: number): Board[] {
  const gap = W * 0.3;
  const bs = ALL.map((f) => f(P, W, H));
  return bs.map((b, i) => b.build(-i * (W + gap), 0, i + 1 < bs.length ? bs[i + 1].from - 0.8 : Infinity));
}
