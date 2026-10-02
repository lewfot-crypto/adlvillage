import numpy as np,os,shutil,json
from PIL import Image
from scipy import ndimage as ndi
D='/mnt/user-data/outputs/game_demo/assets/'
TARGET={'orga':87,'bran':106,'master':104,'alesendo':106,'wella':91}
dark=np.array([30,22,30])
res={}
for n,t in TARGET.items():
    f=D+f'npc_{n}.png';src=D+f'npc_{n}_src.png'
    if not os.path.exists(src):shutil.copy(f,src)
    im=Image.open(src).convert('RGBA');al=np.array(im)[...,3]>128
    ys,xs=np.where(al);bb=im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
    w,h=bb.size
    k=min(1.0,322/h,232/w)
    if k<1:bb=bb.resize((max(1,round(w*k)),max(1,round(h*k))),Image.LANCZOS);a=bb.getchannel('A').point(lambda v:255 if v>110 else 0);bb.putalpha(a)
    cv=Image.new('RGBA',(240,330),(0,0,0,0))
    ox=(240-bb.size[0])//2;oy=328-bb.size[1]
    cv.alpha_composite(bb,(ox,oy))
    a=np.array(cv).astype(float);al=a[...,3]>128
    band=al&~ndi.binary_erosion(al,iterations=2)
    for c in range(3):a[...,c][band]=a[...,c][band]*0.45+dark[c]*0.55
    out=ndi.binary_dilation(al,structure=np.ones((3,3)),iterations=2)&~al
    for c in range(3):a[...,c][out]=dark[c]
    a[...,3][out]=255
    r=Image.fromarray(a.astype('uint8'));r.save(f)
    ys,xs=np.where(a[...,3]>128);hc=ys.max()-ys.min()+1
    res[n]=round(t/100*329/hc,3)
print(res)
w=Image.new('RGBA',(240*6,330),(120,90,60,255))
for i,n in enumerate(['amelia2_down','npc_orga','npc_bran','npc_master','npc_alesendo','npc_wella']):
    im=Image.open(D+n+'.png').convert('RGBA')
    sc=res.get(n[4:],1.0)
    im=im.resize((round(240*sc),round(330*sc)),Image.LANCZOS)
    w.alpha_composite(im,(240*i+(240-im.size[0])//2,330-im.size[1]))
w.save('/tmp/all2.png')
