// Promo 2: guided tour of the lesson library, one scene per voice line (series/promo2/script.txt).
// Every scene opens real files (PDF pages, Word pages, LaTeX source) and closes them again.
// Timing comes from data/promo2.json (estimated now, replaced by the ElevenLabs word timings later).
import React from 'react';
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import data from '../data/promo2.json';
import { FontGate, NASKH, RUQAA } from '../lib/fonts';

type W = { w: string; start: number; end: number };
type Line = { text: string; start: number; end: number; words: W[] };
const LINES = (data as { lines: Line[] }).lines;
const ASSETS = (data as { assets: Record<string, { pdf: string[]; pages: number }> }).assets;
const TEX = (data as { tex: string[] }).tex;
export const PROMO2_SECONDS = Math.ceil((data as { duration: number }).duration + 1.5);

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
      <div style={{ position: 'absolute', inset: 0, transformOrigin: 'left center', transform: `rotateY(${-165 * turn}deg)`, backfaceVisibility: 'hidden', boxShadow: `${-30 * turn}px 0 40px rgba(0,0,0,${0.35 * turn})` }}>
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
const Tile: React.FC<{ src: string; label: string; active: boolean; o?: number; color?: string }> = ({ src, label, active, o = 1, color = C.gold }) => (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, opacity: o, transform: `scale(${active ? 1.1 : 1})` }}>
    <div style={{ width: 150, height: 210, borderRadius: 8, overflow: 'hidden', border: `3px solid ${active ? color : 'rgba(255,255,255,0.25)'}`, boxShadow: active ? `0 0 30px ${color}` : '0 10px 25px rgba(0,0,0,0.5)' }}><Paper src={src} /></div>
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
        <Title size={46} font={NASKH} color={C.dim} o={ramp(t, d * 0.2, d * 0.32)}>في القسم أو في دروس الدعم</Title>
        <Title size={80} color={C.gold} o={ramp(t, d * 0.45, d * 0.58)} y={ramp(t, d * 0.45, d * 0.58, 40, 0)}>ولكل تلميذ في الثانوي</Title>
        <Chip size={40} o={ramp(t, d * 0.7, d * 0.8)} s={ramp(t, d * 0.7, d * 0.8, 0.6, 1)}>خاصة تلاميذ البكالوريا</Chip>
      </AbsoluteFill>
    </>
  );
};

const Library: React.FC<SP> = ({ t, d, frame }) => {
  const covers = Object.keys(ASSETS).map(COVER);
  const n = Math.round(ramp(t, d * 0.15, d * 0.6, 0, 140));
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
        <Chip size={34} o={ramp(t, d * 0.65, d * 0.78)}>مطابقة للمنهاج وللتوزيع السنوي الجديد</Chip>
      </AbsoluteFill>
    </>
  );
};

const Content: React.FC<SP> = ({ t, d }) => {
  const cards = [
    { label: 'ملخصات', src: P('molakhas_integ_3as') },
    { label: 'مذكرات', src: P('modhakira_wahda2a_3as') },
    { label: 'سلاسل تمارين نموذجية', src: P('tamarin_exp_3as') },
    { label: 'تمارين البكالوريا', src: P('bac_ln_3as') },
  ];
  const fmts: Kind[] = ['pdf', 'word', 'tex'];
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 34 }}>
      <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: 36 }}>
        {cards.map((c, i) => {
          const s = t - i * d * 0.12;
          return (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14, opacity: ramp(s, 0, 10), transform: `translateY(${ramp(s, 0, 14, 80, 0)}px)` }}>
              <div style={{ width: 300, height: 420, position: 'relative', borderRadius: 10, overflow: 'hidden', border: `4px solid ${C.gold}`, boxShadow: '0 30px 60px rgba(0,0,0,0.6)' }}><Flipper pages={c.src} t={s} every={34} /></div>
              <Chip size={30}>{c.label}</Chip>
            </div>
          );
        })}
      </div>
      <Title size={44} font={NASKH} color={C.goldLight} o={ramp(t, d * 0.5, d * 0.6)}>جميعها بالحل المفصل</Title>
      <div style={{ display: 'flex', gap: 24, direction: 'ltr' }}>
        {fmts.map((k, i) => (
          <div key={k} style={{ padding: '10px 34px', borderRadius: 12, background: FMT[k].color, color: '#fff', fontFamily: `'DejaVu Sans', sans-serif`, fontWeight: 700, fontSize: 38, opacity: ramp(t, d * 0.68 + i * 8, d * 0.68 + i * 8 + 10), transform: `scale(${ramp(t, d * 0.68 + i * 8, d * 0.68 + i * 8 + 10, 0.4, 1)})` }}>{FMT[k].name}</div>
        ))}
      </div>
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
    { label: 'المذكرة', src: COVER('modhakira_wahda2a_3as') },
    { label: 'ملخص الدرس', src: COVER('molakhas_exp_3as') },
    { label: 'سلسلة تمارين نموذجية', src: COVER('tamarin_exp_3as') },
    { label: 'حلول تمارين البكالوريا', src: COVER('bac_exp_3as') },
  ];
  const streams = ['علوم تجريبية', 'رياضيات', 'تقني رياضي', 'تسيير واقتصاد'];
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 30 }}>
      <Banner t={t} level="السنة الثالثة ثانوي" />
      <Title size={44} font={NASKH} o={ramp(t, d * 0.12, d * 0.2)}>كل درس = أربعة ملفات</Title>
      <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: 34 }}>
        {four.map((f, i) => {
          const s = t - d * (0.2 + i * 0.1);
          return <div key={i} style={{ opacity: ramp(s, 0, 10), transform: `translateY(${ramp(s, 0, 14, 60, 0)}px) rotate(${(i - 1.5) * 2}deg)` }}><Tile src={f.src} label={f.label} active={s > 0 && s < d * 0.1} /></div>;
        })}
      </div>
      <div style={{ display: 'flex', flexDirection: 'row-reverse', gap: 16 }}>
        {streams.map((s, i) => <Chip key={s} size={28} color={i === 3 ? '#7FD1AE' : C.gold} o={ramp(t, d * (0.68 + i * 0.06), d * (0.68 + i * 0.06) + 10)}>{s}</Chip>)}
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

const Social: React.FC<{ icon: string; color: string; text: string; o: number }> = ({ icon, color, text, o }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 16, opacity: o, direction: 'ltr' }}>
    <div style={{ width: 56, height: 56, borderRadius: 28, background: color, color: '#fff', fontFamily: `'DejaVu Sans', sans-serif`, fontWeight: 700, fontSize: 30, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{icon}</div>
    <span style={{ fontFamily: text.includes('_') ? `'DejaVu Sans', sans-serif` : NASKH, fontWeight: 700, fontSize: 38, color: C.text }}>{text}</span>
  </div>
);

const End: React.FC<SP & { at: number }> = ({ t, d, at }) => {
  const pop = ramp(t, at, at + 12);
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', gap: 26 }}>
      <Title size={60} o={ramp(t, 0, 12)}>للحصول على جميع الملفات</Title>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14, alignItems: 'flex-start' }}>
        <Social icon="f" color="#1877F2" text="الأستاذ سوايسية هشام للرياضيات" o={ramp(t, d * 0.15, d * 0.25)} />
        <Social icon="✈" color="#229ED9" text="الأستاذ سوايسية هشام للرياضيات" o={ramp(t, d * 0.22, d * 0.32)} />
        <Social icon="◎" color="#D62976" text="prof_hicham_math" o={ramp(t, d * 0.29, d * 0.39)} />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 28, direction: 'ltr', padding: '18px 44px', borderRadius: 28, background: 'rgba(37,211,102,0.14)', border: `3px solid ${C.wa}`, opacity: pop, transform: `scale(${0.6 + 0.4 * pop + Math.sin(Math.max(0, t - at) / 8) * 0.015})`, boxShadow: `0 0 ${40 * pop}px rgba(37,211,102,0.5)` }}>
        <WhatsApp size={110} />
        <span style={{ fontFamily: `'DejaVu Sans', sans-serif`, fontWeight: 700, fontSize: 96, color: '#fff', letterSpacing: 4 }}>0699 92 80 24</span>
      </div>
    </AbsoluteFill>
  );
};

// ---------- captions (the line being said, words lit as they are spoken) ----------
const Caption: React.FC<{ sec: number; line: Line | undefined }> = ({ sec, line }) => {
  if (!line) return null;
  const o = Math.min(ramp(sec, line.start - 0.25, line.start), ramp(sec, line.end + 0.4, line.end + 0.8, 1, 0));
  return (
    <div style={{ position: 'absolute', left: 120, right: 120, bottom: 26, padding: '12px 30px', borderRadius: 18, background: 'rgba(4,10,28,0.78)', border: '1px solid rgba(245,181,74,0.35)', direction: 'rtl', textAlign: 'center', fontFamily: NASKH, fontSize: 33, lineHeight: 1.55, opacity: o }}>
      {line.words.map((w, i) => (
        <span key={i} style={{ color: sec >= w.start ? C.text : 'rgba(244,241,234,0.35)', textShadow: sec >= w.start && sec < w.end + 0.1 ? `0 0 16px ${C.gold}` : 'none' }}>{w.w} </span>
      ))}
    </div>
  );
};

// ---------- timeline ----------
export const Promo2: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sec = frame / fps;
  const starts = LINES.map((l, i) => (i === 0 ? 0 : l.start - 0.3));
  const idx = Math.max(0, starts.findIndex((s, k) => sec >= s && sec < (starts[k + 1] ?? Infinity)));
  const t = frame - Math.round(starts[idx] * fps);
  const d = Math.round(((starts[idx + 1] ?? PROMO2_SECONDS) - starts[idx]) * fps);
  const lineNow = LINES.find((l, k) => sec >= starts[k] && sec < (starts[k + 1] ?? Infinity));
  const fade = Math.min(ramp(t, 0, 9), idx === LINES.length - 1 ? 1 : ramp(t, d - 7, d, 1, 0));
  const sp = { t, d, frame };
  const L3 = 'السنة الثالثة ثانوي -- الشعب العلمية';
  const GE = 'السنة الثالثة ثانوي -- تسيير واقتصاد';
  const num = LINES[LINES.length - 1].words.find((w) => w.w.includes('الرقم'));
  const scenes = [
    <Hook {...sp} />,
    <Library {...sp} />,
    <Content {...sp} />,
    <ThirdYear {...sp} />,
    <Lesson {...sp} level={L3} title="الدالة الأسية" formats files={[
      { label: 'المذكرة', kind: 'pdf', name: 'modhakira_wahda2a_3as' }, { label: 'الملخص', kind: 'pdf', name: 'molakhas_exp_3as' },
      { label: 'سلسلة التمارين', kind: 'pdf', name: 'tamarin_exp_3as' }, { label: 'البكالوريا', kind: 'pdf', name: 'bac_exp_3as' }]} />,
    <Lesson {...sp} level={L3} title="الدالة اللوغاريتمية" files={[
      { label: 'المذكرة', kind: 'pdf', name: 'modhakira_wahda2b_3as' }, { label: 'الملخص', kind: 'word', name: 'molakhas_ln_3as' },
      { label: 'سلسلة التمارين', kind: 'pdf', name: 'tamarin_ln_3as' }, { label: 'البكالوريا', kind: 'pdf', name: 'bac_ln_3as' }]} />,
    <Lesson {...sp} level={L3} title="الدوال الأصلية والحساب التكاملي" files={[
      { label: 'المذكرة', kind: 'pdf', name: 'modhakira_wahda6_3as' }, { label: 'الملخص', kind: 'pdf', name: 'molakhas_integ_3as' },
      { label: 'سلسلة التمارين', kind: 'pdf', name: 'tamarin_integ_3as' }, { label: 'البكالوريا', kind: 'pdf', name: 'bac_integ_3as' }]} />,
    <Lesson {...sp} level={L3} title="الاحتمالات" files={[
      { label: 'الملخص', kind: 'pdf', name: 'molakhas_proba_3as' }, { label: 'سلسلة التمارين', kind: 'pdf', name: 'tamarin_proba_3as' },
      { label: 'البكالوريا', kind: 'pdf', name: 'bac_proba_3as' }]} />,
    <Carousel {...sp} level={L3} head="وبنفس الطريقة" items={[
      { name: 'molakhas_nihayat_3as', label: 'النهايات' }, { name: 'molakhas_suites_3as', label: 'المتتاليات' }, { name: 'molakhas_cplx_3as', label: 'الأعداد المركبة' },
      { name: 'molakhas_arith_3as', label: 'الأعداد والحساب' }, { name: 'molakhas_fadaa_3as', label: 'الهندسة في الفضاء' }]} />,
    <Lesson {...sp} level={GE} title="المتتاليات العددية" files={[
      { label: 'المذكرة', kind: 'pdf', name: 'modhakira_wahda1_3as_ge' }, { label: 'الملخص', kind: 'word', name: 'molakhas_mutataliyat_3as_ge' },
      { label: 'البكالوريا', kind: 'pdf', name: 'bac_mutataliyat_3as_ge' }]} />,
    <Lesson {...sp} level={GE} title="الدوال الأصلية والحساب التكاملي" files={[
      { label: 'المذكرة', kind: 'pdf', name: 'modhakira_wahda4_3as_ge' }, { label: 'الملخص', kind: 'pdf', name: 'molakhas_takamol_3as_ge' },
      { label: 'البكالوريا', kind: 'pdf', name: 'bac_takamol_3as_ge' }]} />,
    <Carousel {...sp} level={GE} head="وبنفس الطريقة" items={[
      { name: 'molakhas_log_3as_ge', label: 'الدالة اللوغاريتمية' }, { name: 'molakhas_ihsa_3as_ge', label: 'الإحصاء' }, { name: 'molakhas_exp_3as_ge', label: 'الدالة الأسية' }]} />,
    <LevelIntro {...sp} level="السنة الثانية ثانوي" sub="الشعب العلمية" modh="modhakira_wahda2_2as" others={['molakhas_ihtimalat_2as', 'tamarin_ishtiqaq_2as']} />,
    <Lesson {...sp} level="السنة الثانية ثانوي" title="الاشتقاقية ، المرجح ، الاحتمالات ، النهايات" files={[
      { label: 'الاشتقاقية', kind: 'word', name: 'tamarin_ishtiqaq_2as' }, { label: 'المرجح', kind: 'pdf', name: 'tamarin_morajjih_2as' },
      { label: 'الاحتمالات', kind: 'pdf', name: 'molakhas_ihtimalat_2as' }, { label: 'النهايات', kind: 'pdf', name: 'molakhas_nihayat_2as' }]} />,
    <Lesson {...sp} level="السنة الأولى ثانوي -- جذع مشترك علوم وتكنولوجيا" title="المذكرات ، الملخصات ، سلاسل التمارين" files={[
      { label: 'الدوال المرجعية', kind: 'pdf', name: 'tamarin_dawal_marjiiya_1as' }, { label: 'الحساب الشعاعي', kind: 'pdf', name: 'tamarin_hisab_shoaai_1as' },
      { label: 'الهندسة المستوية', kind: 'word', name: 'molakhas_handasa_mostawiya_1as' }, { label: 'المذكرات', kind: 'pdf', name: 'modhakira_wahda4_1as' }]} />,
    <End {...sp} at={num ? Math.round((num.start - starts[LINES.length - 1]) * fps) : Math.round(d * 0.7)} />,
  ];
  return (
    <FontGate>
      <AbsoluteFill style={{ background: C.bg0, overflow: 'hidden' }}>
        <Background frame={frame} />
        <AbsoluteFill style={{ opacity: fade }}>{scenes[idx]}</AbsoluteFill>
        <Caption sec={sec} line={lineNow} />
      </AbsoluteFill>
    </FontGate>
  );
};
