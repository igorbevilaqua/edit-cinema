import numpy as np, soundfile as sf
from takes import TAKES
a, sr = sf.read("audio16k.wav"); hop = sr//100
db = 20*np.log10(np.sqrt(np.convolve(a**2, np.ones(hop*2)/(hop*2), 'same')[::hop])+1e-9)
TH = -58.7 + 11
def regions(s, e, merge=0.22):
    act = db[int(s*100):int(e*100)] > TH
    out=[]; i=0
    while i < len(act):
        if act[i]:
            j=i
            while j<len(act) and act[j]: j+=1
            if out and (i-out[-1][1])/100 < merge: out[-1][1]=j
            else: out.append([i,j])
            i=j
        else: i+=1
    return [(s+x/100, s+y/100) for x,y in out if y-x>6]
if __name__ == "__main__":
    for tid,s,e in TAKES:
        r = regions(s,e); tot=sum(y-x for x,y in r)
        print(f"{tid:10s} speech={tot:5.2f}s  " + " ".join(f"{x:.2f}-{y:.2f}" for x,y in r))
