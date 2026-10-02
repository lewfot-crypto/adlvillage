import numpy as np, cv2
from PIL import Image
A='/mnt/user-data/outputs/game_demo/assets/'
orig=np.asarray(Image.open(A+'attic_bg_orig.png').convert('RGB')).copy()
out=orig.copy()
def mirror_fill(out, x0,x1,y0,y1, sy0,sy1):
    """fill rect with mirrored-tiled rows from [sy0,sy1) of orig (same x)"""
    n=sy1-sy0
    for y in range(y0,y1):
        k=(y-y0)%(2*n)
        r=k if k<n else 2*n-1-k
        out[y,x0:x1]=orig[sy0+r,x0:x1]
def sprite(box, thr_pad=2):
    x0,y0,x1,y1=box
    crop=orig[y0:y1,x0:x1].copy()
    h,w=crop.shape[:2]
    mask=np.zeros((h,w),np.uint8)
    rect=(3,3,w-6,h-6)
    bgd=np.zeros((1,65));fgd=np.zeros((1,65))
    gm=np.full((h,w),cv2.GC_PR_BGD,np.uint8); gm[6:h-6,6:w-6]=cv2.GC_PR_FGD
    gm[:3,:]=cv2.GC_BGD;gm[-3:,:]=cv2.GC_BGD;gm[:,:3]=cv2.GC_BGD;gm[:,-3:]=cv2.GC_BGD
    # dark outline pixels are surely fg
    lum=crop.sum(2)/3
    gm[(lum<30)]=cv2.GC_FGD
    cv2.grabCut(crop,gm,None,bgd,fgd,6,cv2.GC_INIT_WITH_MASK)
    m=((gm==cv2.GC_FGD)|(gm==cv2.GC_PR_FGD)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    # fill holes
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    m2=np.zeros_like(m);cv2.drawContours(m2,cnts,-1,1,-1)
    n,lab,stats,_=cv2.connectedComponentsWithStats(m2)
    best=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);m2=(lab==best).astype(np.uint8)
    return crop,m2
def place(out,box,scale,anchor):
    crop,m=sprite(box)
    h,w=crop.shape[:2]
    # tight bbox of mask
    ys,xs=np.where(m>0);cy0,cy1,cx0,cx1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    c=crop[cy0:cy1,cx0:cx1];mm=m[cy0:cy1,cx0:cx1]
    nw,nh=max(1,round(c.shape[1]*scale)),max(1,round(c.shape[0]*scale))
    c2=cv2.resize(c,(nw,nh),interpolation=cv2.INTER_NEAREST);m2=cv2.resize(mm,(nw,nh),interpolation=cv2.INTER_NEAREST)
    ax,ay=anchor  # bottom-centre target
    x=ax-nw//2;y=ay-nh
    reg=out[y:y+nh,x:x+nw]
    reg[m2>0]=c2[m2>0]
    return (x,y,nw,nh),(box[0]+cx0,box[1]+cy0,cx1-cx0,cy1-cy0)
# 1) clear bag & plant
bag=(878,968,1078,1182);plant=(858,1228,1082,1560);SPR_BAG=(878,968,1066,1182);SPR_PLANT=(858,1228,1066,1560)
def colmed(y0,y1,x0,x1):
    return np.median(orig[y0:y1,x0:x1].astype(float),axis=0)
def extrude(x0,x1,y0,y1):
    cm=colmed(1186,1224,x0,x1)
    if x0<884:
        n=884-x0;cm[:n]=colmed(1266,1292,x0,x0+n)
    # sub-pixel plank texture: faint vertical shade variation by row bands
    for y in range(y0,y1):
        sh=1.0+0.012*np.sin(y/37.0)
        out[y,x0:x1]=np.clip(cm*sh,0,255).astype(np.uint8)
px0,px1,py0,py1=plant
extrude(bag[0],bag[2],bag[1],bag[3])
extrude(px0,px1,py0,py1)
b1,b0=place_ = None,None
# sprites from orig (need orig sprite extraction BEFORE clearing: we use orig array)
(nb,ob)=place(out,SPR_BAG,0.68,(972,1178))
(np_,op)=place(out,SPR_PLANT,0.72,(972,1556))
print('bag new',nb,'old',ob);print('plant new',np_,'old',op)
Image.fromarray(out).save(A+'attic_bg.png')
Image.fromarray(out).crop((780,880,1116,1620)).save('crop_right_new.png')
