"""Chalk sounds for the chalkboard style: video/public/sfx/chalk.wav (a 4 s scratch to trim) and tap.wav.
Coarse noise 0.7-4.5 kHz, short grain crackles, and pressure pulses at 7-11 Hz (STYLE.md section 9).
    uv run --no-project --with numpy python tools/chalk_sfx.py
"""
import wave
from pathlib import Path
import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def write(p: Path, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.7
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def chalk(d=4.0):
    n = int(SR * d)
    t = np.arange(n) / SR
    x = band(rng.standard_normal(n), 700, 4500)
    rate = 9 + 2 * np.sin(2 * np.pi * 0.37 * t)
    press = 0.55 + 0.45 * np.maximum(0, np.sin(2 * np.pi * np.cumsum(rate) / SR)) ** 0.6
    grains = np.zeros(n)
    for i in rng.integers(0, n - 200, int(d * 90)):
        grains[i:i + 120] += rng.standard_normal(120) * np.exp(-np.arange(120) / 25)
    y = x * press + band(grains, 1500, 7000) * 0.8
    f = np.minimum(1, np.minimum(t / 0.02, (d - t) / 0.05))
    return y * f


def tap(d=0.12):
    n = int(SR * d)
    t = np.arange(n) / SR
    y = band(rng.standard_normal(n), 300, 3000) * np.exp(-t / 0.012) + np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.02) * 0.6
    return y


out = Path("video/public/sfx"); out.mkdir(parents=True, exist_ok=True)
write(out / "chalk.wav", chalk())
write(out / "tap.wav", tap())
print("wrote chalk.wav, tap.wav")
