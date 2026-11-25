import json, os
from PIL import Image, ImageDraw, ImageFont
st=json.load(open('states.json')); os.makedirs('sheets',exist_ok=True)
W,H=270,152; C,R=6,6; LAB=18
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
except: font=ImageFont.load_default()
def tc(t): m=int(t//60); s=t-60*m; return f"{m}:{s:05.2f}"
for k in range(0,len(st),C*R):
    grp=st[k:k+C*R]; sheet=Image.new('RGB',(C*(W+4),R*(H+LAB+4)),'white'); d=ImageDraw.Draw(sheet)
    for j,s in enumerate(grp):
        im=Image.open(f"states_full/s{s['id']:04d}.jpg").resize((W,H)); x=(j%C)*(W+4); y=(j//C)*(H+LAB+4)
        sheet.paste(im,(x,y+LAB))
        col=(200,0,0) if s['kind']=='motion' else (0,0,0)
        d.text((x+2,y+2),f"#{s['id']} {tc(s['t0'])} {s['dur_f']/30:.1f}s {'MOTION' if s['kind']=='motion' else ''}",fill=col,font=font)
    sheet.save(f"sheets/sheet_{k//(C*R):02d}.jpg",quality=88)
print(sorted(os.listdir('sheets')))
