# trilha: batida da v1 (bumbo/chimbal/grave/arpejo/pad) + Elgar "Pomp and Circumstance" nº1 tomando espaço
# até o final majestoso; clique corta tudo + som de TV desligando. Depois mixa com a voz -> mix.wav
import subprocess, numpy as np, soundfile as sf, librosa
from beats import BEATS, END, TL, T_OFF, HITS

SR = 48000; N = int(END * SR) + SR
rng = np.random.default_rng(0)
t_all = np.arange(N) / SR

def lp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** 4), len(x))
def hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X * (1 - 1 / np.sqrt(1 + (f / fc) ** 4)), len(x))
def noise(d): return rng.normal(0, 1, int(d * SR))
def ramp(a, b, x): return np.clip((x - a) / (b - a), 0, 1)

# ---------------- clássica: Carl Orff, "O Fortuna" (Carmina Burana) ----------------
# acorde de abertura cai na pancada de "Distribuição é PODER"; o fortíssimo final termina no clique do CTA
from beats import w as _w, F1 as _F1
CH_FILE, END_FILE = 1.25, 157.5                       # acorde inicial e último acorde no arquivo (s)
t_chord = _w("poder", 2) - _F1
SPEED = (END_FILE - CH_FILE) / (T_OFF - t_chord)        # ~1,02-1,03x
PRE = 0.25
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{CH_FILE - PRE:.3f}", "-i", "musica/ofortuna.wav", "-af", f"atempo={SPEED:.5f}", "-ar", str(SR), "-ac", "2",
                "musica/classic_fit.wav"], check=True)
cl, _ = sf.read("musica/classic_fit.wav")
classic = np.zeros((N, 2)); i0 = int((t_chord - PRE / SPEED) * SR); n_ = min(N - i0, len(cl)); classic[i0:i0 + n_] = cl[:n_]
mt = (t_all - t_chord) * SPEED + CH_FILE                 # tempo da música em cada instante do vídeo
print("O Fortuna: speed", round(SPEED, 4), "acorde em", round(t_chord, 2), "s")

# grade de tempo da própria peça (a batida segue a orquestra)
_y, _sr = librosa.load("musica/classic_fit.wav", sr=22050, mono=True)
_, _b = librosa.beat.beat_track(y=_y, sr=_sr, units="time", tightness=80)
_b = _b + (t_chord - PRE / SPEED)  # para o tempo do vídeo
_ibi = np.diff(_b); grid = [float(_b[0])]
while grid[-1] < END + 1:
    k = np.searchsorted(_b, grid[-1]); near = _ibi[max(0, k - 4):k + 4]
    step = float(np.median(near)) if len(near) else 0.5
    cand = _b[(_b > grid[-1] + step * 0.8) & (_b < grid[-1] + step * 1.2)]
    grid.append(float(cand[0]) if len(cand) else grid[-1] + step)
while grid[0] - (grid[1] - grid[0]) > 0: grid.insert(0, grid[0] - (grid[1] - grid[0]))

# ---------------- batida da v1 (progressão vi-IV-I-V em Ré: Bm G D A) ----------------
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
roots = [50, 50, 46, 45]; tri = [[0, 3, 7], [0, 3, 7], [0, 4, 7], [0, 4, 7]]  # Ré menor: Dm Dm Bb A (tom do O Fortuna)
kick, bass, hat, arp, pad = (np.zeros(N) for _ in range(5))
for b, t0 in enumerate(grid[:-1]):
    i0 = int(t0 * SR); step = grid[b + 1] - t0
    if i0 >= N: break
    ch = (b // 8) % 4; r = roots[ch]
    seg = np.arange(min(int(0.45 * SR), N - i0)) / SR
    kick[i0:i0 + len(seg)] += np.sin(2 * np.pi * np.cumsum(110 * np.exp(-seg * 22) + 42) / SR) * np.exp(-seg * 7) * 0.9
    for half in (0, 1):
        j = int((t0 + half * step / 2) * SR); m = int(step / 2 * SR * 0.9); s2 = np.arange(max(0, min(m, N - j))) / SR
        bass[j:j + len(s2)] += np.sin(2 * np.pi * hz(r - 24) * s2) * np.exp(-s2 * 5) * 0.5
    j = int((t0 + step / 2) * SR); m = int(0.04 * SR)
    if j + m < N: hat[j:j + m] += rng.normal(0, 1, m) * np.exp(-np.arange(m) / SR / 0.012) * 0.25
    for q in range(4):
        j = int((t0 + q * step / 4) * SR); m = int(0.18 * SR); s2 = np.arange(max(0, min(m, N - j))) / SR
        note = r + 12 + tri[ch][(b * 4 + q) % 3] + (12 if q == 3 else 0)
        arp[j:j + len(s2)] += (np.abs(2 * ((s2 * hz(note)) % 1) - 1) * 2 - 1) * np.exp(-s2 * 18) * 0.06
    if b % 8 == 0:
        n = int(8 * step * SR); s2 = np.arange(max(0, min(n, N - i0))) / SR
        for iv in tri[ch]:
            for det in (-0.08, 0.08):
                pad[i0:i0 + len(s2)] += (2 * ((s2 * hz(r + iv) * 2 ** (det / 12)) % 1) - 1) * 0.05
        pad[i0:i0 + len(s2)] *= np.clip(np.minimum(s2 / 0.6, (n / SR - s2) / 0.6), 0, 1)
hat = hp(hat, 7000); arp = lp(arp, 3500); pad = lp(pad, 1400)
drums_on = np.ones(N)
for a_, b_ in [(TL["ia3"]["t0"], TL["ouvir"]["t0"]), (TL["poder"]["t0"], TL["nomes"]["t0"])]: drums_on[int(a_ * SR):int(b_ * SR)] = 0
drums_on = np.convolve(drums_on, np.ones(2400) / 2400, "same")
tonal_on = 1 - ramp(0.40 * T_OFF, 0.72 * T_OFF, t_all)          # arpejo/pad saem quando a orquestra toma conta
beat = (kick * 0.8 + bass * 0.7 + hat) * drums_on + (arp + pad) * tonal_on

# ---------------- sfx ----------------
sfx = np.zeros(N)
def add(t, x, g):
    i = int(t * SR)
    if i < 0: x = x[-i:]; i = 0
    j = min(i + len(x), N); sfx[i:j] += x[:j - i] * g
def whoosh(d=0.32):
    n = lp(hp(noise(d), 400), 3000); return n * np.sin(np.linspace(0, np.pi, len(n))) ** 2 / (np.abs(n).max() + 1e-9)
def pop():
    s = np.arange(int(0.09 * SR)) / SR; return np.sin(2 * np.pi * np.cumsum(700 * np.exp(-s * 25) + 250) / SR) * np.exp(-s * 40)
def impact():
    s = np.arange(int(1.1 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(70 * np.exp(-s * 4) + 32) / SR) * np.exp(-s * 3.2) + lp(noise(1.1), 2500) * np.exp(-s * 18) * 0.6
def click(): n = hp(noise(0.012), 3000); return n * np.exp(-np.arange(len(n)) / SR / 0.003) / 3
def glitchs(): n = np.round(noise(0.07) * 3) / 3; return hp(n, 1500) * 0.5
def riser(d=1.2):
    n = noise(d); s = np.arange(len(n)) / SR; out = np.zeros_like(n)
    for k in range(6):
        a, b = int(k * len(n) / 6), int((k + 1) * len(n) / 6); out[a:b] = lp(n, 500 + 1500 * k)[a:b]
    return out * (s / d) ** 2 * 0.6
def braam(f0=55.0, d=1.6):  # pancada de trailer: sub + estalo + metais graves
    s = np.arange(int(d * SR)) / SR
    sub = np.sin(2 * np.pi * np.cumsum(f0 * 1.6 * np.exp(-s * 6) + f0) / SR) * np.exp(-s * 2.2)
    brass = sum((2 * ((s * f0 * m * (1 + 0.004 * k)) % 1) - 1) for m in (1, 1.5, 2, 3) for k in (-1, 1)) / 8
    brass = lp(brass, 900) * np.minimum(s / 0.03, 1) * np.exp(-s * 1.6)
    crack = hp(noise(d), 1500) * np.exp(-s * 30)
    return sub * 0.9 + brass * 0.7 + crack * 0.5
def tv_off():  # estalo do botão + "zip" agudo descendo + chiado curto
    s = np.arange(int(0.45 * SR)) / SR
    zap = np.sin(2 * np.pi * np.cumsum(15000 * np.exp(-s * 9) + 200) / SR) * np.exp(-s * 8) * 0.35
    st = hp(noise(0.45), 2000) * np.exp(-s * 22) * 0.5
    btn = np.zeros_like(s); c = click() * 9; btn[:len(c)] = c
    return btn + zap + st
G = dict(whoosh=0.22, pop=0.25, impact=0.5, cut=0.1, riser=0.25, tick=0.08, type=0.06, stutter=0.12)
for b in BEATS:
    t0 = b["t0"]; s = b["sfx"]
    if s == "whoosh": add(t0 - 0.12, whoosh(), G["whoosh"])
    elif s == "pop": add(t0, pop(), G["pop"])
    elif s == "impact":
        if not any(abs(ht - t0) < 0.4 for ht, _ in HITS): add(t0, impact(), G["impact"])
    elif s == "hit": add(t0, braam(b.get("f0", 55.0)), 0.55)
    elif s == "riser": add(t0 - 1.2, riser(), G["riser"]); add(t0, impact(), G["impact"] * 0.5)
    elif s == "stutter":
        for k in range(int((b["t1"] - t0) * 30 / 4)): add(t0 + k * 4 / 30, click() * 3, G["stutter"])
    elif s in ("tick", "type"):
        r_ = 12 if s == "tick" else 16
        for k in range(int((b["t1"] - t0) * r_)): add(t0 + 0.1 + k / r_ + rng.uniform(0, 0.02), click() * 2, G[s])
    else: add(t0, click(), G["cut"])
    if "glitch" in b["fx"]: add(t0, glitchs(), 0.18)
    if "flash" in b["fx"] and not any(abs(ht - t0) < 0.4 for ht, _ in HITS): add(t0, impact(), 0.35)
add(TL["nomes"]["t0"] - 1.2, riser(), 0.35)  # riser_into_names
for ht, f0 in HITS: add(ht, braam(f0), 0.5)
add(T_OFF, tv_off(), 0.9)

# ---------------- voz + mix ----------------
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "voice_raw.wav", "-af",
    "highpass=f=80,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=2,acompressor=threshold=-22dB:ratio=3:attack=5:release=90:makeup=4,alimiter=limit=0.95",
    "-ar", str(SR), "voice.wav"], check=True)
v, _ = sf.read("voice.wav"); v = np.pad(v, (0, max(0, N - len(v))))[:N]
venv = np.convolve(np.abs(v), np.ones(4800) / 4800, "same"); act = np.clip(venv / (venv.max() * 0.08), 0, 1)
act = np.convolve(act, np.ones(9600) / 9600, "same")
rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2))

# orquestra: dinâmica natural da peça (sem normalizar), com envelope: acorde cheio -> recua no 1º fortíssimo
# -> sussurro do coro realçado e crescendo -> fortíssimo final majestoso ~5 dB abaixo da voz
fin = classic.mean(1)[(mt > 102) & (mt < 156)]
G = rms(v) * 10 ** (-3 / 20) / np.sqrt(np.mean(fin ** 2))
env = np.interp(mt, [0, CH_FILE + 2.0, CH_FILE + 5.0, 26.0, 29.0, 98.0, 102.0, 999], [1, 1, 0.42, 0.42, 1.6, 2.0, 1.0, 1.0])
env = np.convolve(env, np.ones(SR // 2) / (SR // 2), "same")
classic *= (G * env * (1 - 0.25 * act))[:, None]
# batida: presente desde o início (~13 dB abaixo da voz), cede um pouco no final para a orquestra
beat *= rms(v) / rms(beat) * 10 ** (-12 / 20) * (1 - 0.2 * act) * (1 - 0.35 * ramp(0.8 * T_OFF, T_OFF, t_all))

# trilha de abertura (opcional): clássica instrumental royalty free, ascendente e de cadência rápida (~130-140 BPM),
# do quadro 0 até a frase-tese, ~15 dB abaixo da voz e subindo; corta seco antes do silêncio estratégico
INTRO_BED = None            # ex.: "musica/abertura_royalty_free.wav"
SILENCES = [(TL["poder"]["t0"] - 0.05, t_chord)]   # frase-tese só na voz, música toda em silêncio, até a pancada/acorde
music = classic + beat[:, None]
if INTRO_BED:
    ib, _ = sf.read(INTRO_BED); ib = ib if ib.ndim == 2 else np.stack([ib, ib], 1)
    t_end = SILENCES[0][0] if SILENCES else 25.0; n_ = min(int(t_end * SR), len(ib))
    bed = np.zeros((N, 2)); bed[:n_] = ib[:n_]
    ramp_db = -18 + 5 * np.clip(t_all / max(t_end, 1), 0, 1)           # sobe ~5 dB até a tese
    bed *= (rms(v) * 10 ** (ramp_db / 20) / (rms(ib[:n_].mean(1)) + 1e-9) * (1 - 0.25 * act))[:, None]
    music = music + bed
for s0, s1 in SILENCES:      # silêncio estratégico: corte seco (fade de 30 ms) de TODA a música
    m = np.ones(N); i0, i1 = int(s0 * SR), int(s1 * SR); m[i0:i1] = 0
    f = int(0.03 * SR); m[i0 - f:i0] = np.linspace(1, 0, f); music *= m[:, None]
cut = (t_all < T_OFF).astype(float); cut[int(T_OFF * SR) - 96:int(T_OFF * SR)] = np.linspace(1, 0, 96)  # o clique corta seco
music *= cut[:, None]
def _db(x, a, b): x = x[int(a * SR):int(b * SR)]; return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
for a_, b_ in ((4, 9), (27, 29), (35, 40), (70, 75), (110, 115), (140, 145), (T_OFF - 5, T_OFF)):
    print(f"{a_:>5.0f}-{b_:.0f}s  voz {_db(v, a_, b_):6.1f}  orquestra {_db(classic.mean(1), a_, b_):6.1f}  batida {_db(beat, a_, b_):6.1f} dB")
sf.write("music.wav", music.astype(np.float32), SR); sf.write("sfx.wav", sfx.astype(np.float32), SR)
mix = v[:, None] + music + (sfx * rms(v) / 0.1 * 0.5)[:, None]
sf.write("mix_pre.wav", (mix / np.abs(mix).max() * 0.9).astype(np.float32), SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "mix_pre.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "mix.wav"], check=True)
print("ok", len(mix) / SR)
