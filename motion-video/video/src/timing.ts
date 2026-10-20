// When every word is said: src/data/words.json, written by the skill's align.py (from the voiceover, or
// from a reading speed when there is none). Scenes never hard-code seconds: they ask for a word.
//
//   const l = line('يصبح الأمر');          // the first line containing these words
//   const w = word(l, 'جنونيا');           // a word of that line (diacritics and alef forms don't matter)
//   const f = toFrame(w.start);            // its first frame
//   const start = cutBefore('يصبح الأمر'); // where a scene that opens on this line should start (s)
//   const k = prog(t, w.start, w.start + 0.45, Easing.out(Easing.cubic)); // 0 -> 1 as the word is said
import data from './data/words.json';
import keys from './data/keys.json';
import { Easing, interpolate } from 'remotion';
import { VIDEO } from './config';

export interface Word { w: string; start: number; end: number; conf?: number }
export interface Line { text: string; start: number; end: number; words: Word[]; key?: string }
export interface Timing { source?: string; audio: string | null; duration: number; lines: Line[] }

/** The timing in use: the lesson's by default; an episode switches to its own with setTiming(). */
export let TIMING = data as Timing;
let KEYS = keys as string[];
export function setTiming(t: Timing, k: string[] = []) {
  TIMING = t;
  KEYS = k;
}
export const LESSON_TIMING = data as Timing;
export const LESSON_KEYS = keys as string[];
export const FPS = VIDEO.fps;

/** Seconds -> frame. */
export const toFrame = (s: number) => Math.round(s * FPS);
/** Frame -> seconds. */
export const toSec = (f: number) => f / FPS;

/** Compare Arabic and Latin text loosely: no diacritics, tatweel or punctuation; one alef, ya and ha. */
export function norm(s: string) {
  return s
    .normalize('NFKC')
    .replace(/[ً-ٰٟـ]/g, '')
    .replace(/[أإآٱ]/g, 'ا')
    .replace(/ى/g, 'ي')
    .replace(/ة/g, 'ه')
    .replace(/[^\p{L}\p{N}\s]/gu, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();
}

/** The first line whose text contains `query`. Queries may also be written against the first draft of the
 *  script (data/keys.json, same lines in the same order): they then find the same line of the narration. */
export function line(query: string): Line {
  const q = norm(query);
  const k = KEYS.findIndex((x) => norm(x).includes(q));
  if (k >= 0 && TIMING.lines[k]) return Object.assign({}, TIMING.lines[k], { key: KEYS[k] });
  const l = TIMING.lines.find((x) => norm(x.text).includes(q));
  if (!l) throw new Error(`No line contains «${query}». Lines: ${TIMING.lines.map((x) => x.text).join(' | ')}`);
  return l;
}

/** A word of a line (or of the line containing `inLine`); `nth` picks a later repeat. A word that is only in
 *  the first draft of the line is placed at the same relative position in the narrated line. */
export function word(inLine: Line | string, query: string, nth = 0): Word {
  const l = typeof inLine === 'string' ? line(inLine) : inLine;
  const q = norm(query);
  const find = (ws: string[]) => ws.map((w, i) => [norm(w), i] as const).filter(([w]) => w === q || w.includes(q)).map(([, i]) => i);
  const hits = find(l.words.map((w) => w.w));
  const keyWords = l.key ? l.key.split(/\s+/) : [];
  const keyHits = find(keyWords);
  if (hits[nth] !== undefined && (!l.key || hits.length >= keyHits.length)) return l.words[hits[nth]];
  if (keyHits[nth] !== undefined) {
    const f = keyHits[nth] / keyWords.length;
    const t = l.start + (l.end - l.start) * f;
    return { w: keyWords[keyHits[nth]], start: t, end: t + (l.end - l.start) / keyWords.length };
  }
  if (hits[nth] !== undefined) return l.words[hits[nth]];
  throw new Error(`No word «${query}» in «${l.text}»`);
}

/** Where a scene that opens on the line containing `query` starts: just before its first word. */
export function cutBefore(query: string, lead = 0.2) {
  return Math.max(0, line(query).start - lead);
}

/** 0 before a, 1 after b, eased in between: the building block of every move. */
export function prog(t: number, a: number, b: number, easing: (x: number) => number = Easing.linear) {
  return interpolate(t, [a, b], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing });
}

/** The whole video's length in frames. */
export const DURATION_FRAMES = Math.max(1, Math.ceil((TIMING.duration + VIDEO.tail) * FPS));
export const durationFrames = (t: Timing) => Math.max(1, Math.ceil((t.duration + VIDEO.tail) * FPS));
