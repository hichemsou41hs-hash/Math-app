// Single frames for checking a detail without rendering the video (allowed at any time).
//   npm run stills -- 4.2 12 30.5          -> out/stills/t004.20.png ... (half size)
//   SCALE=1 npm run stills -- 12           -> full size
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import { mkdir, rm } from "node:fs/promises";
import path from "node:path";

const secs = process.argv.slice(2).map(Number).filter((n) => Number.isFinite(n));
if (!secs.length) {
  console.error("usage: npm run stills -- <seconds> [<seconds> ...]");
  process.exit(1);
}
const out = path.resolve("out/stills");
await mkdir(out, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const id = process.env.COMP ?? "Main";
const browserExecutable = process.env.REMOTION_BROWSER || undefined;
const composition = await selectComposition({ serveUrl, id, browserExecutable });
for (const s of secs) {
  const frame = Math.min(composition.durationInFrames - 1, Math.max(0, Math.round(s * composition.fps)));
  const file = path.join(out, `${id}-t${s.toFixed(2).padStart(6, "0")}.png`);
  await renderStill({ serveUrl, composition, frame, output: file, scale: Number(process.env.SCALE ?? 0.5), browserExecutable });
  console.log(file);
}
await rm(serveUrl, { recursive: true, force: true });
