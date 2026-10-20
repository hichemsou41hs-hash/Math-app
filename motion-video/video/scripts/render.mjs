// The final renders. Only after the user has watched the video and asked for it:
//   npm run render -- --approved            -> out/youtube.mp4 (16:9) and out/reel-1.mp4 ... out/reel-5.mp4 (9:16)
//   npm run render -- --approved --vertical-full   also out/vertical-full.mp4 (the whole lesson in 9:16)
//   npm run render -- --approved --episode ex1     out/ex1-youtube.mp4, out/ex1-reel-1.mp4, out/ex1-reel-2.mp4
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
// --episode ex1 renders an exercise video: Ex1 -> ex1-youtube.mp4, Ex1R1.. -> ex1-reel-1.mp4 ..
const ei = process.argv.indexOf("--episode");
const ep = ei > 0 ? process.argv[ei + 1] : null;
const reels = Number(process.argv[process.argv.indexOf("--reels") + 1]) || (ep ? 2 : 5);
const cap = ep ? ep[0].toUpperCase() + ep.slice(1) : null;
const jobs = ep
  ? [[cap, `${ep}-youtube.mp4`], ...Array.from({ length: reels }, (_, i) => [`${cap}R${i + 1}`, `${ep}-reel-${i + 1}.mp4`])]
  : [["Main", "youtube.mp4"], ...[1, 2, 3, 4, 5].map((n) => [`Reel${n}`, `reel-${n}.mp4`])];
if (process.argv.includes("--vertical-full")) jobs.push([ep ? `${cap}V` : "Vertical", ep ? `${ep}-vertical-full.mp4` : "vertical-full.mp4"]);
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
