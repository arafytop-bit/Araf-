import numpy as np, librosa, json, soundfile as sf
y,sr=sf.read('audio44k.wav'); L,R=y[:,0],y[:,1]; m=(L+R)/2; side=(L-R)/2
print("stereo: corr L/R %.4f ; side/mid RMS ratio %.4f (0=mono)"%(np.corrcoef(L[:sr*600],R[:sr*600])[0,1], np.sqrt(np.mean(side**2))/np.sqrt(np.mean(m**2))))
W=json.load(open('words_aligned.json'))
def db(x): return 20*np.log10(np.sqrt(np.mean(x**2))+1e-12)
# segments
print("level during speech 60-120s: %.1f dBFS RMS"%db(m[60*sr:120*sr]))
print("outro after last word (897.5-903.5s): %.1f dBFS RMS"%db(m[int(897.5*sr):int(903.5*sr)]))
print("very start 0-0.06s: %.1f dBFS"%db(m[:int(0.06*sr)]))
# gaps between words > 0.12s
ws=np.array([w['s'] for w in W]); we=np.array([w['e'] for w in W])
gl=[]
for i in range(len(W)-1):
    a,b=we[i]+0.03,ws[i+1]-0.03
    if b-a>0.1: gl.append(db(m[int(a*sr):int(b*sr)]))
gl=np.array(gl); print("RMS inside inter-word gaps (n=%d): median %.1f dBFS, p10 %.1f, p90 %.1f"%(len(gl),np.median(gl),np.percentile(gl,10),np.percentile(gl,90)))
# pitch of voice (sample 3 windows)
f0s=[]
for t0 in [30,200,400,600,800]:
    seg=m[t0*sr:(t0+20)*sr]; seg=librosa.resample(seg,orig_sr=sr,target_sr=16000)
    f0,vf,vp=librosa.pyin(seg,fmin=60,fmax=400,sr=16000,frame_length=1024)
    f0s+=list(f0[~np.isnan(f0)])
f0s=np.array(f0s); print("voice F0: median %.0f Hz, p10 %.0f, p90 %.0f"%(np.median(f0s),np.percentile(f0s,10),np.percentile(f0s,90)))
# spectral centroid / rolloff of speech
S=np.abs(librosa.stft(m[60*sr:120*sr],n_fft=4096,hop_length=1024))
freqs=librosa.fft_frequencies(sr=sr,n_fft=4096); spec=S.mean(1)
for lo,hi in [(20,80),(80,250),(250,1000),(1000,4000),(4000,8000),(8000,12000),(12000,16000),(16000,22050)]:
    band=(freqs>=lo)&(freqs<hi); print(f"band {lo}-{hi} Hz: {20*np.log10(spec[band].mean()+1e-12):.1f} dB")
