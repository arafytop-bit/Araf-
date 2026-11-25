import json, numpy as np, cv2, os
ev=json.load(open('events.json')); m=np.load('metrics.npz'); chg=m['chg']; N=len(chg)
BA=0.02
sig=[e for e in ev if e['ba_frac']>BA or e['len']>=10]
states=[]; cur=0
for e in sig:
    if e['len']>=10:  # continuous motion: own state
        if e['s']>cur: states.append(dict(s=cur,e=e['s']-1,kind='still'))
        states.append(dict(s=e['s'],e=e['e'],kind='motion')); cur=e['e']+1
    else:
        if e['s']>cur: states.append(dict(s=cur,e=e['s']-1,kind='still'))
        cur=e['s']  # transition frames belong to next state start
# finalize
states.append(dict(s=cur,e=N-1,kind='still'))
# merge zero-length / tiny
clean=[]
for st in states:
    if st['e']<st['s']: continue
    clean.append(st)
for i,st in enumerate(clean):
    st['id']=i; st['dur_f']=st['e']-st['s']+1; st['t0']=round(st['s']/30,3); st['t1']=round((st['e']+1)/30,3)
    st['rep']=int(min(st['e'], st['s']+ (st['e']-st['s'])*2//3))
json.dump(clean,open('states.json','w'),indent=0)
d=np.array([s['dur_f'] for s in clean])/30
print("states",len(clean),"motion",sum(s['kind']=='motion' for s in clean))
print("dur sec: mean %.2f median %.2f p10 %.2f p90 %.2f max %.2f"%(d.mean(),np.median(d),np.percentile(d,10),np.percentile(d,90),d.max()))
# grab representative frames sequentially
need={}
for st in clean: need.setdefault(st['rep'],[]).append(st['id'])
os.makedirs('states_full',exist_ok=True)
cap=cv2.VideoCapture('src.mp4'); i=0
while True:
    ok,fr=cap.read()
    if not ok: break
    if i in need:
        for sid in need[i]: cv2.imwrite(f'states_full/s{sid:04d}.jpg',fr,[cv2.IMWRITE_JPEG_QUALITY,92])
    i+=1
print("saved",len(os.listdir('states_full')))
