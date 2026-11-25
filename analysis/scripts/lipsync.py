import cv2, numpy as np, json, wave
S={s['id']:s for s in json.load(open('states_words.json'))}
geo={g['id']:g for g in json.load(open('host_geom.json'))}
# audio envelope (16k mono)
with wave.open('audio16k.wav') as wf: a=np.frombuffer(wf.readframes(wf.getnframes()),dtype=np.int16).astype(float)
hop=16000//30; env=np.array([np.sqrt(np.mean(a[i*hop:(i+1)*hop]**2)) for i in range(len(a)//hop)])
results={}
for sid in [397,438,10,93]:
    s=S[sid]; g=geo[sid]; cx,cy,R=g['head_cx'],g['head_cy'],g['head_r']
    x0,x1=int(cx-0.45*R),int(cx+0.45*R); y0,y1=int(cy+0.0*R),int(cy+0.6*R)
    cap=cv2.VideoCapture('src.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES,s['s'])
    openness=[]; changes=[]; prev=None
    for f in range(s['s'],s['e']+1):
        ok,fr=cap.read()
        if not ok: break
        m=cv2.cvtColor(fr[y0:y1,x0:x1],cv2.COLOR_BGR2GRAY)
        openness.append(float((m<80).mean()))
        if prev is not None: changes.append(float((cv2.absdiff(m,prev)>40).mean()))
        prev=m
    op=np.array(openness); ch=np.array(changes)
    ev=np.where(ch>0.01)[0]  # mouth shape change frames
    intervals=np.diff(ev)
    e=env[s['s']:s['e']+1]
    n=min(len(op),len(e))
    corr=np.corrcoef(op[:n],e[:n])[0,1]
    # lagged correlation
    lags={L:np.corrcoef(op[max(0,L):n+min(0,L)],e[max(0,-L):n-max(0,L)])[0,1] for L in range(-4,5)}
    results[sid]=dict(frames=len(op),shape_changes=len(ev),changes_per_sec=len(ev)/(len(op)/30),median_interval_frames=float(np.median(intervals)) if len(intervals) else None,
        interval_hist=np.bincount(np.minimum(intervals,12)).tolist() if len(intervals) else [],distinct_openness_levels=sorted(set(np.round(op,2)))[:12],corr_with_audio_env=round(float(corr),3),best_lag=max(lags,key=lags.get),lag_corr={k:round(float(v),3) for k,v in lags.items()})
    print(sid, json.dumps(results[sid]))
