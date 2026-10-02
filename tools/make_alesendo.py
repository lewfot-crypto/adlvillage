"""사용자가 준 예전 게임 알레센도 도트(source_images/alesendo_oldgame.jpg, 초록 배경, 1칸≈21.7px)를
칸 단위로 다시 뽑아 assets/npc_alesendo.png(240x330) 로 만든다. 옷 색은 그대로. 이전 그림은 npc_alesendo_old.png."""
import os
import numpy as np
from PIL import Image
B=os.path.join(os.path.dirname(__file__),'..')+'/'
im=np.array(Image.open(B+'source_images/alesendo_oldgame.jpg').convert('RGB')).astype(float)
PX,OX,PY,OY=21.66,275.5,21.74,412.0
NX,NY=27,52
cells=np.zeros((NY,NX,4),np.uint8)
for j in range(NY):
    for i in range(NX):
        x0=OX+i*PX;y0=OY+j*PY
        a,b=int(x0+PX*.3),int(x0+PX*.7);c,d=int(y0+PY*.3),int(y0+PY*.7)
        blk=im[c:d,a:b].reshape(-1,3)
        if blk.size==0:continue
        m=np.median(blk,axis=0)
        green=m[1]>140 and m[1]-m[0]>55 and m[1]-m[2]>55
        if not green: cells[j,i,:3]=m.clip(0,255); cells[j,i,3]=255
# 거의 검정인 칸은 순수 외곽선 색으로 통일
blk=(cells[:,:,:3].astype(int).sum(2)<110)&(cells[:,:,3]>0)
cells[blk,:3]=(16,14,22)
# 색 정리: 비슷한 색끼리 묶어 JPEG 얼룩 제거
op=cells[:,:,3]>0
cols=cells[op][:,:3].astype(float)
pal=[]
for c in cols:
    if not any(np.abs(p-c).sum()<26 for p in pal): pal.append(c)
pal=np.array(pal)
for j,i in zip(*np.where(op)):
    c=cells[j,i,:3].astype(float); cells[j,i,:3]=pal[np.abs(pal-c).sum(1).argmin()]
ys,xs=np.where(op);cells=cells[ys.min():ys.max()+1,xs.min():xs.max()+1]
print('cells',cells.shape[1],'x',cells.shape[0],'palette',len(pal))
K=6
spr=Image.fromarray(cells,'RGBA').resize((cells.shape[1]*K,cells.shape[0]*K),Image.NEAREST)
out=Image.new('RGBA',(240,330),(0,0,0,0))
out.alpha_composite(spr,((240-spr.size[0])//2,330-spr.size[1]))
out.save(B+'assets/npc_alesendo.png')
print('sprite',spr.size)
