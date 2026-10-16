// The final renders. Only after the user has watched the video and asked for it:
//   npm run render -- --approved            -> out/youtube.mp4 (16:9) and out/reel-1.mp4 ... out/reel-5.mp4 (9:16)
//   npm run render -- --approved --vertical-full   also out/vertical-full.mp4 (the whole lesson in 9:16)
// Set REMOTION_BROWSER to a Chrome/Chromium binary if Remotion cannot download its own.
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "node:path";

if (!process.argv.includes("--approved")) {
  console.error(
    [
      "Not rendering: the user has not approved the video yet.",
      "The rule (AGENTS.md): let the user watch it, and render only when they say so.",
      "لن يتم الرندر: المستخدم لم يوافق بعد. دعه يشاهد الفيديو، ولا ترندر إلا عندما يطلب ذلك.",
      "",
      "When they have: npm run render -- --approved",
    ].join("\n"),
  );
  process.exit(1);
}
const jobs = [["Main", "youtube.mp4"], ...[1, 2, 3, 4, 5].map((n) => [`Reel${n}`, `reel-${n}.mp4`])];
if (process.argv.includes("--vertical-full")) jobs.push(["Vertical", "vertical-full.mp4"]);
const browserExecutable = process.env.REMOTION_BROWSER || undefined;
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
for (const [id, file] of jobs) {
  const composition = await selectComposition({ serveUrl, id, browserExecutable });
  const outputLocation = path.resolve("out", file);
  let last = -1;
  await renderMedia({
    serveUrl, composition, codec: "h264", crf: 18, outputLocation, browserExecutable,
    onProgress: ({ progress }) => {
      const p = Math.floor(progress * 20);
      if (p !== last) { last = p; process.stdout.write(`\r${id}: ${Math.round(progress * 100)}%   `); }
    },
  });
  console.log(`\n${outputLocation}`);
}
