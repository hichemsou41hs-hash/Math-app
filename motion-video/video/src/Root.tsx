import React from 'react';
import { Composition } from 'remotion';
import { HOLD, Video } from './Video';
import { VIDEO } from './config';
import { DURATION_FRAMES, toFrame } from './timing';
import { PART_LINES, partEnd, partStart } from './parts';

// Main: YouTube (16:9). Vertical: the same lesson in 9:16. Reel1..Reel5: the vertical lesson in five parts.
export const Root: React.FC = () => (
  <>
    <Composition id="Main" component={Video} durationInFrames={DURATION_FRAMES} fps={VIDEO.fps} width={1920} height={1080} defaultProps={{}} />
    <Composition id="Vertical" component={Video} durationInFrames={DURATION_FRAMES} fps={VIDEO.fps} width={1080} height={1920} defaultProps={{}} />
    {PART_LINES.map((_, i) => (
      <Composition
        key={i}
        id={`Reel${i + 1}`}
        component={Video}
        durationInFrames={Math.max(1, toFrame(partEnd(i + 1) - partStart(i + 1) + (i + 1 < PART_LINES.length ? HOLD : 0)))}
        fps={VIDEO.fps}
        width={1080}
        height={1920}
        defaultProps={{ part: i + 1 }}
      />
    ))}
  </>
);
