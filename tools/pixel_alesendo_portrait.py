"""알레센도 초상화를 다른 인물(오르가·브란)처럼 또렷한 도트 + 고른 굵은 외곽선으로 만든다.
입력: assets/portrait_alesendo_cut_soft_old.png (부드러운 그림, 190x246)
출력: assets/portrait_alesendo_cut.png (도트 158x205 를 2배로 키운 316x410. build.py 가 오르가처럼 190x246 으로 줄여 넣음)
사용: python3 tools/pixel_alesendo_portrait.py"""
from PIL import Image, ImageFilter
import numpy as np, os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','assets')+'/'
src=Image.open(D+'portrait_alesendo_cut_soft_old.png').convert('RGBA')
GW,GH=158,205                                   # 도트 칸 수 (오르가와 비슷한 밀도)
# 1) 모양(마스크): 칸 크기로 줄이고 반 이상 찬 칸만, 들쭉날쭉한 끝은 열고 닫아 매끈하게
m=src.split()[3].resize((GW,GH),Image.BOX).point(lambda v:255 if v>=128 else 0)
m=m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))   # 작은 구멍·홈 메우기
m=m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))   # 튀어나온 가시 없애기
# 2) 색: 바깥 테두리 찌꺼기(노랑·주황 번짐)를 빼려고 안쪽으로 한 칸 줄인 영역의 색만 평균
a=np.array(src).astype(float);al=a[...,3:4]/255.0
core=np.array(src.split()[3].filter(ImageFilter.MinFilter(5)))>0
rgb=a[...,:3]*core[...,None];w=core.astype(float)
H,W=core.shape;sy,sx=H/GH,W/GW
out=np.zeros((GH,GW,4),np.uint8)
mk=np.array(m)>0
for y in range(GH):
    for x in range(GW):
        y0,y1=int(y*sy),max(int(y*sy)+1,int((y+1)*sy));x0,x1=int(x*sx),max(int(x*sx)+1,int((x+1)*sx))
        ww=w[y0:y1,x0:x1].sum()
        if ww>0:c=rgb[y0:y1,x0:x1].reshape(-1,3).sum(0)/ww
        else:
            # 테두리 칸: 가장 가까운 안쪽 색
            c=None
            for r in range(1,6):
                Y0,Y1,X0,X1=max(0,y0-r),min(H,y1+r),max(0,x0-r),min(W,x1+r);ww=w[Y0:Y1,X0:X1].sum()
                if ww>0:c=rgb[Y0:Y1,X0:X1].reshape(-1,3).sum(0)/ww;break
            if c is None:c=np.array([40,38,52])
        out[y,x,:3]=c;out[y,x,3]=255 if mk[y,x] else 0
img=Image.fromarray(out,'RGBA')
# 3) 색 수 줄이기(또렷하게)
rgbimg=img.convert('RGB').quantize(colors=40,method=Image.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
q=np.array(rgbimg);o=np.dstack([q,out[...,3]])
# 4) 외곽선: 모양 바깥 둘레 한 칸을 짙은 색으로 (다른 초상화와 같은 톤)
tr=o[...,3]==0
adj=np.zeros(tr.shape,bool)
for d in ((1,0),(-1,0),(0,1),(0,-1)):
    sh=np.roll(tr,d,(0,1))
    if d==(1,0):sh[0,:]=True
    if d==(-1,0):sh[-1,:]=False
    if d==(0,1):sh[:,0]=True
    if d==(0,-1):sh[:,-1]=True
    adj|=sh
edge=(~tr)&adj
edge[-1,:]=False                                # 아래쪽(틀에 잘리는 쪽)은 외곽선 없음
o[edge,:3]=(26,16,14)
# 5) 외곽선 바로 안쪽(1~3칸)에 남은 배경 번짐 정리: 모자·로브 자리에서 붉은기·튀는 밝은 점·겹친 짙은 덩어리를 안쪽 옷 색으로
from collections import deque
op=o[...,3]>0;dist=np.full(op.shape,99);dq=deque()
for y,x in zip(*np.where(edge)):dist[y,x]=0;dq.append((y,x))
while dq:
    y,x=dq.popleft()
    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
        ny,nx=y+dy,x+dx
        if 0<=ny<GH and 0<=nx<GW and op[ny,nx] and dist[ny,nx]>dist[y,x]+1:dist[ny,nx]=dist[y,x]+1;dq.append((ny,nx))
yy,xx=np.mgrid[0:GH,0:GW]
cloth=(yy<52)|((yy>92)&((xx<48)|(xx>112))&(yy<175))     # 모자 + 양쪽 로브(얼굴·머리·손·책 제외)
r,g,b=o[...,0].astype(int),o[...,1].astype(int),o[...,2].astype(int);lum=(r*3+g*6+b)/10
band=(dist>=1)&(dist<=6)&cloth
bad=band&((r>=b+2)|((dist<=3)&(lum>105))|((dist<=2)&(lum<32)))
def inward(y,x):
    for rad in range(1,6):
        cs=[]
        for yy2 in range(y-rad,y+rad+1):
            for xx2 in range(x-rad,x+rad+1):
                if 0<=yy2<GH and 0<=xx2<GW and op[yy2,xx2] and dist[yy2,xx2]>2 and cloth[yy2,xx2] and not bad[yy2,xx2]:cs.append(o[yy2,xx2,:3])
        if cs:return np.median(np.array(cs),0)
    return None
fix=0
for y,x in zip(*np.where(bad)):
    c=inward(y,x)
    if c is not None:o[y,x,:3]=c;fix+=1
print('edge fix',fix)
res=Image.fromarray(o.astype(np.uint8),'RGBA').resize((GW*2,GH*2),Image.NEAREST)
res.save(D+'portrait_alesendo_cut.png');print('saved',res.size)
