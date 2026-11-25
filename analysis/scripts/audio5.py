import numpy as np, soundfile as sf, json, librosa
y,sr=sf.read('audio44k.wav'); side=(y[:,0]-y[:,1])/2
S=json.load(open('states_words.json'))
# title-card cut times (states whose frame is a title card): ids from inspection
tc_ids=[68,129,164,228,268,307,345,377,401,436]
times=[S[i]['s']/30 for i in tc_ids]
segs=[side[int((t-0.3)*sr):int((t+1.2)*sr)] for t in times]
def feat(x):
    e=librosa.feature.rms(y=x,frame_length=1024,hop_length=441)[0]
    return 20*np.log10(e+1e-9)
print("title-card SFX envelopes (side ch, dB every 50ms from -0.3s to +1.2s):")
for t,sgm in zip(times,segs):
    e=feat(sgm); print(f"{int(t//60)}:{t%60:05.2f}", ' '.join(f"{v:4.0f}" for v in e[::5]))
# pairwise max normalized cross-correlation of waveforms (are they the same sample?)
from scipy.signal import correlate
def ncc(a,b):
    a=(a-a.mean())/(a.std()+1e-9); b=(b-b.mean())/(b.std()+1e-9)
    c=correlate(a,b,mode='full')/len(a); return c.max()
M=np.zeros((len(segs),len(segs)))
for i in range(len(segs)):
    for j in range(len(segs)): M[i,j]=ncc(segs[i],segs[j])
print("pairwise NCC (1=identical sample):"); print(np.round(M,2))
# spectral centroid of the loudest 150 ms after cut
for t,sgm in zip(times,segs):
    k=int(0.3*sr); w=sgm[k:k+int(0.4*sr)]
    cent=librosa.feature.spectral_centroid(y=w,sr=sr).mean(); flat=librosa.feature.spectral_flatness(y=w).mean()
    print(f"{int(t//60)}:{t%60:05.2f} centroid {cent:6.0f} Hz flatness {flat:.3f}")
