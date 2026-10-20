// A long video is also cut into reels (Instagram / Facebook / Shorts, each under 3 minutes).
// A reel starts as the camera starts moving to its first board and ends before the next reel's board.
import { TIMING, cutBefore } from './timing';
import { VIDEO } from './config';
import { Episode, useEpisode } from './episodes';

export function partStart(ep: Episode, n: number) {
  useEpisode(ep);
  return n === 1 ? 0 : cutBefore(ep.parts[n - 1]) - 0.7;
}
export function partEnd(ep: Episode, n: number) {
  useEpisode(ep);
  return n >= ep.parts.length ? TIMING.duration + VIDEO.tail : cutBefore(ep.parts[n]) - 0.7;
}
/** The first board of a reel starts at this time (boards start at cutBefore of their first line). */
export function partBoardFrom(ep: Episode, n: number) {
  useEpisode(ep);
  return n === 1 ? 0 : cutBefore(ep.parts[n - 1]);
}
