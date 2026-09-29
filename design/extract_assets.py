"""AI로 만든 디자인 시트(design/generated/sheet_0N.webp)에서 게임용 에셋을 잘라 assets/ 에 저장합니다.
실행: pip install pillow numpy && python3 design/extract_assets.py
좌표는 1672x941 시트 기준입니다. 시트를 새로 만들면 좌표를 다시 맞춰야 합니다.
"""
import os, math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np
D=os.path.join(ROOT,'design','generated')+'/'
OUT=os.path.join(ROOT,'assets')+'/'
# 키 = 사용자에게 받은 순서 (1=시트05, 2=시트04, 3=시트03, 4=시트02, 5=시트01)
S={i:Image.open(D+f'sheet_0{6-i}.webp').convert('RGB') for i in range(1,6)}

def cutout(img, thresh=38, feather=1.2):
    w,h=img.size
    work=img.copy()
    SENT=(255,0,255)
    step=6
    seeds=[(x,0) for x in range(0,w,step)]+[(x,h-1) for x in range(0,w,step)]+[(0,y) for y in range(0,h,step)]+[(w-1,y) for y in range(0,h,step)]
    for s in seeds:
        if work.getpixel(s)!=SENT:
            ImageDraw.floodfill(work,s,SENT,thresh=thresh)
    a=np.array(work); m=((a[...,0]==255)&(a[...,1]==0)&(a[...,2]==255))
    bg=Image.fromarray((m*255).astype('uint8'))
    bg=bg.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(feather))
    alpha=ImageChops.invert(bg)
    out=img.convert('RGBA'); out.putalpha(alpha)
    return out.crop(out.getbbox())

def save(im, name, maxw=None):
    if maxw and im.width>maxw:
        im=im.resize((maxw, round(im.height*maxw/im.width)), Image.LANCZOS)
    im.save(OUT+name, optimize=True)
    print(name, im.size)

save(cutout(S[5].crop((70,190,1070,760))), 'logo_title.png', 900)
save(cutout(S[5].crop((1178,300,1545,668)),thresh=30), 'app_icon.png')
save(cutout(S[4].crop((1230,215,1420,400))), 'roulette_pointer.png')
save(cutout(S[4].crop((1072,562,1328,762))), 'badge_bok.png', 400)
save(cutout(S[4].crop((1330,562,1588,762))), 'badge_bul.png', 400)
for n,b in (('box_bok',(70,215,555,725)),('box_bul',(598,215,1080,725)),('box_person',(1125,215,1605,725))):
    save(cutout(S[3].crop(b)), n+'.png', 480)
for n,b in (('card_coffee',(72,185,556,778)),('card_charger',(598,185,1082,778)),('card_battery',(1122,185,1606,778))):
    save(cutout(S[2].crop(b)), n+'.png', 480)
for n,b in (('card_toast',(72,180,556,778)),('card_poem',(598,180,1082,778))):
    save(cutout(S[1].crop(b)), n+'.png', 480)
bg=S[1].crop((1240,226,1488,742)).resize((540,1124),Image.LANCZOS).filter(ImageFilter.GaussianBlur(2))
bg.save(OUT+'bg_mobile.jpg',quality=85); print('bg', bg.size)

# ---------- 룰렛 프레임 / 허브 / 앱 아이콘 ----------
src=S[4]
cx,cy=549,479.5; hx=320; hy=320/1.045
crop=src.crop((round(cx-hx),round(cy-hy),round(cx+hx),round(cy+hy))).resize((640,640),Image.LANCZOS)
a=np.array(crop).astype(int)
# hub radius: walk outwards from center along several angles until saturated color
rs=[]
for ang in range(0,360,15):
    t=math.radians(ang)
    for r in range(30,160):
        x=int(320+r*math.sin(t)); y=int(320-r*math.cos(t))
        R,G,B=a[y,x]
        if B<110 and R>150: rs.append(r); break
print('hub edge', sorted(rs))
outer=[]
for ang in range(0,360,15):
    t=math.radians(ang); run=0
    for r in range(298,150,-1):
        x=int(320+r*math.sin(t)); y=int(320-r*math.cos(t))
        R,G,B=a[y,x]
        if R>190 and B<80:
            run+=1
            if run>=6: outer.append(r+5); break
        else: run=0
print('seg outer', sorted(outer))
fr=cutout(crop.copy())  # note: cutout crops to bbox — redo without bbox
def cut_nobbox(img,thresh=38):
    w,h=img.size; work=img.copy(); SENT=(255,0,255)
    for s in [(x,0) for x in range(0,w,6)]+[(x,h-1) for x in range(0,w,6)]+[(0,y) for y in range(0,h,6)]+[(w-1,y) for y in range(0,h,6)]:
        if work.getpixel(s)!=SENT: ImageDraw.floodfill(work,s,SENT,thresh=thresh)
    m=np.array(work); m=((m[...,0]==255)&(m[...,1]==0)&(m[...,2]==255))
    bg=Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    return np.array(ImageChops.invert(bg)).astype(float)/255
al=cut_nobbox(crop)
yy,xx=np.mgrid[0:640,0:640]; r=np.hypot(xx-319.5,yy-319.5)
hole=np.clip((r-70)/2,0,1)*np.clip((257-r)/2,0,1)   # 1 inside annulus
al=al*(1-hole)
# 바깥쪽 원 밖은 제거 (색종이 조각 정리)
al=al*np.clip((310-r)/3,0,1)
out=crop.convert('RGBA'); out.putalpha(Image.fromarray((al*255).astype('uint8')))
out.save(OUT+'roulette_frame.png',optimize=True)
# 앱 아이콘: 룰렛 부분만 잘라 보라 그라데이션 정사각형에 배치
wheel=S[5].crop((1226,350,1494,618)).resize((380,380),Image.LANCZOS)
m=Image.new('L',(380,380),0); ImageDraw.Draw(m).ellipse((2,2,377,377),fill=255); m=m.filter(ImageFilter.GaussianBlur(1))
icon=Image.new('RGB',(512,512))
g=np.zeros((512,512,3)); t=(np.mgrid[0:512,0:512].sum(0)/1022.0)[...,None]
g=(np.array([167,139,250])*(1-t)+np.array([91,33,182])*t).astype('uint8')
icon=Image.fromarray(g); icon.paste(wheel,(66,66),m); icon.save(OUT+'app_icon.png',optimize=True)
# 허브(GO)를 분리: 회전하지 않도록 별도 이미지
hub_al=np.clip((75-r)/2,0,1)
hub=crop.convert('RGBA'); hub.putalpha(Image.fromarray((hub_al*255).astype('uint8')))
hub=hub.crop((320-80,320-80,320+80,320+80)); hub.save(OUT+'roulette_hub.png',optimize=True)
al2=al*np.clip((r-70)/2,0,1)  # 프레임에서 허브 영역 제거
fr2=crop.convert('RGBA'); fr2.putalpha(Image.fromarray((al2*255).astype('uint8')))
fr2.save(OUT+'roulette_frame.png',optimize=True)

# 최종: PNG → WebP 변환 (app_icon.png 제외)
import glob
for f in glob.glob(OUT+'*.png'):
    if f.endswith('app_icon.png'): continue
    Image.open(f).save(f[:-4]+'.webp', quality=88, method=6); os.remove(f)
Image.open(OUT+'bg_mobile.jpg').save(OUT+'bg_mobile.webp', quality=80, method=6); os.remove(OUT+'bg_mobile.jpg')
