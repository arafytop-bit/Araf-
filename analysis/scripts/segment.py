import numpy as np, json
m=np.load('metrics.npz'); chg=m['chg']; hist=m['hist']
G=np.load('metrics_gray160.npy').astype(np.int16)
N=len(chg); fps=30.0
EV_TH=0.004   # frame is "active" if >0.4% pixels change (above mouth-flap level)
act=chg>EV_TH
# group active frames into events allowing gaps of <=2 frames
events=[]; i=1
while i<N:
    if act[i]:
        s=i; e=i; j=i+1
        while j<N and (act[j] or (j+1<N and act[j+1]) or (j+2<N and act[j+2])):
            if act[j]: e=j
            j+=1
        events.append([s,e]); i=e+1
    else: i+=1
def stable_frame_before(s):  # last frame before event
    return max(0,s-1)
res=[]
for s,e in events:
    b=stable_frame_before(s); a=min(N-1,e)  # frame index e is the first frame AFTER last change (chg[e] is diff e-1->e) -> frame e is new state
    d=np.abs(G[a]-G[b]); frac=(d>25).mean()
    length=e-s+1
    res.append(dict(s=int(s),e=int(e),len=int(length),maxchg=float(chg[s:e+1].max()),sumchg=float(chg[s:e+1].sum()),ba_frac=float(frac),maxhist=float(hist[s:e+1].max())))
json.dump(res,open('events.json','w'))
print("events:",len(res))
ba=np.array([r['ba_frac'] for r in res]); L=np.array([r['len'] for r in res])
for th in [0.02,0.05,0.1,0.2,0.3,0.5]:
    print(f"before/after diff >{th}: {(ba>th).sum()}")
print("event length distribution:",np.bincount(np.minimum(L,40)))
