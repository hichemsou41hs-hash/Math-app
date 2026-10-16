// All boards, in order. Each board is a function of the orientation (P = portrait) and the board size.
// Times always come from the script (words.json) through at().
import { Board } from '../lib/engine';
import { intro, history, numberE, definition } from './ch1';
import { props } from './ch2';
import { deriv, limits, curve } from './ch3';
import { famous, indet1, indet2 } from './ch4';
import { equations, equations2, sign1, sign2, outro } from './ch5';

const ALL = [intro, history, numberE, definition, props, deriv, limits, curve, famous, indet1, indet2, equations, equations2, sign1, sign2, outro];

export function buildBoards(P: boolean, W: number, H: number): Board[] {
  const gap = W * 0.3;
  const bs = ALL.map((f) => f(P, W, H));
  return bs.map((b, i) => b.build(-i * (W + gap), 0, i + 1 < bs.length ? bs[i + 1].from - 0.8 : Infinity));
}
