// The whole video: the soundtrack, then one <Sequence> per scene (scenes live in src/scenes/).
// A scene's start and end come from the script (cutBefore), never from typed-in seconds.
//
//   import { Hook } from './scenes/Hook';      // export const Hook: React.FC<{ from: number }>
//   const SCENES: Scene[] = [
//     { id: 'hook', from: 0, to: cutBefore('السطر الثاني'), C: Hook },
//     ...
//   ];
import React from 'react';
import { AbsoluteFill, Html5Audio, Sequence, staticFile } from 'remotion';
import { TIMING, toFrame } from './timing';

type Scene = { id: string; from: number; to: number; C: React.FC<{ from: number }> };
const SCENES: Scene[] = [];

export const Video: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: '#000' }}>
    {TIMING.audio ? <Html5Audio src={staticFile(TIMING.audio)} /> : null}
    {SCENES.map((s) => (
      <Sequence key={s.id} name={s.id} from={toFrame(s.from)} durationInFrames={Math.max(1, toFrame(s.to) - toFrame(s.from))} premountFor={30}>
        <s.C from={s.from} />
      </Sequence>
    ))}
    {SCENES.length === 0 ? (
      <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', color: '#888', fontFamily: 'sans-serif', fontSize: 40 }}>
        No scenes yet: the agent builds them in src/scenes/
      </AbsoluteFill>
    ) : null}
  </AbsoluteFill>
);
