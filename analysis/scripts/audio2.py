import numpy as np, librosa, soundfile as sf, json
y,sr=sf.read('audio44k.wav'); L,R=y[:,0],y[:,1]; side=(L-R)/2; mid=(L+R)/2
def db(x): return 20*np.log10(np.sqrt(np.mean(x**2))+1e-12)
# side-channel level per 10 s
print("side (music proxy) / mid level per 15s window:")
row=[]
for t in range(0,904,15):
    s=side[t*sr:(t+15)*sr]; mm=mid[t*sr:(t+15)*sr]
    row.append(f"{t//60}:{t%60:02d} S{db(s):6.1f} M{db(mm):6.1f}")
for i in range(0,len(row),4): print(" | ".join(row[i:i+4]))
# tempo of side channel per minute
sd=librosa.resample(side,orig_sr=sr,target_sr=22050)
print("\ntempo estimates (side channel) per 60s window:")
for t in range(0,900,60):
    seg=sd[t*22050:(t+60)*22050]
    if np.sqrt(np.mean(seg**2))<1e-4: print(t,"silent"); continue
    oenv=librosa.onset.onset_strength(y=seg,sr=22050)
    tempo=librosa.feature.tempo(onset_envelope=oenv,sr=22050,aggregate=None)
    print(f"{t//60}:{t%60:02d} median tempo {np.median(tempo):.1f} BPM", end=' ; ')
print()
# chroma-based novelty to find music track changes
C=librosa.feature.chroma_cqt(y=sd,sr=22050,hop_length=22050)  # 1 frame/sec
M=librosa.feature.mfcc(y=sd,sr=22050,hop_length=22050,n_mfcc=13)
F=np.vstack([C,M/50]); F=(F-F.mean(1,keepdims=True))/(F.std(1,keepdims=True)+1e-6)
nov=[np.linalg.norm(F[:,max(0,i-8):i].mean(1)-F[:,i:i+8].mean(1)) for i in range(F.shape[1])]
nov=np.array(nov); peaks=[i for i in range(8,len(nov)-8) if nov[i]==nov[i-6:i+7].max() and nov[i]>np.percentile(nov,93)]
print("music novelty peaks (possible track changes) at s:",[f"{p//60}:{p%60:02d}" for p in peaks])
# key estimate overall
chroma=C.mean(1); keys=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
print("dominant chroma pitch classes:",[keys[i] for i in np.argsort(-chroma)[:4]])
