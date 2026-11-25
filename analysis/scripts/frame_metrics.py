import cv2, numpy as np, sys, time
src=sys.argv[1]; out=sys.argv[2]
cap=cv2.VideoCapture(src)
N=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
print("N",N,"fps",fps,flush=True)
gray_small=[]; col_small=[]
m_diff=[]; m_chg=[]; m_chg_big=[]; m_hist=[]; m_lum=[]; m_std=[]; m_rgb=[]
prev=None; prevh=None; t0=time.time(); i=0
while True:
    ok,fr=cap.read()
    if not ok: break
    g=cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY)
    gs=cv2.resize(g,(160,90),interpolation=cv2.INTER_AREA)
    cs=cv2.resize(fr,(80,45),interpolation=cv2.INTER_AREA)
    gray_small.append(gs); col_small.append(cs)
    hsv=cv2.cvtColor(fr,cv2.COLOR_BGR2HSV)
    h=cv2.calcHist([hsv],[0,1,2],None,[16,8,8],[0,180,0,256,0,256]); cv2.normalize(h,h)
    if prev is not None:
        d=cv2.absdiff(g,prev)
        m_diff.append(float(d.mean())); m_chg.append(float((d>25).mean())); m_chg_big.append(float((d>60).mean()))
        m_hist.append(float(cv2.compareHist(prevh,h,cv2.HISTCMP_BHATTACHARYYA)))
    else:
        m_diff.append(0.0); m_chg.append(0.0); m_chg_big.append(0.0); m_hist.append(0.0)
    m_lum.append(float(g.mean())); m_std.append(float(g.std())); m_rgb.append(fr.reshape(-1,3).mean(0)[::-1].tolist())
    prev=g; prevh=h; i+=1
    if i%5000==0: print(i, round(time.time()-t0,1),"s",flush=True)
np.savez_compressed(out, diff=np.array(m_diff), chg=np.array(m_chg), chgbig=np.array(m_chg_big), hist=np.array(m_hist), lum=np.array(m_lum), std=np.array(m_std), rgb=np.array(m_rgb))
np.save(out.replace('.npz','_gray160.npy'), np.array(gray_small))
np.save(out.replace('.npz','_col80.npy'), np.array(col_small))
print("done",i,"frames",round(time.time()-t0,1),"s")
