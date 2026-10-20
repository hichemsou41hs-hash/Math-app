// Exercise series, episode 1: simplifying expressions and proving identities (no ln: the students have not
// met it yet). One board per exercise: the statement in a box, a «try it yourself» pause, then the solution.
import { Board, BBox, Builder, C } from '../lib/engine';
import { check, rect, seg } from '../lib/geom';
import { at, board as lessonBoard, heading } from '../boards/util';

/** Exercise boards may zoom out a little when the solution is long. */
function board(id: string, chapter: string, first: string, P: boolean, W: number, H: number) {
  const b = lessonBoard(id, chapter, first, P, W, H);
  b.minZoom = 0.82;
  return b;
}

/** Writes rows one under the other, centred, and remembers where the next row goes. */
export function column(b: Builder, y: number, gap = b.P ? 70 : 52) {
  let cur = y;
  const put = (box: BBox, extra = 0) => {
    cur = box.y + box.h + gap + extra;
    return box;
  };
  return {
    get y() {
      return cur;
    },
    skip(dy: number) {
      cur += dy;
    },
    math(src: string, t: number, o: { size?: number; color?: string; x?: number; align?: 'c' | 'r' | 'l' } = {}) {
      const size = o.size ?? (b.P ? 54 : 52);
      return put(b.math(src, { x: o.x ?? b.W / 2, y: cur + size * 0.8, size, color: o.color ?? C.white, at: t, align: o.align, maxW: b.W - 150 }));
    },
    text(str: string, t: number, o: { size?: number; color?: string } = {}) {
      const size = o.size ?? (b.P ? 42 : 40);
      return put(b.text(str, { x: b.W / 2, y: cur + size * 0.85, size, color: o.color ?? C.white, at: t, maxW: b.W - 150 }));
    },
  };
}

/** A box drawn around the statement (or the result) once it is written. */
export function frame(b: Builder, boxes: BBox[], t: number, color = C.white, pad = 26) {
  const x0 = Math.min(...boxes.map((x) => x.x)) - pad;
  const y0 = Math.min(...boxes.map((x) => x.y)) - pad;
  const x1 = Math.max(...boxes.map((x) => x.x + x.w)) + pad;
  const y1 = Math.max(...boxes.map((x) => x.y + x.h)) + pad;
  b.stroke([rect(x0, y0, x1 - x0, y1 - y0)], { at: t, color, width: 4 });
}

function intro(P: boolean, W: number, H: number) {
  const b = board('intro', 'مقدمة', 'السلام عليكم', P, W, H);
  const cx = W / 2;
  b.text('الأستاذ سوايسية هشام', { x: cx, y: P ? 330 : 190, size: 56, color: C.white, at: at('السلام عليكم', 'معكم') });
  const t = b.text('تمارين محلولة', { x: cx, y: P ? 520 : 350, size: P ? 104 : 110, color: C.yellow, at: at('هذه هي الحلقة', 'التمارين') });
  b.stroke([seg([t.x + t.w + 30, t.y + t.h + 6], [t.x - 30, t.y + t.h + 14])], { at: at('هذه هي الحلقة', 'المحلولة'), color: C.yellow, width: 6 });
  b.text('الدالة الأسية: الحلقة 1', { x: cx, y: P ? 700 : 510, size: P ? 64 : 62, color: C.pink, at: at('هذه هي الحلقة', 'الدالة') });
  b.text('تبسيط العبارات وإثبات المساواة', { x: cx, y: P ? 860 : 650, size: P ? 54 : 56, color: C.blue, at: at('موضوعنا اليوم', 'تبسيط') });
  b.text('أوقف الفيديو وحاول قبل رؤية الحل', { x: cx, y: P ? 1020 : 800, size: 40, color: C.white, at: at('في كل تمرين', 'أوقف') });
  return b;
}

function ex1(P: boolean, W: number, H: number) {
  const q = 'التمرين الأول';
  const b = board('ex1', 'التمرين 1', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 1', at(q)) - 20);
  const s1 = c.text('بسّط العبارة :', at(q, 'بسط'), { color: C.blue });
  const s2 = c.math('A = \\frac{e^{2x+1} \\times e^{1-x}}{e^{x+2}}', at(q, 'A') - 0.2, { size: P ? 62 : 60 });
  frame(b, [s1, s2], at(q, 'A') + 1.0);
  c.skip(20);
  c.math('(2x + 1) + (1 - x) = x + 2', at('نجمع أسي البسط', 'اثنان'), { color: C.blue });
  c.math('A = \\frac{e^{x+2}}{e^{x+2}}', at('إذن البسط يساوي', 'يساوي'));
  const r = c.math('A = e^{0} = 1', at('ومنه A يساوي', 'صفر') - 0.3, { color: C.yellow, size: P ? 62 : 60 });
  frame(b, [r], at('ومنه A يساوي', 'واحدا'), C.yellow, 20);
  b.sound(at('ومنه A يساوي', 'واحدا') + 0.6, 'shimmer', 0.3);
  return b;
}

function ex2(P: boolean, W: number, H: number) {
  const q = 'التمرين الثاني';
  const b = board('ex2', 'التمرين 2', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 2', at(q)) - 20);
  const s1 = c.text('بيّن أنه من أجل كل عدد حقيقي x :', at(q, 'بين'), { color: C.blue });
  const s2 = c.math('\\frac{e^{x} - e^{-x}}{e^{x} + e^{-x}} = \\frac{e^{2x} - 1}{e^{2x} + 1}', at(q, 'المساواة'), { size: P ? 56 : 60 });
  frame(b, [s1, s2], at(q, 'التالية') + 0.4);
  c.skip(20);
  c.text('نضرب البسط والمقام في eˣ', at('الفكرة: نضرب', 'نضرب'), { color: C.pink });
  c.math('e^{x} \\times e^{x} = e^{2x} \\quad ; \\quad e^{-x} \\times e^{x} = e^{0} = 1', at('في البسط', 'يعطي'), { color: C.blue, size: P ? 46 : 50 });
  const r = c.math('\\frac{(e^{x} - e^{-x})e^{x}}{(e^{x} + e^{-x})e^{x}} = \\frac{e^{2x} - 1}{e^{2x} + 1}', at('وبنفس الطريقة في المقام'), { color: C.yellow, size: P ? 50 : 54 });
  frame(b, [r], at('وبنفس الطريقة في المقام', 'المطلوبة'), C.yellow, 20);
  b.sound(at('وبنفس الطريقة في المقام', 'المطلوبة') + 0.6, 'shimmer', 0.3);
  return b;
}

function ex3(P: boolean, W: number, H: number) {
  const q = 'التمرين الثالث';
  const b = board('ex3', 'التمرين 3', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 3', at(q)) - 20);
  const s1 = c.text('بيّن أنه من أجل كل عدد حقيقي x :', at(q, 'بين'), { color: C.blue });
  const s2 = c.math('\\frac{e^{x}}{e^{x} + 1} + \\frac{e^{-x}}{e^{-x} + 1} = 1', at(q, 'الكسرين'), { size: P ? 58 : 60 });
  frame(b, [s1, s2], at(q, 'واحدا') + 0.3);
  c.skip(20);
  c.math('\\frac{e^{-x}}{e^{-x} + 1} = \\frac{e^{-x} \\times e^{x}}{(e^{-x} + 1)e^{x}} = \\frac{1}{1 + e^{x}}', at('نضرب بسط ومقام الكسر الثاني', 'الثاني'), { color: C.blue, size: P ? 48 : 52 });
  c.text('نفس المقام : eˣ + 1', at('الكسران لهما نفس المقام', 'المقام'), { color: C.pink });
  const r = c.math('\\frac{e^{x}}{e^{x} + 1} + \\frac{1}{e^{x} + 1} = \\frac{e^{x} + 1}{e^{x} + 1} = 1', at('نجمع البسطين', 'فنجد'), { color: C.yellow, size: P ? 50 : 54 });
  frame(b, [r], at('نجمع البسطين', 'يساوي'), C.yellow, 20);
  b.sound(at('نجمع البسطين', 'يساوي') + 0.8, 'shimmer', 0.3);
  return b;
}

function ex4(P: boolean, W: number, H: number) {
  const q = 'التمرين الرابع';
  const b = board('ex4', 'التمرين 4', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 4', at(q)) - 20, P ? 60 : 40);
  const s1 = c.text('f الدالة المعرفة على ℝ بـ :', at(q, 'الدالة'), { color: C.blue });
  const s2 = c.math('f(x) = \\frac{e^{x} - 1}{e^{x} + 1}', at(q, 'R') - 0.2, { size: P ? 60 : 60 });
  const s3 = c.text('بيّن أن f دالة فردية.', at(q, 'بين'), { color: C.blue });
  frame(b, [s1, s2, s3], at(q, 'فردية') + 0.6);
  c.skip(20);
  c.text('ℝ متناظرة بالنسبة إلى 0', at('مجموعة التعريف', 'متناظرة'), { color: C.pink });
  c.math('f(-x) = \\frac{e^{-x} - 1}{e^{-x} + 1} = \\frac{(e^{-x} - 1)e^{x}}{(e^{-x} + 1)e^{x}} = \\frac{1 - e^{x}}{1 + e^{x}}', at('نضرب البسط والمقام في e أس x، فنجد'), { size: P ? 46 : 50 });
  const r = c.math('f(-x) = -f(x)', at('وهذا يساوي ناقص', 'ناقص'), { color: C.yellow, size: P ? 62 : 60 });
  frame(b, [r], at('وهذا يساوي ناقص', 'فردية'), C.yellow, 20);
  c.text('f فردية، و (Cf) متناظر بالنسبة إلى المبدأ O', at('وهذا يساوي ناقص', 'ومنحناها'), { color: C.green, size: P ? 40 : 40 });
  b.stroke(check([r.x - 60, r.y + r.h / 2], 46), { at: at('وهذا يساوي ناقص', 'فردية') + 0.6, color: C.green, width: 6 });
  return b;
}

function ex5(P: boolean, W: number, H: number) {
  const q = 'التمرين الخامس';
  const b = board('ex5', 'التمرين 5', q, P, W, H);
  const c = column(b, heading(b, 'التمرين 5', at(q)) - 20);
  const s1 = c.text('بيّن أنه من أجل كل عددين حقيقيين a و b :', at(q, 'بين'), { color: C.blue });
  const s2 = c.math('e^{a} + e^{b} \\ge 2e^{\\frac{a+b}{2}}', at(q, 'المتراجحة'), { size: P ? 64 : 64 });
  frame(b, [s1, s2], at(q, 'التالية') + 0.4);
  c.skip(20);
  c.math('\\left(e^{\\frac{a}{2}} - e^{\\frac{b}{2}}\\right)^{2} \\ge 0', at('ننطلق من مربع', 'أس'), { color: C.blue, size: P ? 56 : 56 });
  c.math('\\left(e^{\\frac{a}{2}}\\right)^{2} = e^{a} \\quad ; \\quad \\left(e^{\\frac{b}{2}}\\right)^{2} = e^{b}', at('ننشر', 'مربع'), { size: P ? 46 : 50 });
  c.math('2 \\times e^{\\frac{a}{2}} \\times e^{\\frac{b}{2}} = 2e^{\\frac{a+b}{2}}', at('والجداء المضاعف', 'يساوي'), { size: P ? 48 : 50 });
  const r = c.math('e^{a} + e^{b} - 2e^{\\frac{a+b}{2}} \\ge 0', at('إذن e أس a زائد', 'أكبر') - 0.4, { color: C.yellow, size: P ? 58 : 58 });
  frame(b, [r], at('إذن e أس a زائد', 'المطلوب'), C.yellow, 20);
  b.sound(at('إذن e أس a زائد', 'المطلوب') + 0.6, 'shimmer', 0.3);
  return b;
}

function outro(P: boolean, W: number, H: number) {
  const q = 'الخلاصة: اجمع الأسس';
  const b = board('outro', 'خلاصة', q, P, W, H);
  const c = column(b, heading(b, 'خلاصة', at(q)) - 10, P ? 60 : 44);
  c.text('اجمع الأسس : eᵃ × eᵇ = eᵃ⁺ᵇ', at(q, 'اجمع'), { color: C.yellow });
  c.text('اضرب في eˣ للتخلص من e⁻ˣ', at(q, 'واضرب'), { color: C.pink });
  c.text('فكّر في المربعات : ( … )² ≥ 0', at(q, 'وفكر'), { color: C.blue });
  c.skip(30);
  c.text('الحلقة القادمة : حل المعادلات والمتراجحات', at('في الحلقة القادمة', 'القادمة'), { color: C.white, size: P ? 42 : 42 });
  const nm = c.text('الأستاذ سوايسية هشام', at('كنتم مع الأستاذ', 'الأستاذ'), { color: C.yellow, size: P ? 64 : 60 });
  b.stroke([seg([nm.x + nm.w + 20, nm.y + nm.h + 4], [nm.x - 20, nm.y + nm.h + 10])], { at: at('كنتم مع الأستاذ', 'الأستاذ') + 1.0, color: C.yellow, width: 5 });
  b.sound(at('كنتم مع الأستاذ', 'بالتوفيق') + 0.5, 'swell', 0.3, 3);
  return b;
}

const ALL = [intro, ex1, ex2, ex3, ex4, ex5, outro];

export function buildEx1(P: boolean, W: number, H: number): Board[] {
  const gap = W * 0.3;
  const bs = ALL.map((f) => f(P, W, H));
  return bs.map((b, i) => b.build(-i * (W + gap), 0, i + 1 < bs.length ? bs[i + 1].from - 0.8 : Infinity));
}
