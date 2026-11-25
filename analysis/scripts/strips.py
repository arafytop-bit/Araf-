import cv2, json, sys, os
from PIL import Image, ImageDraw, ImageFont
# ranges: name -> (start_frame, end_frame, step)
R=json.loads(sys.argv[1]); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
need=set()
for k,(a,b,st) in R.items(): need.update(range(a,b+1,st))
cap=cv2.VideoCapture('src.mp4'); frames={}; i=0; mx=max(need)
while i<=mx:
    ok,fr=cap.read()
    if not ok: break
    if i in need: frames[i]=Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB))
    i+=1
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
TW,TH=240,135; C=7
for k,(a,b,st) in R.items():
    idx=list(range(a,b+1,st)); rows=(len(idx)+C-1)//C
    sh=Image.new('RGB',(C*(TW+3),rows*(TH+20)),'white'); d=ImageDraw.Draw(sh)
    for j,f in enumerate(idx):
        if f not in frames: continue
        x=(j%C)*(TW+3); y=(j//C)*(TH+20)
        sh.paste(frames[f].resize((TW,TH)),(x,y+18)); d.text((x+2,y+2),f"f{f} {f/30:.2f}s",fill=(0,0,0),font=font)
    sh.save(f"{out}/{k}.jpg",quality=88)
print(sorted(os.listdir(out)))
