"""Word timings from the Colab edge-tts notebook (tts/lesson_voice_colab.ipynb) -> video/src/data/words.json.

The notebook speaks tts/lines_tashkeel.txt (same words as script.txt, with diacritics and the Latin symbols
spelled out) and records edge-tts WordBoundary events. Word n of a line in timings.json is word n of the same
line in script.txt; when the counts differ, the line's time is shared out by word length.

    python3 tools/edge_to_words.py lesson_voice.zip      (or: ... voice.mp3 timings.json)
"""
import json, shutil, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "video/public"


def load(args):
    if len(args) == 1 and args[0].endswith(".zip"):
        with zipfile.ZipFile(args[0]) as z:
            z.extract("voice.mp3", PUB)
            return json.loads(z.read("timings.json"))
    voice, timings = args
    shutil.copy(voice, PUB / "voice.mp3")
    return json.loads(Path(timings).read_text(encoding="utf-8"))


def main():
    t = load(sys.argv[1:])
    script = [l.split() for l in (ROOT / "script.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    if len(script) != len(t["lines"]):
        raise SystemExit(f"script.txt has {len(script)} lines, timings.json {len(t['lines'])}")
    lines, shared = [], 0
    for toks, L in zip(script, t["lines"]):
        ws = L["words"]
        if len(ws) == len(toks):
            words = [{"w": tok, "start": round(w["start"], 3), "end": round(w["end"], 3)} for tok, w in zip(toks, ws)]
        else:
            shared += 1
            a = ws[0]["start"] if ws else L["start"]
            b = ws[-1]["end"] if ws else L["end"]
            n = [max(1, len(x)) for x in toks]
            tot, acc, words = sum(n), 0, []
            for tok, k in zip(toks, n):
                s = a + (b - a) * acc / tot
                acc += k
                words.append({"w": tok, "start": round(s, 3), "end": round(a + (b - a) * acc / tot, 3)})
        lines.append({"text": " ".join(toks), "start": words[0]["start"], "end": words[-1]["end"], "words": words})
    out = {"source": f"edge-tts {t.get('voice')} ({t.get('rate')})", "audio": "voice.mp3", "duration": round(t["duration"], 3), "lines": lines}
    (ROOT / "video/src/data/words.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(lines)} lines, {shared} with shared-out word times, duration {out['duration']:.1f}s")


main()
