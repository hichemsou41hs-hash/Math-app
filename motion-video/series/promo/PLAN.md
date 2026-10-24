# Promo video (teacher's request, to be built after the remaining lessons)

Goal: sell the document packs to teachers and pupils. ONE video, 16:9.

Teacher's visual brief:
- 3D motion graphics: the camera flies between the lesson files in a 3D space, enters a file, then moves on to the next.
- Inside each lesson, the three formats appear (PDF, Word, LaTeX); each one opens and quickly shows its real content (page renders flipping / scrolling), then the camera moves to the next file.
- Cover all levels (1AS, 2AS, 3AS) and all lessons; show the three document kinds per lesson (summary, practice exercises with solutions, BAC exercises with solutions up to 2026).

Tech plan: Remotion + @remotion/three (react-three-fiber) for the 3D camera path; each file = a 3D card/folder with a texture made from real page renders (pdftoppm PNGs of the PDFs, LibreOffice exports of the .docx, a syntax-highlighted .tex snippet); camera keyframes from data, every frame a function of time (no Math.random, no CSS animations). End card: counts (lessons/exercises/pages), contact (Facebook/Telegram «الأستاذ سوايسية هشام للرياضيات», Instagram prof_hicham_math), price/how to buy (ask the teacher).
Open questions for the teacher: price and purchase method; voice (his own) or music + on-screen text; length (60–120 s).
Before selling: replace or get permission for content derived from other teachers' files (the 14 exercises in bac_nihayat_3as «تمارين بمستوى البكالوريا», the complex-numbers summary reference).
