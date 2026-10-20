"""Add a breath of silence before the lines that open a new board, in the voice and the word timings together.

    python3 tools/pad_sections.py ex4 1.2 "التمرين" "المشتقة" "وبما أن" "المماس" "الخلاصة"

A line opens a board when its text (diacritics stripped) starts with one of the given prefixes. Used when a
recorded voice is faster than the boards' writing and the console reports LATE boards.
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ep, sec, prefixes = sys.argv[1], float(sys.argv[2]), tuple(sys.argv[3:])
words_path = ROOT / f"video/src/data/{ep}.words.json"
voice = ROOT / f"video/public/{ep}/voice.mp3"

strip = lambda s: re.sub(r"[ً-ْٰ]", "", s)
d = json.loads(words_path.read_text(encoding="utf-8"))
cuts = [L["start"] for i, L in enumerate(d["lines"]) if i and strip(L["text"]).startswith(prefixes)]
if not cuts:
    sys.exit("no line starts with these prefixes")

# a cut sits just before its line, in the gap after the previous line
gaps = []
for i, L in enumerate(d["lines"]):
    if i and L["start"] in cuts:
        gaps.append((d["lines"][i - 1]["end"] + L["start"]) / 2)

with tempfile.TemporaryDirectory() as tmp:
    parts, t = [], 0.0
    sil = Path(tmp) / "sil.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono", "-t", str(sec), str(sil)], check=True)
    for k, g in enumerate(gaps + [None]):
        part = Path(tmp) / f"p{k}.wav"
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(voice), "-ss", str(t)] + (["-to", str(g)] if g else []) + ["-ar", "48000", "-ac", "1", str(part)]
        subprocess.run(cmd, check=True)
        parts.append(part)
        if g:
            parts.append(sil)
            t = g
    lst = Path(tmp) / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    out = Path(tmp) / "voice.mp3"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-b:a", "192k", str(out)], check=True)
    voice.write_bytes(out.read_bytes())

shift = lambda x: x + sec * sum(1 for g in gaps if g < x)
for L in d["lines"]:
    for w in L["words"]:
        w["start"], w["end"] = round(shift(w["start"]), 3), round(shift(w["end"]), 3)
    L["start"], L["end"] = L["words"][0]["start"], L["words"][-1]["end"]
d["duration"] = round(d["duration"] + sec * len(gaps), 3)
words_path.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(gaps)} breaths of {sec}s added; duration {d['duration']}s")
