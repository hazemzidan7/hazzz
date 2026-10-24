"""Original instrumental soundtrack for the reel (generated from scratch, no samples).
120 BPM, 22.5 bars = 45 s. Sections: intro 0-4, build 4-12, groove 12-28, break 28-30, peak 30-40, outro 40-45."""
import numpy as np, wave, sys
SR = 48000; BPM = 120; BEAT = 60 / BPM; BAR = 4 * BEAT; DUR = 45.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def t(n): return np.arange(n) / SR
def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[: N - i]; buf[i:i + len(sig)] += sig * gain
def addst(start, sig, g=1.0, pan=0.0):
    add(L, start, sig, g * np.cos((pan + 1) * np.pi / 4) * 1.414)
    add(R, start, sig, g * np.sin((pan + 1) * np.pi / 4) * 1.414)
def midi(m): return 440 * 2 ** ((m - 69) / 12)
def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    # vectorised one-pole via lfilter-like recursion
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)
def onepole_hp(x, fc):
    return x - lowpass(x, fc)
def saw(f, n, detune=(0,)):
    tt = t(n); out = 0
    for d in detune:
        ff = f * 2 ** (d / 1200); out = out + 2 * ((tt * ff + rng.random()) % 1) - 1
    return out / len(detune)
def env_adsr(n, a, d, s, r):
    e = np.ones(n) * s; ai = int(a * SR); di = int(d * SR); ri = int(r * SR)
    e[:ai] = np.linspace(0, 1, ai) if ai else 1
    e[ai:ai + di] = np.linspace(1, s, len(e[ai:ai + di]))
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e

# --- drums ---
def kick(big=False):
    n = int(0.5 * SR); tt = t(n)
    f = 45 + 110 * np.exp(-tt * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    k = np.sin(ph) * np.exp(-tt * (5 if big else 7))
    k += 0.3 * np.exp(-tt * 300) * rng.standard_normal(n)
    return np.tanh(k * 1.6)
def clap():
    n = int(0.35 * SR); tt = t(n); nz = rng.standard_normal(n)
    e = np.exp(-tt * 18) + sum(np.exp(-(tt - o) * 120) * (tt >= o) for o in (0.0, 0.012, 0.024))
    return onepole_hp(nz, 900) * e * 0.5
def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); tt = t(n)
    return onepole_hp(rng.standard_normal(n), 7000) * np.exp(-tt * (14 if open_ else 70))
def impact():
    n = int(4.5 * SR); tt = t(n)
    boom = np.sin(2 * np.pi * np.cumsum(35 + 60 * np.exp(-tt * 6)) / SR) * np.exp(-tt * 1.2)
    nz = lowpass(rng.standard_normal(n), 1500) * np.exp(-tt * 2.5)
    return np.tanh(1.5 * boom) * 0.9 + nz * 0.4
def riser(dur):
    n = int(dur * SR); tt = t(n); x = rng.standard_normal(n)
    out = np.zeros(n); seg = int(0.05 * SR)
    for i in range(0, n, seg):  # sweeping filtered noise
        fc = 300 + 9000 * (i / n) ** 2
        out[i:i + seg] = onepole_hp(x[i:i + seg], fc * 0.3)
    return out * (tt / dur) ** 2

# --- harmony: Am - F - C - G (i-VI-III-VII), cinematic/uplifting ---
prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
bass_root = [45, 41, 48, 43]

def pad_chord(notes, dur, bright):
    n = int(dur * SR); s = 0
    for m in notes + [notes[0] + 12]:
        s = s + saw(midi(m), n, detune=(-9, 0, 9))
    s = lowpass(s, bright) * env_adsr(n, 0.4, 0.3, 0.8, 0.6)
    return s * 0.12
def arp(notes, dur, step, bright, gain):
    out = np.zeros(int(dur * SR)); seq = notes + [notes[0] + 12, notes[1] + 12]
    k = 0; pos = 0.0
    while pos < dur - 1e-6:
        m = seq[k % len(seq)] + 12; n = int(step * 0.9 * SR)
        s = saw(midi(m), n, detune=(-5, 5)) * np.exp(-t(n) * 9)
        s = lowpass(s, bright); i = int(pos * SR); out[i:i + n] += s[: len(out) - i]
        k += 1; pos += step
    return out * gain
def bassline(root, dur, step):
    out = np.zeros(int(dur * SR)); pos = 0.0
    while pos < dur - 1e-6:
        n = int(step * 0.85 * SR); f = midi(root)
        s = (np.sin(2 * np.pi * f * t(n)) + 0.5 * lowpass(saw(f, n), 400)) * env_adsr(n, 0.005, 0.1, 0.7, 0.04)
        i = int(pos * SR); out[i:i + n] += s[: len(out) - i]; pos += step
    return out * 0.35

def section(b0, b1):
    return [(b, b * BAR) for b in range(b0, b1)]

nbars = int(np.ceil(DUR / BAR))
for b in range(nbars):
    st = b * BAR; c = b % 4; tsec = st
    in_intro = tsec < 4; in_build = 4 <= tsec < 12; in_groove = 12 <= tsec < 28
    in_break = 28 <= tsec < 30; in_peak = 30 <= tsec < 40; in_outro = tsec >= 40
    if in_outro: continue
    bright = 900 if in_intro else 1600 if in_build else 2600 if in_groove else 1200 if in_break else 4200
    addst(st, pad_chord(prog[c], BAR + 0.5, bright), 1.0 if not in_peak else 1.15)
    if not in_intro:
        addst(st, arp(prog[c], BAR, BEAT / 4 if (in_peak or in_groove) else BEAT / 2, 3000 if in_peak else 2000, 0.07), 1, pan=0.35)
        addst(st + BEAT / 8, arp(prog[c], BAR - BEAT / 8, BEAT / 2, 1500, 0.04), 1, pan=-0.4)
    if in_groove or in_peak:
        addst(st, bassline(bass_root[c], BAR, BEAT / 2))
    for q in range(4):
        bt = st + q * BEAT
        if in_build or in_groove or in_peak:
            addst(bt, kick(), 0.9 if in_build else 1.0)
        if (in_groove or in_peak) and q in (1, 3):
            addst(bt, clap(), 0.55)
        if in_groove or in_peak:
            addst(bt + BEAT / 2, hat(open_=in_peak), 0.18, pan=0.2)
            if in_peak: addst(bt + BEAT / 4, hat(), 0.08, pan=-0.2); addst(bt + 3 * BEAT / 4, hat(), 0.08, pan=-0.2)
        if in_build and tsec >= 8:
            addst(bt + BEAT / 2, hat(), 0.12)
    if in_break:  # snare roll + riser into the peak
        for k in range(16):
            addst(st + k * BAR / 16, clap(), 0.15 + 0.35 * k / 16)
# intro riser into the build and the break riser into the peak
addst(2.0, riser(2.0), 0.25)
addst(28.0, riser(2.0), 0.35)
addst(10.0, riser(2.0), 0.18)
# impacts on section downbeats
addst(0.0, impact(), 0.55)
addst(12.0, kick(big=True), 0.6)
addst(30.0, impact(), 0.7)
# outro: final big hit + long chord tail ending exactly at 45 s
addst(40.0, impact(), 0.8)
tail = pad_chord([57, 60, 64, 69], 5.0, 2200)
tail *= np.linspace(1, 0, len(tail)) ** 1.5
addst(40.0, tail, 1.4)
addst(40.0, arp([57, 60, 64], 2.0, BEAT / 4, 2500, 0.06) * np.linspace(1, 0, int(2.0 * SR)), 1, pan=0.3)

# sidechain-style ducking of pads/arps on kicks for groove (applied to whole mix lightly)
duck = np.ones(N)
for k in np.arange(4, 40, BEAT):
    if 28 <= k < 30: continue
    i = int(k * SR); n = int(0.25 * SR)
    duck[i:i + n] = np.minimum(duck[i:i + n], 0.75 + 0.25 * np.linspace(0, 1, len(duck[i:i + n])))
mix = np.stack([L * duck, R * duck])
# master: gentle glue, normalise, soft limit, fade last 60 ms, fade-in 10 ms
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) 
mix = mix / np.max(np.abs(mix)) * 0.89
mix[:, -int(0.06 * SR):] *= np.linspace(1, 0, int(0.06 * SR))
mix[:, :int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
pcm = (mix.T * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote", sys.argv[1], DUR, "s")
