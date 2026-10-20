"""Build a Colab notebook where the teacher records an episode in his own voice (DJI microphone).

    python3 tools/make_record_notebook.py ex4        -> tts/ex4_record_colab.ipynb   (series/ex4/script.txt)
    python3 tools/make_record_notebook.py lesson     -> tts/lesson_record_colab.ipynb (script.txt)

The notebook records one line at a time (teleprompter, takes saved in Google Drive), cleans the audio,
adds the pause after each «حاول بنفسك», and finds every word's time with Whisper. It downloads
<name>_voice.zip (voice.mp3 + timings.json), which tools/edge_to_words.py imports like the TTS voices.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
name = sys.argv[1]
script = ROOT / ("script.txt" if name == "lesson" else f"series/{name}/script.txt")
lines = [l.strip() for l in script.read_text(encoding="utf-8").splitlines() if l.strip()]
title = "درس الدالة الأسية النيبيرية" if name == "lesson" else f"تمارين محلولة: الدالة الأسية — الحلقة {name[2:]}"

md = f"""# تسجيل صوت الأستاذ سوايسية هشام — {title}
**{len(lines)} جملة**، كل جملة تُسجَّل وحدها، ثم يستخرج Whisper توقيت كل كلمة فيتحرك الطباشير مع صوتك.

**قبل البدء:**
1. صِل مستقبِل DJI بالحاسوب (USB)، واستعمل **Google Chrome**، واسمح لـ Colab بالميكروفون.
2. غرفة هادئة، والميكروفون على بعد شبر من فمك.
3. **الأفضل:** Runtime ← Change runtime type ← **T4 GPU** (يجعل Whisper أسرع بكثير).

**الخطوات:** شغّل الخلايا بالترتيب.
- **الخلية 4:** لكل جملة اضغط **● ابدأ**، اقرأ، اضغط **■ إيقاف**، استمع، ثم: `Enter` التالي، `r` إعادة، `q` توقف (تُكمل لاحقًا من حيث توقفت).
- اقرأ بإيقاعك الطبيعي كما تشرح في القسم. عند «حَاوِلْ بِنَفْسِكَ» لا تنتظر: الدفتر يضيف مهلة العدّاد وحده.
- **الخلية 5:** تنظّف الصوت وتوحّد مستواه وتستخرج التوقيت، ثم تحمّل `{name}_voice.zip`. أرسله كما هو.
- **الخلية 6 (اختيارية):** لإعادة جمل محددة.

التسجيلات تُحفظ في Google Drive (`{name}_voice/clips`)، فلا يضيع شيء إن انقطع الاتصال.
"""

cell1 = """# 1) التثبيت وربط Google Drive (لحفظ التسجيلات)
!pip -q install pydub faster-whisper "audioop-lts; python_version>='3.13'"
from google.colab import drive
drive.mount('/content/drive')
"""

cell2 = f"""# 2) الإعدادات والنص (لا تغيّر ترتيب الجمل ولا عددها)
import os
NAME = {json.dumps(name)}
MIC_NAME = "DJI"        # جزء من اسم الميكروفون كما يظهر في الخلية 3
GAP = 0.6               # صمت بين الجمل في الملف النهائي (ثوانٍ)
LEAD = 0.6              # صمت في البداية
PAUSE = 5.0             # مهلة بعد «حَاوِلْ بِنَفْسِكَ» (عدّاد «أوقف الفيديو» في الفيديو)
CLIPS = f"/content/drive/MyDrive/{{NAME}}_voice/clips"
os.makedirs(CLIPS, exist_ok=True)
clip = lambda i: f"{{CLIPS}}/{{i:02d}}.wav"

LINES = [
""" + ",\n".join(" " + json.dumps(l, ensure_ascii=False) for l in lines) + """
]
print(len(LINES), "جملة —", sum(os.path.exists(clip(i)) for i in range(1, len(LINES) + 1)), "مسجَّلة سابقًا")
"""

cell3 = """# 3) اختيار الميكروفون
import json
from google.colab.output import eval_js

MICS = eval_js('''
(async () => {
  const s = await navigator.mediaDevices.getUserMedia({audio: true});
  const d = (await navigator.mediaDevices.enumerateDevices()).filter(x => x.kind === 'audioinput').map(x => x.label);
  s.getTracks().forEach(t => t.stop());
  return d;
})()
''')
for k, m in enumerate(MICS):
    print(k, m, "  ← سيُستعمل" if MIC_NAME.lower() in m.lower() else "")
if not any(MIC_NAME.lower() in m.lower() for m in MICS):
    print("⚠️ لم أجد ميكروفون DJI. غيّر MIC_NAME في الخلية 2 إلى جزء من اسمه كما يظهر أعلاه، ثم أعد تشغيل 2 و3.")
"""

cell4 = """# 4) التسجيل، جملة بعد جملة
import base64, subprocess
from pydub import AudioSegment
from pydub.silence import detect_leading_silence
from IPython.display import Audio, display, clear_output

RECORD_JS = r'''
async function recordLine(micName, idx, total, text) {
  const devs = (await navigator.mediaDevices.enumerateDevices()).filter(x => x.kind === 'audioinput');
  const dev = devs.find(x => x.label.toLowerCase().includes(micName.toLowerCase()));
  const stream = await navigator.mediaDevices.getUserMedia({audio: {
    deviceId: dev ? {exact: dev.deviceId} : undefined,
    echoCancellation: false, noiseSuppression: false, autoGainControl: false, channelCount: 1, sampleRate: 48000}});
  const box = document.createElement('div');
  box.dir = 'rtl';
  box.style = 'font: 30px/1.9 "Amiri", "Noto Naskh Arabic", serif; padding: 18px 22px; border: 2px solid #b08a52; border-radius: 14px; background: #24443a; color: #f3f1e7; margin: 8px 0';
  box.innerHTML = '<div style="font-size:16px;opacity:.75">الجملة ' + idx + ' من ' + total + (dev ? ' — ' + dev.label : ' — ⚠️ الميكروفون الافتراضي') + '</div><div>' + text + '</div>';
  const btn = document.createElement('button');
  btn.style = 'font-size: 22px; padding: 10px 26px; margin-top: 12px; border-radius: 10px; cursor: pointer';
  btn.textContent = '● ابدأ';
  box.appendChild(btn);
  document.body.appendChild(box);
  const click = () => new Promise(r => btn.onclick = r);
  await click();
  const rec = new MediaRecorder(stream);
  const chunks = [];
  rec.ondataavailable = e => chunks.push(e.data);
  rec.start();
  btn.textContent = '■ إيقاف'; btn.style.background = '#c0392b'; btn.style.color = '#fff';
  await click();
  const stopped = new Promise(r => rec.onstop = r);
  rec.stop(); await stopped;
  stream.getTracks().forEach(t => t.stop());
  btn.remove();
  const blob = new Blob(chunks);
  return await new Promise(r => { const f = new FileReader(); f.onloadend = () => r(f.result.split(',')[1]); f.readAsDataURL(blob); });
}
'''

def trim(seg, thresh=-45, keep=120):
    a = max(0, detect_leading_silence(seg, silence_threshold=thresh) - keep)
    b = max(0, detect_leading_silence(seg.reverse(), silence_threshold=thresh) - keep)
    return seg[a:len(seg) - b]

def record(i):
    b64 = eval_js(RECORD_JS + f"\\nrecordLine({json.dumps(MIC_NAME)}, {i}, {len(LINES)}, {json.dumps(LINES[i - 1])})", timeout_sec=600)
    open("/tmp/take.webm", "wb").write(base64.b64decode(b64))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "/tmp/take.webm", "-ac", "1", "-ar", "48000", "/tmp/take.wav"], check=True)
    seg = trim(AudioSegment.from_wav("/tmp/take.wav"))
    seg.export(clip(i), format="wav")
    return seg

START = 1   # من أي جملة نبدأ (الجمل المسجَّلة سابقًا تُتخطّى تلقائيًا)
ans = ""
for i in range(START, len(LINES) + 1):
    if os.path.exists(clip(i)):
        continue
    while True:
        clear_output()
        seg = record(i)
        print(f"الجملة {i}: {len(seg) / 1000:.1f} ثانية — مستوى الصوت {seg.dBFS:.0f} dBFS")
        display(Audio(clip(i)))
        ans = input("Enter = التالي ، r = إعادة ، q = توقف: ").strip().lower()
        if ans != "r":
            break
        os.remove(clip(i))
    if ans == "q":
        break
missing = [i for i in range(1, len(LINES) + 1) if not os.path.exists(clip(i))]
print("✅ كل الجمل مسجَّلة" if not missing else f"باقٍ {len(missing)} جملة: {missing}")
"""

cell5 = """# 5) تنظيف الصوت + توقيت كل كلمة (Whisper) + التجميع، ثم التحميل
import json, zipfile, subprocess
from pydub import AudioSegment
from google.colab import files
from faster_whisper import WhisperModel

missing = [i for i in range(1, len(LINES) + 1) if not os.path.exists(clip(i))]
assert not missing, f"جمل غير مسجَّلة: {missing} (أعد تشغيل الخلية 4)"

# تنظيف بمعايير البث: إزالة الهمهمة المنخفضة، إزالة ضوضاء خفيفة، ضغط لطيف، ثم مستوى صوت موحّد (-16 LUFS)
CLEAN = "highpass=f=75,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=7"
os.makedirs("clean", exist_ok=True)
for i in range(1, len(LINES) + 1):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", clip(i), "-af", CLEAN, "-ar", "48000", "-ac", "1", f"clean/{i:02d}.wav"], check=True)

try:
    import torch; gpu = torch.cuda.is_available()
except Exception:
    gpu = False
model = WhisperModel("large-v3" if gpu else "medium", device="cuda" if gpu else "cpu", compute_type="float16" if gpu else "int8")
print("Whisper:", "large-v3 على GPU" if gpu else "medium على CPU (أبطأ؛ فعّل T4 GPU لنتيجة أدق)")

full = AudioSegment.silent(duration=int(LEAD * 1000), frame_rate=48000)
out = []
for i, text in enumerate(LINES, 1):
    seg = AudioSegment.from_wav(f"clean/{i:02d}.wav").fade_in(15).fade_out(40)
    segs, _ = model.transcribe(f"clean/{i:02d}.wav", language="ar", word_timestamps=True, initial_prompt=text, vad_filter=False, beam_size=5)
    t0 = len(full) / 1000
    words = [{"text": w.word.strip(), "start": t0 + w.start, "end": t0 + w.end} for s in segs for w in (s.words or [])]
    out.append({"i": i, "spoken": text, "start": t0, "end": t0 + len(seg) / 1000, "words": words})
    pause = GAP + (PAUSE if "حَاوِلْ بِنَفْسِكَ" in text else 0)
    full += seg + AudioSegment.silent(duration=int(pause * 1000), frame_rate=48000)
    print(f"{i:02d}  {len(seg) / 1000:5.1f}s  {len(words)} كلمة")

full.export("voice.mp3", format="mp3", bitrate="192k")
json.dump({"voice": "teacher-dji", "rate": "", "gap": GAP, "duration": len(full) / 1000, "lines": out},
          open("timings.json", "w"), ensure_ascii=False, indent=1)
with zipfile.ZipFile(f"{NAME}_voice.zip", "w") as z:
    z.write("voice.mp3"); z.write("timings.json")
print("المدة:", round(len(full) / 1000), "ثانية")
display(Audio("voice.mp3"))
files.download(f"{NAME}_voice.zip")
"""

cell6 = """# 6) (اختياري) إعادة جمل محددة: اكتب أرقامها ثم شغّل هذه الخلية، ثم الخلية 5 من جديد
REDO = []   # مثال: [4, 28]
for i in REDO:
    while True:
        clear_output()
        seg = record(i)
        display(Audio(clip(i)))
        if input("Enter = حفظ ، r = إعادة: ").strip().lower() != "r":
            break
"""


def cell(kind, src):
    c = {"cell_type": kind, "metadata": {}, "source": src.splitlines(keepends=True)}
    if kind == "code":
        c.update(outputs=[], execution_count=None)
    return c


nb = {"nbformat": 4, "nbformat_minor": 0,
      "metadata": {"colab": {"provenance": []}, "kernelspec": {"name": "python3", "display_name": "Python 3"},
                   "language_info": {"name": "python"}, "accelerator": "GPU"},
      "cells": [cell("markdown", md), cell("code", cell1), cell("code", cell2), cell("code", cell3),
                cell("code", cell4), cell("code", cell5), cell("code", cell6)]}
dest = ROOT / f"tts/{name}_record_colab.ipynb"
dest.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(dest.relative_to(ROOT), len(lines), "lines")
