import cv2, numpy as np, json, pytesseract
S=json.load(open('states_words.json')); out=[]
for s in S:
    im=cv2.imread(f"states_full/s{s['id']:04d}.jpg"); b,g,r=[im[:,:,k].astype(int) for k in range(3)]
    texts=[]
    for name,mask in [('white',(r>200)&(g>200)&(b>200)),('red',(r>140)&(r-g>80)&(r-b>80))]:
        m=(mask*255).astype(np.uint8)
        m=cv2.resize(m,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
        inv=255-m
        t=pytesseract.image_to_string(inv,config='--psm 11').strip()
        t=' '.join(w for w in t.split() if len(w)>1 and sum(c.isalnum() for c in w)>=2)
        if t: texts.append(f"[{name}] {t}")
    out.append(dict(id=s['id'],t0=s['t0'],ocr=' | '.join(texts)))
json.dump(out,open('ocr_states.json','w'),indent=0); print("done",len(out))
