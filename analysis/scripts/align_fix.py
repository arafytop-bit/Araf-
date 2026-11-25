import json, sys
sys.path.insert(0,'../scripts')
from align import align_chunk, norm_tokens
tr=json.load(open('yt_transcript.json'))['data']['transcript']
segs=sorted([(int(float(s['start_ms'])),s['text']) for s in tr if s['text'].strip() and s['text'].strip()!='n'])
A=json.load(open('align_words.json')); CH=4; total=903.95
failed=[e[0] for e in A['errors']]
fixed={}
for idx in failed:
    k=idx*CH; grp=segs[k:k+CH]
    base_t0=max(0,grp[0][0]/1000-0.35); base_t1=(segs[k+CH][0]/1000+0.12) if k+CH<len(segs) else total
    ok=None
    for dt0,dt1 in [(0,0.4),(-0.3,0.6),(0.1,0.25),(-0.5,1.0),(0.2,0.0)]:
        r=align_chunk((idx,max(0,base_t0+dt0),min(total,base_t1+dt1),' '.join(g[1] for g in grp),'audio16k.wav'))
        if not r[2]: ok=r[1]; print("chunk",idx,"fixed with",dt0,dt1,len(ok)); break
    if ok is None:
        # per-line fallback
        out=[]
        for j,(st,txt) in enumerate(grp):
            t0=max(0,st/1000-0.3); t1=(segs[k+j+1][0]/1000+0.15) if k+j+1<len(segs) else total
            r=align_chunk((idx,t0,t1,txt,'audio16k.wav'))
            if r[2]:
                r=align_chunk((idx,t0-0.2,t1+0.5,txt,'audio16k.wav'))
            if r[2]: print("  line fail",idx,j,txt); 
            else: out+=r[1]
        ok=out; print("chunk",idx,"per-line",len(ok))
    fixed[idx]=ok
# rebuild word list in time order: drop words falling in failed chunk windows, then add fixed
words=A['words']
allw=[w for w in words]
for idx,ws in fixed.items(): allw+=ws
allw=[w for w in allw if w['w'] not in ('<s>','</s>','<sil>','[NOISE]')]
allw.sort(key=lambda w:w['s'])
# remove overlaps/dupes created by window margins (keep first)
clean=[]
for w in allw:
    if clean and w['s']<clean[-1]['e']-0.02 and w['w'].split('(')[0]==clean[-1]['w'].split('(')[0]: continue
    clean.append(w)
for w in clean: w['w']=w['w'].split('(')[0]
json.dump(clean,open('words_aligned.json','w'))
print("final words",len(clean))
