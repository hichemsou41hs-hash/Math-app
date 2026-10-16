// The whole video: one long chalkboard (the world), a camera over it, one chalk, the wooden frame with
// the teacher's nameplate, the voice and the sound effects. Boards come from src/boards/.
import React, { useMemo } from 'react';
import { AbsoluteFill, Html5Audio, Sequence, random, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { TIMING, toFrame, toSec } from './timing';
import { FontGate, RUQAA } from './lib/fonts';
import { C, Timeline, boardAt, camera, chalkState, progress, timeline, toScreen, toWorld } from './lib/engine';
import { buildBoards } from './boards';
import { Pt } from './lib/geom';
import { PART_LINES, partBoardFrom, partEnd, partStart } from './parts';

export const TEACHER = 'الأستاذ سوايسية هشام';
export const TITLE = 'الدالة الأسية النيبيرية';
/** Seconds a reel holds its finished board at the end. */
export const HOLD = 2.5;
/** Chalk scratches and taps under every write. Off: the teacher found them distracting under the voice. */
const CHALK_SOUND = false;

export const Video: React.FC<{ part?: number }> = ({ part }) => (
  <AbsoluteFill style={{ backgroundColor: C.board }}>
    <FontGate>
      <Stage part={part} />
    </FontGate>
  </AbsoluteFill>
);

const Stage: React.FC<{ part?: number }> = ({ part }) => {
  const { width: W, height: H } = useVideoConfig();
  const P = H > W;
  const tl = useMemo(() => {
    const boards = buildBoards(P, W, H);
    boards.forEach((b, i) => {
      const next = boards[i + 1];
      const last = Math.max(...b.items.map((x) => x.t1));
      if (next && last > next.from - 0.75) console.warn(`LATE board ${b.id}: last write ends ${last.toFixed(2)}, next board at ${(next.from - 0.75).toFixed(2)}`);
    });
    return timeline(boards, W, H, TIMING.duration);
  }, [P, W, H]);
  const off = part ? partStart(part) : 0;
  // a reel holds its last picture for HOLD seconds, silently
  const stop = part ? partEnd(part) - 0.05 : Infinity;
  const audioFrames = Number.isFinite(stop) ? toFrame(stop) : undefined;
  return (
    <Sequence from={-toFrame(off)} layout="none">
      <World tl={tl} part={part} stop={stop} />
      <Sequence durationInFrames={audioFrames} layout="none">
        {TIMING.audio ? <Html5Audio src={staticFile(TIMING.audio)} /> : null}
        <Sounds tl={tl} />
      </Sequence>
    </Sequence>
  );
};


const World: React.FC<{ tl: Timeline; part?: number; stop: number }> = ({ tl, part, stop }) => {
  const now = toSec(useCurrentFrame());
  const t = Math.min(now, stop);
  const { W, H } = tl;
  const u = Math.min(W, H) / 1080;
  const cam = camera(tl, t);
  const bi = boardAt(tl, t);
  // in a reel, the boards of earlier reels are never shown: the first board slides in onto a clean board
  const first = part ? tl.boards.findIndex((b) => Math.abs(b.from - partBoardFrom(part)) < 0.01) : 0;
  const visible = tl.boards.filter((_, i) => Math.abs(i - bi) <= 1 && i >= first);
  const tray: Pt = toWorld(tl, cam, [W * 0.2, H - 20 * u]);
  const ch = chalkState(tl, t, tray);
  const chS = toScreen(tl, cam, ch.p);

  // chalk dust: the last 14 moments the chalk was drawing
  const dust: React.ReactNode[] = [];
  for (let d = 1; d <= 14; d++) {
    const ta = t - d / 30;
    const s = chalkState(tl, ta, tray);
    if (!s.drawing) continue;
    for (let j = 0; j < 2; j++) {
      const seed = `dust-${Math.round(ta * 30)}-${j}`;
      if (random(seed) < 0.35) continue;
      const age = d / 30;
      const p = toScreen(tl, cam, [s.p[0] + (random(seed + 'x') - 0.5) * 10, s.p[1] + random(seed + 'y') * 6]);
      dust.push(
        <circle key={`${d}-${j}`} cx={p[0] + (random(seed + 'v') - 0.5) * 30 * age} cy={p[1] + 0.5 * 1100 * age * age * u} r={(1.2 + random(seed + 'r') * 1.8) * u} fill={s.color} opacity={(1 - age / 0.5) * 0.7} />,
      );
    }
  }

  const chapter = tl.boards[bi].chapter;
  return (
    <AbsoluteFill>
      {/* the board surface and everything written on it, in world coordinates */}
      <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
        <defs>
          <radialGradient id="smudge">
            <stop offset="0" stopColor="#fff" stopOpacity="0.06" />
            <stop offset="1" stopColor="#fff" stopOpacity="0" />
          </radialGradient>
        </defs>
        <g transform={`translate(${W / 2} ${H / 2}) scale(${cam.z}) translate(${-cam.x} ${-cam.y})`}>
          {visible.map((b) => (
            <g key={b.id}>
              {[0, 1, 2, 3].map((i) => (
                <ellipse key={i} cx={b.ox + random(b.id + i) * b.W} cy={b.oy + random(b.id + i + 'y') * b.H} rx={b.W * (0.25 + random(b.id + i + 'r') * 0.25)} ry={b.H * 0.12} fill="url(#smudge)" />
              ))}
              <g transform={`translate(${b.ox} ${b.oy})`}>
                {b.items.map((it) => (t >= it.t0 ? <React.Fragment key={it.id}>{it.draw(progress(it, t))}</React.Fragment> : null))}
              </g>
            </g>
          ))}
        </g>
      </svg>
      <Grain W={W} H={H} />
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 42%, rgba(70,110,95,0.35) 0%, rgba(0,0,0,0) 45%, rgba(8,22,18,0.55) 100%)' }} />
      <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
        {dust}
      </svg>
      <Frame W={W} H={H} u={u} chapter={chapter} part={part} />
      {part && part < PART_LINES.length ? <NextPart t={now} end={partEnd(part) + HOLD} part={part} u={u} W={W} H={H} /> : null}
      <Chalk p={chS} lift={ch.lift} color={ch.color} u={u} />
    </AbsoluteFill>
  );
};

/** The last seconds of a reel: «continued in part n+1». */
const NextPart: React.FC<{ t: number; end: number; part: number; u: number; W: number; H: number }> = ({ t, end, part, u, W, H }) => {
  const k = Math.min(1, Math.max(0, (t - (end - HOLD - 0.3)) / 0.4));
  if (k <= 0) return null;
  return (
    <AbsoluteFill style={{ backgroundColor: `rgba(10,20,16,${0.45 * k})` }}>
      <div
        dir="rtl"
        style={{
          position: 'absolute',
          left: W / 2 - 230 * u,
          width: 460 * u,
          top: H / 2 - 50 * u + (1 - k) * 30 * u,
          opacity: k,
          padding: `${14 * u}px 0`,
          textAlign: 'center',
          borderRadius: 14 * u,
          background: 'linear-gradient(180deg, #5a3c22, #3f2915)',
          border: `${2 * u}px solid #b08a52`,
          boxShadow: '0 10px 30px rgba(0,0,0,0.6)',
          fontFamily: RUQAA,
          fontWeight: 700,
          fontSize: 44 * u,
          lineHeight: 1.5,
          color: '#F1D9A6',
        }}
      >
        {`يتبع في الجزء ${part + 1}`}
      </div>
    </AbsoluteFill>
  );
};

const Grain: React.FC<{ W: number; H: number }> = ({ W, H }) => (
  <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" />
      <feColorMatrix type="matrix" values="0 0 0 0 0.2  0 0 0 0 0.33  0 0 0 0 0.29  0 0 0 -2.6 1.45" />
    </filter>
    <rect width={W} height={H} filter="url(#grain)" opacity={0.55} />
  </svg>
);

const Chalk: React.FC<{ p: Pt; lift: number; color: string; u: number }> = ({ p, lift, color, u }) => {
  const L = 92 * u;
  const T = 17 * u;
  const up = 10 * u * lift;
  const sh = (6 + 22 * lift) * u;
  return (
    <svg style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible' }} width={1} height={1}>
      <defs>
        <linearGradient id="chalkbody" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#fff" stopOpacity="0.55" />
          <stop offset="0.45" stopColor="#fff" stopOpacity="0" />
          <stop offset="1" stopColor="#000" stopOpacity="0.22" />
        </linearGradient>
        <filter id="chalkshadow">
          <feGaussianBlur stdDeviation={3 * u + 3 * u * lift} />
        </filter>
      </defs>
      <g transform={`translate(${p[0] + sh * 0.6} ${p[1] + sh}) rotate(30)`} opacity={0.4 - 0.15 * lift} filter="url(#chalkshadow)">
        <rect x={0} y={-T / 2} width={L} height={T} rx={T * 0.35} fill="#000" />
      </g>
      <g transform={`translate(${p[0]} ${p[1] - up}) rotate(30) scale(${1 + 0.06 * lift})`}>
        <rect x={0} y={-T / 2} width={L} height={T} rx={T * 0.35} fill={color} />
        <rect x={0} y={-T / 2} width={L} height={T} rx={T * 0.35} fill="url(#chalkbody)" />
        <rect x={0} y={-T / 2} width={T * 0.5} height={T} rx={T * 0.25} fill="#000" opacity={0.08} />
      </g>
    </svg>
  );
};

const Frame: React.FC<{ W: number; H: number; u: number; chapter: string; part?: number }> = ({ W, H, u, chapter, part }) => {
  const f = 24 * u;
  const wood = 'linear-gradient(180deg, #7a5433 0%, #604329 45%, #4d3420 100%)';
  const woodV = 'linear-gradient(90deg, #7a5433 0%, #604329 45%, #4d3420 100%)';
  const bar: React.CSSProperties = { position: 'absolute', boxShadow: '0 0 12px rgba(0,0,0,0.55)' };
  const plateW = Math.min(W * 0.62, 560 * u);
  return (
    <AbsoluteFill>
      <div style={{ ...bar, left: 0, top: 0, width: W, height: f, background: wood }} />
      <div style={{ ...bar, left: 0, top: 0, width: f, height: H, background: woodV }} />
      <div style={{ ...bar, right: 0, top: 0, width: f, height: H, background: woodV }} />
      <div style={{ ...bar, left: 0, bottom: 0, width: W, height: f * 1.25, background: wood }} />
      {/* the tray: two chalk pieces and an eraser */}
      <div style={{ position: 'absolute', left: W * 0.08, bottom: f * 1.25 - 4 * u, width: 34 * u, height: 9 * u, borderRadius: 4 * u, background: C.yellow, boxShadow: '0 2px 3px rgba(0,0,0,0.4)' }} />
      <div style={{ position: 'absolute', left: W * 0.08 + 40 * u, bottom: f * 1.25 - 4 * u, width: 26 * u, height: 9 * u, borderRadius: 4 * u, background: C.pink, boxShadow: '0 2px 3px rgba(0,0,0,0.4)' }} />
      <div style={{ position: 'absolute', right: W * 0.08, bottom: f * 1.25 - 6 * u, width: 90 * u, height: 16 * u, borderRadius: 3 * u, background: 'linear-gradient(180deg,#c8a87a 0 45%,#3b3b3b 45% 100%)', boxShadow: '0 2px 4px rgba(0,0,0,0.5)' }} />
      {/* the nameplate */}
      <div
        dir="rtl"
        style={{
          position: 'absolute',
          left: (W - plateW) / 2,
          bottom: 4 * u,
          width: plateW,
          height: 58 * u,
          borderRadius: 8 * u,
          background: 'linear-gradient(180deg, #5a3c22, #3f2915)',
          border: `${2 * u}px solid #b08a52`,
          boxShadow: '0 4px 10px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: RUQAA,
          fontWeight: 700,
          fontSize: 34 * u,
          color: '#F1D9A6',
          lineHeight: 1.4,
          textShadow: '0 1px 0 rgba(0,0,0,0.6)',
        }}
      >
        {TEACHER}
      </div>
      {/* chapter tag */}
      <div
        dir="rtl"
        style={{
          position: 'absolute',
          right: 46 * u,
          top: 2 * u,
          height: f + 26 * u,
          padding: `0 ${16 * u}px`,
          borderRadius: `0 0 ${10 * u}px ${10 * u}px`,
          background: 'linear-gradient(180deg, #4d3420, #3a2715)',
          border: `${1.5 * u}px solid #8f6d3e`,
          borderTop: 'none',
          display: 'flex',
          alignItems: 'center',
          gap: 12 * u,
          fontFamily: RUQAA,
          fontSize: 24 * u,
          color: '#F1D9A6',
          lineHeight: 1.4,
          boxShadow: '0 4px 8px rgba(0,0,0,0.5)',
        }}
      >
        <span style={{ fontWeight: 700 }}>{TITLE}</span>
        <span style={{ opacity: 0.6 }}>|</span>
        <span>{chapter}</span>
        {part ? (
          <>
            <span style={{ opacity: 0.6 }}>|</span>
            <span style={{ color: C.yellow }}>{`الجزء ${part}`}</span>
          </>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/** Chalk scratches under every write, whooshes between boards, sparkles where boards ask. */
const Sounds: React.FC<{ tl: Timeline }> = ({ tl }) => {
  const out: React.ReactNode[] = [];
  for (const it of tl.items) {
    if (!CHALK_SOUND || !it.sound) continue;
    const d = Math.max(1, toFrame(it.t1) - toFrame(it.t0));
    const skip = Math.floor(random(it.id + 's') * 60);
    out.push(
      <Sequence key={it.id} from={toFrame(it.t0)} durationInFrames={Math.min(d, 110)} layout="none">
        <Html5Audio src={staticFile('sfx/chalk.wav')} volume={TIMING.audio ? 0.16 : 0.35} trimBefore={skip} />
      </Sequence>,
    );
    if (it.sound === 'line')
      out.push(
        <Sequence key={it.id + 't'} from={toFrame(it.t0)} durationInFrames={6} layout="none">
          <Html5Audio src={staticFile('sfx/tap.wav')} volume={0.22} />
        </Sequence>,
      );
  }
  tl.boards.forEach((b, i) => {
    if (i > 0)
      out.push(
        <Sequence key={b.id + 'w'} from={toFrame(b.from - 0.75)} durationInFrames={40} layout="none">
          <Html5Audio src={staticFile('sfx/whoosh.wav')} volume={0.4} />
        </Sequence>,
      );
    b.sfx.forEach((s, j) =>
      out.push(
        <Sequence key={`${b.id}-s${j}`} from={toFrame(s.t)} durationInFrames={toFrame(s.dur)} layout="none">
          <Html5Audio src={staticFile(`sfx/${s.src}.wav`)} volume={s.vol} />
        </Sequence>,
      ),
    );
  });
  return <>{out}</>;
};
