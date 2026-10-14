# final speech segments (src seconds) after region verification
from takes import TAKES
from regions import regions, db
PICK = {"injusta": 1, "narr2": -1, "davinci": -1, "bom": -1, "padroes": -1, "recompensa": -1}
FLOOR = -58.7
SKIP = {"embreve"}  # redundante com o estudo dos 51% (corte para caber em 3 min)
MAXEND = {"arte": 558.50}  # a soft false start follows right after

def tail(e, limit):
    """follow the decay of the last syllable until it reaches the room noise (max 0.4 s, never past limit)"""
    i, quiet, lo, lo_i = int(e * 100), 0, 0.0, int(e * 100)
    while i < int(min(e + 0.4, limit) * 100) and quiet < 3:
        if db[i] < lo: lo, lo_i = db[i], i
        if db[i] > lo + 6 and i > lo_i: return lo_i / 100  # a new word starts: cut at the valley
        quiet = quiet + 1 if db[i] < FLOOR + 5 else 0; i += 1
    return i / 100 + 0.03

def head(s, limit):
    i, quiet = int(s * 100), 0
    while i > int(max(s - 0.15, limit) * 100) and quiet < 2:
        quiet = quiet + 1 if db[i] < FLOOR + 5 else 0; i -= 1
    return i / 100 - 0.02

def segments():
    out = []
    for tid, s, e in TAKES:
        if tid in SKIP: continue
        r = [x for x in regions(s, e) if x[1] - x[0] > 0.25]
        if tid in PICK: r = [r[PICK[tid]]]
        nxt = min([x[0] for x in regions(r[-1][1], r[-1][1] + 1.0) if x[0] > r[-1][1] + 0.05] or [r[-1][1] + 1.0])
        out.append((tid, head(r[0][0], s - 0.3), min(tail(r[-1][1], nxt - 0.05), MAXEND.get(tid, 1e9))))
    return out

if __name__ == "__main__":
    S = segments(); print(round(sum(e - s for _, s, e in S), 2), len(S))
    for tid, s, e in S: print(f"{tid:10s} {s:8.2f} {e:8.2f}")
