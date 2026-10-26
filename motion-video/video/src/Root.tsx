import React from 'react';
import { Composition } from 'remotion';
import { HOLD, Video } from './Video';
import { VIDEO } from './config';
import { durationFrames, toFrame } from './timing';
import { partEnd, partStart } from './parts';
import { EPISODES } from './episodes';
import { Promo, PROMO_SECONDS } from './promo/Promo';

// For every video: <Id> 16:9 (YouTube), <Id>V 9:16 whole, <Id>R1… 9:16 reels.
// The lesson keeps its first names: Main, Vertical, Reel1..Reel5.
export const Root: React.FC = () => (
  <>
    <Composition id="Promo" component={Promo} durationInFrames={PROMO_SECONDS * VIDEO.fps} fps={VIDEO.fps} width={1920} height={1080} />
    {Object.values(EPISODES).map((ep) => {
      const name = ep.id === 'lesson' ? { main: 'Main', vert: 'Vertical', reel: 'Reel' } : { main: cap(ep.id), vert: cap(ep.id) + 'V', reel: cap(ep.id) + 'R' };
      const full = durationFrames(ep.timing);
      return (
        <React.Fragment key={ep.id}>
          <Composition id={name.main} component={Video} durationInFrames={full} fps={VIDEO.fps} width={1920} height={1080} defaultProps={{ episode: ep.id }} />
          <Composition id={name.vert} component={Video} durationInFrames={full} fps={VIDEO.fps} width={1080} height={1920} defaultProps={{ episode: ep.id }} />
          {ep.parts.map((_, i) => (
            <Composition
              key={i}
              id={`${name.reel}${i + 1}`}
              component={Video}
              durationInFrames={Math.max(1, toFrame(partEnd(ep, i + 1) - partStart(ep, i + 1) + (i + 1 < ep.parts.length ? HOLD : 0)))}
              fps={VIDEO.fps}
              width={1080}
              height={1920}
              defaultProps={{ episode: ep.id, part: i + 1 }}
            />
          ))}
        </React.Fragment>
      );
    })}
  </>
);

function cap(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}
