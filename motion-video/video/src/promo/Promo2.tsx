// Promo 2: guided tour of the lesson library, one scene per voice line (series/promo2/script.txt).
// Every scene opens real files (PDF pages, Word pages, LaTeX source) and closes them again.
// Timing comes from data/promo2.json (estimated now, replaced by the ElevenLabs word timings later).
import React from 'react';
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import data from '../data/promo2.json';
import { CAIRO, FontGate, NASKH, RUQAA } from '../lib/fonts';

type W = { w: string; start: number; end: number };
type Line = { text: string; start: number; end: number; words: W[] };
const RAW = (data as { lines: Line[] }).lines;
/** Silence (seconds) inserted after a voice line so its scene can breathe: the 2AS and 1AS boards.
 *  When the voice is added, each line's audio is played from its shifted start (raw start + SHIFT[i]). */
const PAD_AFTER: Record<number, number> = { 12: 2.5, 13: 3.5, 14: 3.5 };
const SHIFT = RAW.map((_, i) => RAW.slice(0, i).reduce((q, __, k) => q + (PAD_AFTER[k] ?? 0), 0));
const LINES: Line[] = RAW.map((l, i) => ({ ...l, start: l.start + SHIFT[i], end: l.end + SHIFT[i], words: l.words.map((w) => ({ ...w, start: w.start + SHIFT[i], end: w.end + SHIFT[i] })) }));
const ASSETS = (data as { assets: Record<string, { pdf: string[]; pages: number }> }).assets;
const TEX = (data as { tex: string[] }).tex;
const BOOK = (data as unknown as { book: Record<string, string[]> }).book;
const BK = (name: string) => (BOOK[name] ?? []).map((f) => staticFile('promo2/b/' + f));
export const PROMO2_SECONDS = Math.ceil((data as { duration: number }).duration + SHIFT[SHIFT.length - 1] + 1.5);

const C = {
  bg0: '#06102A', bg1: '#123063', gold: '#F5B54A', goldLight: '#FFE3A3', text: '#F4F1EA', dim: '#9FB0CF',
  pdf: '#D93025', word: '#2B579A', tex: '#1F8A5B', code: '#14182B', wa: '#25D366',
};
const CL = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const EASE = Easing.bezier(0.45, 0, 0.2, 1);
const ramp = (t: number, a: number, b: number, from = 0, to = 1) => interpolate(t, [a, b], [from, to], { ...CL, easing: EASE });
const hash = (i: number, k = 1) => {
  const x = Math.sin(i * 127.1 * k + k * 311.7) * 43758.5453;
  return x - Math.floor(x);
};
const P = (name: string) => (ASSETS[name]?.pdf ?? []).map((f) => staticFile('promo2/p/' + f));
const WD = (name: string) => [1, 2, 3].map((k) => staticFile(`promo2/w/${name}-0${k}.png`));
const COVER = (name: string) => P(name)[0];

// ---------- building blocks ----------

const Paper: React.FC<{ src: string; style?: React.CSSProperties }> = ({ src, style }) => (
  <Img src={src} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top', background: '#fff', ...style }} />
);

/** Pages turning: the top page rotates around its left edge and reveals the next one. */
const Flipper: React.FC<{ pages: string[]; t: number; every?: number }> = ({ pages, t, every = 30 }) => {
  const n = pages.length;
  const i = Math.floor(Math.max(0, t) / every);
  const q = (Math.max(0, t) % every) / every;
  const turn = ramp(q, 0.6, 1);
  return (
    <div style={{ position: 'absolute', inset: 0, perspective: 1600 }}>
      <Paper src={pages[(i + 1) % n]} style={{ position: 'absolute', inset: 0 }} />
      <div style={{ position: 'absolute', inset: 0, transformOrigin: 'right center', transform: `rotateY(${165 * turn}deg)`, backfaceVisibility: 'hidden', boxShadow: `${30 * turn}px 0 40px rgba(0,0,0,${0.35 * turn})` }}>
        <Paper src={pages[i % n]} style={{ transform: `translateY(${-ramp(q, 0.05, 0.6, 0, 7)}%)` }} />
      </div>
    </div>
  );
};

function colorize(s: string) {
  const parts = s.split(/(\\[a-zA-Z]+|\$[^$]*\$?|[{}[\]])/g);
  return parts.map((p, i) => {
    const color = p.startsWith('\\') ? '#5EC8D8' : p.startsWith('$') ? '#F59BC4' : /^[{}[\]]$/.test(p) ? C.gold : undefined;
    return <span key={i} style={{ color }}>{p}</span>;
  });
}
const Code: React.FC<{ t: number }> = ({ t }) => {
  let left = Math.max(0, t) * 14;
  return (
    <div style={{ position: 'absolute', inset: 0, background: C.code, padding: '16px 18px', fontFamily: `'DejaVu Sans Mono', monospace`, fontSize: 17, lineHeight: 1.5, color: '#E6E6F0', overflow: 'hidden' }}>
      {TEX.map((ln, k) => {
        const shown = ln.slice(0, Math.max(0, Math.min(ln.length, left)));
        left -= ln.length + 3;
        return (
          <div key={k} style={{ whiteSpace: 'pre', direction: 'ltr', unicodeBidi: 'plaintext', display: 'flex', gap: 12 }}>
            <span style={{ color: '#4C5578', width: 26, textAlign: 'right' }}>{k + 1}</span>
            <span>{colorize(shown)}</span>
          </div>
        );
      })}
    </div>
  );
};

type Kind = 'pdf' | 'word' | 'tex';
const FMT: Record<Kind, { name: string; color: string }> = {
  pdf: { name: 'PDF', color: C.pdf },
  word: { name: 'Word', color: C.word },
  tex: { name: 'LaTeX', color: C.tex },
};

/** File-type icon: a coloured sheet with a folded corner and the format mark. */
const FmtIcon: React.FC<{ kind: Kind; size: number }> = ({ kind, size }) => {
  const f = FMT[kind];
  const mark = kind === 'pdf' ? 'PDF' : kind === 'word' ? 'W' : 'TeX';
  return (
    <svg width={size} height={size * 1.2} viewBox="0 0 40 48" style={{ flex: 'none', filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.45))' }}>
      <path d="M4 2 H27 L38 13 V44 a2 2 0 0 1 -2 2 H4 a2 2 0 0 1 -2 -2 V4 a2 2 0 0 1 2 -2 Z" fill={f.color} />
      <path d="M27 2 V11 a2 2 0 0 0 2 2 H38 Z" fill="rgba(255,255,255,0.45)" />
      <rect x="7" y="18" width="18" height="2.4" rx="1.2" fill="rgba(255,255,255,0.5)" />
      <text x="20" y={kind === 'word' ? 41 : 39} textAnchor="middle" fill="#fff" fontFamily="'DejaVu Sans', sans-serif" fontWeight={700} fontSize={kind === 'word' ? 20 : kind === 'pdf' ? 12 : 13}>{mark}</text>
    </svg>
  );
};
const FMT3: Kind[] = ['pdf', 'word', 'tex'];

/** A document window: coloured title bar (format + file label), pages or code inside. */
const Win: React.FC<{ kind: Kind; w: number; h: number; t: number; pages?: string[]; label: string; every?: number }> = ({ kind, w, h, t, pages = [], label, every }) => {
  const f = FMT[kind];
  return (
    <div style={{ width: w, height: h, borderRadius: 14, overflow: 'hidden', background: '#fff', boxShadow: '0 40px 90px rgba(0,0,0,0.6)', border: `3px solid ${f.color}` }}>
      <div style={{ height: 50, background: f.color, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px', color: '#fff' }}>
        <div style={{ display: 'flex', gap: 8 }}>{['#FF5F57', '#FEBC2E', '#28C840'].map((c) => <div key={c} style={{ width: 14, height: 14, borderRadius: 7, background: c }} />)}</div>
        <span style={{ fontFamily: NASKH, fontSize: 24, direction: 'rtl' }}>{label}</span>
        <span style={{ fontFamily: `'DejaVu Sans', sans-serif`, fontWeight: 700, fontSize: 22, letterSpacing: 1 }}>{f.name}</span>
      </div>
      <div style={{ position: 'relative', height: h - 50 }}>{kind === 'tex' ? <Code t={t} /> : <Flipper pages={pages} t={t} every={every} />}</div>
    </div>
  );
};

const Title: React.FC<{ children: React.ReactNode; size?: number; color?: string; o?: number; y?: number; font?: string }> = ({ children, size = 72, color = C.text, o = 1, y = 0, font = RUQAA }) => (
  <div style={{ fontFamily: font, fontSize: size, color, direction: 'rtl', textAlign: 'center', opacity: o, transform: `translateY(${y}px)`, textShadow: '0 6px 30px rgba(0,0,0,0.6)', lineHeight: 1.35 }}>{children}</div>
);
const Chip: React.FC<{ children: React.ReactNode; color?: string; fg?: string; size?: number; o?: number; s?: number }> = ({ children, color = C.gold, fg = '#10203F', size = 30, o = 1, s = 1 }) => (
  <span style={{ display: 'inline-block', padding: '6px 24px', borderRadius: 40, background: color, color: fg, fontFamily: NASKH, fontWeight: 700, fontSize: size, direction: 'rtl', opacity: o, transform: `scale(${s})` }}>{children}</span>
);

const Background: React.FC<{ frame: number }> = ({ frame }) => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 30%, ${C.bg1} 0%, ${C.bg0} 72%)` }}>
    <AbsoluteFill style={{ perspective: 900 }}>
      <div style={{ position: 'absolute', left: '-50%', width: '200%', top: '60%', height: '90%', transform: 'rotateX(78deg)', transformOrigin: 'top',
        backgroundImage: `linear-gradient(rgba(245,181,74,0.13) 2px, transparent 2px), linear-gradient(90deg, rgba(245,181,74,0.13) 2px, transparent 2px)`,
        backgroundSize: '120px 120px', backgroundPosition: `0 ${(frame * 3) % 120}px` }} />
    </AbsoluteFill>
    {Array.from({ length: 36 }, (_, i) => {
      const y = (hash(i, 3) * 100 - frame * (0.04 + hash(i, 4) * 0.08)) % 100;
      return <div key={i} style={{ position: 'absolute', left: `${hash(i, 2) * 100}%`, top: `${y < 0 ? y + 100 : y}%`, width: 3 + hash(i, 5) * 4, height: 3 + hash(i, 5) * 4, borderRadius: 9, background: C.goldLight, opacity: 0.2 + 0.3 * hash(i, 6) }} />;
    })}
  </AbsoluteFill>
);

/** Small file card: cover + label (a tile of the open lesson folder). */
const Tile: React.FC<{ src: string; label: string; active: boolean; o?: number; color?: string; pages?: string[]; t?: number }> = ({ src, label, active, o = 1, color = C.gold, pages, t = 0 }) => (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, opacity: o, transform: `scale(${active ? 1.1 : 1})` }}>
    <div style={{ width: 150, height: 210, borderRadius: 8, overflow: 'hidden', border: `3px solid ${active ? color : 'rgba(255,255,255,0.25)'}`, boxShadow: active ? `0 0 30px ${color}` : '0 10px 25px rgba(0,0,0,0.5)', position: 'relative' }}>{pages && pages.length > 1 ? <Flipper pages={pages} t={Math.max(0, t)} every={26} /> : <Paper src={src} />}</div>
    <Chip size={20} color={active ? color : 'rgba(255,255,255,0.15)'} fg={active ? '#10203F' : C.text}>{label}</Chip>
  </div>
);

// ---------- scenes (t: frames since the line started, d: frames until the next line) ----------
type SP = { t: number; d: number; frame: number };

const Hook: React.FC<SP> = ({ t, d, frame }) => {
  const covers = Object.keys(ASSETS).map(COVER);
  const fly = ramp(t, 0, d, 0, 2200);
  return (
    <>
      <AbsoluteFill style={{ perspective: 1400 }}>
        <div style={{ position: 'absolute', left: '50%', top: '50%', transformStyle: 'preserve-3d', transform: `translateZ(${fly}px) rotateY(${Math.sin(frame / 60) * 6}deg)` }}>
          {covers.slice(0, 40).map((src, i) => (
            <div key={i} style={{ position: 'absolute', transform: `translate3d(${(hash(i, 7) * 2 - 1) * 1200}px, ${(hash(i, 8) * 2 - 1) * 600}px, ${-300 - i * 60}px) translate(-50%,-50%) rotateY(${(hash(i, 9) - 0.5) * 60}deg) rotateZ(${(hash(i, 11) - 0.5) * 16}deg)`, width: 220, height: 310, boxShadow: '0 20px 40px rgba(0,0,0,0.5)' }}><Paper src={src} /></div>
          ))}
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 18, background: `rgba(6,16,42,${ramp(t, 0, d * 0.25, 0.2, 0.65)})` }}>
        <Title size={80} o={ramp(t, 4, 20)} y={ramp(t, 4, 20, 40, 0)}>لكل أستاذ تعليم ثانوي</Title>
        <Title size={58} font={NASKH} color="#9FE7FF" o={ramp(t, d * 0.2, d * 0.32)} y={ramp(t, d * 0.2, d * 0.32, 24, 0)}><span style={{ fontWeight: 700 }}>يدرّس في القسم أو في دروس الدعم</span></Title>
        <div style={{ fontFamily: CAIRO, fontWeight: 800, fontSize: 84, direction: 'rtl', lineHeight: 1.3, opacity: ramp(t, d * 0.45, d * 0.58), transform: `translateY(${ramp(t, d * 0.45, d * 0.58, 40, 0)}px)`, background: 'linear-gradient(180deg, #FFE29A 0%, #F5B54A 55%, #E08A1E 100%)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', filter: 'drop-shadow(0 6px 18px rgba(0,0,0,0.65))' }}>ولكل تلميذ يدرس في الثانوية</div>
        <Chip size={40} o={ramp(t, d * 0.7, d * 0.8)} s={ramp(t, d * 0.7, d * 0.8, 0.6, 1)}>خاصة تلاميذ البكالوريا</Chip>
      </AbsoluteFill>
    </>
  );
};

const Library: React.FC<SP> = ({ t, d, frame }) => {
  const covers = Object.keys(ASSETS).map(COVER);
  const n = Math.round(ramp(t, d * 0.12, d * 0.5, 0, 140));
  return (
    <>
      <AbsoluteFill style={{ perspective: 1600 }}>
        <div style={{ position: 'absolute', left: '50%', top: '52%', transform: `translate(-50%,-50%) rotateX(18deg) rotateY(${ramp(t, 0, d, -14, 14)}deg) scale(${ramp(t, 0, d, 0.9, 1.05)})`, display: 'grid', gridTemplateColumns: 'repeat(12, 130px)', gap: 14 }}>
          {Array.from({ length: 48 }, (_, i) => (
            <div key={i} style={{ width: 130, height: 184, boxShadow: '0 10px 20px rgba(0,0,0,0.5)', opacity: ramp(t, i * 0.8, i * 0.8 + 10), transform: `translateY(${ramp(t, i * 0.8, i * 0.8 + 12, -80, 0)}px)` }}><Paper src={covers[i % covers.length]} /></div>
          ))}
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 10, background: 'radial-gradient(ellipse at center, rgba(6,16,42,0.85) 0%, rgba(6,16,42,0.2) 60%)' }}>
        <Title size={56} o={ramp(t, 0, 14)}>مكتبة الأستاذ سوايسية هشام</Title>
        <div style={{ fontFamily: `'DejaVu Sans', sans-serif`, fontWeight: 700, fontSize: 170, color: C.gold, textShadow: '0 10px 40px rgba(0,0,0,0.7)', direction: 'ltr' }}>+{n}</div>
        <Title size={52} font={NASKH} o={ramp(t, d * 0.3, d * 0.42)}>ملفًا</Title>
        <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: 34, margin: '14px 0 18px' }}>
          {[['1', 'أولى ثانوي'], ['2', 'ثانية ثانوي'], ['3', 'ثالثة ثانوي']].map(([k, lb], i) => {
            const a = d * 0.56 + i * 7;
            const p = interpolate(t, [a, a + 14], [0, 1], { ...CL, easing: Easing.out(Easing.back(2.2)) });
            const glow = ramp(t, a + 10, a + 20) * (1 - ramp(t, a + 20, a + 34));
            return (
              <div key={k} style={{ width: 250, height: 128, borderRadius: 22, background: `linear-gradient(160deg, ${C.gold}, #E08A1E)`, display: 'flex', flexDirection: 'row-reverse', alignItems: 'center', justifyContent: 'center', gap: 14, opacity: Math.min(1, p * 1.5), transform: `translateY(${(1 - p) * 90}px) scale(${0.3 + 0.7 * p}) rotate(${(1 - p) * (i - 1) * 12}deg)`, boxShadow: `0 18px 40px rgba(0,0,0,0.55), 0 0 ${10 + 40 * glow}px rgba(255,214,120,${0.3 + 0.5 * glow})` }}>
                <div style={{ width: 74, height: 74, borderRadius: 37, background: '#10203F', color: C.gold, fontFamily: `'DejaVu Sans', sans-serif`, fontWeight: 700, fontSize: 46, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{k}</div>
                <span style={{ fontFamily: RUQAA, fontSize: 40, color: '#10203F', direction: 'rtl' }}>{lb}</span>
              </div>
            );
          })}
        </div>
        <Chip size={34} o={ramp(t, d * 0.8, d * 0.9)}>مطابقة للمنهاج وللتوزيع السنوي الجديد</Chip>
      </AbsoluteFill>
    </>
  );
};

const Content: React.FC<SP> = ({ t, d }) => {
  const cards = [
    { label: 'ملخصات', src: P('molakhas_integ_3as') },
    { label: 'مذكرات', src: P('modhakira_wahda2a_3as') },
    { label: 'تمارين نموذجية مع الحلول', src: P('tamarin_exp_3as') },
    { label: 'تمارين البكالوريا مع الحلول', src: P('bac_ln_3as') },
  ];
  // arrow tree: one stem from each file, splitting into three branches (PDF, Word, LaTeX)
  const TW = 330, TH = 130, xs = [55, 165, 275];
  return (
    <AbsoluteFill style={{ alignItems: 'center', paddingTop: 40 }}>
      <Title size={44} font={NASKH} color={C.goldLight} o={ramp(t, d * 0.45, d * 0.55)}>جميعها بالحل المفصل</Title>
      <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: 40, marginTop: 14 }}>
        {cards.map((c, i) => {
          const s = t - i * d * 0.1;
          const a0 = d * 0.6 + i * 10; // arrows start once the formats are said
          const stem = ramp(t, a0, a0 + 8), br = ramp(t, a0 + 8, a0 + 18);
          return (
            <div key={i} style={{ width: TW, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, opacity: ramp(s, 0, 10), transform: `translateY(${ramp(s, 0, 14, 80, 0)}px)` }}>
              <div style={{ width: 250, height: 350, position: 'relative', borderRadius: 10, overflow: 'hidden', border: `4px solid ${C.gold}`, boxShadow: '0 30px 60px rgba(0,0,0,0.6)' }}><Flipper pages={c.src} t={s} every={34} /></div>
              <Chip size={28}>{c.label}</Chip>
              <svg width={TW} height={TH} viewBox={`0 0 ${TW} ${TH}`} style={{ overflow: 'visible' }}>
                <line x1={TW / 2} y1={0} x2={TW / 2} y2={46 * stem} stroke={C.gold} strokeWidth={5} strokeLinecap="round" />
                {xs.map((x, k) => {
                  const ex = TW / 2 + (x - TW / 2) * br, ey = 46 + (TH - 18 - 46) * br;
                  const ang = Math.atan2(TH - 18 - 46, x - TW / 2);
                  const hd = (q: number) => `${ex - 16 * Math.cos(ang + q)},${ey - 16 * Math.sin(ang + q)}`;
                  return br > 0 ? (
                    <g key={k}>
                      <line x1={TW / 2} y1={46} x2={ex} y2={ey} stroke={FMT[FMT3[k]].color} strokeWidth={5} strokeLinecap="round" />
                      {br > 0.6 && <polygon points={`${ex},${ey} ${hd(0.45)} ${hd(-0.45)}`} fill={FMT[FMT3[k]].color} />}
                    </g>
                  ) : null;
                })}
              </svg>
              <div style={{ width: TW, height: 70, position: 'relative', direction: 'ltr' }}>
                {xs.map((x, k) => {
                  const p = ramp(t, a0 + 16 + k * 3, a0 + 26 + k * 3);
                  return (
                    <div key={k} style={{ position: 'absolute', left: x - 44, width: 88, top: -8, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, opacity: p, transform: `scale(${0.4 + 0.6 * p})` }}>
                      <FmtIcon kind={FMT3[k]} size={44} />
                      <span style={{ fontFamily: `'DejaVu Sans', sans-serif`, fontWeight: 700, fontSize: 17, color: C.text }}>{FMT[FMT3[k]].name}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
      {(() => {
        const e0 = d * 0.78, p = interpolate(t, [e0, e0 + 14], [0, 1], { ...CL, easing: Easing.out(Easing.back(1.8)) });
        const glow = 0.5 + 0.5 * Math.sin(t / 7);
        return (
          <div style={{ position: 'absolute', bottom: 70, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: Math.min(1, p * 1.4), transform: `translateY(${(1 - p) * 60}px) scale(${0.7 + 0.3 * p})` }}>
            <div style={{ display: 'flex', flexDirection: 'row-reverse', alignItems: 'center', gap: 18, padding: '12px 40px', borderRadius: 50, background: 'linear-gradient(90deg, #00C9A7, #12B5E8 50%, #6C5CE7)', boxShadow: `0 0 ${20 + 22 * glow}px rgba(18,181,232,0.7), 0 14px 30px rgba(0,0,0,0.5)`, border: '2px solid rgba(255,255,255,0.7)' }}>
              <svg width={46} height={46} viewBox="0 0 24 24"><path fill="#fff" d="M3 17.25V21h3.75L17.8 9.94l-3.75-3.75L3 17.25zm17.7-10.2a1 1 0 0 0 0-1.42l-2.33-2.33a1 1 0 0 0-1.42 0l-1.83 1.83 3.75 3.75 1.83-1.83z" /></svg>
              <span style={{ fontFamily: CAIRO, fontWeight: 800, fontSize: 50, color: '#fff', direction: 'rtl', textShadow: '0 3px 10px rgba(0,0,0,0.35)' }}>كل الملفات قابلة للتعديل</span>
            </div>
          </div>
        );
      })()}
    </AbsoluteFill>
  );
};

const Banner: React.FC<{ t: number; level: string; sub?: string }> = ({ t, level, sub }) => (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
    <Title size={88} color={C.gold} o={ramp(t, 0, 12)} y={ramp(t, 0, 14, -40, 0)}>{level}</Title>
    {sub && <Title size={40} font={NASKH} o={ramp(t, 8, 20)}>{sub}</Title>}
  </div>
);

const ThirdYear: React.FC<SP> = ({ t, d }) => {
  const four = [
    { label: 'المذكرة', src: COVER('modhakira_wahda2a_3as'), pages: P('modhakira_wahda2a_3as') },
    { label: 'ملخص الدرس', src: COVER('molakhas_exp_3as'), pages: P('molakhas_exp_3as') },
    { label: 'تمارين نموذجية مع الحلول', src: COVER('tamarin_exp_3as'), pages: P('tamarin_exp_3as') },
    { label: 'تمارين البكالوريا مع الحلول', src: COVER('bac_exp_3as'), pages: P('bac_exp_3as') },
  ];
  const streams = ['علوم تجريبية', 'رياضيات', 'تقني رياضي', 'تسيير واقتصاد'];
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 30, transform: `scale(${1 + 0.1 * ramp(t, d * 0.3, d, 0, 1)})` }}>
      <Banner t={t} level="السنة الثالثة ثانوي" />
      <Title size={44} font={NASKH} o={ramp(t, d * 0.05, d * 0.12)}>كل درس = أربعة ملفات</Title>
      <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: 34 }}>
        {four.map((f, i) => {
          const s = t - d * (0.1 + i * 0.07);
          // once all four are shown, a spotlight keeps travelling from file to file (no frozen frame)
          const cyc = t > d * 0.6 ? Math.floor((t - d * 0.6) / 22) % 4 === i : s > 0 && s < d * 0.08;
          const fl = Math.sin(t / 14 + i * 1.3) * 8;
          return <div key={i} style={{ opacity: ramp(s, 0, 10), transform: `translateY(${ramp(s, 0, 14, 60, 0) + fl}px) rotate(${(i - 1.5) * 2 + Math.sin(t / 20 + i) * 1.2}deg)` }}><Tile src={f.src} pages={f.pages} t={s} label={f.label} active={cyc} /></div>;
        })}
      </div>
      <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: 16 }}>
        {streams.map((s, i) => <Chip key={s} size={28} color={i === 3 ? '#7FD1AE' : C.gold} o={ramp(t, d * (0.42 + i * 0.05), d * (0.42 + i * 0.05) + 10)} s={ramp(t, d * (0.42 + i * 0.05), d * (0.42 + i * 0.05) + 10, 0.5, 1) * (1 + 0.06 * Math.max(0, Math.sin(t / 9 - i * 0.9)) * ramp(t, d * 0.6, d * 0.65))}>{s}</Chip>)}
      </div>
    </AbsoluteFill>
  );
};

type F = { label: string; kind: Kind; name: string; word?: boolean };
/** Opens a lesson: header, row of file tiles; each file in turn opens big (enter), pages flip, then closes (exit). */
const Lesson: React.FC<SP & { level: string; title: string; files: F[]; formats?: boolean }> = ({ t, d, level, title, files, formats }) => {
  const steps = files.length + (formats ? 1 : 0);
  const seg = (d - 18) / steps;
  const k = Math.min(steps - 1, Math.max(0, Math.floor((t - 18) / seg)));
  const s = t - 18 - k * seg;
  const p = s / seg;
  const enter = ramp(p, 0, 0.16);
  const exit = ramp(p, 0.86, 1);
  const open = t >= 18;
  const f = files[k];
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', top: 26, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
        <Chip size={26} o={ramp(t, 0, 10)}>{level}</Chip>
        <Title size={64} o={ramp(t, 0, 12)} y={ramp(t, 0, 12, -30, 0)}>📂 {title}</Title>
      </div>
      <div style={{ position: 'absolute', right: 60, top: 220, display: 'flex', flexDirection: 'column', gap: 14 }}>
        {files.map((x, i) => (
          <div key={i} style={{ opacity: ramp(t, 4 + i * 3, 14 + i * 3), transform: `translateX(${ramp(t, 4 + i * 3, 14 + i * 3, 120, 0)}px) scale(0.62)`, transformOrigin: 'right top', height: 160 }}>
            <Tile src={COVER(x.name)} label={x.label} active={open && i === k && !(formats && k === files.length)} />
          </div>
        ))}
      </div>
      {open && f && !(formats && k === files.length) && (
        <div style={{ position: "absolute", left: 600, top: 200, transform: `translateX(${(1 - enter) * 500 - exit * 300}px) scale(${0.35 + 0.65 * enter - exit * 0.5})`, opacity: enter * (1 - exit), transformOrigin: 'right center' }}>
          <Win kind={f.kind} w={700} h={720} t={s} pages={f.kind === 'word' ? WD(f.name) : P(f.name)} label={f.label + ' · ' + title} every={Math.max(16, Math.floor(seg / 3.2))} />
        </div>
      )}
      {open && formats && k === files.length && (
        <div style={{ position: 'absolute', left: 0, right: 330, top: 210, display: 'flex', justifyContent: 'center', gap: 26, direction: 'ltr' }}>
          {(['pdf', 'word', 'tex'] as Kind[]).map((kk, i) => {
            const ss = s - i * 6;
            return (
              <div key={kk} style={{ opacity: ramp(ss, 0, 10), transform: `translateY(${ramp(ss, 0, 14, 80, 0)}px) rotateY(${(1 - i) * 10}deg)` }}>
                <Win kind={kk} w={470} h={640} t={ss} pages={kk === 'word' ? WD('molakhas_exp_3as') : P('molakhas_exp_3as')} label="الدالة الأسية" every={18} />
              </div>
            );
          })}
        </div>
      )}
    </AbsoluteFill>
  );
};

/** Quick carousel of covers with their titles (lessons named but not opened). */
const Carousel: React.FC<SP & { items: { name: string; label: string }[]; head: string; level: string }> = ({ t, d, items, head, level }) => {
  const n = items.length;
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 28 }}>
      <Chip size={28} o={ramp(t, 0, 10)}>{level}</Chip>
      <Title size={60} o={ramp(t, 0, 12)}>{head}</Title>
      <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: 28, perspective: 1400 }}>
        {items.map((it, i) => {
          const s = t - (i * d * 0.75) / n;
          return (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, opacity: ramp(s, 0, 10), transform: `translateY(${ramp(s, 0, 14, 90, 0)}px) rotateY(${ramp(s, 0, 16, -60, 0)}deg)` }}>
              <div style={{ width: 250, height: 352, position: 'relative', borderRadius: 8, overflow: 'hidden', border: `3px solid ${C.gold}`, boxShadow: '0 30px 60px rgba(0,0,0,0.6)' }}><Flipper pages={P(it.name)} t={s} every={28} /></div>
              <Chip size={26}>{it.label}</Chip>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const LevelIntro: React.FC<SP & { level: string; sub: string; modh: string; others: string[] }> = ({ t, d, level, sub, modh, others }) => {
  const tiles = [{ label: 'المذكرات', src: COVER(modh) }, ...others.map((o, i) => ({ label: i === 0 ? 'الملخصات' : 'سلاسل التمارين بالحلول', src: COVER(o) }))];
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 40 }}>
      <Banner t={t} level={level} sub={sub} />
      <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: 44 }}>
        {tiles.map((x, i) => {
          const s = t - d * (0.35 + i * 0.15);
          return <div key={i} style={{ opacity: ramp(s, 0, 10), transform: `translateY(${ramp(s, 0, 14, 60, 0)}px)` }}><Tile src={x.src} label={x.label} active={s > 0} /></div>;
        })}
      </div>
    </AbsoluteFill>
  );
};

const WhatsApp: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 32 32">
    <circle cx="16" cy="16" r="16" fill={C.wa} />
    <path fill="#fff" d="M16 6.2a9.7 9.7 0 0 0-8.4 14.6L6.3 25.7l5-1.3A9.7 9.7 0 1 0 16 6.2zm0 17.7a8 8 0 0 1-4.1-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 1 1 16 23.9zm4.4-6c-.2-.1-1.4-.7-1.7-.8-.2-.1-.4-.1-.5.1l-.8 1c-.1.2-.3.2-.5.1a6.6 6.6 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.5-.4h-.5a.9.9 0 0 0-.6.3 2.7 2.7 0 0 0-.8 2c0 1.2.9 2.3 1 2.5.1.2 1.7 2.6 4.2 3.7 1.6.7 2.2.7 3 .6.5-.1 1.4-.6 1.6-1.1.2-.6.2-1 .1-1.1l-.6-.4z" />
  </svg>
);

const Facebook: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 32 32">
    <circle cx="16" cy="16" r="16" fill="#1877F2" />
    <path fill="#fff" d="M17.6 26V17.4h2.9l.4-3.4h-3.3v-2.1c0-1 .3-1.6 1.7-1.6h1.8v-3a24 24 0 0 0-2.6-.1c-2.6 0-4.3 1.6-4.3 4.4V14h-2.9v3.4h2.9V26z" />
  </svg>
);
const Instagram: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 32 32">
    <defs><linearGradient id="igg" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stopColor="#FEDA75" /><stop offset="0.35" stopColor="#FA7E1E" /><stop offset="0.6" stopColor="#D62976" /><stop offset="1" stopColor="#4F5BD5" /></linearGradient></defs>
    <rect width="32" height="32" rx="9" fill="url(#igg)" />
    <rect x="7.5" y="7.5" width="17" height="17" rx="5" fill="none" stroke="#fff" strokeWidth="2.2" />
    <circle cx="16" cy="16" r="4.2" fill="none" stroke="#fff" strokeWidth="2.2" />
    <circle cx="21.3" cy="10.7" r="1.3" fill="#fff" />
  </svg>
);

/** One platform card: logo, platform name, and the page / handle / number. */
const Platform: React.FC<{ logo: React.ReactNode; name: string; value: string; color: string; o: number; y: number; s?: number; latin?: boolean; vo?: number }> = ({ logo, name, value, color, o, y, s = 1, latin, vo = 1 }) => (
  <div style={{ width: 520, padding: '26px 18px 24px', borderRadius: 26, background: 'rgba(255,255,255,0.07)', border: `3px solid ${color}`, boxShadow: `0 0 34px ${color}66, 0 20px 40px rgba(0,0,0,0.5)`, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, opacity: o, transform: `translateY(${y}px) scale(${s})` }}>
    {logo}
    <span style={{ fontFamily: NASKH, fontWeight: 700, fontSize: 34, color, direction: 'rtl' }}>{name}</span>
    <span style={{ fontFamily: latin ? `'DejaVu Sans', sans-serif` : NASKH, fontWeight: 700, fontSize: latin ? 38 : 32, color: '#fff', direction: latin ? 'ltr' : 'rtl', letterSpacing: latin ? 1 : 0, whiteSpace: 'nowrap', opacity: vo, transform: `scale(${0.6 + 0.4 * vo})` }}>{value}</span>
  </div>
);

const End: React.FC<SP & { at: number }> = ({ t, d, at }) => {
  const pop = ramp(t, at, at + 12);
  const card = (k: number) => ({ o: ramp(t, d * 0.12 + k * 6, d * 0.12 + k * 6 + 12), y: ramp(t, d * 0.12 + k * 6, d * 0.12 + k * 6 + 14, 70, 0) });
  const wa = card(1);
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 22 }}>
      <Title size={64} o={ramp(t, 0, 12)}>لمعرفة سعر جميع الملفات</Title>
      <Title size={40} font={NASKH} color={C.goldLight} o={ramp(t, 6, 18)}>أرسل رسالة في إحدى المنصات الثلاث: فايسبوك، واتساب، إنستغرام</Title>
      <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: 34, marginTop: 26, alignItems: 'center' }}>
        <Platform logo={<Facebook size={96} />} name="فايسبوك" value="الأستاذ سوايسية هشام للرياضيات" color="#4C8DFF" {...card(0)} />
        <Platform logo={<WhatsApp size={96} />} name="واتساب" value="0699 92 80 24" color={C.wa} latin o={wa.o} y={wa.y} vo={pop}
          s={1 + 0.1 * pop + Math.sin(Math.max(0, t - at) / 8) * 0.015 * pop} />
        <Platform logo={<Instagram size={96} />} name="إنستغرام" value="prof_hicham_math" color="#E1306C" latin {...card(2)} />
      </div>
    </AbsoluteFill>
  );
};

// ---------- flip-book: open spread, leaves turn from left to right ----------
const Book: React.FC<{ pages: string[]; t: number; flipF: number; flips: number; w: number; h: number }> = ({ pages, t, flipF, flips, w, h }) => {
  const n = pages.length;
  const pg = (k: number) => pages[((k % n) + n) % n];
  const i = Math.min(flips, Math.floor(Math.max(0, t) / flipF));
  const q = i >= flips ? 0 : (Math.max(0, t) % flipF) / flipF;
  const turn = ramp(q, 0.05, 0.95);
  const half = w / 2;
  const face = (src: string, st: React.CSSProperties = {}) => <Img src={src} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top', background: '#fff', ...st }} />;
  return (
    <div style={{ position: 'relative', width: w, height: h, perspective: 2200 }}>
      <div style={{ position: 'absolute', left: 0, top: 0, width: half, height: h, boxShadow: '0 30px 70px rgba(0,0,0,0.6)' }}>{face(pg(2 * i + (q > 0 ? 3 : 1)))}<div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(90deg, rgba(0,0,0,0) 80%, rgba(0,0,0,0.25))' }} /></div>
      <div style={{ position: 'absolute', left: half, top: 0, width: half, height: h, boxShadow: '0 30px 70px rgba(0,0,0,0.6)' }}>{face(pg(2 * i))}<div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(270deg, rgba(0,0,0,0) 80%, rgba(0,0,0,0.25))' }} /></div>
      {q > 0 && (
        <div style={{ position: 'absolute', left: 0, top: 0, width: half, height: h, transformOrigin: 'right center', transformStyle: 'preserve-3d', transform: `rotateY(${180 * turn}deg)` }}>
          <div style={{ position: 'absolute', inset: 0, backfaceVisibility: 'hidden' }}>{face(pg(2 * i + 1))}<div style={{ position: 'absolute', inset: 0, background: `rgba(0,0,0,${0.3 * turn})` }} /></div>
          <div style={{ position: 'absolute', inset: 0, backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}>{face(pg(2 * i + 2))}<div style={{ position: 'absolute', inset: 0, background: `rgba(0,0,0,${0.3 * (1 - turn)})` }} /></div>
        </div>
      )}
      <div style={{ position: 'absolute', left: half - 3, top: 0, width: 6, height: h, background: 'linear-gradient(90deg, rgba(0,0,0,0.35), rgba(255,255,255,0.4), rgba(0,0,0,0.35))' }} />
    </div>
  );
};

const Cursor: React.FC<{ x: number; y: number; click: number }> = ({ x, y, click }) => (
  <div style={{ position: 'absolute', left: x, top: y, zIndex: 50, pointerEvents: 'none' }}>
    {click > 0 && click < 1 && <div style={{ position: 'absolute', left: -30 * (0.4 + click), top: -30 * (0.4 + click), width: 60 * (0.4 + click), height: 60 * (0.4 + click), borderRadius: '50%', border: `4px solid ${C.gold}`, opacity: 1 - click }} />}
    <svg width={44} height={44} viewBox="0 0 24 24" style={{ filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.6))', transform: `scale(${1 - 0.15 * Math.sin(Math.PI * Math.min(1, Math.max(0, click * 2)))})`, transformOrigin: 'top left' }}>
      <path d="M3 2 L3 19 L8 14.5 L11.5 22 L14.5 20.6 L11 13.4 L18 13.4 Z" fill="#fff" stroke="#111" strokeWidth={1.4} strokeLinejoin="round" />
    </svg>
  </div>
);

type Col = { title: string; files: { label: string; name: string }[] };
type Step = { line: number; opens: [number, number][]; formats?: boolean; hover?: number[]; pre?: number[] };
/** A level as a table filling the screen: every lesson of the year in two rows (right to left, in the order of the
 *  annual distribution), each lesson a column (title, then its files with their three formats).
 *  The cursor clicks a file, it flies to the centre as an open book, flips pages, flies back.
 *  A step with only `hover` moves the cursor slowly from lesson to lesson, lighting each title. */
const Board: React.FC<{ sec: number; fps: number; header: string; cols: Col[]; top: number; steps: Step[]; starts: number[]; g0: number; g1: number }> = ({ sec, fps, header, cols, top, steps, starts, g0, g1 }) => {
  const W = 1920;
  const per = Math.max(top, cols.length - top);
  const colW = Math.min(440, (W - 90) / per);
  const rowOf = (i: number) => (i < top ? 0 : 1);
  const inRow = (i: number) => (i < top ? i : i - top);
  const nRow = (r: number) => (r === 0 ? top : cols.length - top);
  const cx = (i: number) => W / 2 + ((nRow(rowOf(i)) - 1) / 2 - inRow(i)) * colW;
  const Y0 = 90, rowH = 482, TH = 64;
  const maxF = Math.max(...cols.map((c) => c.files.length));
  const tileH = Math.min(118, (rowH - TH - 30 - (maxF - 1) * 8) / maxF);
  const thH = tileH - 12, thW = thH / 1.414;
  const colTop = (i: number) => Y0 + rowOf(i) * rowH;
  const tileTop = (i: number, j: number) => colTop(i) + TH + 10 + j * (tileH + 8);
  const thumb = (i: number, j: number) => ({ x: cx(i) + colW / 2 - 8 - 8 - thW / 2, y: tileTop(i, j) + tileH / 2 });
  const tg = (sec - g0) * fps;
  type Op = { c: number; f: number; a: number; b: number; formats?: boolean; hop?: boolean };
  const ops: Op[] = [];
  steps.forEach((s, k) => {
    const a = starts[s.line] - (k === 0 ? 0 : 0.3);
    const b = k + 1 < steps.length ? starts[steps[k + 1].line] - 0.3 : g1 - 0.4;
    const items: Op[] = (s.pre ?? []).map((c) => ({ c, f: -1, a: 0, b: 0, hop: true }));
    s.opens.forEach(([c, f]) => items.push({ c, f, a: 0, b: 0 }));
    if (s.formats) items.push({ c: s.opens[0][0], f: 1, a: 0, b: 0, formats: true });
    (s.hover ?? []).forEach((c) => items.push({ c, f: -1, a: 0, b: 0, hop: true }));
    const sa = k === 0 ? Math.max(a, g0 + 1.2) : a;
    const wt = (o: Op) => (o.hop ? 0.45 : 1);
    const unit = (b - sa) / Math.max(0.45, items.reduce((q, o) => q + wt(o), 0));
    let x = sa;
    items.forEach((it) => { ops.push({ ...it, a: x, b: x + wt(it) * unit }); x += wt(it) * unit; });
  });
  const cur = ops.findIndex((o) => sec >= o.a && sec < o.b);
  const op = cur >= 0 ? ops[cur] : undefined;
  const u = op ? (sec - op.a) / (op.b - op.a) : 0;
  const pos = (o?: Op) => (!o ? { x: W - 120, y: 1000 } : o.hop || o.formats ? { x: cx(o.c), y: colTop(o.c) + TH / 2 } : thumb(o.c, o.f));
  const prev = cur > 0 ? pos(ops[cur - 1]) : { x: W / 2, y: 1040 };
  const tgt = pos(op);
  const mv = op?.hop ? ramp(u, 0, 0.35) : ramp(u, 0, 0.14);
  const cursor = op ? { x: prev.x + (tgt.x - prev.x) * mv, y: prev.y + (tgt.y - prev.y) * mv } : prev;
  const click = op && !op.hop ? (u - 0.14) / 0.08 : -1;
  const book = op && !op.formats && !op.hop;
  const fly = book ? Math.min(ramp(u, 0.2, 0.32), ramp(u, 0.86, 0.98, 1, 0)) : 0;
  const opened = book && u > 0.3 && u < 0.88;
  const dim = book ? Math.min(ramp(u, 0.18, 0.3), ramp(u, 0.86, 0.98, 1, 0)) : 0;
  // lessons lit: the one being opened, and every lesson hovered so far in the current step
  const lit = new Set<number>();
  if (op) lit.add(op.c);
  ops.forEach((o) => { if (o.hop && op?.hop && sec >= o.a + 0.35 * (o.b - o.a) && sec - o.a < 4) lit.add(o.c); });
  const BW = 980, BH = 680, BX = W / 2, BY = 560;
  const f0 = book && op ? cols[op.c].files[op.f] : undefined;
  const flipT = (sec - (op ? op.a + 0.32 * (op.b - op.a) : 0)) * fps;
  const flipWindow = op ? 0.52 * (op.b - op.a) * fps : 1;
  const flipF = Math.max(6, Math.floor(flipWindow / 6.5));
  const ic = Math.max(20, Math.min(32, tileH * 0.27));
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', top: 22, width: '100%', textAlign: 'center' }}><Chip size={30} o={ramp(tg, 0, 12)}>{header}</Chip></div>
      <AbsoluteFill style={{ opacity: 1 - 0.7 * dim, filter: dim > 0 ? `blur(${3 * dim}px)` : undefined }}>
        {cols.map((col, i) => {
          const on = lit.has(i);
          const d0 = 4 + i * 2.5;
          return (
            <div key={i} style={{ position: 'absolute', left: cx(i) - colW / 2 + 8, top: colTop(i), width: colW - 16, opacity: ramp(tg, d0, d0 + 12), transform: `translateY(${ramp(tg, d0, d0 + 14, 50, 0)}px)` }}>
              {(() => {
                const ph = sec * 2 * Math.PI * 0.33 + i * 0.9;
                const fy = Math.sin(ph) * 5, rot = Math.sin(ph * 0.7) * 0.8;
                const pulse = 0.5 + 0.5 * Math.sin(sec * 2 * Math.PI * 0.5 + i);
                const shine = ((sec * 0.45 + i * 0.13) % 1.6) - 0.3;
                return (
                  <div style={{ position: 'relative', height: TH, borderRadius: 14, overflow: 'hidden', padding: '0 8px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: on ? `linear-gradient(135deg, #FFD36E, ${C.gold} 55%, #E08A1E)` : 'linear-gradient(135deg, #12B5E8 0%, #4F6BFF 55%, #8B5CF6 100%)',
                    border: `2px solid ${on ? '#FFF1C9' : 'rgba(170,230,255,0.85)'}`,
                    boxShadow: on ? `0 0 ${26 + 14 * pulse}px rgba(245,181,74,0.75)` : `0 0 ${12 + 14 * pulse}px rgba(80,170,255,${0.45 + 0.25 * pulse}), 0 10px 20px rgba(0,0,0,0.45)`,
                    transform: `translateY(${fy}px) rotate(${rot}deg) scale(${on ? 1.05 : 1})` }}>
                    <div style={{ position: 'absolute', top: 0, bottom: 0, left: `${shine * 100}%`, width: '28%', background: 'linear-gradient(100deg, transparent, rgba(255,255,255,0.38), transparent)', transform: 'skewX(-20deg)' }} />
                    <span style={{ position: 'relative', fontFamily: RUQAA, fontSize: col.title.length > 22 ? 24 : col.title.length > 15 ? 28 : 34, color: on ? '#10203F' : '#FFFFFF', direction: 'rtl', textAlign: 'center', lineHeight: 1.15, textShadow: on ? 'none' : '0 2px 6px rgba(10,20,60,0.6)' }}>{col.title}</span>
                  </div>
                );
              })()}
              {col.files.map((f, j) => {
                const active = book && op && op.c === i && op.f === j;
                const e0 = d0 + 6 + j * 3;
                return (
                  <div key={j} style={{ position: 'absolute', top: TH + 10 + j * (tileH + 8), left: 0, right: 0, height: tileH, display: 'flex', flexDirection: 'row-reverse', alignItems: 'center', gap: 10, padding: '0 8px', borderRadius: 10, background: active ? 'rgba(245,181,74,0.22)' : 'rgba(255,255,255,0.06)', border: `2px solid ${active ? C.gold : 'rgba(255,255,255,0.12)'}`, opacity: ramp(tg, e0, e0 + 10) }}>
                    <div style={{ width: thW, height: thH, flex: 'none', borderRadius: 4, overflow: 'hidden', boxShadow: '0 6px 14px rgba(0,0,0,0.5)', opacity: active && fly > 0.02 ? 0 : 1 }}><Paper src={BK(f.name)[0]} /></div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 5, minWidth: 0, flex: 1 }}>
                      <span style={{ fontFamily: NASKH, fontWeight: 700, fontSize: Math.min(26, tileH * 0.21), color: C.text, direction: 'rtl', textAlign: 'right', lineHeight: 1.1 }}>{f.label}</span>
                      <div style={{ display: 'flex', gap: 6, direction: 'ltr' }}>
                        {FMT3.map((k, q) => {
                          const p = ramp(tg, e0 + 8 + q * 2, e0 + 16 + q * 2);
                          return <div key={k} style={{ opacity: p, transform: `scale(${0.5 + 0.5 * p})` }}><FmtIcon kind={k} size={ic} /></div>;
                        })}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          );
        })}
      </AbsoluteFill>
      {book && op && f0 && fly > 0 && (() => {
        const th = thumb(op.c, op.f);
        const from = { x: th.x, y: th.y, w: thW, h: thH };
        const to = { x: BX + BW / 4, y: BY, w: BW / 2, h: BH };
        const x = from.x + (to.x - from.x) * fly, y = from.y + (to.y - from.y) * fly, w = from.w + (to.w - from.w) * fly, h = from.h + (to.h - from.h) * fly;
        if (opened) {
          const openK = Math.min(ramp(u, 0.3, 0.36), ramp(u, 0.8, 0.86, 1, 0));
          return (
            <div style={{ position: 'absolute', left: BX - BW / 2, top: BY - BH / 2, width: BW, height: BH }}>
              <div style={{ position: 'absolute', left: 0, top: 0, transformOrigin: '75% 50%', transform: `scale(${0.6 + 0.4 * openK})`, opacity: 0.4 + 0.6 * openK }}>
                <Book pages={BK(f0.name)} t={flipT} flipF={flipF} flips={6} w={BW} h={BH} />
              </div>
              <div style={{ position: 'absolute', top: -58, width: '100%', textAlign: 'center' }}><Chip size={30}>{f0.label} · {cols[op.c].title}</Chip></div>
            </div>
          );
        }
        return <div style={{ position: 'absolute', left: x - w / 2, top: y - h / 2, width: w, height: h, boxShadow: '0 30px 70px rgba(0,0,0,0.6)', borderRadius: 4, overflow: 'hidden' }}><Paper src={BK(f0.name)[0]} /></div>;
      })()}
      {op && op.formats && (
        <div style={{ position: 'absolute', left: 0, right: 0, top: 200, display: 'flex', justifyContent: 'center', gap: 26, direction: 'ltr', opacity: Math.min(ramp(u, 0, 0.12), ramp(u, 0.88, 1, 1, 0)) }}>
          {FMT3.map((kk, i) => {
            const ss = (sec - op.a) * fps - i * 5;
            return (
              <div key={kk} style={{ transform: `translateY(${ramp(ss, 0, 14, 80, 0)}px)` }}>
                <Win kind={kk} w={520} h={660} t={ss} pages={kk === 'word' ? WD('molakhas_exp_3as') : P('molakhas_exp_3as')} label="الدالة الأسية" every={14} />
              </div>
            );
          })}
        </div>
      )}
      {op && !op.formats && <Cursor x={cursor.x} y={cursor.y} click={click} />}
    </AbsoluteFill>
  );
};

// ---------- captions: short phrases, the spoken word lit in gold; gone as soon as the voice stops ----------
type Chunk = { words: W[]; start: number; end: number };
const CHUNKS: Chunk[] = (() => {
  const out: Chunk[] = [];
  LINES.forEach((l) => {
    let cur: W[] = [];
    const push = () => { if (cur.length) out.push({ words: cur, start: cur[0].start, end: cur[cur.length - 1].end }); cur = []; };
    l.words.forEach((w, i) => {
      cur.push(w);
      const left = l.words.length - 1 - i;
      if ((/[،,:؛.]$/.test(w.w) && cur.length >= 3 && left >= 2) || cur.length >= 7) push();
    });
    push();
  });
  return out;
})();
const Caption: React.FC<{ sec: number; fps: number }> = ({ sec, fps }) => {
  const k = CHUNKS.findIndex((c) => sec >= c.start - 0.12 && sec < c.end + 0.22);
  if (k < 0) return null;
  const c = CHUNKS[k];
  const inT = (sec - (c.start - 0.12)) * fps;
  const o = Math.min(ramp(inT, 0, 5), ramp(sec, c.end + 0.06, c.end + 0.22, 1, 0));
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 38, display: 'flex', justifyContent: 'center', opacity: o, transform: `translateY(${ramp(inT, 0, 7, 26, 0)}px) scale(${ramp(inT, 0, 7, 0.94, 1)})` }}>
      <div style={{ padding: '12px 38px 16px', borderRadius: 22, background: 'linear-gradient(180deg, rgba(10,18,44,0.88), rgba(4,8,24,0.92))', border: '2px solid rgba(245,181,74,0.55)', boxShadow: '0 18px 40px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.08)', direction: 'rtl', fontFamily: NASKH, fontWeight: 700, fontSize: 46, lineHeight: 1.45, whiteSpace: 'nowrap', display: 'flex', gap: 14 }}>
        {c.words.map((w, i) => {
          const on = sec >= w.start && sec < w.end + 0.05;
          const done = sec >= w.start;
          const pop = ramp((sec - w.start) * fps, 0, 4);
          return (
            <span key={i} style={{ position: 'relative', color: on ? C.gold : done ? '#FFFFFF' : 'rgba(244,241,234,0.45)', transform: `scale(${on ? 1 + 0.08 * pop : 1})`, display: 'inline-block', textShadow: on ? '0 0 18px rgba(245,181,74,0.55)' : '0 2px 6px rgba(0,0,0,0.6)' }}>
              {w.w}
              {on && <span style={{ position: 'absolute', left: 0, right: 0, bottom: 2, height: 4, borderRadius: 2, background: C.gold, transformOrigin: 'right', transform: `scaleX(${ramp((sec - w.start) / Math.max(0.05, w.end - w.start), 0, 1)})`, boxShadow: `0 0 10px ${C.gold}` }} />}
            </span>
          );
        })}
      </div>
    </div>
  );
};

// ---------- timeline ----------
export const Promo2: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sec = frame / fps;
  const starts = LINES.map((l, i) => (i === 0 ? 0 : l.start - 0.3));
  const END = PROMO2_SECONDS;
  const L3 = 'السنة الثالثة ثانوي -- الشعب العلمية';
  const GE = 'السنة الثالثة ثانوي -- تسيير واقتصاد';
  const f4 = (m: string, s: string, e: string, b: string) => [{ label: 'المذكرة', name: m }, { label: 'الملخص', name: s }, { label: 'تمارين نموذجية مع الحلول', name: e }, { label: 'تمارين البكالوريا مع الحلول', name: b }];
  const num = LINES[LINES.length - 1].words.find((w) => w.w.includes('الرقم'));
  // groups of voice lines that share one scene: [first line, last line, scene]
  type G = [number, number, (sp: SP, g0: number, g1: number) => React.ReactNode];
  const groups: G[] = [
    [0, 0, (sp) => <Hook {...sp} />],
    [1, 1, (sp) => <Library {...sp} />],
    [2, 2, (sp) => <Content {...sp} />],
    [3, 3, (sp) => <ThirdYear {...sp} />],
    [4, 8, (_, g0, g1) => <Board sec={sec} fps={fps} starts={starts} g0={g0} g1={g1} header={L3} top={6}
      cols={[
        { title: 'الاشتقاقية والاستمرارية', files: [{ label: 'المذكرة', name: 'modhakira_wahda1_3as' }, { label: 'الملخص', name: 'molakhas_nihayat_3as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_nihayat_3as' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_nihayat_3as' }] },
        { title: 'الدالة الأسية', files: [{ label: 'المذكرة', name: 'modhakira_wahda2a_3as' }, { label: 'الملخص', name: 'molakhas_exp_3as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_exp_3as' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_exp_3as' }] },
        { title: 'الدالة اللوغاريتمية', files: [{ label: 'المذكرة', name: 'modhakira_wahda2b_3as' }, { label: 'الملخص', name: 'molakhas_ln_3as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_ln_3as' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_ln_3as' }] },
        { title: 'النهايات', files: [{ label: 'المذكرة', name: 'modhakira_wahda3_3as' }, { label: 'الملخص', name: 'molakhas_nihayat_3as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_nihayat_3as' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_nihayat_3as' }] },
        { title: 'التزايد المقارن', files: [{ label: 'المذكرة', name: 'modhakira_wahda4_3as' }, { label: 'الملخص', name: 'molakhas_tazayud_3as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_qiwa_3as' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_qiwa_3as' }] },
        { title: 'المتتاليات العددية', files: [{ label: 'المذكرة', name: 'modhakira_wahda5_3as' }, { label: 'الملخص', name: 'molakhas_suites_3as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_suites_3as' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_suites_3as' }] },
        { title: 'الدوال الأصلية والحساب التكاملي', files: [{ label: 'المذكرة', name: 'modhakira_wahda6_3as' }, { label: 'الملخص', name: 'molakhas_integ_3as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_integ_3as' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_integ_3as' }] },
        { title: 'الأعداد والحساب', files: [{ label: 'المذكرة', name: 'modhakira_wahda8_3as_riyadiyat' }, { label: 'الملخص', name: 'molakhas_arith_3as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_arith_3as' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_arith_3as' }] },
        { title: 'الاحتمالات', files: [{ label: 'المذكرة', name: 'modhakira_wahda7_3as' }, { label: 'الملخص', name: 'molakhas_proba_3as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_proba_3as' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_proba_3as' }] },
        { title: 'الأعداد المركبة', files: [{ label: 'المذكرة', name: 'modhakira_wahda9_3as' }, { label: 'الملخص', name: 'molakhas_cplx_3as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_cplx_3as' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_cplx_3as' }] },
        { title: 'الهندسة في الفضاء', files: [{ label: 'المذكرة', name: 'modhakira_wahda10_3as' }, { label: 'الملخص', name: 'molakhas_fadaa_3as' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_fadaa_3as' }] },
      ]}
      steps={[
        { line: 4, opens: [[1, 0], [1, 1], [1, 2], [1, 3]], formats: true },
        { line: 5, opens: [[2, 0], [2, 1], [2, 2], [2, 3]] },
        { line: 6, opens: [[6, 0], [6, 1], [6, 2], [6, 3]] },
        { line: 7, opens: [[8, 1], [8, 2], [8, 3]] },
        { line: 8, opens: [], hover: [0, 3, 4, 5, 7, 9, 10] },
      ]} />],
    [9, 11, (_, g0, g1) => <Board sec={sec} fps={fps} starts={starts} g0={g0} g1={g1} header={GE} top={4}
      cols={[
        { title: 'المتتاليات العددية', files: [{ label: 'المذكرة', name: 'modhakira_wahda1_3as_ge' }, { label: 'الملخص', name: 'molakhas_mutataliyat_3as_ge' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_mutataliyat_3as_ge' }] },
        { title: 'الاشتقاقية والاستمرارية', files: [{ label: 'المذكرة', name: 'modhakira_wahda2_3as_ge' }, { label: 'الملخص', name: 'molakhas_dawal_3as_ge' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_dawal_3as_ge' }] },
        { title: 'النهايات ودراسة الدوال', files: [{ label: 'المذكرة', name: 'modhakira_wahda3_3as_ge' }, { label: 'الملخص', name: 'molakhas_dawal_3as_ge' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_dawal_3as_ge' }] },
        { title: 'الدوال الأصلية والحساب التكاملي', files: [{ label: 'المذكرة', name: 'modhakira_wahda4_3as_ge' }, { label: 'الملخص', name: 'molakhas_takamol_3as_ge' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_takamol_3as_ge' }] },
        { title: 'الدالة اللوغاريتمية', files: [{ label: 'المذكرة', name: 'modhakira_wahda5_3as_ge' }, { label: 'الملخص', name: 'molakhas_log_3as_ge' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_log_3as_ge' }] },
        { title: 'الدالة الأسية', files: [{ label: 'المذكرة', name: 'modhakira_wahda6_3as_ge' }, { label: 'الملخص', name: 'molakhas_exp_3as_ge' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_exp_3as_ge' }] },
        { title: 'الإحصاء', files: [{ label: 'المذكرة', name: 'modhakira_wahda7_3as_ge' }, { label: 'الملخص', name: 'molakhas_ihsa_3as_ge' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_ihsa_3as_ge' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_ihsa_3as_ge' }] },
        { title: 'الاحتمالات', files: [{ label: 'المذكرة', name: 'modhakira_wahda8_3as_ge' }, { label: 'الملخص', name: 'molakhas_ihtimalat_3as_ge' }, { label: 'تمارين البكالوريا مع الحلول', name: 'bac_ihtimalat_3as_ge' }] },
      ]}
      steps={[
        { line: 9, opens: [[0, 0], [0, 1], [0, 2]] },
        { line: 10, opens: [[3, 0], [3, 1], [3, 2]] },
        { line: 11, opens: [], hover: [1, 2, 4, 5, 6, 7] },
      ]} />],
    [12, 13, (_, g0, g1) => <Board sec={sec} fps={fps} starts={starts} g0={g0} g1={g1} header="السنة الثانية ثانوي -- الشعب العلمية" top={5}
      cols={[
        { title: 'الدوال', files: [{ label: 'المذكرة', name: 'modhakira_wahda1_2as' }, { label: 'الملخص', name: 'molakhas_2as_wahda1' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_2as_wahda1' }] },
        { title: 'الاشتقاقية', files: [{ label: 'المذكرة', name: 'modhakira_wahda2_2as' }, { label: 'الملخص', name: 'molakhas_ishtiqaq_2as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_ishtiqaq_2as' }] },
        { title: 'الاحتمالات', files: [{ label: 'المذكرة', name: 'modhakira_wahda3_2as' }, { label: 'الملخص', name: 'molakhas_ihtimalat_2as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_ihtimalat_2as' }] },
        { title: 'المرجح', files: [{ label: 'المذكرة', name: 'modhakira_wahda4_2as' }, { label: 'الملخص', name: 'molakhas_morajjih_2as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_morajjih_2as' }] },
        { title: 'النهايات', files: [{ label: 'المذكرة', name: 'modhakira_wahda5_2as' }, { label: 'الملخص', name: 'molakhas_nihayat_2as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_nihayat_2as' }] },
        { title: 'الزوايا الموجهة وحساب المثلثات', files: [{ label: 'المذكرة', name: 'modhakira_wahda6_2as' }, { label: 'الملخص', name: 'molakhas_zawaya_2as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_zawaya_2as' }] },
        { title: 'التحويلات النقطية', files: [{ label: 'المذكرة', name: 'modhakira_wahda7_2as' }, { label: 'الملخص', name: 'molakhas_tahaki_2as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_tahaki_2as' }] },
        { title: 'الجداء السلمي', files: [{ label: 'المذكرة', name: 'modhakira_wahda8_2as' }, { label: 'الملخص', name: 'molakhas_jidaa_salmi_2as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_jidaa_salmi_2as' }] },
        { title: 'المتتاليات العددية', files: [{ label: 'المذكرة', name: 'modhakira_wahda9_2as' }, { label: 'الملخص', name: 'molakhas_motataliat_2as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_motataliat_2as' }] },
      ]}
      steps={[
        { line: 12, opens: [[1, 0], [1, 1], [1, 2]], pre: [0] },
        { line: 13, opens: [[3, 1], [2, 1], [4, 2]], hover: [5, 6, 7, 8] },
      ]} />],
    [14, 14, (_, g0, g1) => <Board sec={sec} fps={fps} starts={starts} g0={g0} g1={g1} header="السنة الأولى ثانوي -- جذع مشترك علوم وتكنولوجيا" top={3}
      cols={[
        { title: 'الأعداد والحساب', files: [{ label: 'المذكرة', name: 'modhakira_wahda1_1as' }, { label: 'الملخص', name: 'molakhas_03_1as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_wahda1_1as' }] },
        { title: 'عموميات على الدوال', files: [{ label: 'المذكرة', name: 'modhakira_wahda2_1as' }, { label: 'الملخص', name: 'molakhas_omomiyat_dawal_1as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_omomiyat_dawal_1as' }] },
        { title: 'الحساب الشعاعي', files: [{ label: 'المذكرة', name: 'modhakira_wahda3_1as' }, { label: 'الملخص', name: 'molakhas_hisab_shoaai_1as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_hisab_shoaai_1as' }] },
        { title: 'الدوال المرجعية', files: [{ label: 'المذكرة', name: 'modhakira_wahda4_1as' }, { label: 'الملخص', name: 'molakhas_dawal_marjiiya_1as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_dawal_marjiiya_1as' }] },
        { title: 'العبارات الجبرية', files: [{ label: 'المذكرة', name: 'modhakira_wahda5_1as' }, { label: 'الملخص', name: 'molakhas_ibarat_jabriya_1as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_ibarat_jabriya_1as' }] },
        { title: 'الهندسة المستوية', files: [{ label: 'المذكرة', name: 'modhakira_wahda6_1as' }, { label: 'الملخص', name: 'molakhas_handasa_mostawiya_1as' }, { label: 'تمارين نموذجية مع الحلول', name: 'tamarin_handasa_mostawiya_1as' }] },
      ]}
      steps={[
        { line: 14, opens: [[4, 1], [3, 0], [2, 1], [5, 1]], pre: [0, 1] },
      ]} />],
    [15, 15, (sp) => <End {...sp} at={num ? Math.round((num.start - starts[15]) * fps) : Math.round(sp.d * 0.7)} />],
  ];
  const gi = Math.max(0, groups.findIndex(([a, b]) => sec >= starts[a] && sec < (starts[b + 1] ?? Infinity)));
  const [ga, gb, scene] = groups[gi];
  const g0 = starts[ga];
  const g1 = starts[gb + 1] ?? END;
  const t = frame - Math.round(g0 * fps);
  const d = Math.round((g1 - g0) * fps);
  const fade = Math.min(ramp(t, 0, 9), gi === groups.length - 1 ? 1 : ramp(t, d - 7, d, 1, 0));
  return (
    <FontGate>
      <AbsoluteFill style={{ background: C.bg0, overflow: 'hidden' }}>
        <Background frame={frame} />
        <AbsoluteFill style={{ opacity: fade }}>{scene({ t, d, frame }, g0, g1)}</AbsoluteFill>
      </AbsoluteFill>
    </FontGate>
  );
};
