import cv2, numpy as np, json
S=json.load(open('states_words.json'))
res=[]
for st in S:
    im=cv2.imread(f"states_full/s{st['id']:04d}.jpg"); H,W=im.shape[:2]
    b,g,r=[im[:,:,k].astype(int) for k in range(3)]
    white=((r>225)&(g>225)&(b>225)).astype(np.uint8)
    red=((r>190)&(g<110)&(b<110)&(r-g>110)).astype(np.uint8)
    n,lab,stats,cent=cv2.connectedComponentsWithStats(white,8)
    best=None
    for k in range(1,n):
        x,y,w,h,a=stats[k]
        if a<300 or w<20: continue
        circ=a/(np.pi*(max(w,h)/2)**2)
        ar=w/h
        if circ>0.72 and 0.85<ar<1.18:
            if best is None or a>best[4]: best=(x,y,w,h,a,circ)
    lum=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    dark=(lum<40).mean()
    rec=dict(id=st['id'],t0=st['t0'],dur=round(st['dur_f']/30,2),dark=round(float(dark),3),red=round(float(red.mean()),4))
    if best:
        x,y,w,h,a,c=best; cx=x+w/2; cy=y+h/2; R=(w+h)/4
        # red shirt below head
        sub=red[int(cy+R*0.8):min(H,int(cy+R*3.5)), max(0,int(cx-R)):min(W,int(cx+R))]
        shirt=sub.mean() if sub.size else 0
        rec.update(head_cx=round(cx,1),head_cy=round(cy,1),head_r=round(R,1),circ=round(c,2),shirt=round(float(shirt),3))
    res.append(rec)
json.dump(res,open('host_geom.json','w'))
hosts=[r for r in res if r.get('head_r') and r.get('shirt',0)>0.25]
print("states with host-like head+red shirt:",len(hosts),"of",len(res))
rs=np.array([h['head_r'] for h in hosts]); cx=np.array([h['head_cx'] for h in hosts]); cy=np.array([h['head_cy'] for h in hosts])
hist,edges=np.histogram(rs,bins=np.arange(5,130,5))
for hh,e in zip(hist,edges): print(f"r {e:5.0f}-{e+5:<4.0f} {'#'*hh}")
