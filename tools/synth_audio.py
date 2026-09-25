"""Synthesised ambient loops for the apartment (no recordings, so nothing to license).

Every loop is seamless: noise is shaped in the frequency domain over the whole loop (a
circular filter, so the end runs straight into the start), and every tone or slow swell
completes a whole number of cycles per loop.

Writes mono 16-bit WAVs to Assets/Apartment/Audio; Unity compresses them to Vorbis.
Run: python tools/synth_audio.py
"""

import os
import wave

import numpy as np

SR = 22050
OUT = os.path.join(os.path.dirname(__file__), "..", "Assets", "Apartment", "Audio")
rng = np.random.default_rng(7)


def shaped_noise(seconds, shape):
    """Circular noise whose amplitude spectrum is shape(freqs)."""
    n = int(SR * seconds)
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec *= shape(np.maximum(f, 1.0))
    x = np.fft.irfft(spec, n)
    return x / np.max(np.abs(x))


def band(lo, hi, tilt=0.0):
    """Soft band-pass, with a tilt of `tilt` dB per octave."""
    def s(f):
        return (1 / (1 + (lo / f) ** 4)) * (1 / (1 + (f / hi) ** 4)) * (f / 1000.0) ** (tilt / 6.02)
    return s


def tone(seconds, hz, amp=1.0):
    n = int(SR * seconds)
    hz = round(hz * seconds) / seconds          # whole cycles per loop
    return amp * np.sin(2 * np.pi * hz * np.arange(n) / SR)


def swell(seconds, cycles, depth, phase=0.0):
    n = int(SR * seconds)
    return 1 - depth * 0.5 * (1 + np.cos(2 * np.pi * cycles * np.arange(n) / n + phase))


def fade_edges(x, s=0.02):
    k = int(SR * s)
    x[:k] *= np.linspace(0, 1, k)
    x[-k:] *= np.linspace(1, 0, k)
    return x


def save(name, x, peak):
    x = x / np.max(np.abs(x)) * peak
    os.makedirs(OUT, exist_ok=True)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    print("wrote", name, f"{len(x) / SR:.1f}s")


def pc_fan():
    T = 12.0
    air = shaped_noise(T, band(150, 3000, -4))
    blade = tone(T, 97, 0.10) + tone(T, 194, 0.05) + tone(T, 291, 0.02)   # ~1450 rpm, 4 blades
    return (air * 0.6 + blade) * swell(T, 3, 0.08)


def bath_fan():
    T = 10.0
    air = shaped_noise(T, band(90, 2500, -3))
    motor = tone(T, 60, 0.18) + tone(T, 120, 0.12) + tone(T, 240, 0.04)
    rattle = shaped_noise(T, band(700, 1400)) * swell(T, 13, 0.7) * 0.08
    return air + motor + rattle


def fridge():
    T = 16.0
    hum = tone(T, 60, 0.35) + tone(T, 120, 0.5) + tone(T, 180, 0.08) + tone(T, 240, 0.1)
    comp = shaped_noise(T, band(40, 400, -6)) * 0.35
    return (hum + comp) * swell(T, 2, 0.15)


def ac():
    T = 12.0
    air = shaped_noise(T, band(120, 4000, -3))
    comp = tone(T, 58, 0.25) + tone(T, 116, 0.12) + shaped_noise(T, band(30, 250, -6)) * 0.3
    return air * 0.8 + comp


def outside():
    """Distant traffic and wind swelling and fading, with a few birds now and then."""
    T = 40.0
    n = int(SR * T)
    traffic = shaped_noise(T, band(40, 900, -6)) * swell(T, 3, 0.55, 1.0) * swell(T, 7, 0.3, 2.0)
    wind = shaped_noise(T, band(200, 2500, -3)) * swell(T, 2, 0.8, 0.3) * 0.35
    x = traffic + wind
    t = np.arange(n) / SR
    birds = np.zeros(n)
    for start in (4.3, 5.1, 5.7, 17.8, 18.3, 29.6, 30.2, 30.7, 31.1):
        for k in range(rng.integers(2, 5)):
            s0 = start + k * 0.17
            d = 0.09 + 0.03 * rng.random()
            m = (t >= s0) & (t < s0 + d)
            u = (t[m] - s0) / d
            f0 = 2800 + 900 * rng.random()
            freq = f0 + 1600 * (1 - u) ** 2                       # a quick falling chirp
            ph = 2 * np.pi * np.cumsum(freq) / SR
            birds[m] += np.sin(ph) * np.sin(np.pi * u) ** 2 * (0.5 + 0.5 * rng.random())
    return x / np.max(np.abs(x)) + birds * 0.12


if __name__ == "__main__":
    save("pc_fan", pc_fan(), 0.5)
    save("bath_fan", bath_fan(), 0.6)
    save("fridge", fridge(), 0.5)
    save("portable_ac", ac(), 0.6)
    save("outside", outside(), 0.6)
