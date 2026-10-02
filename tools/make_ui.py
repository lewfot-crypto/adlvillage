"""UI 도트 틀 생성: assets/ui/*.png (1배 크기 도트. 화면에서는 CSS --px 배로 픽셀 그대로 키움)
- frame_parch / frame_dark : 대화창·설정창·알림용 나무 틀 (9조각, 조각 8칸)
- plate / plate_sel / plate_gold : 버튼·이름표용 작은 판 (9조각, 조각 4칸)
- tex_parch : 양피지 바탕 무늬 (32x32 반복)
사용: python3 tools/make_ui.py"""
from PIL import Image
import random,os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','assets','ui')
os.makedirs(OUT,exist_ok=True)
def c(h,a=255):h=h.lstrip('#');return (int(h[0:2],16),int(h[2:4],16),int(h[4:6],16),a)
O=c('1a0e07');WH=c('b07a46');W=c('7f4f2c');WD=c('5e3a21');WS=c('3e2414')
G=c('f2b24c');GH=c('ffe39a');GD=c('a8691f');DARK=c('2b1c14');DARK2=c('22160f')
P=c('ecd9ad');PD=c('dcc392');PE=c('c9a76f');T=(0,0,0,0)

def ring_frame(n,layers,center):
    """layers: 바깥→안쪽 순서 색 목록. 각 줄의 (위·왼, 아래·오른) 색."""
    im=Image.new('RGBA',(n,n),center)
    px=im.load()
    for i,(tl,br) in enumerate(layers):
        for k in range(i,n-i):
            px[k,i]=tl;px[i,k]=tl;px[k,n-1-i]=br;px[n-1-i,k]=br
        # 모서리 이음새: 오른쪽 위·왼쪽 아래는 바깥쪽 색 기준으로 대각선 정리
        px[n-1-i,i]=tl;px[i,n-1-i]=br
    return im

def round_corners(im,r=2):
    px=im.load();n=im.size[0]
    pts=[(0,0),(1,0),(0,1)] if r>=2 else [(0,0)]
    for x,y in pts:
        for X,Y in [(x,y),(n-1-x,y),(x,n-1-y),(n-1-x,n-1-y)]:px[X,Y]=T
    # 둥근 모서리 안쪽 테두리
    if r>=2:
        for X,Y in [(1,1),(n-2,1),(1,n-2),(n-2,n-2)]:px[X,Y]=O
    return im

def clasp(im):
    """큰 틀 네 모서리에 금색 꺾쇠 + 리벳"""
    px=im.load();n=im.size[0]
    shape=["GGGGG.",
           "GHHHG.",
           "GHDG..",
           "GHG...",
           "GG....",
           "......"]
    col={'G':G,'H':GH,'D':GD}
    for y,row in enumerate(shape):
        for x,ch in enumerate(row):
            if ch=='.':continue
            v=col[ch]
            for X,Y in [(x+1,y+1),(n-2-x,y+1),(x+1,n-2-y),(n-2-x,n-2-y)]:px[X,Y]=v
    # 꺾쇠 바깥 윤곽
    for X,Y in [(1,6),(6,1),(n-2,6),(n-7,1),(1,n-7),(6,n-2),(n-2,n-7),(n-7,n-2)]:px[X,Y]=O
    for X,Y in [(3,3),(n-4,3),(3,n-4),(n-4,n-4)]:px[X,Y]=c('fff6d0')
    return im

def big(center):
    lay=[(O,O),(WH,WS),(W,WD),(W,WD),(WD,WS),(WS,WS),(GH,GD),(O,O)]
    im=ring_frame(24,lay,center)
    return clasp(round_corners(im))

big(T).save(OUT+'/frame_parch.png')
big(DARK).save(OUT+'/frame_dark.png')

def plate(trim,center):
    lay=[(O,O)]+trim
    im=ring_frame(12,lay,center)
    return round_corners(im,1)
plate([(WH,WS),(W,WD),(W,W)],W).save(OUT+'/plate.png')
plate([(GH,GD),(WD,WS),(c('8f5c33'),c('8f5c33'))],c('8f5c33')).save(OUT+'/plate_sel.png')
plate([(GH,GD),(WS,WS),(DARK,DARK)],DARK).save(OUT+'/plate_gold.png')

def title_btn(center,inner):
    lay=[(O,O),(GH,GD),(G,GD),(O,O),(WS,WS)]
    im=ring_frame(16,lay,center);px=im.load()
    for k in range(5,11):px[k,5]=inner;px[k,10]=c('1e120b')
    round_corners(im,2)
    for X,Y in [(2,2),(13,2),(2,13),(13,13)]:px[X,Y]=c('fff6d0')
    return im
title_btn(c('3a2414'),c('5a3a24')).save(OUT+'/btn_title.png')
title_btn(c('5a3420'),c('7a4f2f')).save(OUT+'/btn_title_on.png')

random.seed(7)
tex=Image.new('RGBA',(32,32),P);px=tex.load()
for y in range(32):
    for x in range(32):
        r=random.random()
        if r<.06:px[x,y]=PD
        elif r<.075:px[x,y]=PE
        elif r<.09:px[x,y]=c('f4e4bf')
tex.save(OUT+'/tex_parch.png')
print('ui ->',os.path.abspath(OUT))
