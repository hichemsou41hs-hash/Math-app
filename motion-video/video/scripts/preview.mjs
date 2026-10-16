// A small, low-quality preview clip for review (allowed at any time, like stills):
//   npm run preview -- Main 0 45          -> out/preview-Main-0-45.mp4 (half size)
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "node:path";

const [id = "Main", a = "0", b = "30"] = process.argv.slice(2);
const browserExecutable = process.env.REMOTION_BROWSER || undefined;
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id, browserExecutable });
const fps = composition.fps;
const from = Math.max(0, Math.round(Number(a) * fps));
const to = Math.min(composition.durationInFrames - 1, Math.round(Number(b) * fps) - 1);
const outputLocation = path.resolve("out", `preview-${id}-${a}-${b}.mp4`);
let last = -1;
await renderMedia({
  serveUrl, composition, codec: "h264", crf: 30, scale: Number(process.env.SCALE ?? 0.5), frameRange: [from, to], outputLocation, browserExecutable,
  onProgress: ({ progress }) => {
    const p = Math.floor(progress * 10);
    if (p !== last) { last = p; process.stdout.write(`\r${Math.round(progress * 100)}%   `); }
  },
});
console.log(`\n${outputLocation}`);
