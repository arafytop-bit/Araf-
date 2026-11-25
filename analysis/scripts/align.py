import json, re, os, sys, wave, numpy as np
from multiprocessing import Pool
from num2words import num2words
import pocketsphinx
from pocketsphinx import Decoder
MP=pocketsphinx.get_model_path()
DICT=os.path.join(MP,'en-us','cmudict-en-us.dict')
cmu={}
for line in open(DICT):
    p=line.split(); w=p[0].split('(')[0]
    cmu.setdefault(w,' '.join(p[1:]))
# crude grapheme->phone for OOV names
G2P=[('tch','CH'),('sch','SH'),('ch','CH'),('sh','SH'),('th','TH'),('ph','F'),('ck','K'),('ng','NG'),('qu','K W'),
     ('ee','IY'),('oo','UW'),('ou','AW'),('ai','EY'),('ay','EY'),('ea','IY'),('oa','OW'),('ie','IY'),('ei','EY'),
     ('a','AA'),('b','B'),('c','K'),('d','D'),('e','EH'),('f','F'),('g','G'),('h','HH'),('i','IY'),('j','JH'),('k','K'),
     ('l','L'),('m','M'),('n','N'),('o','OW'),('p','P'),('q','K'),('r','R'),('s','S'),('t','T'),('u','UW'),('v','V'),
     ('w','W'),('x','K S'),('y','Y'),('z','Z')]
def g2p(w):
    w=re.sub(r"[^a-z]","",w.lower()); out=[]; i=0
    while i<len(w):
        for g,p in G2P:
            if w.startswith(g,i): out.append(p); i+=len(g); break
        else: i+=1
    # collapse doubled consonants
    res=[]
    for p in out:
        if res and res[-1]==p: continue
        res.append(p)
    return ' '.join(res) if res else 'AH'
def norm_tokens(text):
    toks=[]
    for raw in text.split():
        w=raw.lower().strip(".,!?\"")
        w=w.replace("’","'")
        if not w: continue
        m=re.fullmatch(r"\$(\d+)",w)
        if m: toks+= (num2words(int(m.group(1)))+" dollars").replace('-',' ').replace(',','').split(); continue
        m=re.fullmatch(r"(\d+)'(\d+)",w)
        if m: toks+= (num2words(int(m.group(1)))+" "+num2words(int(m.group(2)))).replace('-',' ').split(); continue
        m=re.fullmatch(r"(\d+)(st|nd|rd|th)",w)
        if m: toks+= num2words(int(m.group(1)),to='ordinal').replace('-',' ').replace(',','').split(); continue
        if re.fullmatch(r"(19|20)\d\d",w):
            toks+= num2words(int(w),to='year').replace('-',' ').replace(',','').split(); continue
        parts=[p for p in re.split(r"-",w) if p]
        for p in parts:
            if re.fullmatch(r"\d+",p): toks+= num2words(int(p)).replace('-',' ').replace(',','').split()
            else:
                p2=re.sub(r"[^a-z0-9']","",p)
                if p2: toks.append(p2)
    return toks
def align_chunk(args):
    idx,t0,t1,text,wavpath=args
    with wave.open(wavpath) as wf:
        sr=wf.getframerate(); wf.setpos(int(t0*sr)); raw=wf.readframes(int((t1-t0)*sr))
    toks=norm_tokens(text)
    dec=Decoder(samprate=16000,bestpath=False,loglevel='FATAL')
    clean=[]
    for t in toks:
        if t not in cmu:
            try: dec.add_word(t,g2p(t),True)
            except Exception: continue
        clean.append(t)
    try:
        dec.set_align_text(' '.join(clean))
        dec.start_utt(); dec.process_raw(raw,full_utt=True); dec.end_utt()
        dec.set_alignment()
        dec.start_utt(); dec.process_raw(raw,full_utt=True); dec.end_utt()
        out=[]
        for w in dec.get_alignment():
            out.append(dict(w=w.name,s=round(t0+w.start/100,3),e=round(t0+(w.start+w.duration)/100,3)))
        return idx,out,None
    except Exception as ex:
        return idx,[],repr(ex)
if __name__=='__main__':
    tr=json.load(open(sys.argv[1]))['data']['transcript']
    segs=[(int(float(s['start_ms'])),s['text']) for s in tr if s['text'].strip() and s['text'].strip()!='n']
    segs.sort()
    total=float(sys.argv[3]); CH=4; jobs=[]
    for k in range(0,len(segs),CH):
        grp=segs[k:k+CH]
        t0=max(0,grp[0][0]/1000-0.35)
        t1=(segs[k+CH][0]/1000+0.12) if k+CH<len(segs) else total
        jobs.append((k//CH,t0,t1,' '.join(g[1] for g in grp),sys.argv[2]))
    with Pool(3) as p: res=p.map(align_chunk,jobs)
    res.sort(); words=[]; errs=[]
    for idx,out,err in res:
        if err: errs.append((idx,err))
        words+=out
    json.dump(dict(words=words,errors=errs),open(sys.argv[4],'w'))
    print("chunks",len(jobs),"errors",len(errs),"tokens",len(words)); print(errs[:5])
