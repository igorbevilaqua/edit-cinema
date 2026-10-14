# layouts (image/presenter) and motion graphics. every builder returns dr(t, lt, dur) -> HxWx3 uint8
from lib import *
from lib import _S

def P(lt, dur): return clamp(lt / max(dur, 0.1))

# ---------- image layouts ----------
def full(k, z=(1.0, 1.1), f=(0.5, 0.5), d=(0, 0), dark=0.12):
    def dr(t, lt, dur, ow=W, oh=H):
        fr = kb(im(k), ow, oh, P(lt, dur), z, f, d)
        return (fr * (1 - dark)).astype(np.uint8) if dark else fr
    return dr

def burst(keys, nfr=4, z=(1.12, 1.0), dark=0.15):
    def dr(t, lt, dur):
        i = int(lt * FPS + 1e-6) // nfr
        q = (lt * FPS - i * nfr) / nfr; k = keys[i % len(keys)]
        src = _shot(k, lt * FPS) if k.startswith(("f_", "v_", "fan_")) else im(k)
        return (kb(src, W, H, q, z) * (1 - dark)).astype(np.uint8)
    return dr

def cardl(k, bg=BLACK, wf=0.88, aspect=16 / 9, cy=960, z=(1.0, 1.08), f=(0.5, 0.5), glow=0.32):
    def dr(t, lt, dur):
        fr = solid(bg); k_in = eout(lt / (6 * F1))
        cw = int(W * wf * lerp(0.9, 1, k_in)); ch = int(cw / aspect)
        c = kb(im(k), cw, ch, P(lt, dur), z, f)
        card(fr, c, W / 2, cy + math.sin(lt * 1.7) * 7, glow=glow if bg == BLACK else 0, shadow=0.35 if bg != BLACK else 0, a=k_in)
        return fr
    return dr

def tipo(bg=BLACK, dots=False):
    def dr(t, lt, dur):
        fr = solid(bg)
        if bg == BLACK:  # faint moving dust so nothing is static
            rng = np.random.default_rng(7)
            for i in range(40):
                x = (rng.uniform(0, W) + lt * rng.uniform(-20, 20)) % W; y = (rng.uniform(0, H) - lt * rng.uniform(10, 40)) % H
                cv2.circle(fr, (int(x), int(y)), int(rng.integers(1, 3)), (40, 40, 46), -1, cv2.LINE_AA)
        return fr
    return dr

def switch(*pairs):
    """[(t_start, dr), ...] choose by absolute time"""
    def dr(t, lt, dur, **kw):
        cur = pairs[0][1]; t0 = pairs[0][0]
        for ts, d in pairs:
            if t >= ts - F1: cur, t0 = d, ts
        return cur(t, t - t0, dur, **kw)
    return dr

# ---------- presenter layouts ----------
def p_cut(tid, side, bg, height=0.6, behind=None, behind_y=600, bgdark=0.7, bgblur=4):
    def dr(t, lt, dur):
        fr = bg(t, lt, dur)
        if bgblur: fr = cv2.GaussianBlur(fr, (0, 0), bgblur)
        fr = (fr * bgdark).astype(np.uint8)
        if behind: draw_text(fr, behind, t, behind_y, "dark")
        cutout(fr, tid, t, lt, side, height)
        return fr
    return dr

def p_split(tid, top, seam=960):
    def dr(t, lt, dur):
        fr = np.empty((H, W, 3), np.uint8)
        fr[:seam] = top(t, lt, dur, ow=W, oh=seam)
        fr[seam:] = pcrop(tid, t, W, H - seam, zoom=1.12, face_at=0.40)
        k = eout(lt / (8 * F1))  # bottom panel wipes up
        if k < 1: fr[seam:] = (fr[seam:] * k).astype(np.uint8)
        fr[seam - 3:seam + 3] = (255, 255, 255)
        return fr
    return dr

TVQ = np.float32([[0.1445, 0.130], [0.428, 0.124], [0.422, 0.452], [0.146, 0.458]])
def p_tv(tid):
    def dr(t, lt, dur):
        src = im("oldtv"); h, w_ = src.shape[:2]; p = P(lt, dur)
        s = W / (0.56 * w_) * lerp(1.0, 1.07, p); cx, cy = 0.29 * w_, 0.42 * h
        M = np.float32([[s, 0, W / 2 - s * cx], [0, s, 1010 - s * cy]])
        fr = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=BLACK)
        ytop, ybot = M[1, 2], M[1, 2] + h * s
        ys = np.arange(H, dtype=np.float32)
        fade = np.clip((ys - ytop) / 220, 0, 1) * np.clip((ybot - ys) / 220, 0, 1)
        fr = (fr * fade[:, None, None] * 0.82).astype(np.uint8)
        q = TVQ * np.float32([w_, h]); qd = (q @ M[:, :2].T) + M[:, 2]
        pw, ph = 640, 500
        pres = pcrop(tid, t, pw, ph, zoom=1.3, face_at=0.42).astype(np.float32)
        pres[::3] *= 0.72  # scanlines
        pres = pres * (1 + 0.04 * math.sin(lt * 37)) * np.float32([0.92, 1.0, 1.08])
        pres = np.clip(pres, 0, 255).astype(np.uint8)
        Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [pw, 0], [pw, ph], [0, ph]]), qd.astype(np.float32))
        wp = cv2.warpPerspective(pres, Hm, (W, H))
        m = cv2.warpPerspective(rrmask(pw, ph, 70), Hm, (W, H)) * 0.86
        fr = (fr * (1 - m[..., None]) + wp * m[..., None]).astype(np.uint8)
        return fr
    return dr

PHQ = np.float32([[0.431, 0.278], [0.605, 0.337], [0.524, 0.740], [0.331, 0.696]])
_PHM = {}
def p_phone(tid):
    def dr(t, lt, dur):
        src = im("phone"); h, w_ = src.shape[:2]; p = P(lt, dur)
        if "m" not in _PHM:
            raw = cv2.imread("imgs/phone.jpg"); quad = np.zeros(raw.shape[:2], np.uint8)
            cv2.fillConvexPoly(quad, (PHQ * np.float32([w_, h])).astype(np.int32), 255)
            quad = cv2.dilate(quad, np.ones((15, 15), np.uint8))
            white = (raw.min(2) > 215).astype(np.uint8) * 255
            _PHM["m"] = cv2.GaussianBlur((quad & white).astype(np.float32) / 255, (0, 0), 1.5)
        s = max(W / w_, H / h) * lerp(1.05, 1.16, p); cx, cy = 0.47 * w_, 0.51 * h
        M = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
        fr = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        fr = (fr * 0.62).astype(np.uint8)  # dim the room, keep screen bright
        m = cv2.warpAffine(_PHM["m"], M, (W, H))
        qd = (PHQ * np.float32([w_, h])) @ M[:, :2].T + M[:, 2]
        pw, ph = 540, 1080
        pres = pcrop(tid, t, pw, ph, zoom=1.0, face_at=0.36)
        # instagram-ish chrome: top bar + bottom icons
        cv2.rectangle(pres, (0, 0), (pw, 70), (250, 250, 250), -1)
        cv2.circle(pres, (40, 35), 20, BLUE, -1, cv2.LINE_AA)
        cv2.rectangle(pres, (75, 25), (230, 45), (200, 200, 205), -1)
        for i, x in enumerate((60, 150, 240)):
            beat = clamp((t - (TL[tid]["t0"] + 0.9 + i * 0.35)) / 0.2)
            cv2.circle(pres, (x, ph - 70), int(18 + 10 * math.sin(beat * math.pi)), (240, 60, 80) if beat > 0 else (230, 230, 235), -1, cv2.LINE_AA)
        Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [pw, 0], [pw, ph], [0, ph]]), qd.astype(np.float32))
        wp = cv2.warpPerspective(pres, Hm, (W, H))
        return (fr * (1 - m[..., None]) + wp * m[..., None]).astype(np.uint8)
    return dr

_GOLD = None
def goldframe(iw, ih, b):
    ramp = [(70, 45, 15), (150, 105, 40), (215, 175, 90), (240, 210, 130), (180, 130, 55), (110, 75, 25), (200, 160, 80), (90, 60, 20)]
    fw, fh = iw + 2 * b, ih + 2 * b
    g = np.zeros((fh, fw, 3), np.uint8)
    for i in range(b):
        c = np.array(ramp[int(i / b * (len(ramp) - 1e-6))], np.float32) * (0.85 + 0.15 * math.sin(i * 0.9))
        cv2.rectangle(g, (i, i), (fw - 1 - i, fh - 1 - i), c.tolist(), 1)
    return g

def p_frame(tid):
    wall = None
    def dr(t, lt, dur):
        nonlocal wall
        if wall is None:
            yy = np.linspace(0, 1, H)[:, None, None]
            wall = (np.array([22, 38, 34]) * (1 - yy) + np.array([10, 18, 16]) * yy) * np.ones((1, W, 3))
            n = np.random.default_rng(1).normal(0, 4, (H // 4, W // 4, 1))
            wall = np.clip(wall + cv2.resize(n, (W, H))[..., None], 0, 255).astype(np.uint8)
            for (x, y, r) in ((300, 420, 380), (600, 1020, 620)):
                yy2, xx2 = np.mgrid[0:H, 0:W]; l = np.exp(-((xx2 - x) ** 2 + (yy2 - y) ** 2) / (2 * r * r))
                wall = np.clip(wall + l[..., None] * 60, 0, 255).astype(np.uint8)
        p = P(lt, dur); fr = wall.copy()
        dx, dy = -20 * p, 10 * math.sin(lt)
        # mona lisa (top-left), presenter (big)
        mw, mh, mb = 280, 418, 30
        ml = goldframe(mw, mh, mb); ml[mb:mb + mh, mb:mb + mw] = kb(im("monalisa"), mw, mh, 0.5, (1.0, 1.0))
        card(fr, ml, 250 + dx, 470 + dy, r=4, glow=0, shadow=0.6)
        pw, ph, pb = 600, 760, 42
        pf = goldframe(pw, ph, pb); pf[pb:pb + ph, pb:pb + pw] = pcrop(tid, t, pw, ph, zoom=1.15, face_at=0.40)
        card(fr, pf, 620 + dx * 1.4, 1130 + dy, r=4, glow=0, shadow=0.6)
        # plaques
        for (cx, cy, s) in ((250 + dx, 720 + dy, "DA VINCI, 1503"), (620 + dx * 1.4, 1570 + dy, "OBRA HUMANA")):
            r, pad, tw, sz = styled(s, "cap", "light")
            pl = solid((235, 230, 220), r.shape[0] - 2 * pad + 24, tw + 40)
            paste(fr, pl, cx - pl.shape[1] / 2, cy - pl.shape[0] / 2)
            paste(fr, r, cx - r.shape[1] / 2, cy - r.shape[0] / 2 - sz * 0.1)
        return fr
    return dr

def p_cardfull(tid, tg):
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur); k = ease((t - tg) / (10 * F1))
        rw, rh = int(lerp(760, W, k)), int(lerp(950, H, k))
        c = pcrop(tid, t, rw, rh, zoom=lerp(1.2, 1.0, k), face_at=lerp(0.42, 0.33, k))
        k_in = eout(lt / (6 * F1))
        card(fr, c, W / 2, lerp(930, 960, k) + math.sin(lt * 1.7) * 6 * (1 - k), r=int(lerp(28, 0, k)), glow=0.3 * (1 - k), a=k_in)
        return fr
    return dr

def p_cta(tid):
    def dr(t, lt, dur):
        fr = solid(WHITE)
        k_in = eout(lt / (7 * F1))
        c = pcrop(tid, t, 640, 800, zoom=1.15, face_at=0.40)
        card(fr, c, W / 2, 700 + 40 * (1 - k_in), r=36, glow=0, shadow=0.45, a=k_in)
        # follow button
        tb, tap = w(tid, 0) - F1, w(tid, 2)
        kb_ = back((t - tb) / 0.25)
        if t >= tb:
            bw, bh = int(560 * kb_), int(124 * kb_)
            if bw > 10 and bh > 10:
                done = t > tap + 0.25
                btn = solid((236, 236, 240) if done else BLUE, bh, bw)
                txt = "Seguindo" if done else "Seguir"
                r, pad, tw, sz = styled(txt, "md", "light" if done else "dark", INK if done else (255, 255, 255))
                rr = cv2.resize(r, (max(int(r.shape[1] * 0.62 * kb_), 1), max(int(r.shape[0] * 0.62 * kb_), 1)))
                paste(btn, rr, bw / 2 - rr.shape[1] / 2, bh / 2 - rr.shape[0] / 2 - 6)
                paste(fr, btn, W / 2 - bw / 2, 1250 - bh / 2, 1, rrmask(bw, bh, bh // 2))
        # tap ripple + cursor
        q = (t - tap) / 0.45
        if 0 <= q <= 1:
            cv2.circle(fr, (W // 2 + 150, 1265), int(30 + 90 * q), (150, 150, 160), 3, cv2.LINE_AA)
        if tap - 0.5 < t < tap + 0.8:
            m = eout((t - tap + 0.5) / 0.5)
            cx, cy = int(lerp(W - 80, W // 2 + 150, m)), int(lerp(1600, 1265, m))
            pts = np.array([[cx, cy], [cx + 26, cy + 64], [cx + 36, cy + 38], [cx + 62, cy + 30]], np.int32)
            cv2.fillPoly(fr, [pts], INK, cv2.LINE_AA)
        return fr
    return dr

# ---------- motion graphics ----------
def _plain(s, wt, sz, color):
    key = ("plain", s, wt, sz, color)
    if key not in _S:
        f = font(wt, sz); a, d = f.getmetrics()
        img = Image.new("RGBA", (max(int(f.getlength(s)) + 4, 4), a + d + 4), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((2, 2), s, font=f, fill=tuple(color) + (255,))
        _S[key] = np.array(img)
    return _S[key]

def mg_chat(prompt, t_type, cps=24, strike=None, dark=True):
    def dr(t, lt, dur):
        bg, panel, ink, sub = ((14, 14, 17), (32, 32, 38), (235, 235, 240), (70, 70, 80)) if dark else (WHITE, (255, 255, 255), INK, (220, 220, 226))
        fr = solid(bg); k = eout(lt / (6 * F1))
        pw, ph = 960, 760; x0, y0 = (W - pw) // 2, int(560 + 60 * (1 - k))
        win = solid(panel, ph, pw)
        for i, c in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))): cv2.circle(win, (40 + 34 * i, 38), 11, c, -1, cv2.LINE_AA)
        paste(win, _plain("Chat IA", 600, 34, sub if dark else (120, 120, 130)), pw / 2 - 60, 14)
        # input box
        cv2.rectangle(win, (30, ph - 150), (pw - 30, ph - 40), sub, 2, cv2.LINE_AA)
        n = int(clamp((t - t_type) * cps, 0, len(prompt)))
        s = prompt[:n] + ("|" if int(lt * 3) % 2 == 0 or n < len(prompt) else " ")
        paste(win, _plain(s, 500, 44, ink), 56, ph - 128)
        cv2.circle(win, (pw - 85, ph - 95), 32, BLUE if n == len(prompt) else sub, -1, cv2.LINE_AA)
        # response skeleton after typing
        t_done = t_type + len(prompt) / cps
        for i in range(6):
            q = clamp((t - t_done - 0.05 * i) / 0.25)
            if q > 0:
                ln = int((pw - 140 - (i % 3) * 120) * eout(q))
                cv2.rectangle(win, (60, 100 + i * 70), (60 + ln, 130 + i * 70), sub, -1, cv2.LINE_AA)
        paste(fr, win, x0, y0, k, rrmask(pw, ph, 30))
        if strike is not None and t >= strike:
            q = eout((t - strike) / 0.18); c = (W // 2, y0 + ph // 2)
            for sgn in (1, -1):
                e = (int(c[0] + sgn * 380 * q), int(c[1] + 380 * q)); s0 = (c[0] - sgn * 380, c[1] - 380)
                cv2.line(fr, s0, (int(lerp(s0[0], c[0] + sgn * 380, q)), int(lerp(s0[1], c[1] + 380, q))), RED, 34, cv2.LINE_AA)
        return fr
    return dr

def mg_ring(n_to, unit, t0, t1, frac, label_s=None):
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur); k = ease((t - t0) / max(t1 - t0, 0.1))
        c, r = (W // 2, 900), 330
        cv2.circle(fr, c, r, (40, 40, 46), 30, cv2.LINE_AA)
        if k > 0: cv2.ellipse(fr, c, (r, r), -90, 0, 360 * frac * k, BLUE, 30, cv2.LINE_AA)
        for i in range(24):
            a = i / 24 * 2 * math.pi - math.pi / 2
            cv2.line(fr, (int(c[0] + (r - 50) * math.cos(a)), int(c[1] + (r - 50) * math.sin(a))),
                     (int(c[0] + (r - 66) * math.cos(a)), int(c[1] + (r - 66) * math.sin(a))), (90, 90, 100), 3, cv2.LINE_AA)
        v = int(round(n_to * k))
        r_, pad, tw, sz = styled(f"{v}{unit}", "xl", "dark")
        paste(fr, r_, c[0] - r_.shape[1] / 2, c[1] - r_.shape[0] / 2 - 20)
        return fr
    return dr

def mg_bars(seg):
    def dr(t, lt, dur):
        fr = solid(WHITE)
        rows = [("BRASIL", "9h13", 9.22, BLUE, w(seg, 0) - 0.6, 760), ("MUNDO", "6h40", 6.67, (170, 170, 178), w(seg, 0) - 0.3, 1060)]
        maxw = 860
        for name, val, h_, col, ts, y in rows:
            k = eout((t - ts) / 0.5)
            label(fr, name, "cap", "light", 110 + 90, y - 80, t, ts)
            ln = int(maxw * h_ / 9.22 * k)
            if ln > 2: paste(fr, solid(col, 90, ln), 110, y - 45, 1, rrmask(ln, 90, 20))
            label(fr, val, "md", "light", 110 + ln - 110 if ln > 230 else 110 + ln + 110, y, t, ts + 0.35, (255, 255, 255) if ln > 230 else INK)
        # +3h bracket
        tb = w(seg, 1) - F1
        if t >= tb:
            q = eout((t - tb) / 0.3); x0, x1 = 110 + int(maxw * 6.67 / 9.22), 110 + maxw
            cv2.line(fr, (x0, 1200), (int(lerp(x0, x1, q)), 1200), BLUE, 8, cv2.LINE_AA)
            for x in (x0, x1): cv2.line(fr, (x, 1170), (x, 1230), BLUE, 8, cv2.LINE_AA)
            label(fr, "+2h33", "big", "light", min((x0 + x1) / 2, W - 300), 1330, t, tb, BLUE)
        footnote(fr, "Fonte: DataReportal / We Are Social & Meltwater — Digital 2024", 1610, t, w(seg, 0) - 0.6, dark=False)
        return fr
    return dr

def mg_dots(mode, t0, t1=None, bg=BLACK, cy=980):
    t1 = t0 + 0.4 if t1 is None else t1
    order = np.random.default_rng(3).permutation(100)
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur) if bg == BLACK else solid(bg)
        sp, r = 84, 28; x0 = W / 2 - 4.5 * sp; y0 = cy - 4.5 * sp
        k = ease((t - t0) / max(t1 - t0, 0.1))
        if mode == "pct":
            n = int(round(51 * k))
            r_, pad, tw, sz = styled(f"{n}%", "xl", "dark"); paste(fr, r_, W / 2 - r_.shape[1] / 2, 250 - pad)
        for i in range(100):
            x, y = int(x0 + (i % 10) * sp), int(y0 + (i // 10) * sp)
            rank = int(np.where(order == i)[0][0])
            pop = eout((lt - (i % 10 + i // 10) * 0.012) / 0.2)
            rr = int(r * pop); col, glow = (60, 60, 68), False
            if mode == "pct" and rank < 51 * k: col = BLUE
            if mode == "maioria" and rank < 90 * k: col = (78, 78, 86)
            elif mode == "maioria": col = (240, 240, 240)
            if mode == "destaque" and i == 44:
                q = back((t - t0) / 0.35)
                if t >= t0: col, rr, glow = BLUE, int(r * (1 + 0.8 * q)), True
            if mode == "destaque" and i != 44 and t >= t0: col = (48, 48, 54)
            if glow: cv2.circle(fr, (x, y), rr + 22, (20, 26, 120), -1, cv2.LINE_AA)
            if rr > 0: cv2.circle(fr, (x, y), rr, col, -1, cv2.LINE_AA)
        return fr
    return dr

def mg_tvwall(keys):
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur); p = P(lt, dur)
        s = lerp(1.18, 1.0, eout(p * 1.3)); cw, ch, gap = int(300 * s), int(225 * s), int(22 * s)
        gw, gh = 3 * cw + 2 * gap, 4 * ch + 3 * gap
        for i, k in enumerate(keys[:12]):
            cx = W / 2 - gw / 2 + (i % 3) * (cw + gap) + cw / 2; cy = 930 - gh / 2 + (i // 3) * (ch + gap) + ch / 2
            src_ = _shot(k, lt * FPS) if k.startswith(("fan_", "f_")) else im(k)
            c = kb(src_, cw, ch, (p + i * 0.07) % 1, (1.15, 1.35) if k.startswith("fan_") else (1.05, 1.15)).astype(np.float32)
            c[::3] *= 0.75; c *= 0.9 + 0.1 * math.sin(lt * 23 + i * 2.1)
            on = clamp((lt - i * 0.04) / 0.08)
            card(fr, np.clip(c, 0, 255).astype(np.uint8), cx, cy, r=14, glow=0.12, a=on)
        return fr
    return dr

def mg_ab(seg):
    def dr(t, lt, dur):
        fr = solid(WHITE)
        rows = [(560, "DISTRIBUIÇÃO ÓTIMA", w(seg, 7), 900, BLUE, None),
                (1180, "PRODUTO ÓTIMO", w(seg, 11), 330, (180, 180, 188), ("+ DISTRIBUIÇÃO RUIM", w(seg, 14)))]
        for y, name, ts, ln_, col, extra in rows:
            label(fr, name, "md", "light", W / 2, y - 120, t, ts - F1, INK)
            if extra: label(fr, extra[0], "sm", "light", W / 2, y - 30, t, extra[1] - F1, RED)
            k = eout((t - ts) / 0.6); ln = int(ln_ * k)
            if ln > 4: paste(fr, solid(col, 70, ln), W / 2 - 450, y + 50, 1, rrmask(ln, 70, 35))
        tv = w(seg, 9) - F1
        if t >= tv:
            q = back((t - tv) / 0.3)
            badge = solid(BLUE, int(120 * q) + 1, int(440 * q) + 1)
            paste(fr, badge, W / 2 + 120 - badge.shape[1] / 2, 830 - badge.shape[0] / 2, 1, rrmask(badge.shape[1], badge.shape[0], badge.shape[0] // 2))
            if q > 0.6: label(fr, "VENCE", "md", "dark", W / 2 + 120, 822, t, tv + 0.08, (255, 255, 255))
        return fr
    return dr

def mg_particles(t_burst):
    rng = np.random.default_rng(5); n = 160
    ang = rng.uniform(0, 2 * math.pi, n); spd = rng.uniform(250, 1100, n); sz = rng.integers(3, 10, n)
    def dr(t, lt, dur):
        fr = solid(WHITE); c = (W // 2, 1060)
        if t < t_burst:
            r = int(6 + 34 * ease(lt / max(t_burst - (t - lt), 0.1)))
            cv2.circle(fr, c, r, INK, -1, cv2.LINE_AA)
        else:
            q = t - t_burst; d = spd * (1 - math.exp(-q * 3)) / 3
            a = clamp(1 - q / 1.4)
            for i in range(n):
                x, y = int(c[0] + math.cos(ang[i]) * d[i]), int(c[1] + math.sin(ang[i]) * d[i])
                col = tuple(int(lerp(244, v, a)) for v in (BLUE if i % 9 == 0 else INK))
                cv2.circle(fr, (x, y), int(sz[i]), col, -1, cv2.LINE_AA)
        return fr
    return dr

def mg_average(keys):
    mos = {}
    def dr(t, lt, dur):
        if "m" not in mos:
            cols, rows = 4, 7; cw, ch = W // cols, H // rows + 1
            m = np.zeros((rows * ch, cols * cw, 3), np.uint8)
            for i in range(cols * rows): m[(i // cols) * ch:(i // cols + 1) * ch, (i % cols) * cw:(i % cols + 1) * cw] = kb(im(keys[i % len(keys)]), cw, ch, 0.5, (1, 1))
            m = m[:H, :W]; mos["m"] = m.astype(np.float32)
            mos["a"] = np.full_like(mos["m"], m.reshape(-1, 3).mean(0))
        p = P(lt, dur); k = ease((p - 0.25) / 0.6)
        out = mos["m"] * (1 - k) + mos["a"] * k
        out = cv2.GaussianBlur(out, (0, 0), 1 + 30 * k) if k > 0.01 else out
        return np.clip(out, 0, 255).astype(np.uint8)
    return dr

def mg_checks():
    def dr(t, lt, dur):
        fr = solid(WHITE)
        for i in range(30):
            x, y = 150 + (i % 5) * 195, 380 + (i // 5) * 210
            q = eout((lt - i * 0.02) / 0.15)
            if q <= 0: continue
            pts = np.array([[x - 40, y], [x - 12, y + 30], [x + 44, y - 34]], np.float32)
            pts = ((pts - [x, y]) * q + [x, y]).astype(np.int32)
            cv2.polylines(fr, [pts], False, (200, 200, 206), 12, cv2.LINE_AA)
        return fr
    return dr

def mg_xstamp(base, t_x):
    def dr(t, lt, dur):
        fr = base(t, lt, dur)
        if t >= t_x:
            q = back((t - t_x) / 0.2); c = (W // 2, 980); L = int(330 * q)
            for sgn in (1, -1):
                cv2.line(fr, (c[0] - L, c[1] - sgn * L), (c[0] + L, c[1] + sgn * L), RED, 46, cv2.LINE_AA)
        return fr
    return dr

def mg_zero(seg):
    def dr(t, lt, dur):
        fr = solid(WHITE); k = eout(lt / (6 * F1))
        pw, ph = 920, 620; win = solid((255, 255, 255), ph, pw)
        cv2.rectangle(win, (0, 0), (pw - 1, ph - 1), (220, 220, 226), 3)
        paste(win, _plain("Visualizações", 600, 40, (110, 110, 120)), 50, 40)
        paste(win, _plain("0", 800, 170, INK), 50, 90)
        pts = [(50 + i * 20, 520 - int(6 * math.sin(i * 1.3 + lt * 4))) for i in range(42)]
        cv2.polylines(win, [np.array(pts, np.int32)], False, (200, 60, 70), 6, cv2.LINE_AA)
        cv2.line(win, (50, 540), (pw - 50, 540), (225, 225, 230), 2)
        card(fr, win, W / 2, 900 + 40 * (1 - k), r=28, glow=0, shadow=0.25, a=k)
        return fr
    return dr

def mg_collage(keys, hl=None, bg=BLACK):
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur) if bg == BLACK else solid(bg)
        cw, ch, gap = 320, 569, 34
        for col in range(3):
            speed = (60, -45, 75)[col]; x = W / 2 + (col - 1) * (cw + gap)
            off = (lt * speed + col * 230) % (ch + gap)
            for j in range(-1, 4):
                y = 120 + j * (ch + gap) + off - (ch + gap) / 2
                k = keys[(col * 5 + j + 10) % len(keys)]
                c = kb(_shot(k, lt * FPS) if k.startswith(("f_", "fan_")) else im(k), cw, ch, 0.5, (1.0, 1.0)).copy()
                cv2.rectangle(c, (0, ch - 90), (cw, ch), (0, 0, 0), -1)
                cv2.circle(c, (40, ch - 45), 18, (240, 60, 80), -1, cv2.LINE_AA)
                cv2.rectangle(c, (72, ch - 55), (200, ch - 35), (200, 200, 205), -1)
                if hl is not None and t >= hl:
                    q = clamp((t - hl) / 0.25)
                    cv2.rectangle(c, (10, 10), (cw - 10, int(ch * 0.3)), BLUE, int(2 + 8 * q))
                card(fr, c, x, y + ch / 2, r=22, glow=0.1)
        return fr
    return dr

def mg_people(t0, t1):
    rng = np.random.default_rng(11); order = rng.permutation(8 * 11)
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur); k = (t - t0) / max(t1 - t0, 0.1)
        for i in range(88):
            x, y = 120 + (i % 8) * 120, 330 + (i // 8) * 120
            rank = int(np.where(order == i)[0][0]); on = clamp((k * 88 - rank) / 3)
            col = tuple(int(lerp(a, b, on)) for a, b in zip((70, 70, 78), BLUE))
            s = 1 + 0.35 * math.sin(on * math.pi)
            cv2.circle(fr, (x, int(y - 22 * s)), int(17 * s), col, -1, cv2.LINE_AA)
            cv2.ellipse(fr, (x, int(y + 26 * s)), (int(32 * s), int(24 * s)), 0, 180, 360, col, -1, cv2.LINE_AA)
        return fr
    return dr

def mg_post(t_tap):
    def dr(t, lt, dur):
        fr = solid(WHITE); k = back(lt / 0.25)
        press = 1 - 0.08 * math.sin(clamp((t - t_tap) / 0.2) * math.pi)
        bw, bh = int(620 * k * press), int(150 * k * press)
        if bw > 10:
            btn = solid(BLUE, bh, bw)
            r, pad, tw, sz = styled("Publicar", "md", "dark", (255, 255, 255))
            rr = cv2.resize(r, (max(int(r.shape[1] * 0.75 * k), 1), max(int(r.shape[0] * 0.75 * k), 1)))
            paste(btn, rr, bw / 2 - rr.shape[1] / 2, bh / 2 - rr.shape[0] / 2 - 8)
            paste(fr, btn, W / 2 - bw / 2, 1150 - bh / 2, 1, rrmask(bw, bh, bh // 2))
        q = (t - t_tap) / 0.5
        if 0 <= q <= 1: cv2.circle(fr, (W // 2, 1150), int(80 + 260 * q), (190, 195, 255), 4, cv2.LINE_AA)
        return fr
    return dr

def mg_profile(keys, avatar_tid):
    def dr(t, lt, dur):
        fr = solid(WHITE)
        k = back(lt / 0.3); r = int(120 * k)
        if r > 4:
            cv2.circle(fr, (W // 2, 520), r + 14, (0, 0, 0), -1, cv2.LINE_AA); cv2.circle(fr, (W // 2, 520), r + 6, WHITE, -1, cv2.LINE_AA)
            av = vm_avatar(r)
            m = np.zeros((2 * r, 2 * r), np.float32); cv2.circle(m, (r, r), r, 1, -1, cv2.LINE_AA)
            paste(fr, av, W // 2 - r, 520 - r, 1, m)
        for i in range(9):
            q = eout((lt - 0.15 - i * 0.06) / 0.2)
            if q <= 0: continue
            s = 262; x, y = W / 2 + (i % 3 - 1) * (s + 12), 960 + (i // 3) * (s + 12)
            c = kb(im(keys[i % len(keys)]), int(s * q) + 1, int(s * q) + 1, 0.5, (1, 1))
            paste(fr, c, x - c.shape[1] / 2, y - c.shape[0] / 2)
        return fr
    return dr

# ---------- comparativo: Big Mac (distribuição) × hambúrguer artesanal (produto) ----------
def _star(c, r):
    return np.array([(c[0] + (r if i % 2 == 0 else r * 0.45) * math.sin(i * math.pi / 5), c[1] - (r if i % 2 == 0 else r * 0.45) * math.cos(i * math.pi / 5)) for i in range(10)], np.int32)

def stars_pill(dst, x, y, n, t, tin):
    if t < tin: return
    pw, ph = 250, 62; pill = solid((255, 255, 255), ph, pw)
    for i in range(5):
        q = back((t - tin - i * 0.07) / 0.2)
        if q <= 0: continue
        cv2.fillPoly(pill, [_star((28 + i * 48, 32), int(20 * q))], (255, 186, 20) if i < n else (210, 210, 216), cv2.LINE_AA)
    paste(dst, pill, x, y, 1, rrmask(pw, ph, 31))

def pill(dst, s, x, y, bg, fg, t, tin, sty="cap"):
    if t < tin: return
    q = back((t - tin) / 0.25)
    r, pad, tw, sz = styled(s, sty, "light", fg, maxw=2000)
    pw, ph = int((tw + 50) * q) + 1, int((sz * 1.5) * q) + 1
    p = solid(bg, ph, pw)
    rr = cv2.resize(r, (max(int(r.shape[1] * q), 1), max(int(r.shape[0] * q), 1)))
    paste(p, rr, pw / 2 - rr.shape[1] / 2, ph / 2 - rr.shape[0] / 2 - sz * 0.08 * q)
    paste(dst, p, x, y, 1, rrmask(pw, ph, ph // 2))

_BILLS = []
def _bills():
    if not _BILLS:
        bw, bh = 132, 64
        b3 = solid((46, 140, 80), bh, bw)
        cv2.rectangle(b3, (6, 6), (bw - 7, bh - 7), (150, 210, 160), 2)
        cv2.circle(b3, (bw // 2, bh // 2), 20, (70, 165, 100), -1, cv2.LINE_AA)
        d = _plain("$", 800, 34, (230, 255, 235)); paste(b3, d, bw / 2 - d.shape[1] / 2, bh / 2 - d.shape[0] / 2 - 2)
        b = np.dstack([b3, np.full((bh, bw), 255, np.uint8)])
        pad = 40; big = np.zeros((bh + 2 * pad, bw + 2 * pad, 4), np.uint8); big[pad:pad + bh, pad:pad + bw] = b
        for k in range(24):
            M = cv2.getRotationMatrix2D((big.shape[1] / 2, big.shape[0] / 2), k * 15, 1.0)
            _BILLS.append(cv2.warpAffine(big, M, (big.shape[1], big.shape[0]), flags=cv2.INTER_LINEAR))
    return _BILLS

def mg_burgers(seg):
    rng = np.random.default_rng(21); NB = 170
    birth = np.sort(rng.uniform(0, 4.5, NB)); vx = rng.choice([-1, 1], NB) * rng.uniform(350, 950, NB); vy = rng.uniform(-750, -250, NB)
    spin = rng.uniform(-7, 7, NB); a0 = rng.uniform(0, 2 * math.pi, NB); ox = rng.uniform(-160, 160, NB); scl = rng.uniform(0.7, 1.15, NB)
    cw, chh, ytop, ybot = 820, 500, 660, 1270
    def dr(t, lt, dur):
        fr = solid(WHITE)
        t7, t9, t11, t14 = [w(seg, i) - F1 for i in (7, 9, 11, 14)]
        p = P(lt, dur)
        # --- topo: Big Mac, distribuição ótima
        k = back((t - t7) / 0.35)
        if t >= t7:
            x = lerp(-W * 0.6, W / 2, k)
            card(fr, kb(im("bigmac"), cw, chh, p, (1.0, 1.1), (0.5, 0.55)), x, ytop, r=28, glow=0, shadow=0.35)
            stars_pill(fr, x - cw / 2 + 24, ytop - chh / 2 + 24, 2, t, t7 + 0.25)
            pill(fr, "US$ 26,9 bi em 2025", x - cw / 2 + 24, ytop + chh / 2 - 92, BLUE, (255, 255, 255), t, t9 + 0.25, "sm")
        # --- baixo: artesanal, produto ótimo + distribuição ruim
        if t >= t11:
            k2 = back((t - t11) / 0.35); x2 = lerp(W * 1.6, W / 2, k2)
            g = kb(im("gourmet"), cw, chh, p, (1.0, 1.1), (0.5, 0.5))
            if t >= t14:
                q = ease((t - t14) / 0.7); gr = g.mean(2, keepdims=True)
                g = np.clip((g * (1 - q * 0.75) + gr * q * 0.75) * (1 - 0.35 * q), 0, 255).astype(np.uint8)
            card(fr, g, x2, ybot, r=28, glow=0, shadow=0.35)
            stars_pill(fr, x2 - cw / 2 + 24, ybot - chh / 2 + 24, 5, t, t11 + 0.15)
            pill(fr, "R$ 0", x2 - cw / 2 + 24, ybot + chh / 2 - 92, (120, 120, 128), (255, 255, 255), t, t14 + 0.35, "sm")
        label(fr, "produto ótimo", "md", "light", W / 2, ybot + chh / 2 + 80, t, t11, INK)
        label(fr, "+ distribuição ruim", "sm", "light", W / 2, ybot + chh / 2 + 170, t, t14, RED)
        footnote(fr, "Faturamento McDonald's: resultados anuais 2025 (fev/2026)", ybot + chh / 2 + 250, t, t9 + 0.25, dark=False)
        # --- dinheiro jorrando do Big Mac
        if t >= t9:
            B_ = _bills(); x = W / 2
            for i in range(NB):
                a = t - t9 - birth[i]
                if a <= 0 or a > 2.2: continue
                px = x + ox[i] + vx[i] * a; py = ytop + 40 + vy[i] * a + 0.5 * 1700 * a * a
                if py > H + 80 or px < -100 or px > W + 100: continue
                s = B_[int(((a0[i] + spin[i] * a) % (2 * math.pi)) / (2 * math.pi) * 24) % 24]
                if scl[i] != 1: s = cv2.resize(s, (int(s.shape[1] * scl[i]), int(s.shape[0] * scl[i])))
                paste(fr, s, px - s.shape[1] / 2, py - s.shape[0] / 2, clamp(a / 0.08))
        label(fr, "distribuição ótima", "md", "light", W / 2, ytop - chh / 2 - 120, t, t7, BLUE)
        if t >= t9:
            q = back((t - t9) / 0.3); bw_, bh_ = int(330 * q) + 1, int(110 * q) + 1
            paste(fr, solid(BLUE, bh_, bw_), W / 2 + cw / 2 - 30 - bw_, ytop - chh / 2 - bh_ / 2 + 10, 1, rrmask(bw_, bh_, bh_ // 2))
            if q > 0.6: label(fr, "VENCE", "md", "dark", W / 2 + cw / 2 - 195, ytop - chh / 2 + 6, t, t9 + 0.08, (255, 255, 255))
        return fr
    return dr

# ---------- globo com o Brasil em destaque ----------
_WORLD = []
def _world():
    if not _WORLD:
        d = json.load(open("countries.geo.json"))
        for f in d["features"]:
            g = f["geometry"]; polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            for poly in polys:
                r = np.array(poly[0], float)
                for _ in range(2):  # chaikin smoothing so the zoom doesn't look jagged
                    q = np.roll(r, -1, 0); r = np.stack([0.75 * r + 0.25 * q, 0.25 * r + 0.75 * q], 1).reshape(-1, 2)
                _WORLD.append((f["id"], r))
    return _WORLD

def ortho(lonlat, lon0, lat0, cx, cy, R):
    lo, la = np.radians(lonlat[:, 0] - lon0), np.radians(lonlat[:, 1]); l0 = math.radians(lat0)
    x = np.cos(la) * np.sin(lo); y = math.cos(l0) * np.sin(la) - math.sin(l0) * np.cos(la) * np.cos(lo)
    c = math.sin(l0) * np.sin(la) + math.cos(l0) * np.cos(la) * np.cos(lo)
    back_ = c < 0; n = np.hypot(x, y) + 1e-9
    x = np.where(back_, x / n, x); y = np.where(back_, y / n, y)
    return np.stack([cx + R * x, cy - R * y], 1), back_

def mg_globe(t_zoom_end, focus=(-52, -13)):
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur)
        k = ease(lt / max(t_zoom_end - (t - lt), 0.2))
        lon0, lat0 = lerp(-5, focus[0], k), lerp(12, focus[1], k)
        R = lerp(430, 2300, k ** 1.6); cx, cy = W / 2, lerp(1080, 1180, k)
        # atmosphere + ocean
        glow = np.zeros((H // 4, W // 4, 3), np.uint8)
        cv2.circle(glow, (int(cx / 4), int(cy / 4)), int(R / 4) + 6, (40, 60, 200), -1, cv2.LINE_AA)
        addlight(fr, cv2.resize(cv2.GaussianBlur(glow, (0, 0), 10), (W, H)), 0, 0, 0.55)
        cv2.circle(fr, (int(cx), int(cy)), int(R), (12, 16, 30), -1, cv2.LINE_AA)
        # graticule
        for lon in range(-180, 180, 30):
            pts, bk = ortho(np.array([(lon, la) for la in range(-90, 91, 3)], float), lon0, lat0, cx, cy, R)
            for a, b_, ba, bb in zip(pts[:-1], pts[1:], bk[:-1], bk[1:]):
                if not (ba or bb): cv2.line(fr, tuple(a.astype(int)), tuple(b_.astype(int)), (26, 32, 52), 2, cv2.LINE_AA)
        for la in range(-60, 61, 30):
            pts, bk = ortho(np.array([(lo, la) for lo in range(-180, 181, 3)], float), lon0, lat0, cx, cy, R)
            for a, b_, ba, bb in zip(pts[:-1], pts[1:], bk[:-1], bk[1:]):
                if not (ba or bb): cv2.line(fr, tuple(a.astype(int)), tuple(b_.astype(int)), (26, 32, 52), 2, cv2.LINE_AA)
        bra = []
        for cid, ring in _world():
            pts, bk = ortho(ring, lon0, lat0, cx, cy, R)
            if bk.all(): continue
            p = pts.astype(np.int32)
            if cid == "BRA": bra.append(p); continue
            cv2.fillPoly(fr, [p], (62, 66, 78), cv2.LINE_AA); cv2.polylines(fr, [p], True, (34, 36, 44), 2, cv2.LINE_AA)
        # Brasil: azul com brilho pulsando
        m = np.zeros((H // 4, W // 4), np.uint8)
        for p in bra: cv2.fillPoly(m, [p // 4], 255, cv2.LINE_AA)
        pulse = 0.55 + 0.25 * math.sin(lt * 9)
        addlight(fr, cv2.resize(cv2.cvtColor(cv2.GaussianBlur(m, (0, 0), 9), cv2.COLOR_GRAY2RGB), (W, H)) * np.float32([0.25, 0.3, 1.0]), 0, 0, pulse)
        for p in bra:
            cv2.fillPoly(fr, [p], BLUE, cv2.LINE_AA); cv2.polylines(fr, [p], True, (255, 255, 255), 3, cv2.LINE_AA)
        return fr
    return dr

# ---------- cenas de filme (O Impossível, 2012) ----------
_FS = {}
_BOX = {}
TRIM = {"crash": (2, 25)}  # 1º quadro ainda é o plano anterior
def _box(name):
    """área útil do plano (corta faixas pretas de letterbox/pillarbox), medida em 3 quadros"""
    if name not in _BOX:
        import os
        n = len([f for f in os.listdir(f"filme/shots/{name}") if f.endswith(".jpg")])
        acc = sum(cv2.imread(f"filme/shots/{name}/{k:04d}.jpg", 0).astype(np.float32) for k in (1, max(1, n // 2), n))
        rows, cols = np.where(acc.mean(1) > 3 * 9)[0], np.where(acc.mean(0) > 3 * 9)[0]
        box = (rows[0] + 2, rows[-1] - 2, cols[0] + 2, cols[-1] - 2) if len(rows) and len(cols) else (0, acc.shape[0], 0, acc.shape[1])
        # cortes de cena escondidos no trecho: usa só o pedaço contínuo mais longo
        prev, cuts = None, [0]
        for k in range(1, n + 1):
            g = cv2.resize(cv2.imread(f"filme/shots/{name}/{k:04d}.jpg", 0), (160, 90)).astype(np.float32)
            if prev is not None and np.abs(g - prev).mean() > 60: cuts.append(k - 1)
            prev = g
        cuts.append(n); a, b = max(zip(cuts[:-1], cuts[1:]), key=lambda x: x[1] - x[0])
        a, b = TRIM.get(name, (a, b))
        _BOX[name] = box + (a, b)
    return _BOX[name]

def _shot(name, i, dur=None):
    y0, y1, x0, x1, a, b = _box(name)
    if dur: i = i * min(1.0, max(0.55, (b - a) / (dur * FPS)))  # câmera lenta se o pedaço for curto
    i = int(clamp(a + i, a, b - 1)) + 1
    if (name, i) not in _FS:
        if len(_FS) > 10: _FS.clear()
        f = cv2.imread(f"filme/shots/{name}/{i:04d}.jpg")[y0:y1, x0:x1]
        _FS[(name, i)] = grade(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), 0.95)
    return _FS[(name, i)]

def film(name, mode="letterbox", cy=900, z=(1.0, 1.08), fx=0.5, fx1=None, gain=1.0):
    def rel(x):
        import os
        w0 = cv2.imread(f"filme/shots/{name}/0001.jpg", 0).shape[1]; y0, y1, x0, x1 = _box(name)[:4]
        return clamp((x * w0 - x0) / (x1 - x0))
    fxr = [None, None]
    def dr(t, lt, dur, ow=W, oh=H):
        nonlocal fx, fx1
        if fxr[0] is None: fxr[0] = rel(fx); fxr[1] = rel(fx1 if fx1 is not None else fx)
        fx, fx1 = fxr
        f = _shot(name, lt * FPS, dur); p = P(lt, dur)
        if gain != 1.0: f = np.clip(f.astype(np.float32) * gain, 0, 255).astype(np.uint8)
        if mode == "full":  # recorte vertical centrado no personagem (fx -> fx1 se ele se move)
            return kb(f, ow, oh, p, z, (fx, 0.5), (((fx1 if fx1 is not None else fx) - fx), 0))
        fr = tipo()(t, lt, dur)
        lw, lh = W, int(W * f.shape[0] / f.shape[1])
        card(fr, kb(f, lw, lh, p, z), W / 2, cy, r=0, glow=0.22)
        return fr
    return dr

# ---------- estudo da Graphite: headline numa folha ----------
def _ai_share(x):  # x: 0=jan/2020 .. 1=mai/2025 (forma da curva do estudo: virada em nov/2024)
    pts = [(0, 5), (0.52, 6), (0.62, 22), (0.71, 39), (0.80, 46), (0.89, 50.5), (1.0, 51.5)]
    return float(np.interp(x, [a for a, _ in pts], [b for _, b in pts]))

_PAPER = {}
def mg_paper(seg, t_hl, t_chart):
    PW, PH = 900, 1180; INKP = (24, 24, 28)
    def base():
        if "b" in _PAPER: return _PAPER
        pap = np.full((PH, PW, 3), (247, 245, 238), np.uint8)
        n = np.random.default_rng(4).normal(0, 3, (PH, PW, 1)); pap = np.clip(pap + n, 0, 255).astype(np.uint8)
        y = 60
        for s, wt, sz, col in (("GRAPHITE  ·  FIVE PERCENT RESEARCH", 600, 26, (120, 120, 130)),):
            paste(pap, _plain(s, wt, sz, col), 60, y); y += 60
        cv2.line(pap, (60, y), (PW - 60, y), (210, 208, 200), 2); y += 40
        lines = ["More Articles Are", "Now Created by AI", "Than Humans"]
        heads = [_plain(s, 800, 76, INKP) for s in lines]
        _PAPER["heads"] = [(h, 60, y + i * 92) for i, h in enumerate(heads)]
        hl = heads[1]; _PAPER["hl"] = (60, y + 92 + 18, 60 + hl.shape[1], y + 92 + hl.shape[0] - 6)
        y += 3 * 92 + 30
        paste(pap, _plain("AI Content Overtook Human Content in Late 2024", 500, 32, (90, 90, 100)), 60, y); y += 80
        # chart frame
        cx0, cy0, cx1, cy1 = 90, y + 20, PW - 70, y + 520
        _PAPER["chart"] = (cx0, cy0, cx1, cy1)
        for v in (0, 25, 50, 75, 100):
            yy = int(cy1 - (cy1 - cy0) * v / 100); cv2.line(pap, (cx0, yy), (cx1, yy), (228, 226, 218), 1)
            paste(pap, _plain(f"{v}%", 500, 20, (150, 150, 155)), 40, yy - 14)
        for i, yr in enumerate(("2020", "2021", "2022", "2023", "2024", "2025")):
            xx = int(cx0 + (cx1 - cx0) * i * 12 / 64.5); paste(pap, _plain(yr, 500, 20, (150, 150, 155)), xx - 20, cy1 + 10)
        paste(pap, _plain("Fonte: Graphite (2025), 43 mil artigos do Common Crawl", 500, 22, (140, 140, 148)), 60, PH - 70)
        _PAPER["b"] = pap
        return _PAPER
    def dr(t, lt, dur):
        B_ = base(); pap = B_["b"].copy()
        # marca-texto em "Now Created by AI"
        q = eout((t - t_hl) / 0.45)
        if q > 0:
            x0, y0, x1, y1 = B_["hl"]; xe = int(lerp(x0, x1 + 10, q))
            ov = pap[y0:y1, x0 - 8:xe].astype(np.float32); pap[y0:y1, x0 - 8:xe] = (ov * np.float32([1.0, 0.93, 0.45])).astype(np.uint8)
        for h, x, y in B_["heads"]: paste(pap, h, x, y)
        # linhas IA × humanos se cruzando
        cx0, cy0, cx1, cy1 = B_["chart"]; k = clamp((t - t_chart) / 1.1)
        if k > 0:
            xs = np.linspace(0, k, max(int(200 * k), 2))
            for col, f in ((BLUE, lambda x: _ai_share(x)), ((150, 150, 158), lambda x: 100 - _ai_share(x))):
                pts = np.array([(cx0 + (cx1 - cx0) * x, cy1 - (cy1 - cy0) * f(x) / 100) for x in xs], np.int32)
                cv2.polylines(pap, [pts], False, col, 11, cv2.LINE_AA)
            for lab, col, v in (("IA", BLUE, _ai_share(k)), ("Humanos", (130, 130, 138), 100 - _ai_share(k))):
                paste(pap, _plain(lab, 700, 36, col), cx0 + (cx1 - cx0) * k + 12, cy1 - (cy1 - cy0) * v / 100 - 20)
            if k > 0.9:  # ponto de virada nov/2024
                xx, yy = int(cx0 + (cx1 - cx0) * 0.89), int(cy1 - (cy1 - cy0) * 0.505)
                r_ = int(14 + 40 * eout((k - 0.9) / 0.1)); cv2.circle(pap, (xx, yy), r_, RED, 4, cv2.LINE_AA)
        # mesa escura + folha girada com sombra
        fr = solid((20, 18, 17)); fr = (fr * (1.25 - 0.5 * np.linspace(0, 1, H)[:, None, None])).astype(np.uint8)
        k_in = back(lt / 0.35); p = P(lt, dur)
        s = lerp(0.98, 1.08, p) * lerp(0.7, 1, k_in); ang = lerp(-6, -2, k_in) + 1.5 * p
        cxp, cyp = W / 2, lerp(H * 1.3, 1010, k_in)
        M = cv2.getRotationMatrix2D((PW / 2, PH / 2), ang, s); M[0, 2] += cxp - PW / 2; M[1, 2] += cyp - PH / 2
        sh = cv2.warpAffine(np.ones((PH, PW), np.float32), M, (W, H)); sh = cv2.GaussianBlur(sh, (0, 0), 25) * 0.6
        fr = (fr * (1 - sh[..., None] * 0.9)).astype(np.uint8)
        m = cv2.warpAffine(np.ones((PH, PW), np.float32), M, (W, H))
        wp = cv2.warpAffine(pap, M, (W, H))
        return (fr * (1 - m[..., None]) + wp * m[..., None]).astype(np.uint8)
    return dr

# ---------- políticos mais votados 2026 ----------
POL = [("nikolas", "Nikolas Ferreira", "3,1 mi votos"), ("pavanato", "Lucas Pavanato", "3,0 mi votos"),
       ("eduarda", "Eduarda Campopiano", "1,96 mi votos"), ("anaelisa", "Ana Elisa", "524 mil votos")]
NEWS = [("InfoMoney", "Nikolas e Pavanato lideram os 20 deputados federais mais votados"),
        ("Gazeta do Povo", "Eduarda Campopiano, a deputada estadual mais votada do país")]

def news_card(dst, src, head, cx, cy, t, tin, wdt=980):
    if t < tin: return
    q = back((t - tin) / 0.3)
    c = solid((255, 255, 255), 150, wdt)
    paste(c, _plain(src.upper(), 700, 24, (200, 30, 40)), 28, 18)
    f = font(700, 34); words, lines, cur = head.split(), [], ""
    for w_ in words:
        if f.getlength(cur + " " + w_) > wdt - 60 and cur: lines.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    lines.append(cur)
    for i, ln in enumerate(lines[:2]): paste(c, _plain(ln, 700, 34, INK), 28, 54 + i * 44)
    s = lerp(0.85, 1, q); c2 = cv2.resize(c, (int(wdt * s), int(150 * s)))
    card(dst, c2, cx, cy + 30 * (1 - q), r=18, glow=0.12, a=clamp(q))

def phone_clip(dst, name, cx, cy, cw, ch, lt, a=1.0, label=None, sub=None, t=0, tin=0):
    f = _shot(name, lt * FPS)
    c = kb(f, cw, ch, 0.5, (1.0, 1.0)).copy()
    cv2.rectangle(c, (0, ch - 120), (cw, ch), (0, 0, 0), -1)
    c[ch - 220:ch - 120] = (c[ch - 220:ch - 120] * np.linspace(1, 0.1, 100)[:, None, None]).astype(np.uint8)
    if label: paste(c, _plain(label, 700, 30, (255, 255, 255)), 20, ch - 108)
    if sub: paste(c, _plain(sub, 700, 28, (140, 170, 255)), 20, ch - 64)
    card(dst, c, cx, cy, r=26, glow=0.15, a=a)

def mg_politicos(t0):
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur)
        for i, (n, name, votes) in enumerate(POL):
            tin = t0 + i * 0.16; q = back((t - tin) / 0.28)
            if q <= 0: continue
            cx, cy = (290, 790)[i % 2], (880, 1420)[i // 2]
            phone_clip(fr, n, cx, cy + 60 * (1 - q), int(440 * lerp(0.8, 1, q)), int(530 * lerp(0.8, 1, q)), t - tin, clamp(q), name, votes)
        news_card(fr, *NEWS[0], W / 2, 260, t, t0 + 0.35)
        news_card(fr, *NEWS[1], W / 2, 440, t, t0 + 0.75)
        return fr
    return dr

def mg_duo(a_, b_, t0):
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur)
        for i, (n, name) in enumerate((a_, b_)):
            tin = t0 + i * 0.2; q = back((t - tin) / 0.3)
            if q <= 0: continue
            f = _shot(n, (t - tin) * FPS); cw, ch = 1000, 562
            c = kb(f, cw, ch, P(lt, dur), (1.05, 1.12)).copy()
            cv2.rectangle(c, (0, ch - 80), (cw, ch), (0, 0, 0), -1)
            paste(c, _plain(name, 700, 40, (255, 255, 255)), 28, ch - 70)
            x = W / 2 + (1 - q) * (-W if i == 0 else W)
            card(fr, c, x, (520, 1400)[i], r=24, glow=0.18)
        return fr
    return dr

def vm_avatar(r):
    av = solid((0, 0, 0), 2 * r, 2 * r)
    for sz in range(int(r * 1.0), 10, -4):
        f = font(800, sz)
        if f.getlength(".VM") < r * 1.55: break
    t_ = _plain(".VM", 800, sz, (255, 255, 255))
    paste(av, t_, r - t_.shape[1] / 2, r - t_.shape[0] / 2 - sz * 0.1)
    d = _plain(".", 800, sz, BLUE); paste(av, d, r - t_.shape[1] / 2, r - t_.shape[0] / 2 - sz * 0.1)
    return av

# ---------- Mona Lisa pop "gerada por IA" ----------
_MP = {}
def _monapop(CW, CH):
    if (CW, CH) in _MP: return _MP[(CW, CH)]
    src = cv2.cvtColor(cv2.imread("imgs/monalisa.jpg"), cv2.COLOR_BGR2RGB); h, w = src.shape[:2]
    crop = cv2.resize(src[0:int(0.85 * h), int(0.05 * w):int(0.90 * w)], (CW, CH), interpolation=cv2.INTER_AREA)
    g = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    g = cv2.GaussianBlur(g, (0, 0), 1.2); g = (g - g.min()) / (g.max() - g.min())
    pal = np.array([(28, 30, 90), (200, 40, 110), (245, 130, 45), (255, 222, 120)], np.float32)  # pop: azul, magenta, laranja, amarelo
    pop = pal[np.clip((g * 4).astype(int), 0, 3)]
    pop = pop * 0.75 + crop.astype(np.float32) * 0.25
    yy, xx = np.mgrid[0:CH, 0:CW]; dots = ((np.sin(xx * 0.55) * np.sin(yy * 0.55)) > 0.35)[..., None]  # meio-tom
    pop = np.where(dots & (g[..., None] > 0.3) & (g[..., None] < 0.75), pop * 0.82, pop)
    cv2.rectangle(pop, (0, 0), (CW - 1, CH - 1), (20, 20, 24), 10)
    _MP[(CW, CH)] = (np.clip(pop, 0, 255).astype(np.uint8), cv2.GaussianBlur(np.random.default_rng(2).integers(0, 255, (CH // 8, CW // 8, 3)).astype(np.uint8), (0, 0), 1))
    return _MP[(CW, CH)]

def mg_monapop(t_gen, speed=1.0, prompt="monalisa pop com óculos, pirulito e orelhas de rato", cy=860):
    CW, CH = 720, 900
    P_ = lambda fx, fy: ((fx - 0.05) / 0.85 * CW, fy / 0.85 * CH)   # fração da pintura -> pixel do card
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur); q = (t - t_gen) * speed
        pop, nz = _monapop(CW, CH)
        k = ease(q / 0.45)
        noise_ = cv2.resize(nz, (CW, CH), interpolation=cv2.INTER_NEAREST)
        img = (noise_ * (1 - k) + (cv2.GaussianBlur(pop, (0, 0), 0.5 + 18 * (1 - k)) if k < 1 else pop) * k).astype(np.uint8)
        if 0 < k < 1:  # linha de "renderização" descendo
            y = int(CH * k); img[max(0, y - 3):y + 3] = (255, 255, 255)
        # adereços
        def popin(at): return back((q - at) / 0.18) if q > at + 0.01 else 0
        s = popin(0.85)  # orelhas
        if s > 0:
            for fx in (0.28, 0.64):
                cx, cy_ = P_(fx, 0.105); cv2.circle(img, (int(cx), int(cy_)), int(0.105 * 1920 / 1632 * CW * s * 0.95), (12, 12, 14), -1, cv2.LINE_AA)
        s = popin(0.55)  # óculos caindo
        if s > 0:
            drop = (1 - clamp((q - 0.55) / 0.18)) * -160
            for fx in (0.37, 0.55):
                cx, cy_ = P_(fx, 0.305); rw, rh = int(0.085 * CW / 0.85 * s), int(0.045 * CH / 0.85 * s)
                cv2.rectangle(img, (int(cx - rw), int(cy_ - rh + drop)), (int(cx + rw), int(cy_ + rh + drop)), (8, 8, 10), -1, cv2.LINE_AA)
                cv2.line(img, (int(cx - rw * 0.6), int(cy_ - rh * 0.4 + drop)), (int(cx - rw * 0.1), int(cy_ - rh * 0.4 + drop)), (230, 230, 240), 4, cv2.LINE_AA)
            a, b = P_(0.43, 0.30), P_(0.49, 0.30)
            cv2.line(img, (int(a[0]), int(a[1] + drop)), (int(b[0]), int(b[1] + drop)), (8, 8, 10), 8, cv2.LINE_AA)
        s = popin(0.70)  # pirulito
        if s > 0:
            cx, cy_ = P_(0.29, 0.47); r = int(58 * s)
            cv2.line(img, (int(cx + r * 0.5), int(cy_ + r * 0.5)), (int(cx + 150 * s), int(cy_ + 230 * s)), (245, 245, 245), 10, cv2.LINE_AA)
            cv2.circle(img, (int(cx), int(cy_)), r, (255, 90, 160), -1, cv2.LINE_AA)
            for i in range(1, 4): cv2.ellipse(img, (int(cx), int(cy_)), (int(r * i / 4), int(r * i / 4)), i * 70, 0, 230, (255, 255, 255), 6, cv2.LINE_AA)
        card(fr, img, W / 2, cy, r=26, glow=0.25)
        # prompt
        n = int(clamp(q / 0.5) * len(prompt))
        box = solid((30, 30, 36), 86, 960)
        paste(box, _plain("✦" if False else "IA", 800, 30, (140, 160, 255)), 26, 22)
        paste(box, _plain(prompt[:n] + ("|" if n < len(prompt) else ""), 500, 30, (235, 235, 240)), 90, 22)
        paste(fr, box, W / 2 - 480, cy - CH / 2 - 130, 1, rrmask(960, 86, 43))
        return fr
    return dr

# ---------- credibilidade: manchete, citação e fonte ----------
def footnote(dst, s, y, t=0, tin=0, dark=True):
    if t < tin: return
    r = _plain(s, 500, 28, (160, 160, 168) if dark else (100, 100, 108))
    if r.shape[1] > W - 60: r = cv2.resize(r, (W - 60, int(r.shape[0] * (W - 60) / r.shape[1])))
    paste(dst, r, W / 2 - r.shape[1] / 2, y, clamp((t - tin) / 0.2))

def with_overlay(base, fn):
    def dr(t, lt, dur, **kw):
        fr = base(t, lt, dur, **kw); fn(fr, t, lt, dur); return fr
    return dr

def quote_card(dst, quote, author, cx, cy, t, tin, wdt=960):
    if t < tin: return
    q = back((t - tin) / 0.3)
    f = font(600, 34); lines, cur = [], ""
    for w_ in quote.split():
        if f.getlength(cur + " " + w_) > wdt - 90 and cur: lines.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    lines.append(cur); hh = 60 + len(lines) * 46 + 60
    c = solid((250, 248, 242), hh, wdt)
    paste(c, _plain("“", 800, 90, BLUE), 22, -10)
    for i, ln in enumerate(lines): paste(c, _plain(ln, 600, 34, INK), 70, 40 + i * 46)
    paste(c, _plain(author, 700, 26, (120, 120, 128)), 70, 40 + len(lines) * 46 + 14)
    s = lerp(0.85, 1, q); c2 = cv2.resize(c, (int(wdt * s), int(hh * s)))
    card(dst, c2, cx, cy + 30 * (1 - q), r=20, glow=0.12, a=clamp(q))

def mg_rank(seg, t0):
    rows = [("1º", "África do Sul", "9h24", (150, 150, 158)), ("2º", "Brasil", "9h13", BLUE), ("", "média mundial", "6h40", (110, 110, 118))]
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur)
        for i, (pos, name, val, col) in enumerate(rows):
            tin = t0 + i * 0.22; q = back((t - tin) / 0.3)
            if q <= 0: continue
            y = 820 + i * 190; x = W / 2 + (1 - q) * 300
            rw = 900 if name != "Brasil" else int(900 * lerp(1, 1.06, clamp((t - tin - 0.3) / 0.2)))
            row = solid((26, 26, 32) if name != "Brasil" else (20, 26, 90), 150, rw)
            paste(row, _plain(pos, 800, 64, (255, 255, 255)), 30, 30)
            paste(row, _plain(name, 700, 52, (255, 255, 255)), 140, 40)
            v = _plain(val, 800, 60, (255, 255, 255) if name == "Brasil" else (200, 200, 208)); paste(row, v, rw - v.shape[1] - 36, 34)
            card(fr, row, x, y, r=24, glow=0.25 if name == "Brasil" else 0.05)
        footnote(fr, "Fonte: DataReportal / We Are Social & Meltwater — Digital 2024 (tempo diário online)", 1420, t, t0)
        return fr
    return dr

# ---------- todo mundo dançando igual: grade 3x3 ----------
def mg_grid9(names, t0):
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur); cw, ch, g = 330, 587, 12
        for i, n in enumerate(names[:9]):
            q = eout((t - t0 - (i % 3 + i // 3) * 0.04) / 0.2)
            if q <= 0: continue
            cx = W / 2 + (i % 3 - 1) * (cw + g); cy = 960 + (i // 3 - 1) * (ch + g)
            c = kb(_shot(n, (t - t0) * FPS), int(cw * lerp(0.85, 1, q)), int(ch * lerp(0.85, 1, q)), 0.5, (1.0, 1.0))
            card(fr, c, cx, cy, r=18, glow=0.05, a=q)
        return fr
    return dr

# ---------- cases reais: perfis com contadores subindo (prints em ../cases) ----------
CASES = {  # preencha com SEUS prints (pasta ../cases): avatar (cx, cy, r) no print do cabeçalho; reels = (coluna 0-2, y do rótulo de views) no print do grid
 "voce": dict(head="perfil_cabecalho", grid="perfil_grid", av=(180, 370, 110), name="Seu Nome", user="@seuperfil", fol=500e3, tiles=[(0, 640), (1, 1170), (2, 1700)], views=["100 mil", "200 mil", "300 mil"]),
 "cliente1": dict(head="c1_cabecalho", grid="c1_grid", av=(176, 181, 120), name="Cliente 1", fol=1.0e6, tiles=[(1, 600)], views=["10 mi"]),
 "cliente2": dict(head="c2_cabecalho", grid="c2_grid", av=(176, 181, 120), name="Cliente 2", fol=800e3, tiles=[(1, 650)], views=["5 mi"]),
 "cliente3": dict(head="c3_cabecalho", grid="c3_grid", av=(176, 170, 112), name="Cliente 3", fol=150e3, tiles=[(0, 820)], views=["400 mil"]),
}
_CI = {}
def _case_img(f):
    if f not in _CI: _CI[f] = cv2.cvtColor(cv2.imread(f"../cases/{f}.jpg"), cv2.COLOR_BGR2RGB)
    return _CI[f]
def case_avatar(k, r):
    c = CASES[k]; im = _case_img(c["head"]); cx, cy, rr = c["av"]
    a = cv2.resize(im[cy - rr:cy + rr, cx - rr:cx + rr], (2 * r, 2 * r))
    m = np.zeros((2 * r, 2 * r), np.float32); cv2.circle(m, (r, r), r, 1, -1, cv2.LINE_AA)
    return a, m
def case_tile(k, i, w_):
    col, ly = CASES[k]["tiles"][i]; im = _case_img(CASES[k]["grid"])
    t = im[max(0, ly - 545):ly + 40, col * 402 + 3:col * 402 + 399]
    return cv2.resize(t, (w_, int(w_ * t.shape[0] / t.shape[1])))
def fmt_fol(v):
    return f"{v / 1e6:.1f} mi".replace(".", ",") if v >= 999.5e3 else f"{int(round(v / 1e3))} mil"

def views_pill(dst, txt, cx, cy, t, tin):
    if t < tin: return
    q = back((t - tin) / 0.25)
    r = _plain("▶ " + txt + " views" if False else txt + " views", 800, 34, (255, 255, 255))
    pw, ph = int((r.shape[1] + 40) * q) + 1, int(64 * q) + 1
    p = solid(BLUE, ph, pw)
    if q > 0.5: rr = cv2.resize(r, (max(int(r.shape[1] * q), 1), max(int(r.shape[0] * q), 1))); paste(p, rr, pw / 2 - rr.shape[1] / 2, ph / 2 - rr.shape[0] / 2 - 2)
    paste(dst, p, cx - pw / 2, cy - ph / 2, 1, rrmask(pw, ph, ph // 2))

def mg_cases(seg, t_me, t_cli, phone):
    def counter(fr, v, x, y, sz, t, tin, dur=1.0, col=(255, 255, 255)):
        k = 1 - (1 - clamp((t - tin) / dur)) ** 4
        r = _plain(fmt_fol(v * k), 800, sz, col); paste(fr, r, x, y)
        return r.shape[1]
    def dr(t, lt, dur):
        if t < t_me: return phone(t, lt, dur)
        fr = tipo()(t, lt, dur)
        if t < t_cli:  # meu perfil
            q = back((t - t_me) / 0.3); r = int(150 * clamp(q, 0, 1.2))
            if r > 4:
                a, m = case_avatar("voce", r); cv2.circle(fr, (W // 2, 430), r + 10, BLUE, -1, cv2.LINE_AA); paste(fr, a, W / 2 - r, 430 - r, 1, m)
            u = _plain(CASES["voce"]["user"], 700, 46, (255, 255, 255)); paste(fr, u, W / 2 - u.shape[1] / 2, 610)
            v = _plain(fmt_fol(CASES["voce"]["fol"]), 800, 150, BLUE); vw = v.shape[1]
            cw = _plain(fmt_fol(CASES["voce"]["fol"] * (1 - (1 - clamp((t - t_me) / 1.1)) ** 4)), 800, 150, BLUE)
            paste(fr, cw, W / 2 - vw / 2, 690)
            s = _plain("seguidores", 600, 44, (200, 200, 208)); paste(fr, s, W / 2 - s.shape[1] / 2, 880)
            for i in range(3):
                qi = back((t - t_me - 0.25 - i * 0.12) / 0.3)
                if qi <= 0: continue
                tl_ = case_tile("voce", i, int(310 * clamp(qi, 0.3, 1.1)))
                card(fr, tl_, W / 2 + (i - 1) * 330, 1300, r=16, glow=0.15)
                views_pill(fr, CASES["voce"]["views"][i], W / 2 + (i - 1) * 330, 1300 + 250, t, t_me + 0.45 + i * 0.12)
            return fr
        # clientes
        for i, k in enumerate(("cliente1", "cliente2", "cliente3")):
            tin = t_cli + i * 0.18; q = back((t - tin) / 0.3)
            if q <= 0: continue
            y0 = 300 + i * 530; x_off = (1 - clamp(q)) * -W
            row = solid((22, 22, 28), 500, 1000)
            a, m = case_avatar(k, 85); paste(row, a, 40, 40, 1, m)
            paste(row, _plain(CASES[k]["name"], 700, 40, (255, 255, 255)), 230, 100)
            counter(row, CASES[k]["fol"], 40, 230, 112, t, tin + 0.1, 1.1, BLUE)
            paste(row, _plain("seguidores", 600, 36, (190, 190, 198)), 44, 380)
            tile = case_tile(k, 0, 270); ty = (500 - tile.shape[0]) // 2; paste(row, tile, 700, ty)
            cv2.rectangle(row, (696, ty - 4), (974, ty + tile.shape[0] + 4), BLUE, 4)
            views_pill(row, CASES[k]["views"][0], 835, ty + tile.shape[0] - 40, t, tin + 0.5)
            card(fr, row, W / 2 + x_off, y0 + 250, r=26, glow=0.12)
        return fr
    return dr

# ---------- explosão de views: grade 3x3 de criadores com contador subindo rápido ----------
def fmt_views(v):
    if v >= 1e6: return f"{v / 1e6:.1f} mi".replace(".", ",")
    if v >= 1e3: return f"{int(v / 1e3)} mil"
    return f"{int(v)}"

def mg_viral(tiles, t0):
    """tiles: [(shot, rótulo, fx, offset_frames, views_finais)]; contador exponencial, simbólico"""
    def dr(t, lt, dur):
        fr = tipo()(t, lt, dur); cw, ch, g = 330, 587, 12
        for i, (n, lab, fx, off, vmax) in enumerate(tiles[:9]):
            tin = t0 + (i % 3 + i // 3) * 0.05; q = eout((t - tin) / 0.2)
            if q <= 0: continue
            cx = W / 2 + (i % 3 - 1) * (cw + g); cy = 960 + (i // 3 - 1) * (ch + g)
            c = kb(_shot(n, (t - t0) * FPS + off), cw, ch, 0.5, (1.0, 1.06), (fx, 0.45)).copy()
            c[ch - 150:] = (c[ch - 150:] * np.linspace(1, 0.25, 150)[:, None, None]).astype(np.uint8)
            k = clamp((t - tin - 0.1) / max(dur - 0.4, 0.5)); v = vmax * (np.expm1(5 * k) / np.expm1(5))
            pill_ = _plain("▶ " + fmt_views(v) if False else fmt_views(v) + " views", 800, 34, (255, 255, 255))
            pw = pill_.shape[1] + 30; p = solid(BLUE, 54, pw); paste(p, pill_, 15, 4)
            paste(c, p, 14, ch - 120, 1, rrmask(pw, 54, 27))
            paste(c, _plain(lab, 600, 24, (230, 230, 236)), 16, ch - 56)
            card(fr, c, cx, cy, r=18, glow=0.08, a=q)
        return fr
    return dr
