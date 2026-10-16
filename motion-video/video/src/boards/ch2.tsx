// Chapter 2: algebraic properties.
import { C } from '../lib/engine';
import { rect } from '../lib/geom';
import { at, board, heading } from './util';

export function props(P: boolean, W: number, H: number) {
  const b = board('props', 'الخواص الجبرية', 'نشوفو الخواص الجبرية', P, W, H);
  const y0 = heading(b, 'الخواص الجبرية', at('نشوفو الخواص الجبرية'));
  b.text('من أجل كل عددين حقيقيين a و b ، ومن أجل كل عدد صحيح n :', { x: W / 2, y: y0, size: P ? 40 : 42, color: C.white, at: at('نشوفو الخواص الجبرية', 'كل'), maxW: W - 140 });

  const S = P ? 64 : 62;
  const rows: [string, number, string][] = [
    ['e^{a+b} = e^{a} \\times e^{b}', at('a زايد b', 'يساوي'), C.yellow],
    ['e^{-a} = \\frac{1}{e^{a}}', at('أس ناقص a', 'يساوي'), C.white],
    ['e^{a-b} = \\frac{e^{a}}{e^{b}}', at('a ناقص b', 'يساوي'), C.white],
    ['\\left(e^{a}\\right)^{n} = e^{na}', at('يساوي e أس n ضرب a', 'يساوي'), C.white],
    ['e^{2x} \\times e^{-x} = e^{2x-x} = e^{x}', at('مثال: e أس اثنين', 'يساوي'), C.blue],
    ['e^{a} = e^{b} \\iff a = b', at('وزيد خاصيتين', 'معناها'), C.pink],
    ['e^{a} < e^{b} \\iff a < b', at('أصغر من e أس b', 'معناها'), C.pink],
  ];
  const boxes = rows.map(([src, t, color], i) => {
    let x: number;
    let y: number;
    if (P) {
      x = W / 2;
      y = y0 + 200 + i * 185;
    } else {
      const right = i < 4;
      x = right ? W * 0.73 : W * 0.27;
      y = y0 + 150 + (right ? i : i - 4) * 165;
    }
    return b.math(src, { x, y, size: i === 4 ? S * 0.85 : S, color, at: t, maxW: P ? W - 140 : W * 0.44 });
  });
  // small reading aids
  const note = (i: number, s: string, t: number) =>
    P
      ? b.text(s, { x: boxes[i].x + boxes[i].w / 2, y: boxes[i].y + boxes[i].h + 42, size: 34, color: C.yellow, at: t })
      : b.text(s, { x: boxes[i].x - 40, y: boxes[i].y + boxes[i].h * 0.7, size: 36, color: C.yellow, at: t, align: 'r' });
  note(0, 'المجموع ← جداء', at('a زايد b', 'المجموع'));
  note(2, 'الفرق ← قسمة', at('a ناقص b', 'الفرق'));
  b.text('مثال :', { x: boxes[4].x + boxes[4].w / 2, y: boxes[4].y - 34, size: 38, color: C.blue, at: at('مثال: e أس اثنين') - 0.05 });
  const eq = boxes[5];
  const lt = boxes[6];
  b.stroke([rect(Math.min(eq.x, lt.x) - 30, eq.y - 25, Math.max(eq.w, lt.w) + 60, lt.y + lt.h - eq.y + 50)], { at: at('أصغر من e أس b', 'أصغر', 1), color: C.pink, width: 4 });
  b.sound(at('أصغر من e أس b', 'أصغر', 1) + 0.5, 'shimmer', 0.25);
  return b;
}
