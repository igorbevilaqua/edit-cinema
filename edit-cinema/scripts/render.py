# usage: render.py sheet t1 t2 ... | render.py chunk i n | render.py all [workers]
import sys, subprocess, numpy as np, cv2
from beats import *

def frame_at(f):
    t = f / FPS
    b = next((x for x in BEATS if x["t0"] <= t < x["t1"]), BEATS[-1])
    lt, dur = t - b["t0"], b["t1"] - b["t0"]
    fr = b["draw"](t, lt, dur)
    if b["text"]: draw_text(fr, b["text"], t, b["ty"], b["theme"])
    k = int(round(lt * FPS))
    if "glitch" in b["fx"] and k < 2: fr = glitch(fr, f)
    if "flash" in b["fx"] and k < 4: fr = flash(fr, f)
    for ht, _ in HITS:
        kk = int(round((t - ht) * FPS))
        if 0 <= kk < 3: fr = (fr + (255 - fr.astype(np.float32)) * (0.6, 0.3, 0.1)[kk]).astype(np.uint8)
    if "whiteflash" in b["fx"] and k < 3: fr = (fr + (255 - fr.astype(np.float32)) * (0.7, 0.35, 0.12)[k]).astype(np.uint8)
    fr = lens(fr)
    if t >= T_OFF: fr = tv_off(fr, t - T_OFF)
    return fr

def tv_off(fr, q):
    """CRT desligando: espreme para uma linha branca, encolhe para um ponto e apaga"""
    out = np.zeros_like(fr)
    if q < 0.12:  # espreme verticalmente, clareando
        k = 1 - eout(q / 0.12); h = max(int(H * k), 4)
        sq = cv2.resize(fr, (W, h)).astype(np.float32); sq = sq + (255 - sq) * (1 - k) ** 0.5
        out[(H - h) // 2:(H - h) // 2 + h] = np.clip(sq, 0, 255).astype(np.uint8)
    elif q < 0.24:  # linha encolhe para o centro
        k = 1 - eout((q - 0.12) / 0.12); w_ = max(int(W * k), 6)
        cv2.rectangle(out, ((W - w_) // 2, H // 2 - 3), ((W + w_) // 2, H // 2 + 3), (255, 255, 255), -1)
        g = cv2.GaussianBlur(out, (0, 0), 12); out = np.maximum(out, (g * 2.5).clip(0, 255).astype(np.uint8))
    elif q < 0.42:  # ponto brilhante apagando
        a = 1 - (q - 0.24) / 0.18
        cv2.circle(out, (W // 2, H // 2), 6, (255, 255, 255), -1, cv2.LINE_AA)
        out = (np.maximum(out, cv2.GaussianBlur(out, (0, 0), 14) * 3).clip(0, 255) * a).astype(np.uint8)
    return out

def enc(path):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-vf", "noise=c0s=5:c0f=t+u", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "sheet":
        ts = [float(x) for x in sys.argv[3:]]; out = sys.argv[2]; tw, th = 270, 480
        sh = np.zeros((th * ((len(ts) + 5) // 6), tw * 6, 3), np.uint8)
        for i, t in enumerate(ts):
            fr = cv2.resize(frame_at(int(round(t * FPS))), (tw, th), interpolation=cv2.INTER_AREA)
            cv2.putText(fr, f"{t:.2f}", (4, 16), 0, 0.5, (255, 255, 0), 1)
            sh[(i // 6) * th:(i // 6 + 1) * th, (i % 6) * tw:(i % 6 + 1) * tw] = fr
        cv2.imwrite(out, cv2.cvtColor(sh, cv2.COLOR_RGB2BGR))
    elif mode == "chunk":
        i, n = int(sys.argv[2]), int(sys.argv[3])
        a, b = NF * i // n, NF * (i + 1) // n
        p = enc(f"chunks/c{i:02d}.mp4")
        for f in range(a, b):
            p.stdin.write(frame_at(f).tobytes())
            if (f - a) % 150 == 0: print(f"chunk {i}: {f - a}/{b - a}", flush=True)
        p.stdin.close(); p.wait()
