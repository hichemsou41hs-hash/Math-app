// Every video made with this chalkboard: the lesson and the exercise series. Each has its own narration timing
// (words.json), boards and reels.
import { Board } from './lib/engine';
import { LESSON_KEYS, LESSON_TIMING, Timing, setTiming } from './timing';
import { buildBoards as lessonBoards } from './boards';
import ex1Data from './data/ex1.words.json';
import { buildEx1 } from './episodes/ex1';
import ex2Data from './data/ex2.words.json';
import { buildEx2 } from './episodes/ex2';
import ex3Data from './data/ex3.words.json';
import { buildEx3 } from './episodes/ex3';
import ex4Data from './data/ex4.words.json';
import { buildEx4 } from './episodes/ex4';
import bac1Data from './data/bac1.words.json';
import { buildBac1 } from './episodes/bac1';

export interface Episode {
  id: string;
  /** Left part of the chapter tag. */
  title: string;
  /** Shown after the chapter, e.g. «الحلقة 1 من 5». */
  badge?: string;
  timing: Timing;
  keys: string[];
  build: (P: boolean, W: number, H: number) => Board[];
  /** First words of the line that opens each reel. */
  parts: string[];
}

export const EPISODES: Record<string, Episode> = {
  lesson: {
    id: 'lesson',
    title: 'الدالة الأسية النيبيرية',
    timing: LESSON_TIMING,
    keys: LESSON_KEYS,
    build: lessonBoards,
    parts: ['السلام عليكم', 'نشوفو الخواص', 'المشتقة: e أس x برايم', 'نجيو للنهايات الشهيرة', 'نحلو المعادلات'],
  },
  ex1: {
    id: 'ex1',
    title: 'تمارين محلولة: الدالة الأسية',
    badge: 'الحلقة 1 من 5',
    timing: ex1Data as Timing,
    keys: [],
    build: buildEx1,
    parts: ['السلام عليكم', 'التمرين الرابع'],
  },
  ex2: {
    id: 'ex2',
    title: 'تمارين محلولة: الدالة الأسية',
    badge: 'الحلقة 2 من 5',
    timing: ex2Data as Timing,
    keys: [],
    build: buildEx2,
    parts: ['السلام عليكم', 'التمرين الرابع'],
  },
  ex3: {
    id: 'ex3',
    title: 'تمارين محلولة: الدالة الأسية',
    badge: 'الحلقة 3 من 5',
    timing: ex3Data as Timing,
    keys: [],
    build: buildEx3,
    parts: ['السلام عليكم', 'التمرين الثالث', 'التمرين الخامس'],
  },
  ex4: {
    id: 'ex4',
    title: 'تمارين محلولة: الدالة الأسية',
    badge: 'الحلقة 4 من 5',
    timing: ex4Data as Timing,
    keys: [],
    build: buildEx4,
    parts: ['السلام عليكم', 'المشتقة: f بريم', 'التمرين الثاني'],
  },
  bac1: {
    id: 'bac1',
    title: 'حلول تمارين البكالوريا: الدالة الأسية',
    badge: 'الحلقة 1',
    timing: bac1Data as Timing,
    keys: [],
    build: buildBac1,
    parts: ['السلام عليكم', 'السؤال الثاني', 'ثم: استنتج', 'السؤال الثالث', 'السؤال الرابع', 'السؤال الخامس'],
  },
};

/** Make an episode's narration the one that line()/word()/cutBefore() read. */
export function useEpisode(ep: Episode) {
  setTiming(ep.timing, ep.keys);
}
