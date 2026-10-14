import mlx_whisper, numpy as np, soundfile as sf, sys
from takes import TAKES; from regions import regions, a, sr
ids = sys.argv[1:]
for tid,s,e in TAKES:
    if ids and tid not in ids: continue
    for x,y in regions(s,e):
        seg = a[int((x-.08)*sr):int((y+.08)*sr)].astype("float32")
        t = mlx_whisper.transcribe(seg, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="pt")["text"].strip() if y-x>0.25 else "(blip)"
        print(f"{tid:10s} {x:.2f}-{y:.2f} {t}")
