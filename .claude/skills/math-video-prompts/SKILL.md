---
name: math-video-prompts
description: Write strong prompts for Arabic math explainer videos (Remotion, Manim, HTML-to-MP4, animation prompts) and mine the awesome-opus-5-5-video-prompts repo for techniques. Use for "math video", "فيديو", "فيديو رياضيات", Manim, Remotion, "animation prompt", explainer, lesson teaser, reel, 9:16, scene list, storyboard.
---

# Math video prompts (Arabic lessons)

Source: LeaddeOpenLab/awesome-opus-5-5-video-prompts, commit 5d5ee72 (see SOURCE.md). Link base for ids:
`https://github.com/LeaddeOpenLab/awesome-opus-5-5-video-prompts/blob/main/prompts/<id>.md`

Project rules still win: `motion-video/CLAUDE.md` and `AGENTS.md` (Remotion only, every frame a pure function of time, timing from `words.json`, no full render before the teacher approves in Studio), `series/PEDAGOGY.md`, root CLAUDE.md (curriculum order).

## 1. What the repo is, and what is useful

- 728 community prompts for video/animation/3D generation with Claude Opus 5.5, each: title, original X author, prompt text, tools, a "what is missing" note. Repro status "not_tested" for most.
- 4 MIT templates: 15-second silent 1920x1080 product-marketing animations rendered from HTML.
- Roughly 85 prompts are explainer/educational/science; about 62 mention Remotion; 12 mention Manim; only 1 is a real Manim lesson (derivatives). Almost no prompt is real school maths with proofs, tables or Arabic.
- Many math-related prompts are one-liners ("explain the Pythagorean theorem in JavaScript"). The value is in the 15 to 20 long, structured ones: they show HOW to specify a video, not what maths to show.
- Useful: prompt structure, timing language, verification loops, anti-"AI look" bans, deterministic rendering, the teaser-reel pipeline.
- Not useful: product ads, 3D worlds, music videos, anything needing paid APIs (ElevenLabs, image models) or AI-generated footage. Our kit forbids AI video; our voice is the teacher's own or edge-tts.

## 2. Patterns that make a strong math explainer prompt

1. Inputs block first. List what the agent must ask for (lesson, level, exercise, duration, voice yes/no) and the defaults if skipped. Best prompts end with "ask me, then show the plan before coding".
2. One idea per video, one sentence. "The derivative is the slope of the tangent, seen as the limit of secants." Reject lists of topics.
3. Narrative chain, arrows: write the logic as `question -> intuition -> definition -> example -> trap -> summary`. The neutrino prompt chains 13 steps with arrows so the video explains cause and effect, not just looks good.
4. Scene list with time ranges and ONE job each (hook, recall, build, example, common mistake, summary). Use ranges like `0-5s`, give each a camera/motion verb and an on-screen caption. The Tesla-motor prompt fixes duration, fps, frame count and a per-range storyboard so reruns are comparable.
5. Timing in our project: ranges are budgets only; real cues come from `words.json` (`line()`/`word()`), so the picture follows the spoken word.
6. Style tokens, few and exact: background hex, 2-3 accent hexes with ROLES (given / unknown / result), font per role, line widths, corner radius. Brand-rebuild prompt maps colors to roles instead of listing adjectives.
7. Color coding = meaning. Same object keeps same color for the whole video (f blue, tangent orange, area green, error red). Say it in the prompt.
8. Reveal order: statement of the question, then axes, then curve, then the point, then the construction, then the result box. Never show the answer with the question. Highlight one element at a time, dim the rest (Tesla prompt does this for components).
9. Camera/motion vocabulary that works in 2D: pan along the axis, zoom to a point (secant to tangent), slow push-in on the result, spring settle with tiny overshoot, draw-on stroke (write the curve left to right), morph one shape into the next (one continuous object, no cuts: UI-loop and pencil-to-atom prompts). Avoid whip pans, shake, glows.
10. Real maths, not a drawing of it: "the random walk must be an actual random walk" (photon prompt), "render the actual math" (hydrogen prompt). For us: curves from the function, tangents from the derivative, areas from the integral. Verify numbers with sympy first (PEDAGOGY rule 3).
11. Ban list in the prompt. Typical: crossfades, glows on text, particles, stock templates, `Math.random`, CSS transitions, rainbow gradients, filler text. Good prompts say what NOT to do, plus "avoid AI-slop phrasing" for on-screen text.
12. Verification loop is part of the prompt: render stills per scene (every beat or every key frame), look at each, list defects, fix, re-render; check the first and last frame, text overflow, contrast, a frame mid-transition. Our `npm run stills` does this.
13. Pacing: something changes every 3 to 5 seconds, but a formula stays on screen long enough to read aloud twice. Hold final result 1 to 2 s. Pause (a beat of silence) before a key reveal.
14. Render settings stated once: size, fps, duration, codec, audio, loop or not, deterministic seek. 16:9 = 1920x1080 for lessons and Studio review. 9:16 = 1080x1920 for reels/shorts: one formula per screen, text at least 64px, keep the middle 80 percent safe from UI overlays, hook in 3 s, captions burned in (most watch muted), one idea only, 15 to 45 s. 1:1 = 1080x1080 for posts. Make layout a function of `width/height`, not hard-coded.
15. Autonomy line for long jobs: "decide yourself, tell me the decisions at the end". For us, the opposite is the rule: ask all questions once at the start, then build without stopping.
16. Stage gates: phased milestones (plan, stills, motion, audio, final) with critique at each (hermit-crab short). Matches our "Studio first, render after approval".

## 3. Ready-to-fill prompt templates (replace `{{...}}`)

Common Arabic rules block, paste in every template:
```
Language: Modern Standard Arabic, direction RTL. Never split Arabic words into letters; use real shaping.
Fonts: Amiri for body/titles; math in KaTeX-style LTR islands (formulas always LTR, left to right, inside RTL text).
Numbers: Western digits as in the Algerian textbook; decimal comma like 0{,}3 in text.
Footer on every scene (small, bottom, never overlapping content): «الأستاذ سوايسية هشام للرياضيات» (Facebook, Telegram) · prof_hicham_math (Instagram).
Curriculum: Algerian 3AS order = sequences, exponential, logarithm, antiderivatives/integrals, probability, complex numbers, space geometry. Use NO notion that comes later than {{LESSON}} (e.g. no ln in the exponential lesson).
Spoken text equals board text word for word for every formula (Whisper aligns them).
```

### T1. Remotion lesson explainer (16:9, uses the existing kit)
```
Use the Remotion kit in motion-video/ (read AGENTS.md, STYLE.md, series/PEDAGOGY.md first). Style: {{chalkboard|whiteboard|plotter}}.
[Inputs - ask me once if missing] lesson: {{LESSON}}; branch: {{3AS sciences/math/technique}}; one idea: {{ONE_SENTENCE}}; length: {{3-8}} min; voice: {{teacher recording | edge-tts ar-SA-HamedNeural}}.
[Common Arabic rules block]
[Scenes] 1 Hook 0-8s: a question the pupil cannot yet answer. 2 Recall 8-30s: only prior knowledge: {{PRIOR}}. 3 Build: {{DEFINITION/THEOREM}} drawn step by step. 4 Worked example: {{EXERCISE}} (give each line of the solution its own reveal; "try it yourself" pause before the solution). 5 Common mistake: {{MISTAKE}} shown in red, then fixed. 6 Summary: one box with the method. Timing from words.json.
[Colors as meaning] given {{c1}}, unknown {{c2}}, result {{c3}}, error red. Same object keeps its color.
[Graph/tables] curve and tangent computed from the function, not drawn by hand; variation/sign tables complete as in a bac paper.
[Verify] compute every value with sympy before writing it on screen; run npm run stills, check each scene (overflow, Arabic shaping, formula direction, footer), list defects, fix. Do not render fully until I approve in Studio.
[Ban] crossfades, glows, particles, Math.random, CSS animations, AI video.
```

### T2. Manim lesson (16:9 clip to insert in a lesson)
```
Use ManimCE with Arabic support (skill manim-math-arabic). Scene class {{Name}}, 1920x1080, 60 fps, quality -qh.
[Common Arabic rules block, Arabic via Text with Amiri; formulas via MathTex, never Arabic inside MathTex.]
Topic: {{LESSON}} - one idea: {{ONE_SENTENCE}}. Duration {{60-120}} s.
Sequence with self.wait() cues matching the voice script {{FILE}}: 1 Axes + function {{f(x)}} (Create). 2 Moving point + secant -> tangent via ValueTracker (limit shown, not stated). 3 Result formula with Write, then Indicate. 4 Example {{EXAMPLE}} with colour-coded terms (set_color_by_tex). 5 Summary box.
Rules: only notions taught before {{LESSON}}; every number from sympy; no cuts, objects transform into each other (TransformMatchingTex); keep a stable camera, zoom only with self.camera.frame if needed.
Verify: render with -ql first, extract a still per self.wait, check Arabic direction and overlap, then -qh. Output {{name}}.mp4, silent (voice added later) unless I say edge-tts.
```

### T3. 9:16 teaser reel for a lesson (Remotion, 15-30 s)
```
Remotion composition 1080x1920, 30 fps, {{15-30}} s, captions burned in (Arabic, Amiri, >= 64px, in the safe middle area).
[Common Arabic rules block]
Hook 0-3s: a bac-style question or a surprising result about {{LESSON}} ("لماذا يتساوى ...؟"). 3-20s: ONE formula built in three reveals, one color per meaning. Last 5s: the answer withheld, call to action "الدرس الكامل في القناة" + footer «الأستاذ سوايسية هشام للرياضيات» (Facebook, Telegram) · prof_hicham_math (Instagram).
Layout is a function of width/height. Every frame = f(time). Output stills for each beat, I review, then render --approved.
```

### T4. Exercise-solution video (bac style, "try it yourself" format)
```
Remotion, 16:9. Exercise (verbatim, from the PDF/photo already transcribed and verified): {{EXERCISE_TEXT}}.
Structure: read the statement on screen; pause card "حاول بنفسك" ({{10}} s countdown); solve question by question in Algerian wording ("بيّن أن", "استنتج", "ادرس اتجاه تغير"), each step justified ("لأن", "إذن"); tables complete; graph with shaded region if integrals (relative-position row first); final box with the answer; common mistakes.
Each answer checked with sympy before display. Spoken text = board text.
```

## 4. Index of the most useful prompts

| Title | Tool | Technique learned | Link id |
|---|---|---|---|
| Manim derivatives explainer | Manim, edge-tts | The only real Manim lesson: "easy, with examples, thought-provoking" + TTS in one sentence | 2103128559174971663 |
| Pythagorean theorem explainer, 30 s | JavaScript | Minimal baseline; shows what one line yields (add structure ourselves) | 2102832558602072560 |
| Replica symmetry whiteboard animation | n/s | Two-step flow: draw whiteboard first, then "build mp4 with narration" | 2103667481139441895 |
| Riemann hypothesis explainer | ffmpeg, Kokoro, matplotlib, mpmath, pycairo | Real computation (mpmath) driving the visuals, pure-Python pipeline | 2108716885646639338 |
| Photon journey explainer (60 s) | JavaScript | Autonomous brief: simulate the real thing, honest numbers, stills review loop, reproducible source | 2103629247751618782 |
| Looping UI motion graphics | HTML, Playwright, ffmpeg | XML-like sections (inputs, direction, structure, build, gotchas, start); `seek(t)` purity; closed-form springs; one render per beat; loop = last frame equals first | 2103273003555402193 |
| Brand rebuild product sting | HTML canvas, Playwright | Frame-exact scene list, color roles, ban list, motion blur from subframes | 2104401208958230764 |
| Tesla-style motor, 40 s | Three.js | Fixed duration/fps/frames, per-range storyboard, floating labels, highlight one part at a time | 2110065587279798719 |
| Pencil tip to carbon atom | Three.js | One continuous zoom, stage list, scale bar, labels readable on mobile, loop | 2104909723443302770 |
| Build the Floor kinetic typography | HTML/SVG | Exact words and order, assigned roles per word, timestamped storyboard (useful for key-term reveals) | 2103458245213929495 |
| Neutrino explainer (long brief) | AE-style spec | Numbered sections, causal chain with arrows, "scientific accuracy" rule list, deliverables list | 2108567783789515051 |
| Math motion graphics showreel | n/s | Math as pure motion theme: shape morphs, number counters, 20 s rhythm | 2104486181853610052 |
| Solar system explainer, 3 min | Remotion, edge-tts, Three.js | High-school level wording + bilingual subtitles from edge-tts timing | 2105180179836576206 |
| Paper-cutout educational video | image model | Style + motion terms (anticipation, overshoot) + on-screen-text anti-slop rules | 2104542961081983435 |
| Polymarket explainer (HyperFrames) | HyperFrames, GSAP | Section layout: request, facts, rules, script, voice, scenes, visual, audio, deliverable; facts block avoids invented numbers | 2107594959666728991 |
| Mechanical hermit crab short | code animation | Phased milestones, character bible before code, still-frame critique | 2103793820815245507 |
| Remotion search-history timeline, 15 s | Remotion | Bullet-style timeline: spring year markers, line-art drawn on progressively | 2104466394859593915 |

(n/s = tool not specified by the source.)

## 5. The 15-second HTML template pipeline (MIT, Leadde Open Lab)

Templates: product-ui, feature-demo, product-launch, orbit-launch (a derived example). Each folder: `index.html` (editor + preview), `config.js` (copy and colors as `window.X_CONFIG = {...}`), `motion.js` (canvas scenes and a deterministic `seek(seconds)`), `render.mjs`, `check.mjs`, `package.json` (only Playwright), `example.mp4`.

How it works:
1. All text/colors/images live in `config.js`; the page draws everything on one `<canvas>` as a pure function of time `seek(t)`. Backward/forward scrubbing gives identical frames.
2. `render.mjs` opens the page headless in Chromium with `?render`, waits for `animationReady`, then loops frames 0..449: `page.evaluate(t => seek(t))`, screenshot the canvas as JPEG, pipe to ffmpeg (`image2pipe`, libx264, crf 18, yuv420p, faststart). Result: 15 s, 1920x1080, 30 fps, silent MP4.
3. Needs Node 22+, Playwright Chromium, ffmpeg. No API keys, works offline.

When to use for us: lesson teaser reels, "next lesson" cards, announcement clips, intro/outro stings, a 15 s "formula of the day". Not for lessons: our Remotion kit already does this with React, Arabic shaping, and word-timed audio.
How to adapt (do not copy files into this repo; start a separate scratch folder): keep the pattern `config + seek(t) + headless render`, change canvas to 1080x1920 for 9:16, render text with Amiri loaded via @font-face and `direction: rtl` (canvas `ctx.direction='rtl'`), add audio afterwards with ffmpeg (`-i video -i voice.mp3 -shortest`). The template itself has no RTL support or audio; expect work.
Attribution if you reuse code: "Based on templates by Leadde Open Lab, MIT License, 2026".

## 6. Quick checklist before sending any prompt

- One idea, one sentence. Level and branch named. Notions allowed listed.
- Scene list with ranges, caption and motion verb per scene.
- Style tokens (hex, fonts) with color roles; ban list.
- Spoken text = board text; sympy-verified numbers.
- Output spec: size, fps, duration, silent or voiced, 16:9 or 9:16.
- Stills review step and approval gate before the full render.
