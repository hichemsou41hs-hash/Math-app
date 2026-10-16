// Chapter 1: introduction, where e comes from (Bernoulli's interest), the definition.
import { C } from '../lib/engine';
import { rect, seg, check } from '../lib/geom';
import { at, board, heading } from './util';

export function intro(P: boolean, W: number, H: number) {
  const b = board('intro', 'مقدمة', 'السلام عليكم', P, W, H);
  const cx = W / 2;
  const t1 = at('السلام عليكم', 'معاكم');
  b.text('الأستاذ سوايسية هشام', { x: cx, y: P ? 330 : 200, size: P ? 60 : 58, color: C.white, at: t1 });
  const tt = at('اليوم نشرحو', 'الدالة');
  const title = b.text('الدالة الأسية النيبيرية', { x: cx, y: P ? 520 : 360, size: P ? 104 : 118, color: C.yellow, at: tt, maxW: W - 120 });
  b.stroke([seg([title.x + title.w + 30, title.y + title.h + 6], [title.x - 30, title.y + title.h + 14])], { at: tt + 0.2, color: C.yellow, width: 6 });
  b.math('x \\mapsto e^{x}', { x: cx, y: P ? 760 : 560, size: P ? 96 : 92, color: C.pink, at: at('اليوم نشرحو', 'البكالوريا') });
  b.sound(tt + 1.6, 'shimmer', 0.3);

  // the plan of the lesson, ticked off as it is announced
  const topics: [string, string, string][] = [
    ['نشأة العدد e', 'نبداو بالقصة', 'بالقصة'],
    ['التعريف', 'نبداو بالقصة', 'التعريف'],
    ['الخواص', 'نبداو بالقصة', 'الخواص'],
    ['النهايات', 'نبداو بالقصة', 'النهايات'],
    ['المشتقة', 'نبداو بالقصة', 'المشتقة'],
    ['المنحنى', 'نبداو بالقصة', 'والمنحنى'],
    ['النهايات الشهيرة', 'ومن بعد النهايات الشهيرة', 'الشهيرة'],
    ['المعادلات', 'ومن بعد النهايات الشهيرة', 'المعادلات'],
    ['دراسة الإشارة', 'ومن بعد النهايات الشهيرة', 'الإشارة'],
  ];
  topics.forEach(([s, q, w], i) => {
    const col = P ? i % 2 : i % 3;
    const rowI = P ? Math.floor(i / 2) : Math.floor(i / 3);
    const x = P ? W - 140 - col * 470 : W - 330 - col * 560;
    const y = P ? 960 + rowI * 115 : 720 + rowI * 92;
    b.text(`• ${s}`, { x, y, size: P ? 48 : 44, color: i % 3 === 0 ? C.blue : i % 3 === 1 ? C.white : C.pink, at: at(q, w), align: 'r', maxW: 420 });
  });

  return b;
}

export function history(P: boolean, W: number, H: number) {
  const b = board('history', 'نشأة العدد e', 'في عام ألف', P, W, H);
  const y0 = heading(b, 'نشأة العدد e', at('في عام ألف'));
  b.text('جاكوب برنولي - 1683', { x: W / 2, y: y0 + 10, size: P ? 50 : 46, color: C.white, at: at('في عام ألف', 'جاكوب') });
  // the bank: 1 dinar at 100% a year
  const yb = y0 + (P ? 140 : 110);
  b.text('بنك يعطي فائدة 100% في السنة، نضع 1 دج', { x: W / 2, y: yb, size: P ? 44 : 42, color: C.pink, at: at('تصور بنك'), maxW: W - 160 });

  // the table: how often the interest is paid -> money after one year
  const tw = P ? 920 : 1180;
  const tx = (W - tw) / 2;
  const ty = yb + (P ? 110 : 80);
  const rh = P ? 118 : 92;
  const colX = tx + tw * 0.56; // separator
  const rows: [string, string, number, string?][] = [
    ['مرة في السنة', '1 + 1 = 2', at('تصور بنك', 'جوج')],
    ['كل 6 أشهر', '\\left(1+\\frac{1}{2}\\right)^{2} = 2,25', at('وإذا البنك', 'يولي'), 'وإذا البنك'],
    ['كل شهر', '\\left(1+\\frac{1}{12}\\right)^{12} \\approx 2,613', at('كل شهر', 'اثنين')],
    ['كل يوم', '\\left(1+\\frac{1}{365}\\right)^{365} \\approx 2,7146', at('كل شهر', 'يوم')],
  ];
  const tStart = at('تصور بنك', 'دينار');
  b.stroke([seg([tx + tw, ty], [tx, ty]), seg([colX, ty - rh * 0.1], [colX, ty + rh * rows.length])], { at: tStart, color: C.white, width: 4 });
  rows.forEach(([lab, f, t], i) => {
    const y = ty + rh * i + rh * 0.62;
    b.text(lab, { x: tx + tw - 20, y: y - 4, size: P ? 42 : 40, color: C.blue, at: t - 0.6, align: 'r', maxW: tw - (colX - tx) - 40 });
    b.math(f, { x: tx + 10, y, size: P ? 46 : 46, color: i === 3 ? C.yellow : C.white, at: t, align: 'l', maxW: colX - tx - 30 });
  });
  b.focus(at('كل شهر'), { x: tx, y: ty, w: tw, h: rh * 4 }, 1.25, 1.2);
  b.home(at('كل شهر', 'سبعمية') + 0.3);
  return b;
}

export function numberE(P: boolean, W: number, H: number) {
  const b = board('e', 'نشأة العدد e', 'كلما نكبرو', P, W, H);
  const cx = W / 2;
  const y0 = P ? 300 : 210;
  b.math('\\left(1+\\frac{1}{n}\\right)^{n}', { x: cx, y: y0, size: P ? 92 : 96, color: C.white, at: at('كلما نكبرو', 'العبارة') });
  b.math('n \\to +\\infty', { x: cx, y: y0 + (P ? 190 : 170), size: P ? 52 : 52, color: C.blue, at: at('كلما نكبرو', 'تقرب') });
  b.stroke([seg([cx, y0 + (P ? 220 : 195)], [cx, y0 + (P ? 330 : 280)]), seg([cx - 16, y0 + (P ? 308 : 260)], [cx, y0 + (P ? 332 : 282)]), seg([cx, y0 + (P ? 332 : 282)], [cx + 16, y0 + (P ? 308 : 260)])], { at: at('كلما نكبرو', 'ثابت'), color: C.blue, width: 5 });
  const ye = y0 + (P ? 470 : 400);
  const eb = b.math('e \\approx 2,718281828...', { x: cx, y: ye, size: P ? 92 : 104, color: C.yellow, at: at('هذا العدد هو e', 'تقريبا') });
  b.stroke([rect(eb.x - 36, eb.y - 26, eb.w + 72, eb.h + 52)], { at: at('هذا العدد هو e', 'غير'), color: C.yellow, width: 5 });
  b.sound(at('هذا العدد هو e', 'غير'), 'shimmer', 0.35);
  b.text('عدد غير ناطق', { x: cx, y: ye + (P ? 150 : 130), size: P ? 50 : 50, color: C.pink, at: at('هذا العدد هو e', 'ناطق') });
  const yn = ye + (P ? 300 : 245);
  b.text('الرمز e : نسبة إلى أويلر (Euler)', { x: cx, y: yn, size: P ? 46 : 44, color: C.white, at: at('أويلر هو اللي'), maxW: W - 160 });
  b.text('نيبيرية : نسبة إلى جون نابير (Napier)', { x: cx, y: yn + (P ? 100 : 80), size: P ? 46 : 44, color: C.white, at: at('أويلر هو اللي', 'نيبيري'), maxW: W - 160 });
  b.focus(at('هذا العدد هو e'), eb, 1.7, 1.0);
  b.home(at('أويلر هو اللي'));
  return b;
}

export function definition(P: boolean, W: number, H: number) {
  const b = board('def', 'التعريف', 'ضرك نجيو للتعريف', P, W, H);
  let y = heading(b, 'التعريف', at('ضرك نجيو للتعريف'));
  const cx = W / 2;
  const s = P ? 0.92 : 1;
  const l1 = b.text('توجد دالة وحيدة f قابلة للاشتقاق على ℝ حيث:', { x: cx, y: y + 10, size: 46 * s, color: C.white, at: at('ضرك نجيو للتعريف', 'كاين'), maxW: W - 160 });
  y += P ? 150 : 120;
  const f1 = b.math("f' = f \\quad \\text{و} \\quad f(0) = 1", { x: cx, y, size: 70 * s, color: C.yellow, at: at('المشتقة نتاعها', 'برايم') });
  b.stroke([rect(Math.min(l1.x, f1.x) - 40, l1.y - 30, Math.max(l1.w, f1.w) + 80, f1.y + f1.h - l1.y + 60)], { at: at('المشتقة نتاعها', 'واحد'), color: C.white, width: 4 });
  y += P ? 190 : 150;
  b.math('\\exp(x) = e^{x}', { x: cx, y, size: 80 * s, color: C.pink, at: at('هاذي هي الدالة', 'نكتبو') });
  b.text('تسمى الدالة الأسية النيبيرية', { x: cx, y: y + (P ? 100 : 85), size: 38 * s, color: C.white, at: at('هاذي هي الدالة', 'الأسية') - 0.2 });
  y += P ? 260 : 205;
  if (P) {
    b.math('e^{0} = 1', { x: cx, y, size: 68 * s, color: C.blue, at: at('إذن e أس صفر', 'يساوي') });
    b.math('e^{1} = e', { x: cx, y: y + 110, size: 68 * s, color: C.blue, at: at('إذن e أس صفر', 'يساوي', 1) });
    y += 110;
  } else {
    b.math('e^{0} = 1', { x: cx + 230, y, size: 68, color: C.blue, at: at('إذن e أس صفر', 'يساوي') });
    b.math('e^{1} = e', { x: cx - 230, y, size: 68, color: C.blue, at: at('إذن e أس صفر', 'يساوي', 1) });
  }
  y += P ? 190 : 150;
  b.text('من أجل كل عدد حقيقي x :', { x: cx, y: y - (P ? 50 : 40), size: 42 * s, color: C.white, at: at('وحاجة مهمة بزاف', 'كل') });
  const pos = b.math('e^{x} > 0', { x: cx, y: y + (P ? 70 : 50), size: 88 * s, color: C.yellow, at: at('وحاجة مهمة بزاف', 'موجب') });
  b.stroke(check([pos.x - 70, pos.y + pos.h / 2], 56), { at: at('وحاجة مهمة بزاف', 'عمرو'), color: C.green, width: 7 });
  b.sound(at('وحاجة مهمة بزاف', 'عمرو') + 0.3, 'shimmer', 0.3);
  b.focus(at('وحاجة مهمة بزاف', 'موجب'), pos, 2.6, 0.9);
  b.home(at('وحاجة مهمة بزاف', 'سالب') + 0.4);
  return b;
}
