"""상점 배경의 '404' 네온 간판을 도트풍 나무 간판(초승달·별 문양)으로 교체. 1회성.
원본은 assets/shop_bg_orig.jpg 로 백업하고, 항상 원본에서 다시 그린다."""
import os,shutil
import numpy as np
from PIL import Image
D=os.path.join(os.path.dirname(__file__),'..','assets')+'/'
if not os.path.exists(D+'shop_bg_orig.jpg'): shutil.copy(D+'shop_bg.jpg',D+'shop_bg_orig.jpg')
im=np.array(Image.open(D+'shop_bg_orig.jpg').convert('RGB')).astype(float)

# 1) 옛 간판 자리를 벽 색으로 메움 (각 줄마다 간판 양옆 벽 색을 섞음)
x0,x1,y0,y1=816,1034,474,642
rng=np.random.default_rng(7)
for y in range(y0,y1):
    L=np.median(im[y,800:814],axis=0); R=np.median(im[y,1033:1040],axis=0)
    for x in range(x0,x1):
        t=(x-x0)/(x1-x0); im[y,x]=L*(1-t)+R*t
# 벽 질감: 5px 칸마다 아주 약한 얼룩
for cy in range(y0,y1,5):
    for cx in range(x0,x1,5):
        im[cy:cy+5,cx:cx+5]*=1+rng.normal(0,0.012)

# 2) 저해상도(1칸=5px) 간판 그리기
C=5; GX,GY=812,476; W,H=46,34
O=(42,24,14); WD=(128,80,44); WL=(160,106,58); WH=(190,134,76); WS=(92,56,30); SEAM=(66,38,20)
FR=(104,64,34); FRL=(176,120,66); IRON=(52,48,56); IRONL=(110,104,116)
GOLD=(240,196,80); GOLDL=(255,238,160); GOLDS=(176,128,40); GEM=(150,90,200); GEML=(214,170,255); GEMS=(90,48,130); NAIL=(206,186,140)
g=[[None]*W for _ in range(H)]
def px(x,y,c):
    if 0<=x<W and 0<=y<H: g[y][x]=c
# 걸이(쇠막대 + 고리)
for hx in (9,36):
    for y in range(0,5): px(hx,y,IRON)
    px(hx-1,4,IRON);px(hx+1,4,IRON);px(hx,1,IRONL)
# 판자 외곽 (모서리 깎기) 3..42 x 5..30
bx0,bx1,by0,by1=3,42,5,30
for y in range(by0,by1+1):
    for x in range(bx0,bx1+1):
        corner=(x in(bx0,bx1))and(y in(by0,by1))
        if corner: continue
        edge=x in(bx0,bx1) or y in(by0,by1) or ((x in(bx0+1,bx1-1))and(y in(by0,by1)))
        px(x,y,O if edge else WD)
# 가운데 위 장식 (아치)
for x in range(18,28): px(x,by0-1,O)
for x in range(20,26): px(x,by0-2,O)
for x in range(19,27): px(x,by0,WD)
for x in range(21,25): px(x,by0-1,WD)
# 판자 3장: 결·이음매·밝은 윗줄
planks=[(6,13),(14,21),(22,29)]
for a,b in planks:
    for x in range(bx0+1,bx1):
        px(x,a,WL)
        for y in range(a+1,b+1): px(x,y,WD)
        px(x,b,WS)
    if b<29:
        for x in range(bx0+1,bx1): px(x,b+1 if b+1<=29 else b,SEAM) if False else None
for x in range(bx0+1,bx1):
    px(x,13,SEAM);px(x,21,SEAM)
# 나뭇결
rs=np.random.default_rng(3)
for y in range(7,29):
    if y in(13,14,21,22):continue
    x=bx0+2+int(rs.integers(0,4))
    while x<bx1-2:
        ln=int(rs.integers(4,9))
        if rs.random()<.45:
            for k in range(ln):
                if x+k<bx1-1 and g[y][x+k]==WD: px(x+k,y,WS)
        x+=ln+int(rs.integers(6,14))
# 안쪽 테두리
for x in range(bx0+2,bx1-1): px(x,by0+2,FRL); px(x,by1-2,FR)
for y in range(by0+2,by1-1): px(bx0+2,y,FRL); px(bx1-2,y,FR)
# 못
for (x,y) in ((bx0+1,by0+1),(bx1-1,by0+1),(bx0+1,by1-1),(bx1-1,by1-1)): px(x,y,NAIL)
for (x,y) in ((9,by0+1),(36,by0+1)): px(x,y,NAIL)
# 문양: 초승달 (가운데 왼쪽)
cx,cy,r=16,17.5,6.6
for y in range(H):
    for x in range(W):
        d1=((x-cx)**2+(y-cy)**2)**.5; d2=((x-(cx+3.6))**2+(y-(cy-1.8))**2)**.5
        if d1<=r and d2>r-1.4:
            c=GOLD
            if d1>r-1.0 or d2<r-0.4: c=O
            elif x<cx-2 and y<cy: c=GOLDL
            elif y>cy+2.5: c=GOLDS
            px(x,y,c)
# 큰 별 (오른쪽)
def star(sx,sy,big):
    pts=[(0,0),(0,-1),(0,1),(-1,0),(1,0)]
    if big: pts+= [(0,-2),(0,2),(-2,0),(2,0),(0,-3),(0,3),(-3,0),(3,0),(-1,-1),(1,-1),(-1,1),(1,1)]
    for dx,dy in pts:
        ring=[(sx+dx+a,sy+dy+b) for a,b in((1,0),(-1,0),(0,1),(0,-1))]
        for q in ring:
            if q not in [(sx+e,sy+f) for e,f in pts]: px(q[0],q[1],O)
    for dx,dy in pts: px(sx+dx,sy+dy,GOLD)
    px(sx,sy,GOLDL); px(sx-1 if big else sx,sy-1,GOLDL)
    if big: px(sx+1,sy+1,GOLDS);px(sx,sy+2,GOLDS);px(sx+2,sy,GOLDS)
star(29,16,True)
star(33,22,False); star(24,25,False); star(36,10,False)
# 보석 (아치 장식)
for (x,y,c) in ((22,3,GEM),(23,3,GEM),(22,4,GEMS),(23,4,GEM),(22,3,GEML)): px(x,y,c)

# 3) 그림자 → 간판 순서로 칠하기
sh=np.zeros((H,W),bool)
for y in range(H):
    for x in range(W):
        if g[y][x] is not None and x>=bx0-1 and y>=by0-2: sh[y,x]=True
for y in range(H):
    for x in range(W):
        if y-1>=0 and x-1>=0 and sh[y-1,x-1] and g[y][x] is None:
            Y,X=GY+y*C,GX+x*C; im[Y:Y+C,X:X+C]*=0.78
for y in range(H):
    for x in range(W):
        c=g[y][x]
        if c is None: continue
        Y,X=GY+y*C,GX+x*C
        # 왼쪽 등불 쪽이 살짝 더 따뜻하게
        warm=1+0.08*(1-x/W)
        im[Y:Y+C,X:X+C]=np.clip(np.array(c,float)*[warm,1,1/warm**.5],0,255)

# 4) 오른쪽 아래 구석에 작게 새긴 "404" (2px 점, 파인 느낌)
FONT={'4':['1.1','1.1','111','..1','..1'],'0':['111','1.1','1.1','1.1','111']}
ex,ey,dp=984,604,2
for i,ch in enumerate('404'):
    for r,row in enumerate(FONT[ch]):
        for c,v in enumerate(row):
            if v!='1':continue
            X,Y=ex+i*8+c*dp,ey+r*dp
            im[Y+1:Y+dp+1,X:X+dp]=np.array((200,146,88),float)
            im[Y:Y+dp,X:X+dp]=np.array((62,36,18),float)
Image.fromarray(np.clip(im,0,255).astype(np.uint8)).save(D+'shop_bg.jpg',quality=94)
print('ok')
