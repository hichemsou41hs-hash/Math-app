"""Word timings from the Colab edge-tts notebook (tts/lesson_voice_colab.ipynb) -> video/src/data/words.json.

The notebook speaks tts/lines_tashkeel.txt (same words as script.txt, with diacritics and the Latin symbols
spelled out) and records edge-tts WordBoundary events. Word n of a line in timings.json is word n of the same
line in script.txt; when the counts differ, the line's time is shared out by word length.

    python3 tools/edge_to_words.py lesson_voice.zip      (or: ... voice.mp3 timings.json)
"""
import difflib, json, re, shutil, sys, zipfile
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


def key(w):
    """Compare words without diacritics, punctuation or alef forms; Latin symbols all look alike."""
    w = re.sub(r"[\u064B-\u0652\u0670\u0640]", "", w)
    w = re.sub(r"[أإآٱ]", "ا", w).replace("ى", "ي").replace("ة", "ه")
    w = re.sub(r"[^\w]", "", w)
    return "#" if re.fullmatch(r"[A-Za-z]+", w or "x") else w


def align(toks, ws):
    """Word times for the script's tokens from edge-tts boundaries that may merge or drop symbols:
    match equal words in order, then share out the time between matches by word length."""
    a = [key(t) for t in toks]
    b = [key(w["text"]) for w in ws]
    out = [None] * len(toks)
    for m in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(m.size):
            out[m.a + k] = (ws[m.b + k]["start"], ws[m.b + k]["end"])
    i = 0
    while i < len(toks):
        if out[i]:
            i += 1
            continue
        j = i
        while j < len(toks) and not out[j]:
            j += 1
        t0 = out[i - 1][1] if i else ws[0]["start"]
        t1 = out[j][0] if j < len(toks) else ws[-1]["end"]
        n = [max(1, len(key(t))) for t in toks[i:j]]
        acc = 0
        for k in range(i, j):
            s = t0 + (t1 - t0) * acc / sum(n)
            acc += n[k - i]
            out[k] = (s, t0 + (t1 - t0) * acc / sum(n))
        i = j
    return [{"w": t, "start": round(s, 3), "end": round(e, 3)} for t, (s, e) in zip(toks, out)]


def main():
    t = load(sys.argv[1:])
    script = [l.split() for l in (ROOT / "script.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    if len(script) != len(t["lines"]):
        raise SystemExit(f"script.txt has {len(script)} lines, timings.json {len(t['lines'])}")
    lines, shared = [], 0
    for toks, L in zip(script, t["lines"]):
        ws = L.get("words") or []
        if ws and len(ws) == len(toks):
            words = [{"w": tok, "start": round(w["start"], 3), "end": round(w["end"], 3)} for tok, w in zip(toks, ws)]
        elif ws:
            shared += 1
            words = align(toks, ws)
        else:
            shared += 1
            a = ws[0]["start"] if ws else L["start"]
            b = ws[-1]["end"] if ws else L["end"]
            # share the line's time by how long each word is when spoken (diacritics stripped)
            spoken = (L.get("spoken") or "").split()
            src = spoken if len(spoken) == len(toks) else toks
            n = [max(1, len(re.sub(r"[\u064B-\u0652\u0670\W]", "", x))) + 1 for x in src]
            tot, acc, words = sum(n), 0, []
            for tok, k in zip(toks, n):
                s = a + (b - a) * acc / tot
                acc += k
                words.append({"w": tok, "start": round(s, 3), "end": round(a + (b - a) * acc / tot, 3)})
        lines.append({"text": " ".join(toks), "start": words[0]["start"], "end": words[-1]["end"], "words": words})
    out = {"source": f"edge-tts {t.get('voice')} ({t.get('rate')})", "audio": "voice.mp3", "duration": round(t.get("duration") or t["totalDuration"], 3), "lines": lines}
    (ROOT / "video/src/data/words.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(lines)} lines, {shared} aligned or shared out, duration {out['duration']:.1f}s")


main()
