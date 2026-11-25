import numpy as np, soundfile as sf, json, scipy.signal as ss
y,sr=sf.read('audio44k.wav'); L,R=y[:,0],y[:,1]; side=(L-R)/2; mid=(L+R)/2
S=json.load(open('states_words.json')); ev=json.load(open('events.json'))
hop=int(sr/100)  # 10 ms
def env(x):
    n=len(x)//hop; return np.sqrt((x[:n*hop].reshape(n,hop)**2).mean(1))
b,a=ss.butter(4,[5000/(sr/2),15000/(sr/2)],btype='band'); hf=ss.filtfilt(b,a,mid)
E_hf=20*np.log10(env(hf)+1e-9); E_side=20*np.log10(env(side)+1e-9); E_mid=20*np.log10(env(mid)+1e-9)
def era(E,times,w=50):
    rows=[E[int(t*100)-w:int(t*100)+w] for t in times if int(t*100)-w>0 and int(t*100)+w<len(E)]
    return np.mean(rows,0)
# hard cuts: single-frame events with big before/after change
cuts=[e['s']/30 for e in ev if e['len']<=2 and e['ba_frac']>0.3]
rand=np.random.default_rng(0).uniform(5,895,len(cuts))
for name,E in [('HF 5-15k',E_hf),('side',E_side),('mid',E_mid)]:
    c=era(E,cuts); r=era(E,rand)
    print(f"{name}: around hard cuts (n={len(cuts)}) dB at offsets -300ms..+300ms (step 50ms):")
    print("   cuts:",[round(float(c[i]),1) for i in range(20,81,5)])
    print("   rand:",[round(float(r[i]),1) for i in range(20,81,5)])
# individual: count cuts with an HF jump > 6 dB relative to the 200ms before
cnt=0; idx=[]
for t in cuts:
    k=int(t*100)
    if k<30 or k+15>len(E_hf): continue
    pre=np.median(E_hf[k-30:k-5]); post=E_hf[k-3:k+12].max()
    if post-pre>9: cnt+=1; idx.append(t)
print("cuts with HF burst >9dB:",cnt,"of",len(cuts))
print("examples:",[f"{t//60:.0f}:{t%60:05.2f}" for t in idx[:25]])
