# contact sheet per key prefix: rows = keys, cols = candidates
import sys, glob
from PIL import Image, ImageDraw
keys = sys.argv[2:]; T = 220
rows = [(k, sorted(glob.glob(f"cand/{k}_*.jpg"))) for k in keys]
cols = max([len(f) for _, f in rows] + [1])
sh = Image.new("RGB", (T*cols, T*len(rows)), (40,40,40))
for r,(k,fs) in enumerate(rows):
    for c,f in enumerate(fs):
        try: im = Image.open(f).convert("RGB"); im.thumbnail((T,T))
        except Exception: continue
        sh.paste(im,(c*T,r*T)); d=ImageDraw.Draw(sh); d.rectangle([c*T,r*T,c*T+90,r*T+14],fill=0); d.text((c*T+2,r*T+1),f[5:-4],fill=(255,255,0))
sh.save(sys.argv[1])
