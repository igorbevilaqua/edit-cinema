# extrai trecho 9:16 da compilação de dancinha com rostos desfocados (YuNet). uso: danca_blur.py idx tempo
import subprocess, os, glob, sys, cv2, numpy as np
d1 = cv2.FaceDetectorYN.create("yunet.onnx", "", (540, 960), 0.6, 0.3, 50)
d2 = cv2.FaceDetectorYN.create("yunet.onnx", "", (1080, 1920), 0.8, 0.3, 50)
def detect(fr):
    out = []
    for det, sc, size in ((d1, 1, (540, 960)), (d2, 2, (1080, 1920))):
        img = fr if sc == 1 else cv2.resize(fr, size); det.setInputSize(size); _, faces = det.detect(img)
        for f in ([] if faces is None else faces):
            x, y, w, h = f[:4] / sc
            if 10 < w < 170 and 0.6 < h / max(w, 1) < 1.8 and y + h / 2 < 0.72 * 960: out.append(np.array([x, y, w, h]).astype(int))
    return out
i, t = int(sys.argv[1]), float(sys.argv[2]); tmp = f"danca/d{i}"
subprocess.run(["yt-dlp", "-q", "--extractor-args", "youtube:player_client=web_embedded", "-f", "bv*[height<=1080]", "--download-sections", f"*{t-1}-{t+4}",
                "-o", tmp + ".%(ext)s", "https://www.youtube.com/watch?v=5RZ72VKDD2c"], check=False, stderr=subprocess.DEVNULL)
src = glob.glob(tmp + ".*")[0]
p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", "1", "-i", src, "-t", "3", "-vf", "fps=30,crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=540:960", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
o = f"filme/shots/dance{i}"; os.makedirs(o, exist_ok=True); k, tracks = 0, []
for x in os.listdir(o): os.remove(f"{o}/{x}")
while True:
    buf = p.stdout.read(540 * 960 * 3)
    if len(buf) < 540 * 960 * 3: break
    fr = np.frombuffer(buf, np.uint8).reshape(960, 540, 3).copy(); boxes = detect(fr)
    tracks = [(b, 0) for b in boxes] + [(b, a + 1) for b, a in tracks if a < 10 and all(np.abs(b[:2] - n[:2]).max() > 50 for n in boxes)]
    for (x, y, w, h), _ in tracks:
        cx, cy, s = x + w / 2, y + h / 2, max(w, h) * 1.8
        x0, y0, x1, y1 = int(max(cx - s / 2, 0)), int(max(cy - s / 2, 0)), int(min(cx + s / 2, 540)), int(min(cy + s / 2, 960))
        if x1 - x0 > 4 and y1 - y0 > 4:
            fr[y0:y1, x0:x1] = cv2.GaussianBlur(cv2.resize(cv2.resize(fr[y0:y1, x0:x1], (7, 7)), (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST), (0, 0), 5)
    k += 1; cv2.imwrite(f"{o}/{k:04d}.jpg", fr, [cv2.IMWRITE_JPEG_QUALITY, 90])
os.remove(src); print(f"dance{i}", k)
