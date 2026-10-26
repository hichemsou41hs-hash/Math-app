// Promo video: a 3D (CSS perspective) tour of every lesson pack.
// The camera flies between the lessons, opens each one and shows its three formats
// (PDF, Word, LaTeX) with pages flipping fast. Every frame is a function of the frame number.
import React from 'react';
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import data from '../data/promo.json';
import { FontGate, NASKH, RUQAA } from '../lib/fonts';

type Lesson = { level: string; title: string; id: string; docs: Record<string, string[]>; word: string[]; tex: string[] };
const LESSONS = data as Lesson[];

// Section starts in seconds, one per paragraph of series/promo/script.txt.
// Placeholder estimates: replaced by the teacher's voice timing (words.json) once it is recorded.
export const SEC = [0, 12, 22, 34, 46, 61, 71, 83, 94];
export const PROMO_SECONDS = SEC[SEC.length - 1];

const C = {
  bg0: '#070F22', bg1: '#132A55', gold: '#F5B54A', goldLight: '#FFE3A3', text: '#F4F1EA', dim: '#9FB0CF',
  pdf: '#D93025', word: '#2B579A', tex: '#1F8A5B', code: '#14182B',
};
const CL = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const EASE = Easing.bezier(0.45, 0, 0.2, 1);
const ramp = (t: number, a: number, b: number, from = 0, to = 1) => interpolate(t, [a, b], [from, to], { ...CL, easing: EASE });
const hash = (i: number, k = 1) => {
  const x = Math.sin(i * 127.1 * k + k * 311.7) * 43758.5453;
  return x - Math.floor(x);
};
const LEVEL_NAME: Record<string, string> = { '1AS': 'السنة الأولى ثانوي', '2AS': 'السنة الثانية ثانوي', '3AS': 'السنة الثالثة ثانوي' };

const page = (l: Lesson, kind = 'molakhas') => (l.docs[kind] ?? l.docs.molakhas).map((p) => staticFile('promo/pages/' + p));
const wordPages = (l: Lesson) => l.word.map((p) => staticFile('promo/word/' + p));
const ALL_PAGES = LESSONS.flatMap((l) => Object.values(l.docs).flat()).map((p) => staticFile('promo/pages/' + p));

// ---------- building blocks ----------

const Paper: React.FC<{ src: string; style?: React.CSSProperties }> = ({ src, style }) => (
  <Img src={src} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top', background: '#fff', ...style }} />
);

/** Pages turning fast: the top page rotates around its left edge and reveals the next one. */
const Flipper: React.FC<{ pages: string[]; t: number; every?: number }> = ({ pages, t, every = 9 }) => {
  const n = pages.length;
  const i = Math.floor(Math.max(0, t) / every);
  const q = (Math.max(0, t) % every) / every;
  const turn = ramp(q, 0.45, 1);
  return (
    <div style={{ position: 'absolute', inset: 0, perspective: 1400 }}>
      <Paper src={pages[(i + 1) % n]} style={{ position: 'absolute', inset: 0 }} />
      <div style={{ position: 'absolute', inset: 0, transformOrigin: 'left center', transform: `rotateY(${-170 * turn}deg)`, backfaceVisibility: 'hidden', boxShadow: `${-30 * turn}px 0 40px rgba(0,0,0,${0.35 * turn})` }}>
        <Paper src={pages[i % n]} />
      </div>
    </div>
  );
};

/** LaTeX source: dark editor, lines typed fast and scrolling. */
const Code: React.FC<{ lines: string[]; t: number }> = ({ lines, t }) => {
  const chars = Math.max(0, t) * 9;
  let left = chars;
  return (
    <div style={{ position: 'absolute', inset: 0, background: C.code, padding: '18px 20px', fontFamily: `'DejaVu Sans Mono', monospace`, fontSize: 19, lineHeight: 1.55, color: '#E6E6F0', overflow: 'hidden' }}>
      {lines.map((ln, k) => {
        const shown = ln.slice(0, Math.max(0, Math.min(ln.length, left)));
        left -= ln.length + 4;
        return (
          <div key={k} style={{ whiteSpace: 'pre', direction: 'ltr', unicodeBidi: 'plaintext', display: 'flex', gap: 14 }}>
            <span style={{ color: '#4C5578', width: 28, textAlign: 'right' }}>{k + 1}</span>
            <span>{colorize(shown)}</span>
          </div>
        );
      })}
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

const FORMAT = {
  pdf: { name: 'PDF', color: C.pdf, note: 'جاهز للطباعة' },
  word: { name: 'Word', color: C.word, note: 'قابل للتعديل' },
  tex: { name: 'LaTeX', color: C.tex, note: 'كتابة احترافية' },
} as const;

/** A document window: coloured title bar with the format badge, body = pages or code. */
const Window: React.FC<{ kind: keyof typeof FORMAT; w: number; h: number; t: number; lesson: Lesson; label?: string; every?: number }> = ({ kind, w, h, t, lesson, label, every }) => {
  const f = FORMAT[kind];
  return (
    <div style={{ width: w, height: h, borderRadius: 14, overflow: 'hidden', background: '#fff', boxShadow: '0 40px 80px rgba(0,0,0,0.55)', border: `3px solid ${f.color}` }}>
      <div style={{ height: 52, background: f.color, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 18px', color: '#fff' }}>
        <span style={{ fontFamily: `'DejaVu Sans', sans-serif`, fontWeight: 700, fontSize: 24, letterSpacing: 1 }}>{f.name}</span>
        <span style={{ fontFamily: NASKH, fontSize: 24, direction: 'rtl' }}>{label ?? lesson.title}</span>
      </div>
      <div style={{ position: 'relative', height: h - 52 }}>
        {kind === 'tex' ? <Code lines={lesson.tex} t={t} /> : <Flipper pages={kind === 'pdf' ? page(lesson) : wordPages(lesson)} t={t} every={every} />}
      </div>
    </div>
  );
};

const Title: React.FC<{ children: React.ReactNode; size?: number; color?: string; opacity?: number; y?: number; font?: string }> = ({ children, size = 72, color = C.text, opacity = 1, y = 0, font = RUQAA }) => (
  <div style={{ fontFamily: font, fontSize: size, color, direction: 'rtl', textAlign: 'center', opacity, transform: `translateY(${y}px)`, textShadow: '0 6px 30px rgba(0,0,0,0.6)', lineHeight: 1.35 }}>{children}</div>
);

const Chip: React.FC<{ children: React.ReactNode; color?: string; size?: number }> = ({ children, color = C.gold, size = 30 }) => (
  <span style={{ display: 'inline-block', padding: '6px 22px', borderRadius: 40, background: color, color: '#10203F', fontFamily: NASKH, fontWeight: 700, fontSize: size, direction: 'rtl' }}>{children}</span>
);

/** The 3D stage: perspective + slow camera sway so the angle is always moving. */
const Stage: React.FC<{ children: React.ReactNode; frame: number; rx?: number; ry?: number; z?: number }> = ({ children, frame, rx = 0, ry = 0, z = 0 }) => (
  <AbsoluteFill style={{ perspective: 1500, perspectiveOrigin: '50% 45%' }}>
    <div style={{ position: 'absolute', left: '50%', top: '50%', transformStyle: 'preserve-3d', transform: `translateZ(${z}px) rotateX(${rx + Math.sin(frame / 70) * 3}deg) rotateY(${ry + Math.sin(frame / 55) * 5}deg)` }}>{children}</div>
  </AbsoluteFill>
);

/** Positions a child at (x, y, z) in the stage, centred, with its own rotation. */
const At: React.FC<{ x?: number; y?: number; z?: number; ry?: number; rx?: number; rz?: number; s?: number; o?: number; children: React.ReactNode }> = ({ x = 0, y = 0, z = 0, ry = 0, rx = 0, rz = 0, s = 1, o = 1, children }) => (
  <div style={{ position: 'absolute', left: 0, top: 0, transformStyle: 'preserve-3d', opacity: o, transform: `translate3d(${x}px, ${y}px, ${z}px) translate(-50%, -50%) rotateY(${ry}deg) rotateX(${rx}deg) rotateZ(${rz}deg) scale(${s})` }}>{children}</div>
);

const Background: React.FC<{ frame: number }> = ({ frame }) => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 35%, ${C.bg1} 0%, ${C.bg0} 70%)` }}>
    <AbsoluteFill style={{ perspective: 900 }}>
      <div style={{ position: 'absolute', left: '-50%', width: '200%', top: '58%', height: '90%', transform: 'rotateX(78deg)', transformOrigin: 'top',
        backgroundImage: `linear-gradient(rgba(245,181,74,0.16) 2px, transparent 2px), linear-gradient(90deg, rgba(245,181,74,0.16) 2px, transparent 2px)`,
        backgroundSize: '120px 120px', backgroundPosition: `0 ${(frame * 4) % 120}px` }} />
    </AbsoluteFill>
    {Array.from({ length: 40 }, (_, i) => (
      <div key={i} style={{ position: 'absolute', left: `${hash(i, 2) * 100}%`, top: `${(hash(i, 3) * 100 - frame * (0.05 + hash(i, 4) * 0.1)) % 100 + (hash(i, 3) * 100 - frame * (0.05 + hash(i, 4) * 0.1) < 0 ? 100 : 0)}%`, width: 3 + hash(i, 5) * 4, height: 3 + hash(i, 5) * 4, borderRadius: 9, background: C.goldLight, opacity: 0.25 + 0.35 * hash(i, 6) }} />
    ))}
  </AbsoluteFill>
);

// ---------- scenes (t = frames since the scene started, d = scene length in frames) ----------

const Intro: React.FC<{ t: number; d: number; frame: number }> = ({ t, d, frame }) => {
  const fly = ramp(t, 0, d, 0, 2600);
  return (
    <>
      <Stage frame={frame} z={fly}>
        {ALL_PAGES.slice(0, 48).map((src, i) => (
          <At key={i} x={(hash(i, 7) * 2 - 1) * 1300} y={(hash(i, 8) * 2 - 1) * 650} z={-300 - i * 70} ry={(hash(i, 9) - 0.5) * 70 + t * (hash(i, 10) - 0.5)} rz={(hash(i, 11) - 0.5) * 20}>
            <div style={{ width: 230, height: 325, boxShadow: '0 20px 40px rgba(0,0,0,0.5)' }}><Paper src={src} /></div>
          </At>
        ))}
      </Stage>
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', background: `rgba(7,15,34,${ramp(t, d * 0.05, d * 0.2, 0, 0.6)})` }}>
        <Title size={70} opacity={ramp(t, d * 0.08, d * 0.2)} y={ramp(t, d * 0.08, d * 0.2, 40, 0)}>لكل أستاذ تعليم ثانوي: في القسم أو في دروس الدعم</Title>
        <Title size={70} opacity={ramp(t, d * 0.3, d * 0.42)} y={ramp(t, d * 0.3, d * 0.42, 40, 0)}>ولكل تلميذ في الثانوية: ملخصات وحلول تمارين</Title>
        <Title size={100} color={C.gold} opacity={ramp(t, d * 0.6, d * 0.72)} y={ramp(t, d * 0.6, d * 0.72, 40, 0)}>كل ما تحتاجه، بجميع الصيغ</Title>
      </AbsoluteFill>
    </>
  );
};

const Levels: React.FC<{ t: number; d: number; frame: number }> = ({ t, d, frame }) => {
  const levels = ['1AS', '2AS', '3AS'];
  return (
    <>
      <Stage frame={frame} ry={ramp(t, 0, d, 28, -28)} rx={-8} z={ramp(t, 0, d * 0.3, -900, -300)}>
        {levels.map((lv, k) => {
          const ls = LESSONS.filter((l) => l.level === lv);
          const x = (1 - k) * 560; // 3AS on the left, 1AS on the right (reading order right to left)
          return (
            <At key={lv} x={x} y={0} o={ramp(t, k * 12, k * 12 + 18)}>
              <div style={{ width: 460, display: 'flex', flexDirection: 'column-reverse', gap: 8, alignItems: 'center' }}>
                <Chip size={34}>{LEVEL_NAME[lv]}</Chip>
                {ls.map((l, j) => (
                  <div key={l.id} style={{ width: 420, height: 46, borderRadius: 8, background: `linear-gradient(90deg, ${C.word}, #3D74C9)`, border: '2px solid rgba(255,255,255,0.25)', color: '#fff', fontFamily: NASKH, fontSize: 24, direction: 'rtl', display: 'flex', alignItems: 'center', padding: '0 16px',
                    transform: `translateY(${ramp(t, k * 12 + j * 3, k * 12 + j * 3 + 14, -300, 0)}px)`, opacity: ramp(t, k * 12 + j * 3, k * 12 + j * 3 + 8) }}>📁&nbsp;{l.title}</div>
                ))}
              </div>
            </At>
          );
        })}
      </Stage>
      <AbsoluteFill style={{ justifyContent: 'flex-start', alignItems: 'center', paddingTop: 50 }}>
        <Title size={64} opacity={ramp(t, 6, 20)}>سلسلة دروس الأستاذ سوايسية هشام</Title>
      </AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 60 }}>
        <Chip size={36}>مطابقة للتوزيع السنوي والمنهاج الجزائري</Chip>
      </AbsoluteFill>
    </>
  );
};

const Kinds: React.FC<{ t: number; d: number; frame: number }> = ({ t, d, frame }) => {
  const l = LESSONS.find((x) => x.id === 'exp_3as') ?? LESSONS[1];
  const kinds = [
    { k: 'molakhas', label: 'ملخص شامل بالأمثلة والأشكال' },
    { k: 'tamarin', label: 'تمارين بحلول مفصلة خطوة بخطوة' },
    { k: 'bac', label: 'تمارين البكالوريا محلولة حتى 2026' },
  ];
  return (
    <Stage frame={frame} rx={-4} z={ramp(t, 0, d, -400, 0)}>
      {kinds.map((o, i) => {
        const start = i * d * 0.22;
        const s = t - start;
        return (
          <At key={o.k} x={(1 - i) * 560} y={20} ry={(i - 1) * -18} z={ramp(s, 0, 20, -900, 0)} o={ramp(s, 0, 12)}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22 }}>
              <div style={{ width: 470, height: 640, borderRadius: 10, overflow: 'hidden', position: 'relative', boxShadow: '0 40px 80px rgba(0,0,0,0.6)', border: `4px solid ${C.gold}` }}>
                <Flipper pages={page(l, o.k)} t={s} every={8} />
              </div>
              <Chip size={30}>{o.label}</Chip>
            </div>
          </At>
        );
      })}
    </Stage>
  );
};

const Formats: React.FC<{ t: number; d: number; frame: number }> = ({ t, d, frame }) => {
  const l = LESSONS.find((x) => x.id === 'integ_3as') ?? LESSONS[5];
  const ks: (keyof typeof FORMAT)[] = ['pdf', 'word', 'tex'];
  return (
    <>
      <Stage frame={frame} ry={ramp(t, 0, d, -14, 14)} z={ramp(t, 0, d, -350, -50)}>
        {ks.map((k, i) => {
          const s = t - i * d * 0.2;
          return (
            <At key={k} x={(1 - i) * 600} y={-10} ry={(i - 1) * -20} z={ramp(s, 0, 22, -1200, 0) - Math.abs(i - 1) * 90} o={ramp(s, 0, 10)}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
                <Window kind={k} w={540} h={660} t={s} lesson={l} every={8} />
                <Chip color={FORMAT[k].color} size={32}><span style={{ color: '#fff' }}>{FORMAT[k].note}</span></Chip>
              </div>
            </At>
          );
        })}
      </Stage>
      <AbsoluteFill style={{ justifyContent: 'flex-start', alignItems: 'center', paddingTop: 36 }}>
        <Title size={58} opacity={ramp(t, 0, 12)}>كل ملف بثلاث صيغ</Title>
      </AbsoluteFill>
    </>
  );
};

/** Lesson tour: for each lesson the camera flies in, the three windows fan out with pages flipping, then fly past. */
const Tour: React.FC<{ t: number; d: number; frame: number; lessons: Lesson[]; header: string }> = ({ t, d, frame, lessons, header }) => {
  const seg = d / lessons.length;
  const i = Math.min(lessons.length - 1, Math.floor(t / seg));
  const s = t - i * seg;
  const l = lessons[i];
  const p = s / seg;
  const z = interpolate(p, [0, 0.22, 0.82, 1], [-1800, -150, 0, 900], CL);
  const fan = ramp(p, 0.15, 0.35);
  const out = ramp(p, 0.86, 1, 1, 0);
  const ks: (keyof typeof FORMAT)[] = ['pdf', 'word', 'tex'];
  return (
    <>
      <Stage frame={frame} ry={(i % 2 ? -1 : 1) * ramp(p, 0, 1, 10, -10)} rx={-3} z={z}>
        {ks.map((k, j) => (
          <At key={k} x={(1 - j) * 560 * fan} y={30} z={-Math.abs(j - 1) * 120 * fan} ry={(j - 1) * -24 * fan} o={out}>
            <Window kind={k} w={500} h={600} t={s} lesson={l} every={7} label={k === 'tex' ? l.title : undefined} />
          </At>
        ))}
      </Stage>
      <AbsoluteFill style={{ justifyContent: 'flex-start', alignItems: 'center', paddingTop: 34, gap: 12 }}>
        <Chip size={28}>{header} · {LEVEL_NAME[l.level]}</Chip>
        <Title size={62} opacity={ramp(p, 0.05, 0.2) * out}>{l.title}</Title>
      </AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 30 }}>
        <div style={{ display: 'flex', gap: 10 }}>
          {lessons.map((_, k) => (
            <div key={k} style={{ width: k === i ? 34 : 12, height: 12, borderRadius: 6, background: k <= i ? C.gold : 'rgba(255,255,255,0.25)' }} />
          ))}
        </div>
      </AbsoluteFill>
    </>
  );
};

const CloseUps: React.FC<{ t: number; d: number; frame: number }> = ({ t, d, frame }) => {
  const shots = [
    { src: 'promo/zoom/integ-12.png', label: 'منحنيات ومساحات ملوّنة', y0: 0.15, y1: 0.55 },
    { src: 'promo/zoom/qiwa-5.png', label: 'جداول تغيّرات كاملة', y0: 0.1, y1: 0.5 },
    { src: 'promo/zoom/prob-06.png', label: 'جداول احتمالات منسّقة', y0: 0.2, y1: 0.6 },
  ];
  const seg = d / shots.length;
  const i = Math.min(shots.length - 1, Math.floor(t / seg));
  const s = t - i * seg;
  const p = s / seg;
  const sh = shots[i];
  return (
    <>
      <Stage frame={frame} rx={ramp(p, 0, 1, 14, 4)} ry={ramp(p, 0, 1, -16, 10)} z={ramp(p, 0, 1, -200, 250)}>
        <At o={ramp(p, 0, 0.12) * ramp(p, 0.88, 1, 1, 0)}>
          <div style={{ width: 1100, height: 760, overflow: 'hidden', borderRadius: 12, boxShadow: '0 50px 100px rgba(0,0,0,0.6)', border: `4px solid ${C.gold}` }}>
            <Img src={staticFile(sh.src)} style={{ width: 1100, transform: `translateY(${-ramp(p, 0, 1, sh.y0, sh.y1) * 1556 * 0.6}px)` }} />
          </div>
        </At>
      </Stage>
      <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 46 }}>
        <Chip size={40}>{sh.label}</Chip>
      </AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: 'flex-start', alignItems: 'center', paddingTop: 36 }}>
        <Title size={52} opacity={ramp(t, d * 0.7, d * 0.85)} color={C.goldLight}>كل درس مراجَع ومصحَّح سطراً بسطر</Title>
      </AbsoluteFill>
    </>
  );
};

const Social: React.FC<{ icon: string; color: string; text: string; o: number }> = ({ icon, color, text, o }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 18, opacity: o, direction: 'ltr' }}>
    <div style={{ width: 64, height: 64, borderRadius: 32, background: color, color: '#fff', fontFamily: `'DejaVu Sans', sans-serif`, fontWeight: 700, fontSize: 34, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{icon}</div>
    <span style={{ fontFamily: text.includes('_') ? `'DejaVu Sans', sans-serif` : NASKH, fontWeight: 700, fontSize: 44, color: C.text }}>{text}</span>
  </div>
);

const End: React.FC<{ t: number; d: number; frame: number }> = ({ t, d }) => {
  const nPdf = LESSONS.reduce((a, l) => a + Object.keys(l.docs).length, 0);
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 26 }}>
      <Title size={84} color={C.gold} opacity={ramp(t, 0, 12)}>الأستاذ سوايسية هشام للرياضيات</Title>
      <div style={{ display: 'flex', gap: 24, opacity: ramp(t, 8, 20), direction: 'rtl' }}>
        <Chip size={34}>{LESSONS.length} درساً</Chip>
        <Chip size={34}>{nPdf} ملفاً</Chip>
        <Chip size={34}>PDF · Word · LaTeX</Chip>
      </div>
      <Title size={46} opacity={ramp(t, d * 0.2, d * 0.32)} font={NASKH}>للحصول على الملفات تواصل معنا</Title>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16, alignItems: 'flex-start' }}>
        <Social icon="f" color="#1877F2" text="الأستاذ سوايسية هشام للرياضيات" o={ramp(t, d * 0.3, d * 0.4)} />
        <Social icon="✈" color="#229ED9" text="الأستاذ سوايسية هشام للرياضيات" o={ramp(t, d * 0.4, d * 0.5)} />
        <Social icon="◎" color="#D62976" text="prof_hicham_math" o={ramp(t, d * 0.5, d * 0.6)} />
      </div>
    </AbsoluteFill>
  );
};

// ---------- timeline ----------

export const Promo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = SEC.map((s) => Math.round(s * fps));
  const idx = Math.max(0, f.findIndex((x, k) => frame >= x && frame < (f[k + 1] ?? Infinity)));
  const t = frame - f[idx];
  const d = (f[idx + 1] ?? f[idx] + 1) - f[idx];
  const fade = Math.min(ramp(t, 0, 10), ramp(t, d - 8, d, 1, 0));
  const s3 = LESSONS.filter((l) => l.level === '3AS');
  const s12 = LESSONS.filter((l) => l.level !== '3AS').sort((a, b) => (a.level < b.level ? 1 : -1));
  const scenes = [
    <Intro t={t} d={d} frame={frame} />,
    <Levels t={t} d={d} frame={frame} />,
    <Kinds t={t} d={d} frame={frame} />,
    <Formats t={t} d={d} frame={frame} />,
    <Tour t={t} d={d} frame={frame} lessons={s3} header="جولة في الدروس" />,
    <Tour t={t} d={d} frame={frame} lessons={s12} header="جولة في الدروس" />,
    <CloseUps t={t} d={d} frame={frame} />,
    <End t={t} d={d} frame={frame} />,
  ];
  return (
    <FontGate>
      <AbsoluteFill style={{ background: C.bg0, overflow: 'hidden' }}>
        <Background frame={frame} />
        <AbsoluteFill style={{ opacity: idx === scenes.length - 1 ? 1 : fade }}>{scenes[idx]}</AbsoluteFill>
      </AbsoluteFill>
    </FontGate>
  );
};
