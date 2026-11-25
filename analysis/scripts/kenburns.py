import cv2, numpy as np, json
S=json.load(open('states_words.json')); geo={g['id']:g for g in json.load(open('host_geom.json'))}
targets=[s for s in S if s['kind']=='still' and s['dur_f']>=30]
need={}
for s in targets: need.setdefault(s['s']+2,[]).append(('a',s['id'])); need.setdefault(s['e'],[]).append(('b',s['id']))
cap=cv2.VideoCapture('src.mp4'); i=0; fr_store={}; mx=max(need)
while i<=mx:
    ok,fr=cap.read()
    if not ok: break
    if i in need:
        for tag,sid in need[i]: fr_store[(tag,sid)]=cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY)
    i+=1
orb=cv2.ORB_create(2000); out=[]
for s in targets:
    A=fr_store.get(('a',s['id'])); B=fr_store.get(('b',s['id']))
    if A is None or B is None: continue
    ka,da=orb.detectAndCompute(A,None); kb,db=orb.detectAndCompute(B,None)
    if da is None or db is None or len(ka)<20 or len(kb)<20: continue
    mt=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True).match(da,db)
    if len(mt)<15: continue
    pa=np.float32([ka[m.queryIdx].pt for m in mt]); pb=np.float32([kb[m.trainIdx].pt for m in mt])
    M,inl=cv2.estimateAffinePartial2D(pa,pb,ransacReprojThreshold=2.0)
    if M is None or inl.sum()<12: continue
    sc=np.sqrt(M[0,0]**2+M[1,0]**2); dur=(s['e']-s['s']-2)/30
    g=geo[s['id']]; host=bool(g.get('head_r') and g.get('shirt',0)>0.04)
    out.append(dict(id=s['id'],t0=s['t0'],dur=round(dur,2),scale=round(float(sc),4),scale_per_s=round(float(sc**(1/dur)),4),tx=round(float(M[0,2]),1),ty=round(float(M[1,2]),1),inliers=int(inl.sum()),host=host))
json.dump(out,open('kenburns.json','w'))
nh=[o for o in out if not o['host']]; hh=[o for o in out if o['host']]
def summ(L,name):
    sp=np.array([o['scale_per_s'] for o in L]); 
    moving=(np.abs(sp-1)>0.004)
    print(f"{name}: n={len(L)} moving(>0.4%/s)={moving.sum()} ; scale/s of moving: median {np.median(sp[moving]) if moving.any() else 0:.4f}  p10 {np.percentile(sp[moving],10) if moving.any() else 0:.4f} p90 {np.percentile(sp[moving],90) if moving.any() else 0:.4f}")
summ(nh,"non-host holds"); summ(hh,"host holds")
for o in sorted(nh,key=lambda o:-abs(o['scale_per_s']-1))[:12]: print(o)
