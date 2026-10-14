import json; from takes import TAKES
W = json.load(open("words.json"))
for tid, a, b in TAKES:
    ws = [w for w in W if w["start"] >= a and w["end"] <= b + 0.3]
    out, prev = [], None
    for w in ws:
        if prev is not None and w["start"] - prev > 0.3: out.append(f"<{w['start']-prev:.1f}>")
        out.append(w["word"].strip()); prev = w["end"]
    print(f"{tid:10s} {ws[0]['start']:.2f}-{ws[-1]['end']:.2f} " + " ".join(out))
