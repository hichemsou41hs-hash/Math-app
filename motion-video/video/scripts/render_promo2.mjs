// Final renders of the promo, after the teacher approved it: out/promo2-16x9.mp4 and out/promo2-9x16.mp4
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "node:path";
if (!process.argv.includes("--approved")) { console.error("Not rendering: not approved."); process.exit(1); }
const browserExecutable = process.env.REMOTION_BROWSER || undefined;
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
for (const [id, file] of [["Promo2", "promo2-16x9.mp4"], ["Promo2V", "promo2-9x16.mp4"]]) {
  const composition = await selectComposition({ serveUrl, id, browserExecutable });
  let last = -1;
  await renderMedia({ serveUrl, composition, codec: "h264", crf: 18, audioBitrate: "192k", outputLocation: path.resolve("out", file), browserExecutable,
    onProgress: ({ progress }) => { const p = Math.floor(progress * 10); if (p !== last) { last = p; console.log(id, p * 10 + "%"); } } });
  console.log("done", file);
}
