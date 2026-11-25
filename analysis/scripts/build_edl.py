import json, csv, sys, numpy as np
sys.path.insert(0,'../scripts'); from annotations import A
S=json.load(open('states_words.json')); geo={g['id']:g for g in json.load(open('host_geom.json'))}
KB={k['id']:k for k in json.load(open('kenburns.json'))}; OCR={o['id']:o['ocr'] for o in json.load(open('ocr_states.json'))}
W=json.load(open('words_aligned.json'))
def tc(t): m=int(t//60); s=t-60*m; return f"{m:02d}:{s:06.3f}"
ann={}
for gi,(a,b,c,d) in enumerate(A):
    for i in range(a,b+1): ann[i]=(gi,c,d)
rows=[]
for s in S:
    g=geo[s['id']]; gi,cat,desc=ann[s['id']]
    hs=None
    if g.get('head_r') and g.get('shirt',0)>0.04:
        r=g['head_r']; hs='normal(r81)' if 60<r<100 else ('zoom(r123)' if r>=100 else 'small(r38)')
    k=KB.get(s['id'])
    rows.append(dict(state=s['id'],group=gi,start_frame=s['s'],end_frame=s['e'],start_tc=tc(s['s']/30),end_tc=tc((s['e']+1)/30),dur_s=round(s['dur_f']/30,3),
        dur_frames=s['dur_f'],kind=s['kind'],category=cat,description=desc,host_scale=hs,
        push_rate_pct_per_s=(round((k['scale_per_s']-1)*100,2) if k else None),words=s['words'],ocr=OCR.get(s['id'],'')))
json.dump(rows,open('edl.json','w'),indent=1)
with open('edl.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# groups (editorial shots)
G=[]
for gi,(a,b,c,d) in enumerate(A):
    st=[r for r in rows if r['group']==gi]
    t0=st[0]['start_frame']/30; t1=(st[-1]['end_frame']+1)/30
    G.append(dict(group=gi,states=f"{a}-{b}",start_tc=tc(t0),end_tc=tc(t1),dur_s=round(t1-t0,2),category=c,description=d,words=' '.join(r['words'] for r in st)))
json.dump(G,open('edl_groups.json','w'),indent=1)
# category stats
tot=903.9; cs={}
for r in rows:
    c=r['category']; cs.setdefault(c,[0,0]); cs[c][0]+=r['dur_s']; 
for g in G: cs[g['category']][1]+=1
print(f"{'CATEGORY':14s} {'groups':>6s} {'time_s':>7s} {'share':>6s} {'avg_group_s':>11s}")
for c,(t,n) in sorted(cs.items(),key=lambda x:-x[1][0]): print(f"{c:14s} {n:6d} {t:7.1f} {100*t/tot:5.1f}% {t/n:11.2f}")
print("editorial groups:",len(G),"states:",len(rows))
