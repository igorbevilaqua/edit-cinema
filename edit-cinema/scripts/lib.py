# primitives for the edit-voiceover renderer: images, text, cards, presenter, motion graphics, lens
import json, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
F1 = 1 / FPS
TL = {s["id"]: s for s in json.load(open("timeline.json"))}
PINFO = json.load(open("pres/info.json"))
BLUE = (32, 39, 254); BLACK = (8, 8, 10); WHITE = (244, 244, 240); INK = (18, 18, 22); RED = (235, 40, 48); GRAY = (52, 52, 58)

def w(seg, i): return TL[seg]["words"][i]["t0"]
def wend(seg, i): return TL[seg]["words"][i]["t1"]
def clamp(x, a=0.0, b=1.0): return min(max(x, a), b)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x): x = clamp(x); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k

# ---------- grade ----------
_x = np.arange(256) / 255.0
_s = 1 / (1 + np.exp(-(_x - 0.5) * 4.2)); _s = (_s - _s[0]) / (_s[-1] - _s[0])
LUT = np.clip((_s * 255 - 6) * 255 / 249, 0, 255).astype(np.uint8)  # S-curve + crushed blacks

def grade(a, sat=0.88):
    a = cv2.LUT(a, LUT).astype(np.float32)
    g = a.mean(2, keepdims=True)
    a = g + (a - g) * sat
    a[..., 0] *= 1.02; a[..., 2] *= 0.97  # slight warmth
    return np.clip(a, 0, 255).astype(np.uint8)

_I = {}
def im(k):
    if k not in _I: _I[k] = grade(cv2.cvtColor(cv2.imread(f"imgs/{k}.jpg"), cv2.COLOR_BGR2RGB))
    return _I[k]

def solid(c, h=H, w_=W):
    a = np.empty((h, w_, 3), np.uint8); a[:] = c; return a

def kb(src, ow, oh, p, z=(1.0, 1.1), f=(0.5, 0.5), d=(0, 0)):
    """Ken Burns cover crop: zoom z0->z1, focus f (fractions), drift d (fractions of src)"""
    h, w_ = src.shape[:2]
    s = max(ow / w_, oh / h) * lerp(z[0], z[1], p)
    vw, vh = ow / s, oh / s
    cx = f[0] * w_ + d[0] * p * w_; cy = f[1] * h + d[1] * p * h
    cx = clamp(cx, vw / 2, w_ - vw / 2); cy = clamp(cy, vh / 2, h - vh / 2)
    M = np.float32([[s, 0, ow / 2 - s * cx], [0, s, oh / 2 - s * cy]])
    return cv2.warpAffine(src, M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def paste(dst, src, x, y, a=1.0, mask=None):
    h, w_ = src.shape[:2]; x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w_, dst.shape[1]), min(y + h, dst.shape[0])
    if x1 <= x0 or y1 <= y0 or a <= 0: return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    if s.shape[2] == 4: al = s[..., 3:4].astype(np.float32) / 255 * a; s = s[..., :3]
    else: al = np.full(s.shape[:2] + (1,), a, np.float32)
    if mask is not None: al = al * mask[y0 - y:y1 - y, x0 - x:x1 - x, None]
    d = dst[y0:y1, x0:x1]
    d[:] = (d * (1 - al) + s * al).astype(np.uint8)

def addlight(dst, light, x, y, k):
    """screen-ish additive light (uint8 rgb) at x,y"""
    h, w_ = light.shape[:2]; x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w_, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0: return
    s = light[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32) * k
    d = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = (255 - (255 - d) * (255 - s) / 255).astype(np.uint8)

_RR = {}
def rrmask(w_, h, r):
    key = (w_, h, r)
    if key not in _RR:
        m = np.zeros((h, w_), np.uint8); r = int(min(r, w_ // 2, h // 2))
        if r <= 0: m[:] = 255
        else:
            cv2.rectangle(m, (r, 0), (w_ - r - 1, h - 1), 255, -1); cv2.rectangle(m, (0, r), (w_ - 1, h - r - 1), 255, -1)
            for cx, cy in [(r, r), (w_ - r - 1, r), (r, h - r - 1), (w_ - r - 1, h - r - 1)]: cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
        if len(_RR) > 200: _RR.clear()
        _RR[key] = m.astype(np.float32) / 255
    return _RR[key]

def card(dst, content, cx, cy, r=24, glow=0.32, a=1.0, shadow=0.0):
    h, w_ = content.shape[:2]; x, y = cx - w_ / 2, cy - h / 2
    if glow > 0 or shadow > 0:
        pad = 90; sw, sh = (w_ + 2 * pad) // 6, (h + 2 * pad) // 6
        g = np.zeros((sh, sw, 3), np.uint8)
        g[pad // 6:pad // 6 + h // 6, pad // 6:pad // 6 + w_ // 6] = cv2.resize(content, (w_ // 6, h // 6), interpolation=cv2.INTER_AREA)
        g = cv2.resize(cv2.GaussianBlur(g, (0, 0), 6), (w_ + 2 * pad, h + 2 * pad))
        if glow > 0: addlight(dst, g, x - pad, y - pad, glow * a)
        if shadow > 0:
            m = np.zeros((sh, sw), np.float32); m[pad // 6 + 2:pad // 6 + h // 6 + 2, pad // 6:pad // 6 + w_ // 6] = 1
            m = cv2.resize(cv2.GaussianBlur(m, (0, 0), 5), (w_ + 2 * pad, h + 2 * pad)) * shadow * a
            paste(dst, np.zeros((h + 2 * pad, w_ + 2 * pad, 3), np.uint8), x - pad, y - pad + 18, 1.0, m)
    paste(dst, content, x, y, a, rrmask(w_, h, r))

# ---------- text ----------
FONTS = {k: f"fonts/Poppins-{k}.ttf" for k in (300, 500, 600, 700, 800)}
STY = {"sm": (62, 600, 0, False), "md": (96, 700, 0, True), "big": (176, 800, -0.01, True), "xl": (300, 800, -0.02, True),
       "lt": (64, 300, 0.28, True), "cap": (40, 600, 0.14, True)}
_F, _S = {}, {}
def font(wt, sz):
    if (wt, sz) not in _F: _F[(wt, sz)] = ImageFont.truetype(FONTS[wt], sz)
    return _F[(wt, sz)]
def twidth(f, s, tr): return f.getlength(s) if tr == 0 else sum(f.getlength(c) + tr for c in s) - tr

def blurf(a, sig): return cv2.GaussianBlur(a, (0, 0), sig)

def styled(word, sty, theme, color=None, maxw=980):
    """RGBA raster with shadow/glow baked in. returns (rgba, pad, textwidth, sz)"""
    key = (word, sty, theme, color, maxw)
    if key in _S: return _S[key]
    sz, wt, tr, up = STY[sty]
    s = word.upper() if up else word
    f = font(wt, sz)
    while twidth(f, s, tr * sz) > maxw and sz > 28: sz = int(sz * 0.93); f = font(wt, sz)
    asc, desc = f.getmetrics(); pad = int(sz * 0.45) + 16
    tw = int(math.ceil(twidth(f, s, tr * sz)))
    img = Image.new("L", (tw + 2 * pad, asc + desc + 2 * pad), 0); d = ImageDraw.Draw(img)
    if tr == 0: d.text((pad, pad), s, font=f, fill=255)
    else:
        x = pad
        for ch in s: d.text((x, pad), ch, font=f, fill=255); x += f.getlength(ch) + tr * sz
    a = np.asarray(img).astype(np.float32) / 255
    col = np.array(color if color else (INK if theme == "light" else (255, 255, 255)), np.float32)
    P = np.zeros(a.shape + (3,), np.float32); A = np.zeros_like(a)
    def over(c, aa):
        nonlocal P, A
        P = np.array(c, np.float32) * aa[..., None] + P * (1 - aa[..., None]); A = aa + A * (1 - aa)
    if theme == "img":
        over((0, 0, 0), np.clip(blurf(a, sz * 0.07 + 3) * 1.1, 0, 0.85))
        over((255, 255, 255), blurf(a, sz * 0.12 + 5) * 0.2)
    elif theme == "dark":
        over((255, 255, 255), blurf(a, sz * 0.13 + 6) * 0.42)
    over(col, a)
    rgb = np.where(A[..., None] > 1e-4, P / np.maximum(A[..., None], 1e-4), 0)
    out = np.dstack([np.clip(rgb, 0, 255), A * 255]).astype(np.uint8)
    _S[key] = (out, pad, tw, sz)
    return _S[key]

def Tx(s, seg, i, sty="sm", together=None, color=None, y=None, out=None):
    """text item: words reveal at word times of seg starting at index i"""
    n = len(TL[seg]["words"]); ws = s.split()
    if together is None: together = sty in ("md", "big", "xl")
    toks = [(x, (w(seg, i) if together else w(seg, min(i + j, n - 1))) - F1) for j, x in enumerate(ws)]
    return dict(toks=toks, sty=sty, color=color, y=y, out=out)

def At(s, t, sty="sm", color=None, y=None, out=None):
    return dict(toks=[(x, t) for x in s.split()], sty=sty, color=color, y=y, out=out)

_L = {}
def layout(items, theme, maxw=980):
    key = (id(items), theme)
    if key in _L: return _L[key]
    lines = []
    for it in items:
        sz = STY[it["sty"]][0]
        lh = sz * (1.02 if it["sty"] in ("md", "big", "xl") else 1.3)
        cur, curw = [], 0
        for word, tin in it["toks"]:
            r, pad, tw, rsz = styled(word, it["sty"], theme, it["color"])
            sp = rsz * (0.27 + 2 * STY[it['sty']][2])
            if cur and curw + sp + tw > maxw:
                lines.append(dict(toks=cur, w=curw, lh=lh, it=it)); cur, curw = [], 0
            cur.append((word, tin, tw)); curw += (sp if len(cur) > 1 else 0) + tw
        if cur: lines.append(dict(toks=cur, w=curw, lh=lh, it=it))
    _L[key] = lines
    return lines

def draw_items(dst, items, t, cy, theme):
    lines = layout(items, theme)
    total = sum(l["lh"] for l in lines)
    y = cy - total / 2
    for l in lines:
        it = l["it"]; x = (W - l["w"]) / 2
        for word, tin, tw in l["toks"]:
            r, pad, _, rsz = styled(word, it["sty"], theme, it["color"])
            p = (t - tin) / 0.14
            if p > 0:
                a = eout(p); dy = 18 * (1 - eout(p)); img = r
                if it.get("out") is not None and t > it["out"]:
                    q = clamp((t - it["out"]) / 0.5); a *= 1 - q
                    img = cv2.GaussianBlur(img, (0, 0), 1 + 14 * q)
                elif p < 1:
                    img = cv2.GaussianBlur(img, (0, 0), 0.3 + 5 * (1 - p))
                ox, oy = x - pad, y - pad + dy - rsz * 0.12
                if it["sty"] in ("big", "xl", "md"):
                    sc = 1 + 0.15 * (1 - eout((t - tin) / (5 * F1)))
                    if sc > 1.002:
                        hh, ww = img.shape[:2]; img = cv2.resize(img, (int(ww * sc), int(hh * sc)))
                        ox -= (img.shape[1] - ww) / 2; oy -= (img.shape[0] - hh) / 2
                paste(dst, img, ox, oy, a)
            x += tw + rsz * (0.27 + 2 * STY[it['sty']][2])
        y += l["lh"]

def draw_text(dst, items, t, cy, theme):
    groups = {}
    for it in items: groups.setdefault(it["y"] if it["y"] is not None else cy, []).append(it)
    for gy, its in groups.items():
        key = id(its)
        draw_items(dst, _grp(items, gy, its), t, gy, theme)

_G = {}
def _grp(items, gy, its):  # stable list object per (beat items, y) so layout cache works
    k = (id(items), gy)
    if k not in _G: _G[k] = its
    return _G[k]

def label(dst, s, sty, theme, cx, cy, t, tin, color=None, maxw=980):
    """single styled token centered at cx,cy with reveal"""
    r, pad, tw, rsz = styled(s, sty, theme, color, maxw=maxw)
    p = (t - tin) / 0.16
    if p <= 0: return
    img = r if p >= 1 else cv2.GaussianBlur(r, (0, 0), 0.3 + 4 * (1 - p))
    paste(dst, img, cx - img.shape[1] / 2, cy - img.shape[0] / 2 + 14 * (1 - eout(p)), eout(p))

# ---------- presenter ----------
_PF = {}
def pframe(tid, t):
    s = TL[tid]; n = PINFO[tid]["n"]
    i = int(clamp(round((t - s["t0"]) * FPS * s.get("speed", 1.0)), 0, n - 1))
    if (tid, i) not in _PF:
        if len(_PF) > 8: _PF.clear()
        f = cv2.cvtColor(cv2.imread(f"pres/{tid}/{i:04d}.jpg"), cv2.COLOR_BGR2RGB)
        a = cv2.imread(f"pres/{tid}/a{i:04d}.png", 0) if PINFO[tid]["cut"] else None
        _PF[(tid, i)] = (grade(f, 0.85), a)
    return _PF[(tid, i)]

def pcrop(tid, t, ow, oh, zoom=1.0, face_at=0.40):
    f, _ = pframe(tid, t); fx, fy, fw = PINFO[tid]["face"]
    ch = 1080 / zoom; cw = ch * ow / oh
    if cw > 1920: cw = 1920; ch = cw * oh / ow
    cx = clamp(fx, cw / 2, 1920 - cw / 2); cy = clamp(fy + ch * (0.5 - face_at), ch / 2, 1080 - ch / 2)
    s = ow / cw
    M = np.float32([[s, 0, ow / 2 - s * cx], [0, s, oh / 2 - s * cy]])
    return cv2.warpAffine(f, M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

def cutout(dst, tid, t, lt, side, height=0.58, slide=True):
    f, a = pframe(tid, t); fx = PINFO[tid]["face"][0]
    s = H * height / 1080
    x0, x1 = int(max(fx - 800, 0)), int(min(fx + 800, 1920))
    sw, sh = int((x1 - x0) * s), int(1080 * s)
    sub = cv2.resize(f[:, x0:x1], (sw, sh)); al = cv2.resize(a[:, x0:x1], (sw, sh)).astype(np.float32) / 255
    er = cv2.erode(al, np.ones((9, 9), np.uint8))
    rim = np.clip(al - er, 0, 1)[..., None]
    sub = np.clip(sub.astype(np.float32) + rim * 70, 0, 255).astype(np.uint8)
    anchor = {"L": W * 0.30, "R": W * 0.70, "C": W * 0.5}[side]
    k = back(lt / 0.22) if slide else 1
    off = (1 - k) * {"L": -W * 0.7, "R": W * 0.7, "C": 0}[side]
    rise = (1 - k) * (H * 0.4 if side == "C" else 0)
    px = anchor - (fx - x0) * s + off; py = H - sh + rise
    # contact shadow
    sh_m = cv2.GaussianBlur(cv2.resize(al, (sw // 4, sh // 4)), (0, 0), 6)
    paste(dst, np.zeros((sh, sw, 3), np.uint8), px + 14, py + 10, 0.5, cv2.resize(sh_m, (sw, sh)))
    paste(dst, sub, px, py, 1.0, al)

# ---------- lens ----------
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
def _smap(k): return ((_xx - W / 2) * k + W / 2).astype(np.float32), ((_yy - H / 2) * k + H / 2).astype(np.float32)
MR, MB = _smap(1 / 1.0038), _smap(1 / 0.9962)
_r2 = ((_xx - W / 2) / (W / 2)) ** 2 * 0.55 + ((_yy - H / 2) / (H / 2)) ** 2 * 0.45
VIG = np.clip(1 - 0.32 * _r2 ** 1.4, 0.5, 1)[..., None].astype(np.float32)
del _yy, _xx

def lens(fr):
    r = cv2.remap(fr[..., 0], MR[0], MR[1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    b = cv2.remap(fr[..., 2], MB[0], MB[1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    fr = np.dstack([r, fr[..., 1], b])
    sm = cv2.resize(fr, (W // 4, H // 4), interpolation=cv2.INTER_AREA).astype(np.float32)
    br = np.clip((sm - 200) * 3.2, 0, 255)
    br = cv2.resize(cv2.GaussianBlur(br, (0, 0), 6), (W, H)) * 0.24
    f = fr.astype(np.float32)
    f = 255 - (255 - f) * (255 - br) / 255
    return np.clip(film_grade(f) * VIG, 0, 255).astype(np.uint8)

# tratamento de cor cinematográfico aplicado ao vídeo inteiro: cor contida, sombras frias, altas luzes quentes, preto levantado
_FC = np.clip(255 * (1 / (1 + np.exp(-(np.arange(256) / 255 - 0.5) * 3.2)) - 1 / (1 + np.exp(1.6))) / (1 / (1 + np.exp(-1.6)) - 1 / (1 + np.exp(1.6))), 0, 255).astype(np.float32)
def film_grade(f, sat=0.72):
    L = (f[..., 0] * 0.299 + f[..., 1] * 0.587 + f[..., 2] * 0.114)[..., None]
    f = L + (f - L) * sat
    l = L / 255; sh = (1 - l) ** 2; hi = l ** 2
    f = f + np.concatenate([12 * hi - 9 * sh, 3 * hi + 2 * sh, -12 * hi + 9 * sh], axis=2)
    f = _FC[np.clip(f, 0, 255).astype(np.uint8)]
    return 14 + f * (236 / 255)

def glitch(fr, seed):
    rng = np.random.default_rng(seed); out = fr.copy()
    sh = int(rng.integers(8, 16))
    out[..., 0] = np.roll(fr[..., 0], sh, 1); out[..., 2] = np.roll(fr[..., 2], -sh, 1)
    for _ in range(5):
        y = int(rng.integers(0, H - 120)); h = int(rng.integers(20, 120)); dx = int(rng.integers(-70, 70))
        out[y:y + h] = np.roll(out[y:y + h], dx, 1)
    return out

def flash(fr, k):
    g = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY).astype(np.float32)
    g = 255 - np.clip((g - 128) * 2.2 + 128, 0, 255)
    rng = np.random.default_rng(int(k * 100))
    for _ in range(4):
        x = int(rng.integers(0, W)); g[:, max(x - 3, 0):x + 3] = 255
    out = np.repeat(g[..., None], 3, 2).astype(np.uint8)
    return out
