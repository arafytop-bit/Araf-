import numpy as np, soundfile as sf, json, librosa
y,sr=sf.read('audio44k.wav'); L,R=y[:,0],y[:,1]; side=(L-R)/2; mid=(L+R)/2
hop=441
def env(x):
    n=len(x)//hop; return np.sqrt((x[:n*hop].reshape(n,hop)**2).mean(1))
Es=20*np.log10(env(side)+1e-9); Em=20*np.log10(env(mid)+1e-9)
# local baseline of side (2 s median), find excursions > 12 dB lasting >= 30ms
from scipy.ndimage import median_filter
base=median_filter(Es,size=301)
exc=Es-base
cand=[]; i=0
while i<len(exc):
    if exc[i]>12:
        j=i
        while j<len(exc) and exc[j]>6: j+=1
        if j-i>=3: cand.append((i/100,(j-i)/100,float(exc[i:j].max()),float(Es[i:j].max())))
        i=j
    else: i+=1
print("side-channel transients (time, dur, excess dB, level dB):",len(cand))
for c in sorted(cand,key=lambda c:-c[3])[:40]: print(f"  {int(c[0]//60)}:{c[0]%60:05.2f} dur {c[1]:.2f}s +{c[2]:.1f}dB level {c[3]:.1f}")
