"""5일차 이후 점검: 마법서 1~5장 + 엔딩, 8일차 부탁(약초·단풍잎) + 이야기 1편(사라진 가을 불빛) + 2편(시나의 잃어버린 방울) + 3편(브란의 가을 수프 대회).
사용: python3 tools/playtest_late.py [스크린샷폴더]   (playtest_story 와 같은 방식으로 5일차까지 먼저 진행)"""
import asyncio,os,sys,json
from playwright.async_api import async_playwright
SHOT=sys.argv[1] if len(sys.argv)>1 else None
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await (await b.new_context(viewport={'width':560,'height':1000})).new_page()
        errs=[]
        pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e)))
        pg.on('console',lambda m:m.type=='error' and errs.append('CONSOLE '+m.text))
        await pg.goto('file://'+os.getcwd()+'/game_dbg.html'); await pg.wait_for_timeout(2500)
        ev=pg.evaluate
        await ev("(()=>{__g.SETo.timeMode='story';document.getElementById('guide').hidden=true})()")
        SPN={'inn1':'inn1Door','attic':'atticWake','tavern':'tavernDoor','school':'schoolDoor','shop':'shopDoor','plaza':'plazaInn'}
        last=['']; nshot=[0]
        async def shot(tag):
            if not SHOT: return
            nshot[0]+=1; await pg.screenshot(path='%s/%02d_%s.png'%(SHOT,nshot[0],tag))
        async def settle(tag,cap=160,pick=0,shoot=None):
            shotted=False
            for i in range(cap):
                st=await ev("__g.st()")
                if st=='play':
                    await pg.wait_for_timeout(250)
                    if await ev("__g.st()")=='play': return True
                elif st=='dialog':
                    t=await ev("(()=>{const d=document.getElementById('dlg');return d.querySelector('.nm').textContent+': '+d.querySelector('.tx').textContent})()")
                    ch=await ev("[...document.querySelectorAll('#dlg .ch > *')].map(x=>x.textContent)")
                    if t!=last[0]: print('   ',t[:110],('  ?'+'/'.join(ch)) if ch else '',flush=True)
                    last[0]=t
                    if shoot and not shotted:
                        await pg.wait_for_timeout(900); await shot(shoot); shotted=True
                        ch=await ev("[...document.querySelectorAll('#dlg .ch > *')].map(x=>x.textContent)")
                    if ch: await pg.wait_for_timeout(350); await ev("document.querySelectorAll('#dlg .ch > *')[%d].click()"%min(pick,len(ch)-1))
                    else: await pg.mouse.click(280,880)
                elif st=='mini':
                    await ev("(()=>{const M=__g.mini();if(M){M.n=M.need;M.ok=true;M.fin=0.01}})()")
                await pg.wait_for_timeout(300)
            print('  !!settle timeout',await ev("__g.st()"),tag,flush=True); return False
        async def go(sc,sp=None):
            await ev("__g.go('%s','%s')"%(sc,sp or SPN[sc])); await pg.wait_for_timeout(900); await settle('go '+sc)
        async def ia(o,pick=0,shoot=None):
            n=await ev("(()=>{const x=__g.SC[__g.pos()[2]].objs.filter(x=>x.id=='%s')[0];return x?__g.tapObj(x):-9})()"%o)
            if n==-9: print('  (no obj',o,'here:',await ev("__g.pos()[2]"),')',flush=True); return False
            for _ in range(60):
                await pg.wait_for_timeout(300)
                if await ev("__g.st()")!='play': break
            await settle(o,pick=pick,shoot=shoot); return True
        async def phase(n): await ev("(()=>{__g.S().phase=%d;__g.ap()})()"%n)
        async def at(sc,ph):
            await go(sc); await phase(ph); await pg.wait_for_timeout(400)
        async def sleep():
            await go('attic'); await phase(3); await ia('bed')
        async def info():
            return json.loads(await ev("(()=>{const s=__g.S(),B=s.book||{};return JSON.stringify({day:s.day,cal:s.cal.m+'/'+s.cal.d,main:s.q.main&&s.q.main.st,herb:s.q.herb&&s.q.herb.st,leaves:s.q.leaves&&s.q.leaves.st,lights:s.q.lights&&s.q.lights.st,bell:s.q.bell&&s.q.bell.st,soup:s.q.soup&&s.q.soup.st,bellDay:s.bellDay||0,book:Object.keys(B.pg||{}),bkey:B.key,end:B.ended,gold:s.gold,inv:s.inv,magic:s.magic})})()"))
        # ---- 1~5일차 빠르게 (playtest_story 와 같은 경로)
        async def walkout():
            await ev("__g.set('inn1',500,1300,'down')"); await pg.keyboard.down('ArrowDown'); await pg.wait_for_timeout(2500)
            await pg.keyboard.up('ArrowDown'); await settle('walkout')
        async def enter(sc):
            P={'school':(520,490,'up','ArrowUp')}[sc]
            await go('plaza'); await ev("__g.set('plaza',%d,%d,'%s')"%(P[0],P[1],P[2])); await pg.keyboard.down(P[3]); await pg.wait_for_timeout(2500)
            await pg.keyboard.up(P[3]); await settle('enter '+sc)
        await settle('intro')
        for k in range(30):
            m=(await info())['main']
            if m=='free': break
            if m=='counter': await ia('counter')
            elif m=='attic': await ia('stairs')
            elif m=='unpack': await ia('bag')
            elif m=='bed': await ia('bed')
            elif m=='morning': await go('inn1'); await phase(0); await ia('counter'); await walkout()
            elif m=='wella': await phase(0); await go('plaza'); await ia('wella')
            elif m=='school': await phase(0); await enter('school'); await ia('teacher')
            elif m=='candle': await ia('sdesk0')
            elif m in('explore','explore2','explore3'):
                if m=='explore2': await go('attic'); await ia('window')
                await sleep()
            elif m in('breeze','glow'): await phase(0); await enter('school')
            else: print('unhandled',m); break
        print('## 5일차 도착',await info(),flush=True)
        # ---- 5일차부터: 마법서 + 8일차 부탁
        for k in range(14):
            i=await info(); print('#',i['day'],'일차',i['cal'],{x:i.get(x) for x in('main','herb','leaves','lights','bell','soup','book','bkey','gold')},flush=True)
            B=i['book']
            if '1' not in B:
                await at('inn1',2); await ia('fire',shoot='book1')
            elif '2' not in B:
                await go('attic'); await phase(0)
                for _ in range(3): await ia('window')   # 바람결 Lv2 만들기
                await at('plaza',1); await ia('fountain',shoot='book2')
            elif '3' not in B:
                if not i.get('bkey'): await at('school',1); await ia('teacher',shoot='master_key')
                await at('school',1); await ia('shelf',shoot='book3')
            elif '4' not in B:
                await at('shop',1); await ia('counter',shoot='book4')
            elif '5' not in B and i['day']>=8 and i.get('lights')=='done':
                await go('attic'); await phase(3); await ia('window',shoot='book5')
            if i['day']>=8:
                if not i.get('lights'): await at('inn1',1); await ia('counter',shoot='orga_lights')
                i=await info()
                if i.get('lights')=='clues':
                    await at('tavern',1); await ia('counter')        # 메뉴 첫 줄 = 등불 이야기
                    await at('school',1); await ia('teacher')
                i=await info()
                if i.get('lights')=='shop': await at('shop',1); await ia('counter',shoot='lights_shop')
                i=await info()
                if i.get('lights')=='flower': await at('shop',1); await ia('flower')
                i=await info()
                if i.get('lights')=='sina':
                    await at('plaza',2); await shot('plaza_eve'); await ia('sina',shoot='lights_sina')
                i=await info()
                if not i.get('leaves'): await at('plaza',1); await ia('wella')
                i=await info()
                if i.get('leaves')=='collect':
                    for l in 'ABC': await ia('leaf'+l)
                    await shot('leaves')
                i=await info()
                if i.get('leaves')=='return': await ia('wella')
                i=await info()
                if not i.get('herb'):
                    await at('tavern',1); await ia('counter')
                i=await info()
                if i.get('herb')=='buy':
                    await at('shop',1); await ev("(()=>{const s=__g.S();s.inv.herb=2})()"); await ev("__g.S().q.herb={st:'return'}")
                i=await info()
                if i.get('herb')=='return': await at('tavern',1); await ia('counter')
                # 이야기 2편: 시나의 잃어버린 방울 (사라진 가을 불빛 다음 날부터)
                i=await info()
                if i.get('lights')=='done' and not i.get('bell'): await at('plaza',1); await ia('sina',shoot='bell_start')
                i=await info()
                if i.get('bell')=='clues':
                    await at('inn1',1); await ia('counter',shoot='bell_orga')
                    await at('tavern',1); await ia('counter')        # 메뉴 첫 줄 = 방울 이야기
                i=await info()
                if i.get('bell')=='wind': await at('plaza',1); await ia('fountain',shoot='bell_wind')
                i=await info()
                if i.get('bell')=='wella': await at('plaza',1); await ia('wella',shoot='bell_wella')
                i=await info()
                if i.get('bell')=='return': await at('plaza',1); await ia('sina',shoot='bell_return')
                # 이야기 3편: 브란의 가을 수프 대회 (2편 다음 날부터)
                i=await info()
                if i.get('bell')=='done' and not i.get('soup') and i['day']>i.get('bellDay',0): await at('tavern',1); await ia('counter',shoot='soup_start')   # 메뉴 첫 줄 = 수프 대회
                i=await info()
                if i.get('soup')=='gather':
                    await ev("(()=>{const s=__g.S();s.inv.herb=(s.inv.herb||0)+1})()")   # 상점 구매 화면은 건너뜀
                    await at('plaza',1); await ia('wella',shoot='soup_wella')
                    await at('school',1); await ia('teacher',shoot='soup_master')
                    await at('tavern',1); await ia('counter',shoot='soup_give')
                i=await info()
                if i.get('soup')=='cook': await at('tavern',1); await ia('counter')
                i=await info()
                if i.get('soup')=='judge': await at('tavern',2); await ia('counter',shoot='soup_judge')
            i=await info()
            if i.get('end') and i.get('soup')=='done': print('## 엔딩·이야기 2·3편 확인'); break
            await sleep(); await pg.wait_for_timeout(800); await settle('wake',shoot='wake%d'%(i['day']+1))
        print('## 끝',await info()); print('ERRORS',errs); await b.close()
asyncio.run(main())
