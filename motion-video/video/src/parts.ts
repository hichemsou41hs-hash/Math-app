// The vertical video is also cut into five reels (Instagram / Facebook / Shorts, each under 3 minutes).
// A reel starts as the camera starts moving to its first board and ends before the next reel's board.
import { TIMING, cutBefore } from './timing';
import { VIDEO } from './config';

export const PART_LINES = ['السلام عليكم', 'نشوفو الخواص', 'المشتقة: e أس x برايم', 'نجيو للنهايات الشهيرة', 'نحلو المعادلات'];

export function partStart(n: number) {
  return n === 1 ? 0 : cutBefore(PART_LINES[n - 1]) - 0.7;
}
export function partEnd(n: number) {
  return n >= PART_LINES.length ? TIMING.duration + VIDEO.tail : cutBefore(PART_LINES[n]) - 0.7;
}
/** The first board of a reel starts at this time (boards start at cutBefore of their first line). */
export function partBoardFrom(n: number) {
  return n === 1 ? 0 : cutBefore(PART_LINES[n - 1]);
}
