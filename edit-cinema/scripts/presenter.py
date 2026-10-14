# extract presenter frames (30fps) for on-camera segments; RVM alpha for cutout ones; face center per segment
import json, os, subprocess, numpy as np, cv2, onnxruntime as ort
SRC = "../2026-10-13 21-23-35.mp4"
PRES = {"hook2": 1, "mcd2": 0, "gente": 0, "media": 1, "davinci": 0, "padroes": 0, "oferta": 1, "eusei": 0, "verdade": 1, "segue": 0}
WARM = 0.6
tl = {s["id"]: s for s in json.load(open("timeline.json"))}
sess = ort.InferenceSession("rvm.onnx", providers=["CPUExecutionProvider"])
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
info = {}
for tid, cut in PRES.items():
    s = tl[tid]; d = f"pres/{tid}"; os.makedirs(d, exist_ok=True)
    dur = s["t1"] - s["t0"] + 0.4
    ss = s["src"] - (WARM if cut else 0)
    p = subprocess.Popen(["ffmpeg","-v","error","-ss",str(ss),"-i",SRC,"-t",str(dur + (WARM if cut else 0)),"-vf","fps=30",
                          "-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
    rec = [np.zeros([1,1,1,1], np.float32)]*4; k = 0; faces = []
    skip = int(round(WARM*30)) if cut else 0
    while True:
        buf = p.stdout.read(1920*1080*3)
        if len(buf) < 1920*1080*3: break
        fr = np.frombuffer(buf, np.uint8).reshape(1080,1920,3)
        if cut:
            x = (fr.astype(np.float32)/255).transpose(2,0,1)[None]
            fgr, pha, *rec = sess.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": np.array([0.25], np.float32)})
        if k >= skip:
            i = k - skip
            cv2.imwrite(f"{d}/{i:04d}.jpg", cv2.cvtColor(fr, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 93])
            if cut: cv2.imwrite(f"{d}/a{i:04d}.png", (pha[0,0]*255).astype(np.uint8))
            if i % 10 == 0:
                g = cv2.cvtColor(fr[::2,::2], cv2.COLOR_RGB2GRAY); f = casc.detectMultiScale(g, 1.1, 6, minSize=(60,60))
                if len(f): x0,y0,w,h = max(f, key=lambda r: r[2]*r[3]); faces.append((2*(x0+w/2), 2*(y0+h/2), 2*w))
        k += 1
    fc = np.median(np.array(faces), 0).tolist() if faces else [960, 400, 300]
    info[tid] = dict(n=k-skip, face=fc, cut=cut); print(tid, info[tid])
json.dump(info, open("pres/info.json","w"))
