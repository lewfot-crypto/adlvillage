from PIL import Image
import numpy as np, base64, json, io, sys
import os,tempfile
BASE=os.path.dirname(os.path.abspath(__file__))
U=BASE+"/source_images/"
TMP=tempfile.mkdtemp()+"/"
D=BASE+"/assets/"
src={"tavern":"92c6a134-image.jpg","school":"2d45173a-image.jpg","inn1":"4108a15b-image.jpg"}
for k,f in src.items():
    im=Image.open(U+f).convert("RGB").resize((1116,2000),Image.LANCZOS)
    a=np.array(im)
    fill=np.median(a[1950:1990,800:900].reshape(-1,3),axis=0).astype(np.uint8)
    a[1870:1985,985:1090]=fill
    if k=="inn1":
        import cv2
        f=a.astype(float);RR,GG,BB=f[...,0],f[...,1],f[...,2]
        reg=np.zeros(RR.shape,bool);reg[700:1350,0:420]=True
        core=(reg&(((BB>GG+25)&(BB>RR*0.7))|((GG>RR+10)&(GG>BB-10)))).astype(np.uint8)*255
        bad=cv2.dilate(core,np.ones((5,5),np.uint8),iterations=6)>0
        reg2=np.zeros(bad.shape,bool);reg2[745:1330,0:372]=True;bad&=reg2
        src_a=a.copy();filled=~bad.copy()
        for (dx,dy) in [(94,76),(-94,-76),(188,152),(-188,-152),(138,112),(-138,-112)]:
            ys,xs=np.where(bad&~filled) if False else np.where(bad)
            ys2=ys+dy;xs2=xs+dx
            ok=(ys2>=700)&(ys2<1350)&(xs2>=30)&(xs2<400)
            ys,xs,ys2,xs2=ys[ok],xs[ok],ys2[ok],xs2[ok]
            good=~bad[ys2,xs2]
            todo=~filled[ys,xs]
            sel=good&todo
            a[ys[sel],xs[sel]]=src_a[ys2[sel],xs2[sel]];filled[ys[sel],xs[sel]]=True
        rest=(bad&~filled).astype(np.uint8)*255
        if rest.any():
            a=cv2.inpaint(a,cv2.dilate(rest,np.ones((3,3),np.uint8)),4,cv2.INPAINT_TELEA)
        # soften seam with slight blur on the patched area boundary only
        edge=cv2.dilate(bad.astype(np.uint8),np.ones((3,3),np.uint8))-cv2.erode(bad.astype(np.uint8),np.ones((3,3),np.uint8))
        bl=cv2.GaussianBlur(a,(3,3),0);a[edge>0]=bl[edge>0]
    Image.fromarray(a).save(D+f"{k}_bg.png",optimize=True)
    Image.fromarray(a).save(TMP+f"{k}_bg.jpg",quality=88)
def b64(p,m): return "data:%s;base64,%s"%(m,base64.b64encode(open(p,"rb").read()).decode())
def pj(n):
    im=Image.open(D+f"portrait_{n}_cut.png" if n!="amelia" else D+"portrait_amelia.png").convert("RGBA")
    if n=="bran":
        im=im.crop((30,30,360,402)); im=im.resize((190,214),Image.LANCZOS)
    elif n in("orga","amelia"): im=im.resize((190,240),Image.LANCZOS)
    b=io.BytesIO(); im.save(b,"PNG",optimize=True); return "data:image/png;base64,"+base64.b64encode(b.getvalue()).decode()
Image.open(D+"attic_bg.png").convert("RGB").save(TMP+"attic_bg.jpg",quality=88)
assets={"bg_attic":b64(TMP+"attic_bg.jpg","image/jpeg")}
for k in src: assets["bg_"+k]=b64(TMP+f"{k}_bg.jpg","image/jpeg")
for k in ["plaza","shop"]: assets["bg_"+k]=b64(D+f"{k}_bg.jpg","image/jpeg")
for k,f in [("down","amelia2_down"),("up","amelia2_up"),("left","amelia2_left"),("right","amelia2_right")]: assets[k]=b64(D+f+".png","image/png")
assets["attic_wmask"]=b64(D+"attic_window_mask.png","image/png")
for n in ["orga","bran","master","alesendo","sina","wella","magiccat","owl"]: assets["npc_"+n]=b64(D+"npc_"+n+".png","image/png")
import os
if os.path.exists(D+"title_bg.jpg"): assets["title_bg"]=b64(D+"title_bg.jpg","image/jpeg")
if os.path.exists(D+"title_logo.png"): assets["title_logo"]=b64(D+"title_logo.png","image/png")
assets["door_inn1"]=b64(D+"door_inn1_open2.png","image/png")
for n in ["orga","bran","amelia","master","wella","alesendo"]: assets["p_"+n]=pj(n)
S=BASE+"/src/"
head=open(S+"head.html").read(); script=open(S+"script.html").read()
dbg=len(sys.argv)>1
RENDER="""window.__r={theme:function(name,loops){var th=THEMES[name],sr=22050,bd=60/th.bpm*4,dur=bd*8*loops+2.5,oc=new OfflineAudioContext(1,Math.ceil(sr*dur),sr),bus=makeBus(oc);bus.bgm.gain.value=.55*.7;var g=oc.createGain();g.connect(bus.bgm);for(var i=0;i<8*loops;i++)schedBar(oc,g,th,i,i*bd+.1);return oc.startRendering().then(wavB64)},
sfx:function(names){var sr=22050,oc=new OfflineAudioContext(1,sr*(names.length*1.2+.5),sr),sv=[AUD.ctx,AUD.bus,AUD.noise];AUD.ctx=oc;AUD.bus=makeBus(oc);var n=oc.sampleRate,buf=oc.createBuffer(1,n,n),d=buf.getChannelData(0);for(var i=0;i<n;i++)d[i]=Math.random()*2-1;AUD.noise=buf;AUD.bus.sfx.gain.value=.8;names.forEach(function(nm,k){var t=k*1.2+.1;if(nm==='step'){SFX.step(t);SFX.step(t+.28);SFX.step(t+.56);SFX.step(t+.84)}else if(nm==='blip'){for(var j=0;j<8;j++)SFX.blip(t+j*.07,520+(j%4)*14)}else SFX[nm](t)});return oc.startRendering().then(function(r){AUD.ctx=sv[0];AUD.bus=sv[1];AUD.noise=sv[2];return wavB64(r)})}};
function wavB64(buf){var d=buf.getChannelData(0),n=d.length,sr=buf.sampleRate,ab=new ArrayBuffer(44+n*2),v=new DataView(ab),i;function ws(o,s){for(var k=0;k<s.length;k++)v.setUint8(o+k,s.charCodeAt(k))}ws(0,'RIFF');v.setUint32(4,36+n*2,true);ws(8,'WAVE');ws(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,sr,true);v.setUint32(28,sr*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);ws(36,'data');v.setUint32(40,n*2,true);var pk=0;for(i=0;i<n;i++){var x=Math.max(-1,Math.min(1,d[i]));v.setInt16(44+i*2,x*32767,true);if(Math.abs(x)>pk)pk=Math.abs(x)}var bin='',u=new Uint8Array(ab);for(i=0;i<u.length;i+=8192)bin+=String.fromCharCode.apply(null,u.subarray(i,i+8192));return {b64:btoa(bin),peak:pk}}"""
if dbg: script=script.replace("/*DBG*/","window.__noTitle=true;"+RENDER+"window.__g={tl:function(n,a){return tellLore(n,a)},oj:function(t){openJournal();jtab=t;renderJournal()},say:function(a,o){say(a,o)},go:function(n,sp){go(n,sp)},SP:SPAWN,face:function(){return face},bk:{F:bookF,p4:bookPage4,p5:bookPage5,end:bookEnding,ok4:bookP4ok,ok5:bookP5ok},SC:SC,set:function(n,x,y,f){CN=n;C=SC[n];px=x;py=y;face=f;state='play';updateHud()},tgt:findTarget,hit:hit,S:function(){return S},st:function(){return state},pos:function(){return [px,py,CN,doorO]},les:function(){startLesson()},mini:function(){return M},fl:function(){return [S.lesson,S.candleLit,S.day,S.phase]},sl:function(){sleep()},cut:function(id){playCut(id)},ls:function(sp){startSpellLesson(sp)},pr:function(sp){practice(sp)},ia:function(id){interact(C.objs.filter(function(x){return x.id===id})[0])},go:function(n,s){go(n,SPAWN[s])},jr:function(){openJournal()},SETo:SET,ap:function(){applySchedule()},SPAWN:SPAWN,ph:function(){return [S.phase,S.tick]},devTo:function(m,d){devTo(m,d)},devSkip:function(n){devSkip(n)},tapObj:function(o){pend=o;path=planPath(0,0,o);dest=null;if(path&&!path.length)arrive();return path?path.length:-1},wp:function(){return [px,py,face,state]}};")
full=head+script.replace("__ASSETS__",json.dumps(assets))
from fontTools import subset
from fontTools.ttLib import TTFont
txt=set(c for c in head+script if ord(c)>126 or c.isprintable())
txt|=set(chr(i) for i in range(32,127))|set("…·▼▶◀!?—’“”…")
opts=subset.Options(); opts.flavor="woff2"; opts.layout_features=["*"]
f=TTFont(BASE+"/fonts/Galmuri11.ttf"); sb=subset.Subsetter(opts); sb.populate(text="".join(txt)); sb.subset(f)
buf=io.BytesIO(); f.flavor="woff2"; f.save(buf)
ff="@font-face{font-family:'Galmuri11';src:url(data:font/woff2;base64,%s) format('woff2');font-display:block}"%base64.b64encode(buf.getvalue()).decode()
print("font KB",len(buf.getvalue())//1024)
full=full.replace("/*FONT*/",ff)
open(BASE+("/game_dbg.html" if dbg else "/game.html"),"w").write(full)
print(len(full)/1e6,"MB")
# 홈 화면 추가용(GitHub Pages): index.html + manifest.json + sw.js. game.html(Artifact·더블클릭용)은 그대로 둔다.
if not dbg:
    import re,hashlib
    ver=re.search(r"var VERSION='([^']*)'",script).group(1)
    tag=hashlib.md5(full.encode()).hexdigest()[:8]
    PWA_HEAD="""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="theme-color" content="#0b0813"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"><meta name="apple-mobile-web-app-title" content="아델라인 빌리지">
<link rel="manifest" href="manifest.json"><link rel="apple-touch-icon" href="pwa/apple-touch-icon.png"><link rel="icon" href="pwa/icon-192.png">
"""
    PWA_TAIL="""<script>if('serviceWorker' in navigator&&(location.protocol==='https:'||location.hostname==='localhost'))addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){})});</script>"""
    open(BASE+"/index.html","w").write(PWA_HEAD+full+PWA_TAIL)
    open(BASE+"/manifest.json","w").write(json.dumps({"name":"아델라인 빌리지","short_name":"아델라인","start_url":"./","scope":"./","display":"standalone","orientation":"portrait","background_color":"#0b0813","theme_color":"#0b0813","icons":[{"src":"pwa/icon-192.png","sizes":"192x192","type":"image/png"},{"src":"pwa/icon-512.png","sizes":"512x512","type":"image/png"},{"src":"pwa/icon-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]},ensure_ascii=False,indent=1))
    # 캐시 이름에 버전+내용 해시를 넣어, 빌드가 바뀌면 폰이 새 파일을 받게 한다
    open(BASE+"/sw.js","w").write("""const CACHE='adeline-%s-%s';
const FILES=['./','index.html','manifest.json','pwa/icon-192.png','pwa/icon-512.png','pwa/apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
// 인터넷이 되면 새 파일을 먼저 받고, 안 되면 저장해 둔 파일로 실행
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;
  e.respondWith(fetch(e.request).then(r=>{if(r.ok){const cp=r.clone();caches.open(CACHE).then(c=>c.put(e.request,cp))}return r}).catch(()=>caches.match(e.request,{ignoreSearch:true}).then(m=>m||caches.match('index.html'))))});
"""%(ver.replace(' ','_'),tag))
    print("index.html + sw.js",ver,tag)
