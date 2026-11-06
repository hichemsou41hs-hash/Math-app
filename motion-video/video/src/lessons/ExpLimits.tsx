// «نهايات الدالة الأسية في البكالوريا 2020–2026» — 16:9 lesson video.
// Content: documents/exponentielle/bac_exp_3as.tex (solutions), every limit checked with sympy.
// Timing comes from data/explim.json (voice lines); a step appears at the start of its voice line.
import React from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import { AbsoluteFill, Easing, Html5Audio, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import data from '../data/explim.json';
import { DISPLAY, FontGate, LATIN, NASKH } from '../lib/fonts';

type W = { w: string; start: number; end: number };
type Line = { text: string; start: number; end: number; words: W[] };
const D = data as unknown as { duration: number; lines: Line[]; audio?: number[] };
const LINES = D.lines;
const AUDIO = D.audio ?? [];
export const EXPLIM_SECONDS = Math.ceil(D.duration + 1);

const C = { bg0: '#071029', bg1: '#13275A', gold: '#F5B54A', goldL: '#FFE29A', cream: '#FFF8EC', ink: '#13203F', red: '#E5484D', green: '#22A36B', blue: '#3B7BFF', text: '#F4F1EA' };
const CL = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const EASE = Easing.bezier(0.45, 0, 0.2, 1);
const ramp = (t: number, a: number, b: number, from = 0, to = 1) => interpolate(t, [a, b], [from, to], { ...CL, easing: EASE });
const pop = (t: number, a: number, d = 0.45) => interpolate(t, [a, a + d], [0, 1], { ...CL, easing: Easing.out(Easing.back(1.6)) });

const M: React.FC<{ tex: string; size?: number; color?: string }> = ({ tex, size = 40, color }) => (
  <span dir="ltr" style={{ fontSize: size, color, display: 'inline-block', unicodeBidi: 'isolate', whiteSpace: 'nowrap' }}
    dangerouslySetInnerHTML={{ __html: katex.renderToString(tex, { throwOnError: false, displayMode: false }) }} />
);
const start = (i: number) => LINES[i]?.start ?? 0;

// ---------- data ----------
type Kind = 'step' | 'wrong' | 'result' | 'note';
type Step = { line: number; tex?: string; text?: string; kind?: Kind; at?: number };
type Asym = { h?: number; v?: number; a?: number; b?: number };
type Graph = { f: (x: number) => number; xr: [number, number]; yr: [number, number]; end?: 'p' | 'm' | 'z'; asym?: Asym[] };
type Item = { from: number; to: number; bac: string; f: string; steps: Step[]; g: Graph };

const e = Math.exp;
const fA = (x: number) => (x - 1) * (e(2 * x) - 1);
const fB = (x: number) => -1 + (2 * e(x)) / (e(x) - x);
const fC = (x: number) => 1 + (5 - 4 * e(x)) / (e(2 * x) - 1);
const fF = (x: number) => (x * x * e(x)) / (e(x) + 1);
const fG = (x: number) => e(2 * x) - e(x) - x - 2;
const fH = (x: number) => -2 * x + 3 - x * e(-x + 1);
const fJ = (x: number) => 1 + (1 - x - x * x) * e(-x);
const fM = (x: number) => x - (x + 1) * e(-x - 1);

const LIM = (a: string, v: string, f = 'f(x)') => `\\lim\\limits_{x\\to ${a}} ${f} = ${v}`;
const ITEMS: Item[] = [
  { from: 6, to: 8, bac: 'بكالوريا 2023 — علوم تجريبية', f: 'f(x)=(x-1)\\left(e^{2x}-1\\right)', g: { f: fA, xr: [-3, 1.7], yr: [-1.5, 6], end: 'p' }, steps: [
    { line: 7, tex: '\\lim\\limits_{x\\to+\\infty}(x-1)=+\\infty' },
    { line: 7, at: 0.3, tex: '\\lim\\limits_{x\\to+\\infty}\\left(e^{2x}-1\\right)=+\\infty' },
    { line: 7, at: 0.6, kind: 'result', tex: LIM('+\\infty', '+\\infty') },
    { line: 8, tex: '\\lim\\limits_{x\\to-\\infty}(x-1)=-\\infty' },
    { line: 8, at: 0.3, tex: '\\lim\\limits_{x\\to-\\infty}\\left(e^{2x}-1\\right)=-1' },
    { line: 8, at: 0.65, kind: 'result', tex: LIM('-\\infty', '+\\infty') }] },
  { from: 9, to: 10, bac: 'بكالوريا 2020 — علوم تجريبية', f: 'f(x)=-1+\\dfrac{2e^{x}}{e^{x}-x}', g: { f: fB, xr: [-5, 3], yr: [-2, 3], end: 'm', asym: [{ h: -1 }] }, steps: [
    { line: 10, tex: '\\lim\\limits_{x\\to-\\infty}2e^{x}=0 \\quad;\\quad \\lim\\limits_{x\\to-\\infty}\\left(e^{x}-x\\right)=+\\infty' },
    { line: 10, at: 0.6, kind: 'result', tex: LIM('-\\infty', '-1') }] },
  { from: 12, to: 15, bac: 'بكالوريا 2026 — علوم تجريبية', f: 'f(x)=1+\\dfrac{5-4e^{x}}{e^{2x}-1}', g: { f: fC, xr: [-3, 3], yr: [-6, 6], end: 'z', asym: [{ v: 0 }] }, steps: [
    { line: 13, tex: '\\lim\\limits_{x\\to0}\\left(5-4e^{x}\\right)=1 \\quad;\\quad \\lim\\limits_{x\\to0}\\left(e^{2x}-1\\right)=0' },
    { line: 14, tex: 'x>0 \\Rightarrow e^{2x}-1>0 \\quad;\\quad x<0 \\Rightarrow e^{2x}-1<0' },
    { line: 14, at: 0.5, kind: 'result', tex: '\\lim\\limits_{x\\to0^{+}}f(x)=+\\infty' },
    { line: 14, at: 0.75, kind: 'result', tex: '\\lim\\limits_{x\\to0^{-}}f(x)=-\\infty' },
    { line: 15, kind: 'note', tex: 'x=0', text: 'مقارب عمودي' }] },
  { from: 17, to: 18, bac: 'بكالوريا 2026 — علوم تجريبية', f: 'f(x)=1+\\dfrac{5-4e^{x}}{e^{2x}-1}', g: { f: fC, xr: [-1, 4], yr: [-2, 4], end: 'p', asym: [{ h: 1 }] }, steps: [
    { line: 17, at: 0.4, tex: '\\dfrac{5-4e^{x}}{e^{2x}-1}=\\dfrac{5e^{-2x}-4e^{-x}}{1-e^{-2x}}' },
    { line: 18, tex: '\\lim\\limits_{x\\to+\\infty}e^{-x}=\\lim\\limits_{x\\to+\\infty}e^{-2x}=0' },
    { line: 18, at: 0.55, kind: 'result', tex: LIM('+\\infty', '1') }] },
  { from: 19, to: 20, bac: 'بكالوريا 2020 — علوم تجريبية', f: 'f(x)=-1+\\dfrac{2e^{x}}{e^{x}-x}', g: { f: fB, xr: [-2, 6], yr: [-2, 3], end: 'p', asym: [{ h: 1 }] }, steps: [
    { line: 19, at: 0.4, tex: 'e^{x}-x=e^{x}\\left(1-xe^{-x}\\right)' },
    { line: 20, tex: '\\dfrac{2e^{x}}{e^{x}-x}=\\dfrac{2}{1-xe^{-x}} \\quad;\\quad \\lim\\limits_{x\\to+\\infty}xe^{-x}=0' },
    { line: 20, at: 0.6, kind: 'result', tex: LIM('+\\infty', '1') }] },
  { from: 21, to: 21, bac: 'بكالوريا 2026 — رياضيات', f: 'f(x)=\\dfrac{x^{2}e^{x}}{e^{x}+1}', g: { f: fF, xr: [-4, 3], yr: [-0.5, 6], end: 'p' }, steps: [
    { line: 21, at: 0.25, tex: 'f(x)=\\dfrac{x^{2}}{1+e^{-x}}' },
    { line: 21, at: 0.7, kind: 'result', tex: LIM('+\\infty', '+\\infty') }] },
  { from: 23, to: 24, bac: 'بكالوريا 2025 — علوم تجريبية', f: 'f(x)=e^{2x}-e^{x}-x-2', g: { f: fG, xr: [-4, 1.6], yr: [-3, 6], end: 'p' }, steps: [
    { line: 23, at: 0.7, kind: 'note', tex: '\\infty-\\infty', text: 'حالة عدم تعيين' },
    { line: 24, tex: 'f(x)=e^{2x}\\left(1-e^{-x}-xe^{-2x}-2e^{-2x}\\right)' },
    { line: 24, at: 0.6, kind: 'result', tex: LIM('+\\infty', '+\\infty') }] },
  { from: 25, to: 27, bac: 'بكالوريا 2024 — علوم تجريبية', f: 'f(x)=-2x+3-xe^{-x+1}', g: { f: fH, xr: [-2.2, 4], yr: [-6, 6], end: 'm' }, steps: [
    { line: 25, at: 0.6, tex: '-2x+3\\to+\\infty \\quad;\\quad -xe^{-x+1}\\to-\\infty' },
    { line: 26, kind: 'wrong', tex: '(+\\infty)-(+\\infty)=0' },
    { line: 27, tex: 'f(x)=x\\left(-2-e^{-x+1}\\right)+3' },
    { line: 27, at: 0.6, kind: 'result', tex: LIM('-\\infty', '+\\infty') }] },
  { from: 29, to: 29, bac: 'بكالوريا 2024 — علوم تجريبية', f: 'f(x)=-2x+3-xe^{-x+1}', g: { f: fH, xr: [-1, 6], yr: [-8, 4], end: 'p', asym: [{ a: -2, b: 3 }] }, steps: [
    { line: 29, at: 0.15, tex: 'xe^{-x+1}=e\\cdot xe^{-x}\\to0' },
    { line: 29, at: 0.6, kind: 'result', tex: LIM('+\\infty', '-\\infty') }] },
  { from: 30, to: 31, bac: 'بكالوريا 2026 — تقني رياضي', f: 'f(x)=1+\\left(1-x-x^{2}\\right)e^{-x}', g: { f: fJ, xr: [-2, 8], yr: [-3, 2.5], end: 'p', asym: [{ h: 1 }] }, steps: [
    { line: 30, at: 0.75, kind: 'note', tex: '0\\times\\infty', text: 'حالة عدم تعيين' },
    { line: 31, tex: 'f(x)=1+e^{-x}-\\dfrac{x}{e^{x}}-\\dfrac{x^{2}}{e^{x}}' },
    { line: 31, at: 0.55, kind: 'result', tex: LIM('+\\infty', '1') }] },
  { from: 32, to: 32, bac: 'بكالوريا 2026 — رياضيات', f: 'f(x)=\\dfrac{x^{2}e^{x}}{e^{x}+1}', g: { f: fF, xr: [-8, 2], yr: [-0.5, 3], end: 'm', asym: [{ h: 0 }] }, steps: [
    { line: 32, at: 0.3, tex: '\\lim\\limits_{x\\to-\\infty}x^{2}e^{x}=0 \\quad;\\quad \\lim\\limits_{x\\to-\\infty}\\left(e^{x}+1\\right)=1' },
    { line: 32, at: 0.7, kind: 'result', tex: LIM('-\\infty', '0') }] },
  { from: 34, to: 34, bac: 'بكالوريا 2023 — علوم تجريبية', f: 'f(x)=(x-1)\\left(e^{2x}-1\\right)', g: { f: fA, xr: [-4, 1.5], yr: [-1, 6], end: 'm', asym: [{ a: -1, b: 1 }] }, steps: [
    { line: 34, at: 0.1, tex: 'f(x)-(-x+1)=(x-1)e^{2x}' },
    { line: 34, at: 0.35, tex: '\\lim\\limits_{x\\to-\\infty}(x-1)e^{2x}=0' },
    { line: 34, at: 0.65, kind: 'result', tex: 'y=-x+1', text: 'مقارب مائل' }] },
  { from: 35, to: 35, bac: 'بكالوريا 2021 — علوم تجريبية', f: 'f(x)=x-(x+1)e^{-x-1}', g: { f: fM, xr: [-1.5, 5], yr: [-2, 5], end: 'p', asym: [{ a: 1, b: 0 }] }, steps: [
    { line: 35, at: 0.1, tex: 'f(x)-x=-(x+1)e^{-x-1}' },
    { line: 35, at: 0.35, tex: '\\lim\\limits_{x\\to+\\infty}\\left[f(x)-x\\right]=0' },
    { line: 35, at: 0.65, kind: 'result', tex: 'y=x', text: 'مقارب مائل' }] },
];
// method chapters: [line of the chapter title, number, title, form]
const METHODS: [number, string, string, string][] = [
  [5, '01', 'الحساب المباشر', ''], [11, '02', 'عدد على صفر', '\\dfrac{k}{0}'], [16, '03', 'القسمة على الحد الأقوى', '\\dfrac{\\infty}{\\infty}'],
  [22, '04', 'إخراج الحد الأقوى عاملًا', '\\infty-\\infty'], [28, '05', 'التزايد المقارن', '0\\times\\infty'], [33, '06', 'المستقيم المقارب المائل', 'f(x)-(ax+b)\\to0'],
];

// ---------- visuals ----------
const Bg: React.FC<{ f: number }> = ({ f }) => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse at 70% 20%, ${C.bg1} 0%, ${C.bg0} 70%)` }}>
    {Array.from({ length: 7 }, (_, i) => (
      <div key={i} style={{ position: 'absolute', top: 0, bottom: 0, left: `${8 + i * 14}%`, width: 2, background: 'linear-gradient(180deg, transparent, rgba(245,181,74,0.07), transparent)', transform: `translateY(${Math.sin(f / 90 + i) * 30}px)` }} />
    ))}
  </AbsoluteFill>
);

const Progress: React.FC<{ cur: number; t: number }> = ({ cur, t }) => (
  <div style={{ position: 'absolute', top: 34, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 12, direction: 'rtl', opacity: ramp(t, 0, 0.4) }}>
    {METHODS.map((m, i) => (
      <div key={i} style={{ width: i === cur ? 54 : 16, height: 10, borderRadius: 6, background: i === cur ? C.gold : i < cur ? 'rgba(245,181,74,0.55)' : 'rgba(255,255,255,0.18)' }} />
    ))}
  </div>
);

const Chip: React.FC<{ children: React.ReactNode; bg?: string; fg?: string; size?: number }> = ({ children, bg = C.gold, fg = C.ink, size = 28 }) => (
  <span style={{ display: 'inline-block', padding: '6px 22px 8px', borderRadius: 40, background: bg, color: fg, fontFamily: DISPLAY, fontWeight: 800, fontSize: size, direction: 'rtl' }}>{children}</span>
);

/** Function graph with the branch toward the limit drawn last, a travelling dot and dashed asymptotes. */
const Plot: React.FC<{ g: Graph; t: number; w: number; h: number }> = ({ g, t, w, h }) => {
  const [x0, x1] = g.xr, [y0, y1] = g.yr;
  const X = (x: number) => ((x - x0) / (x1 - x0)) * w;
  const Y = (y: number) => h - ((y - y0) / (y1 - y0)) * h;
  const N = 400, draw = ramp(t, 0.3, 2.2);
  const segs: string[] = []; let cur = '';
  for (let k = 0; k <= N * draw; k++) {
    const x = x0 + ((x1 - x0) * k) / N, y = g.f(x);
    const ok = Number.isFinite(y) && y > y0 - 3 * (y1 - y0) && y < y1 + 3 * (y1 - y0);
    if (!ok) { if (cur) segs.push(cur); cur = ''; continue; }
    const yc = Math.max(y0 - (y1 - y0), Math.min(y1 + (y1 - y0), y));
    cur += `${cur ? 'L' : 'M'}${X(x).toFixed(1)},${Y(yc).toFixed(1)}`;
  }
  if (cur) segs.push(cur);
  // dot travelling toward the limit
  const q = (Math.max(0, t - 2.4) % 3) / 3;
  const xd = g.end === 'p' ? x0 + (x1 - x0) * (0.55 + 0.43 * q) : g.end === 'm' ? x1 - (x1 - x0) * (0.55 + 0.43 * q) : (q < 0.5 ? 0.9 - 1.7 * q : -0.9 + 1.7 * (q - 0.5)) * Math.min(1, (x1 - x0) / 6);
  const yd = g.f(xd);
  const showDot = t > 2.4 && Number.isFinite(yd) && yd > y0 && yd < y1;
  return (
    <svg width={w} height={h} style={{ overflow: 'hidden', borderRadius: 18, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.12)' }}>
      {Array.from({ length: Math.floor(x1) - Math.ceil(x0) + 1 }, (_, i) => Math.ceil(x0) + i).map((gx) => <line key={'x' + gx} x1={X(gx)} x2={X(gx)} y1={0} y2={h} stroke="rgba(255,255,255,0.06)" />)}
      {Array.from({ length: Math.floor(y1) - Math.ceil(y0) + 1 }, (_, i) => Math.ceil(y0) + i).map((gy) => <line key={'y' + gy} y1={Y(gy)} y2={Y(gy)} x1={0} x2={w} stroke="rgba(255,255,255,0.06)" />)}
      <line x1={0} x2={w} y1={Y(0)} y2={Y(0)} stroke="rgba(255,255,255,0.55)" strokeWidth={2} />
      <line y1={0} y2={h} x1={X(0)} x2={X(0)} stroke="rgba(255,255,255,0.55)" strokeWidth={2} />
      {(g.asym ?? []).map((a, i) => {
        const o = ramp(t, 1.8, 2.4);
        if (a.h !== undefined) return <line key={i} x1={0} x2={w} y1={Y(a.h)} y2={Y(a.h)} stroke={C.blue} strokeWidth={3} strokeDasharray="12 9" opacity={o} />;
        if (a.v !== undefined) return <line key={i} y1={0} y2={h} x1={X(a.v)} x2={X(a.v)} stroke={C.blue} strokeWidth={3} strokeDasharray="12 9" opacity={o} />;
        return <line key={i} x1={X(x0)} y1={Y(a.a! * x0 + a.b!)} x2={X(x1)} y2={Y(a.a! * x1 + a.b!)} stroke={C.blue} strokeWidth={3} strokeDasharray="12 9" opacity={o} />;
      })}
      {segs.map((d, i) => <path key={i} d={d} fill="none" stroke={C.gold} strokeWidth={5} strokeLinecap="round" style={{ filter: 'drop-shadow(0 0 6px rgba(245,181,74,0.6))' }} />)}
      {showDot && <circle cx={X(xd)} cy={Y(yd)} r={11} fill={C.red} stroke="#fff" strokeWidth={3} />}
      <text x={w - 18} y={Y(0) - 10} fill="#fff" fontSize={26} fontFamily="serif" fontStyle="italic" textAnchor="end">x</text>
      <text x={X(0) + 12} y={28} fill="#fff" fontSize={26} fontFamily="serif" fontStyle="italic">y</text>
    </svg>
  );
};

const StepRow: React.FC<{ s: Step; t: number }> = ({ s, t }) => {
  const p = pop(t, 0);
  const k = s.kind ?? 'step';
  const strike = k === 'wrong' ? ramp(t, 0.9, 1.5) : 0;
  const bg = k === 'result' ? 'rgba(34,163,107,0.14)' : k === 'wrong' ? 'rgba(229,72,77,0.12)' : 'transparent';
  const bd = k === 'result' ? C.green : k === 'wrong' ? C.red : 'transparent';
  return (
    <div style={{ position: 'relative', display: 'flex', flexDirection: 'row-reverse', alignItems: 'center', gap: 18, padding: '10px 22px', borderRadius: 16, background: bg, border: `2px solid ${bd}`, opacity: Math.min(1, p * 1.4), transform: `translateY(${(1 - p) * 30}px)` }}>
      {k === 'result' && <span style={{ width: 46, height: 46, flex: 'none', borderRadius: 23, background: C.green, color: '#fff', fontSize: 30, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${pop(t, 0.3)})` }}>✓</span>}
      {k === 'wrong' && <span style={{ width: 46, height: 46, flex: 'none', borderRadius: 23, background: C.red, color: '#fff', fontSize: 30, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${pop(t, 0.9)})` }}>✗</span>}
      {s.text && <span style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 36, color: k === 'result' ? '#fff' : C.goldL, direction: 'rtl', whiteSpace: 'nowrap' }}>{s.text}</span>}
      {s.tex && <M tex={s.tex} size={k === 'result' ? 44 : 36} color={k === 'result' ? '#fff' : C.text} />}
      {k === 'wrong' && <div style={{ position: 'absolute', left: 70, right: 90, top: '50%', height: 5, borderRadius: 3, background: C.red, transformOrigin: 'right', transform: `scaleX(${strike})` }} />}
    </div>
  );
};

const ItemScene: React.FC<{ it: Item; sec: number; method: number }> = ({ it, sec, method }) => {
  const t = sec - start(it.from) + 0.3;
  const appear = (s: Step) => { const l = LINES[s.line]; return l.start + (s.at ?? 0) * (l.end - l.start); };
  return (
    <AbsoluteFill>
      <Progress cur={method} t={t} />
      <div style={{ position: 'absolute', top: 78, right: 80, direction: 'rtl', opacity: ramp(t, 0, 0.4) }}>
        <span style={{ fontFamily: LATIN, fontWeight: 700, fontSize: 24, color: 'rgba(255,255,255,0.55)', letterSpacing: 3 }}>{METHODS[method][1]} // </span>
        <span style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 28, color: C.goldL }}>{METHODS[method][2]}</span>
      </div>
      <div style={{ position: 'absolute', top: 150, right: 70, width: 1080, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 16 }}>
        <div style={{ transform: `scale(${pop(t, 0)})`, transformOrigin: 'right' }}><Chip>{it.bac}</Chip></div>
        <div style={{ padding: '18px 30px', borderRadius: 22, background: C.cream, boxShadow: '0 20px 50px rgba(0,0,0,0.45)', opacity: ramp(t, 0.2, 0.6), transform: `translateY(${ramp(t, 0.2, 0.7, 40, 0)}px) rotate(${ramp(t, 0.2, 0.7, -1.5, 0)}deg)` }}>
          <M tex={it.f} size={50} color={C.ink} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 12, marginTop: 10 }}>
          {it.steps.map((s, i) => sec >= appear(s) - 0.05 && <StepRow key={i} s={s} t={sec - appear(s)} />)}
        </div>
      </div>
      <div style={{ position: 'absolute', left: 60, top: 230, opacity: ramp(t, 0.2, 0.7) }}><Plot g={it.g} t={t} w={640} h={560} /></div>
    </AbsoluteFill>
  );
};

const MethodTitle: React.FC<{ m: number; t: number; d: number }> = ({ m, t, d }) => {
  const [, n, title, form] = METHODS[m];
  const out = ramp(t, d - 0.35, d, 1, 0);
  return (
    <AbsoluteFill style={{ background: C.gold, justifyContent: 'center', alignItems: 'center', opacity: Math.min(ramp(t, 0, 0.2), out) }}>
      <div style={{ fontFamily: LATIN, fontWeight: 800, fontSize: 40, color: 'rgba(19,32,63,0.6)', letterSpacing: 6, transform: `translateY(${ramp(t, 0, 0.5, -30, 0)}px)` }}>{m < 5 ? `${n}` : '+'}</div>
      <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 108, color: C.ink, direction: 'rtl', transform: `translateX(${ramp(t, 0.05, 0.6, 160, 0)}px)` }}>{title}</div>
      <div style={{ marginTop: 20, padding: '14px 40px', borderRadius: 24, background: C.ink, transform: `scale(${pop(t, 0.4)})` }}>{form ? <M tex={form} size={64} color={C.goldL} /> : <span style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 48, color: C.goldL, direction: 'rtl' }}>لا توجد حالة عدم تعيين</span>}</div>
    </AbsoluteFill>
  );
};

const Hook: React.FC<{ sec: number }> = ({ sec }) => {
  const t = sec;
  const chips = ['k/0', '∞/∞', '∞ − ∞', '0 × ∞', 'مباشر'];
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 26 }}>
      <div style={{ fontFamily: LATIN, fontWeight: 700, fontSize: 34, color: C.gold, letterSpacing: 8, opacity: ramp(t, 0.2, 0.6) }}>BAC 2020 → 2026</div>
      <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 96, color: '#fff', direction: 'rtl', transform: `scale(${pop(t, 0.3, 0.6)})` }}>نهايات الدالة الأسية</div>
      <M tex="\lim_{x\to\pm\infty} e^{x}" size={70} color={C.goldL} />
      <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: 22, marginTop: 20 }}>
        {chips.map((c, i) => <div key={i} style={{ transform: `scale(${pop(t, start(0) + 4 + i * 0.25)})` }}><Chip bg={i === 4 ? C.goldL : C.gold} size={40}>{c}</Chip></div>)}
      </div>
      <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 52, color: C.goldL, direction: 'rtl', opacity: ramp(t, start(1), start(1) + 0.5) }}>5 طرائق لإزالة كل حالات عدم التعيين</div>
    </AbsoluteFill>
  );
};

const Reminder: React.FC<{ sec: number }> = ({ sec }) => {
  const rows: [number, string][] = [
    [2, '\\lim\\limits_{x\\to+\\infty}e^{x}=+\\infty \\qquad \\lim\\limits_{x\\to-\\infty}e^{x}=0'],
    [3, '\\lim\\limits_{x\\to+\\infty}\\dfrac{e^{x}}{x}=+\\infty \\qquad \\lim\\limits_{x\\to-\\infty}xe^{x}=0'],
    [4, '\\infty-\\infty \\quad;\\quad 0\\times\\infty \\quad;\\quad \\dfrac{\\infty}{\\infty} \\quad;\\quad \\dfrac{0}{0}'],
  ];
  const lab = ['قواعد', 'التزايد المقارن', 'حالات عدم التعيين'];
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 34 }}>
      <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 60, color: C.gold, direction: 'rtl' }}>تذكير</div>
      {rows.map(([l, tex], i) => {
        const tt = sec - start(l);
        return sec >= start(l) && (
          <div key={i} style={{ width: 1500, display: 'flex', flexDirection: 'row-reverse', alignItems: 'center', justifyContent: 'space-between', padding: '22px 40px', borderRadius: 24, background: C.cream, boxShadow: '0 20px 50px rgba(0,0,0,0.4)', opacity: Math.min(1, pop(tt, 0) * 1.4), transform: `translateY(${(1 - pop(tt, 0)) * 40}px)` }}>
            <Chip size={30} bg={i === 2 ? C.red : C.ink} fg="#fff">{lab[i]}</Chip>
            <M tex={tex} size={52} color={C.ink} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const TryIt: React.FC<{ sec: number }> = ({ sec }) => {
  const t = sec - start(36);
  const pauseEnd = start(37);
  const left = Math.max(0, Math.ceil(pauseEnd - sec));
  const ans = sec >= start(37);
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 30 }}>
      <Chip size={44}>حاول بنفسك ✍️</Chip>
      <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 34, color: C.goldL, direction: 'rtl' }}>بكالوريا 2022 — تقني رياضي</div>
      <div style={{ padding: '28px 50px', borderRadius: 26, background: C.cream, transform: `scale(${pop(t, 0.3)})` }}>
        <M tex={'\\lim\\limits_{x\\to-\\infty}\\left[e^{-x}-\\dfrac{x+1}{x^{2}+1}\\right] = \\ ?'} size={64} color={C.ink} />
      </div>
      {!ans && sec > LINES[36].end && <div style={{ width: 150, height: 150, borderRadius: 75, border: `8px solid ${C.gold}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: LATIN, fontWeight: 800, fontSize: 72, color: '#fff' }}>{left}</div>}
      {ans && <div style={{ transform: `scale(${pop(sec - start(37), 0)})` }}><StepRow s={{ line: 37, kind: 'result', tex: '= +\\infty' }} t={sec - start(37)} /></div>}
    </AbsoluteFill>
  );
};

const Summary: React.FC<{ sec: number }> = ({ sec }) => {
  const nodes: [string, string, number][] = [
    ['', 'نحسب مباشرة', 0], ['\\dfrac{k}{0}', 'إشارة المقام', 0.3], ['\\dfrac{\\infty}{\\infty}', 'نقسم على الحد الأقوى', 0.6],
    ['\\infty-\\infty', 'نخرج الحد الأقوى عاملًا', 0], ['0\\times\\infty', 'التزايد المقارن', 0.5],
  ];
  const pos = [[-560, -250], [560, -250], [-620, 40], [620, 40], [0, 300]];
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ padding: '30px 50px', borderRadius: 30, background: C.gold, fontFamily: DISPLAY, fontWeight: 800, fontSize: 56, color: C.ink, direction: 'rtl', transform: `scale(${pop(sec - start(38), 0)})` }}>خلاصة الطرائق</div>
      {nodes.map(([tex, lab, at], i) => {
        const l = i < 3 ? 38 : 39; const a = LINES[l].start + at * (LINES[l].end - LINES[l].start);
        const p = pop(sec - a, 0);
        return sec >= a && (
          <React.Fragment key={i}>
            <svg style={{ position: 'absolute', left: 0, top: 0 }} width={1920} height={1080}><line x1={960} y1={540} x2={960 + pos[i][0] * p} y2={540 + pos[i][1] * p} stroke="rgba(245,181,74,0.6)" strokeWidth={3} strokeDasharray="10 8" /></svg>
            <div style={{ position: 'absolute', left: 960 + pos[i][0] - 230, top: 540 + pos[i][1] - 70, width: 460, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, padding: '16px 18px', borderRadius: 22, background: C.cream, boxShadow: '0 16px 40px rgba(0,0,0,0.45)', opacity: p, transform: `scale(${0.6 + 0.4 * p})` }}>
              {tex && <M tex={tex} size={46} color={C.ink} />}
              <span style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 32, color: C.ink, direction: 'rtl', whiteSpace: 'nowrap' }}>{lab}</span>
            </div>
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};

const CTA: React.FC<{ sec: number }> = ({ sec }) => {
  const t = sec - start(40);
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 30 }}>
      <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 64, color: '#fff', direction: 'rtl', transform: `scale(${pop(t, 0)})` }}>كل تمارين البكالوريا في الدالة الأسية</div>
      <Chip size={44}>2008 → 2026 · بالحل المفصل</Chip>
      <div style={{ fontFamily: LATIN, fontWeight: 700, fontSize: 36, color: '#9FE7FF', opacity: ramp(t, 1.5, 2) }}>PDF · Word · LaTeX</div>
      <div style={{ marginTop: 20, display: 'flex', alignItems: 'center', gap: 26, direction: 'ltr', padding: '20px 50px', borderRadius: 30, border: '4px solid #25D366', background: 'rgba(37,211,102,0.12)', transform: `scale(${pop(t, 3)})` }}>
        <svg width={86} height={86} viewBox="0 0 32 32"><circle cx="16" cy="16" r="16" fill="#25D366" /><path fill="#fff" d="M16 6.2a9.7 9.7 0 0 0-8.4 14.6L6.3 25.7l5-1.3A9.7 9.7 0 1 0 16 6.2zm0 17.7a8 8 0 0 1-4.1-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 1 1 16 23.9z" /></svg>
        <span style={{ fontFamily: LATIN, fontWeight: 800, fontSize: 80, color: '#fff', letterSpacing: 3 }}>0699 92 80 24</span>
      </div>
      <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 34, color: '#C9D4F0', direction: 'rtl', opacity: ramp(t, 4, 4.6) }}>الأستاذ سوايسية هشام للرياضيات · prof_hicham_math</div>
    </AbsoluteFill>
  );
};

export const ExpLimits: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sec = frame / fps;
  const b = (i: number) => (i === 0 ? 0 : start(i) - 0.25);
  let scene: React.ReactNode = null;
  if (sec < b(2)) scene = <Hook sec={sec} />;
  else if (sec < b(5)) scene = <Reminder sec={sec} />;
  else if (sec >= b(36) && sec < b(38)) scene = <TryIt sec={sec} />;
  else if (sec >= b(38) && sec < b(40)) scene = <Summary sec={sec} />;
  else if (sec >= b(40)) scene = <CTA sec={sec} />;
  else {
    const mi = METHODS.findIndex(([l]) => sec >= b(l) && sec < b(l + 1));
    if (mi >= 0) scene = <MethodTitle m={mi} t={sec - b(METHODS[mi][0])} d={b(METHODS[mi][0] + 1) - b(METHODS[mi][0])} />;
    else {
      const it = ITEMS.find((x) => sec >= b(x.from) && sec < b(x.to + 1));
      const method = METHODS.reduce((acc, [l], i) => (it && it.from > l ? i : acc), 0);
      if (it) scene = <ItemScene it={it} sec={sec} method={method} />;
    }
  }
  return (
    <FontGate>
      <AbsoluteFill style={{ background: C.bg0, overflow: 'hidden' }}>
        <Bg f={frame} />
        {scene}
        {LINES.map((l, i) => AUDIO.includes(i + 1) && (
          <Sequence key={i} from={Math.round(l.start * fps)} durationInFrames={Math.ceil((l.end - l.start + 0.3) * fps)} layout="none">
            <Html5Audio src={staticFile(`explim/voice/${String(i + 1).padStart(2, '0')}.mp3`)} />
          </Sequence>
        ))}
      </AbsoluteFill>
    </FontGate>
  );
};
