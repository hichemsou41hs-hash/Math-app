// Fonts (STYLE.md section 3), shipped in public/fonts so renders never depend on the network:
// Aref Ruqaa, Amiri, Kalam (SIL OFL) and DejaVu Sans for symbols such as ∞ ℝ ⟺.
// FontGate renders nothing until every font is ready, so text can be measured during render.
import React, { useEffect, useState } from 'react';
import { continueRender, delayRender, staticFile } from 'remotion';

const FACES: [string, string, string][] = [
  ['ChalkRuqaa', 'ArefRuqaa-Regular.ttf', '400'],
  ['ChalkRuqaa', 'ArefRuqaa-Bold.ttf', '700'],
  ['ChalkNaskh', 'Amiri-Regular.ttf', '400'],
  ['ChalkNaskh', 'Amiri-Bold.ttf', '700'],
  ['ChalkHand', 'Kalam-Regular.ttf', '400'],
  ['ChalkHand', 'Kalam-Bold.ttf', '700'],
  ['ChalkSymbols', 'DejaVuSans.ttf', '400'],
];

/** Arabic handwriting (titles, sentences). */
export const RUQAA = `'ChalkRuqaa', 'ChalkNaskh', 'ChalkSymbols'`;
/** Arabic naskh (small labels inside formulas). */
export const NASKH = `'ChalkNaskh', 'ChalkSymbols'`;
/** Latin chalk handwriting for formulas, with symbols from DejaVu. */
export const HAND = `'ChalkHand', 'ChalkSymbols'`;
export const SYM = `'ChalkSymbols'`;

let loading: Promise<unknown> | null = null;
function loadAll() {
  if (!loading)
    loading = Promise.all(
      FACES.map(([family, file, weight]) =>
        new FontFace(family, `url(${staticFile('fonts/' + file)})`, { weight }).load().then((f) => document.fonts.add(f)),
      ),
    ).then(() => document.fonts.ready);
  return loading;
}

export const FontGate: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [handle] = useState(() => delayRender('fonts'));
  const [ready, setReady] = useState(false);
  useEffect(() => {
    loadAll().then(() => {
      setReady(true);
      continueRender(handle);
    });
  }, [handle]);
  return ready ? <>{children}</> : null;
};

let ctx: CanvasRenderingContext2D | null = null;
const cache = new Map<string, number>();
/** Width in px of `s` drawn in `font` (a CSS font shorthand). */
export function measure(s: string, font: string): number {
  const key = font + '|' + s;
  const hit = cache.get(key);
  if (hit !== undefined) return hit;
  if (!ctx) ctx = document.createElement('canvas').getContext('2d');
  ctx!.font = font;
  ctx!.direction = /[؀-ۿ]/.test(s) ? 'rtl' : 'ltr';
  const w = ctx!.measureText(s).width;
  cache.set(key, w);
  return w;
}
