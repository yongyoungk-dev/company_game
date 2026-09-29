"""커피카드 이미지에서 그림과 리본 글자를 지워 빈 복 카드 틀(card_bok_blank.png)을 만듭니다.
실행: python3 design/card_maker/make_blank.py  →  node design/card_maker/compose.js
"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, os
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
src=Image.open(os.path.join(ROOT,'assets','card_coffee.webp')).convert('RGBA')
a=np.array(src).astype(float)
H,W=a.shape[:2]
yy,xx=np.mgrid[0:H,0:W]
# 1) 리본 글자 지우기: 각 행마다 글자 왼쪽/오른쪽 리본 색을 선형 보간
x0,x1=128,352
for y in range(343,424):
    L=a[y,x0,:3]; R=a[y,x1,:3]
    t=((np.arange(x0,x1+1)-x0)/(x1-x0))[:,None]
    a[y,x0:x1+1,:3]=L*(1-t)+R*t
# 2) 윗부분(점선 테두리 안) 새로 칠하기: 크림색 + 금색 원형 글로우
cream=np.array([252,246,230.])
region=np.zeros((H,W)); 
m=Image.new('L',(W,H),0); ImageDraw.Draw(m).rounded_rectangle((50,50,W-50,338),radius=22,fill=255)
m=np.array(m.filter(ImageFilter.GaussianBlur(2)))/255.
cx,cy=238,205; r=np.hypot(xx-cx,yy-cy)
R0=146
disk=np.clip((R0-r)/6,0,1)
tt=np.clip(r/R0,0,1)[...,None]
c_in=np.array([255,247,210.]); c_mid=np.array([255,214,92.]); c_out=np.array([255,192,48.])
gold=np.where(tt<0.55, c_in*(1-tt/0.55)+c_mid*(tt/0.55), c_mid*(1-(tt-0.55)/0.45)+c_out*((tt-0.55)/0.45))
glow=np.clip(1-(r-R0)/40,0,1)[...,None]*0.35*(r>R0)[...,None]
top=cream*(1-glow)+np.array([255,205,80.])*glow
top=top*(1-disk[...,None])+gold*disk[...,None]
a[...,:3]=a[...,:3]*(1-m[...,None])+top*m[...,None]
out=Image.fromarray(a.clip(0,255).astype('uint8'),'RGBA')
out.save(os.path.join(HERE,'card_bok_blank.png'))
