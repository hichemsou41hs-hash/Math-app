import { cutBefore, line, word } from '../timing';
import { Builder } from '../lib/engine';
import { seg } from '../lib/geom';

/** When a line starts, or when a word of it is said (nth repeat). */
export function at(q: string, w?: string, nth = 0): number {
  return w ? word(line(q), w, nth).start : line(q).start;
}
/** When a word ends. */
export function end(q: string, w?: string, nth = 0): number {
  return w ? word(line(q), w, nth).end : line(q).end;
}

export function board(id: string, chapter: string, firstLine: string, P: boolean, W: number, H: number) {
  return new Builder(id, chapter, id === 'intro' ? 0 : cutBefore(firstLine, 0.2), P, W, H);
}

/** A chapter title: yellow chalk heading and its underline. Returns the y under it. */
export function heading(b: Builder, str: string, t: number, y?: number): number {
  const size = (b.P ? 74 : 78) * (b.P ? 1 : 1);
  const yy = y ?? (b.P ? 190 : 140);
  const box = b.text(str, { x: b.W / 2, y: yy, size, color: '#F6E07A', at: t });
  const pad = 30;
  b.stroke([seg([box.x + box.w + pad, yy + size * 0.42], [box.x - pad, yy + size * 0.5])], { at: t + 0.1, color: '#F6E07A', width: 5 });
  return yy + size * 0.5 + (b.P ? 90 : 70);
}

