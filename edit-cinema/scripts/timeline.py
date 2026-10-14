# cut voice segments -> voice.wav (48k) + timeline.json with per-word times on the OUTPUT timeline
import json, subprocess, numpy as np, soundfile as sf, mlx_whisper
from segs import segments
PAUSE_AFTER = {"hook2": 0.15, "poder": 0.35, "brasil": 0.15, "plastico": 0.2, "padroes": 0.15, "recompensa": 0.2, "eusei": 1.3}
SRC = "../2026-10-13 21-23-35.mp4"
MAXLEN = 179.6
PRES = set(json.load(open("pres/info.json")))  # lip-sync: não mexe dentro desses trechos

def tighten(clip, keep=0.12, minrun=0.20):
    """silêncios internos > 0,20 s viram 0,12 s. devolve [(início, fim)] a remover (s)"""
    hop = sr // 100; e = clip[:len(clip) // hop * hop].reshape(-1, hop)
    db = 20 * np.log10(np.sqrt((e ** 2).mean(1)) + 1e-9); quiet = db < -50; cuts = []; i = 5
    while i < len(quiet) - 5:
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            if (j - i) / 100 > minrun and j < len(quiet) - 5: cuts.append(((i / 100) + keep / 2, (j / 100) - keep / 2))
            i = j
        else: i += 1
    return cuts
def shift(x, cuts): return x - sum(min(max(x - a, 0), b - a) for a, b in cuts)
def keep_ranges(cuts, dur):
    r, p = [], 0.0
    for a, b in cuts: r.append((p, a)); p = b
    return r + [(p, dur)]
subprocess.run(["ffmpeg","-v","error","-y","-i",SRC,"-vn","-ac","1","-ar","48000","audio48k.wav"], check=True)
a, sr = sf.read("audio48k.wav"); a16, _ = sf.read("audio16k.wav")
out, tl, t = [], [], 0.0
fade = int(0.006*sr)
for tid, s, e in segments():
    clip = a[int(s*sr):int(e*sr)].copy()
    clip[:fade] *= np.linspace(0,1,fade); clip[-fade:] *= np.linspace(1,0,fade)
    cuts = [] if tid in PRES else tighten(clip)
    r = mlx_whisper.transcribe(a16[int(s*16000):int(e*16000)].astype("float32"), path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
                               language="pt", word_timestamps=True)
    words = [dict(w=x["word"].strip(), t0=round(t+shift(x["start"], cuts),3), t1=round(t+shift(x["end"], cuts),3)) for sg in r["segments"] for x in sg["words"]]
    if cuts: clip = np.concatenate([clip[int(b_*sr):int(e_*sr)] for b_, e_ in keep_ranges(cuts, len(clip)/sr)])
    dur = len(clip)/sr
    tl.append(dict(id=tid, src=s, t0=round(t,3), t1=round(t+dur,3), text=r["text"].strip(), words=words))
    out.append(clip); t += dur
    p = PAUSE_AFTER.get(tid, 0)
    if p: out.append(np.zeros(int(p*sr))); t += p
voice = np.concatenate(out)
SPEED = max(1.0, (t + 1.05) / MAXLEN)   # vídeo = fala + clique/TV (1,05 s)
if SPEED > 1.0005:
    sf.write("voice_pre.wav", voice, sr)
    subprocess.run(["ffmpeg","-v","error","-y","-i","voice_pre.wav","-af",f"atempo={SPEED:.4f}","-ar",str(sr),"voice_raw.wav"], check=True)
    for seg in tl:
        seg.update(t0=round(seg["t0"]/SPEED,3), t1=round(seg["t1"]/SPEED,3), speed=SPEED)
        for w_ in seg["words"]: w_.update(t0=round(w_["t0"]/SPEED,3), t1=round(w_["t1"]/SPEED,3))
    t /= SPEED
else: sf.write("voice_raw.wav", voice, sr)
print("speed", round(SPEED, 4))
json.dump(tl, open("timeline.json","w"), ensure_ascii=False, indent=0)
print("total", round(t,2))
