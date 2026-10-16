// The full render. Only after the user has watched the video in Studio and asked for it:
//   npm run render -- --approved
// Writes out/video.mp4.
import { execSync } from "node:child_process";

if (!process.argv.includes("--approved")) {
  console.error(
    [
      "Not rendering: the user has not approved the video yet.",
      "The rule (AGENTS.md): open Remotion Studio, let the user watch it, and render only when they say so.",
      "لن يتم الرندر: المستخدم لم يوافق بعد. افتح Remotion Studio ودعه يشاهد الفيديو، ولا ترندر إلا عندما يطلب ذلك.",
      "",
      "When they have: npm run render -- --approved",
    ].join("\n"),
  );
  process.exit(1);
}
execSync("npx remotion render src/index.ts Main out/video.mp4", { stdio: "inherit" });
