import asyncio,os,sys,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await (await b.new_context(viewport={'width':560,'height':1000})).new_page()
        errs=[]
        pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e)))
        await pg.goto('file://'+os.getcwd()+'/game_dbg.html'); await pg.wait_for_timeout(2500)
        ev=pg.evaluate
        await ev("(()=>{__g.SETo.timeMode='story';document.getElementById('guide').hidden=true})()")
        SPN={'inn1':'inn1Door','attic':'atticWake','tavern':'tavernDoor','school':'schoolDoor','shop':'shopDoor','plaza':'plazaInn'}
        last=['']
        async def settle(tag,cap=120):
            for i in range(cap):
                st=await ev("__g.st()")
                if st=='play':
                    await pg.wait_for_timeout(250)
                    if await ev("__g.st()")=='play': return True
                elif st=='dialog':
                    t=await ev("(()=>{const d=document.getElementById('dlg');return d.querySelector('.nm').textContent+': '+d.querySelector('.tx').textContent})()")
                    ch=await ev("[...document.querySelectorAll('#dlg .ch > *')].map(x=>x.textContent)")
                    if t!=last[0] and len(t)>6 and t.startswith(last[0][:6])==False or t!=last[0] and ch:
                        print('   ',t[:120],('  ?'+'/'.join(ch)) if ch else '',flush=True)
                    last[0]=t
                    if ch: await ev("document.querySelector('#dlg .ch > *').click()")
                    else: await pg.mouse.click(280,880)
                elif st=='mini':
                    await ev("(()=>{const M=__g.mini();if(M){M.n=M.need;M.ok=true;M.fin=0.01}})()")
                await pg.wait_for_timeout(350)
            print('  !!settle timeout',await ev("__g.st()"),tag,flush=True); return False
        async def go(sc,sp=None):
            await ev("__g.go('%s','%s')"%(sc,sp or SPN[sc])); await pg.wait_for_timeout(900); await settle('go '+sc)
        async def ia(o,sc=None):
            n=await ev("(()=>{const x=__g.SC[__g.pos()[2]].objs.filter(x=>x.id=='%s')[0];return x?__g.tapObj(x):-9})()"%o)
            if n==-9: print('  (no obj',o,'here:',await ev("__g.pos()[2]"),')',flush=True); return False
            for _ in range(60):
                await pg.wait_for_timeout(300)
                if await ev("__g.st()")!='play': break
            await settle(o); return True
        async def walkout():
            await ev("__g.set('inn1',500,1300,'down')"); await pg.keyboard.down('ArrowDown'); await pg.wait_for_timeout(2500)
            await pg.keyboard.up('ArrowDown'); await settle('walkout'); print('   now in',await ev("__g.pos()[2]"),flush=True)
        async def enter(sc):
            P={'school':(520,490,'up','ArrowUp'),'tavern':(900,830,'right','ArrowRight'),'shop':(540,1800,'down','ArrowDown')}[sc]
            await ev("__g.go('plaza','plazaInn')"); await pg.wait_for_timeout(900); await settle('p')
            await ev("__g.set('plaza',%d,%d,'%s')"%(P[0],P[1],P[2])); await pg.keyboard.down(P[3]); await pg.wait_for_timeout(2500)
            await pg.keyboard.up(P[3]); await settle('enter '+sc); print('   entered',await ev("__g.pos()[2]"),flush=True)
        async def info():
            return await ev("(()=>{const s=__g.S();return JSON.stringify({day:s.day,ph:s.phase,les:s.lesson,main:s.q.main&&s.q.main.st,goal:s.goal,metW:s.metWella,spells:s.ls,gold:s.gold})})()")
        async def phase(n):
            await ev("(()=>{__g.S().phase=%d;__g.ap()})()"%n)
        # day1 flow
        await settle('intro'); 
        await ev("document.getElementById('guide').hidden=true"); 
        for k in range(24):
            i=json.loads(await info()); print('#',i,flush=True)
            m=i['main']; sc=await ev("__g.pos()[2]")
            if i['day']>=int(sys.argv[1]) and m in('free','explore3'): break
            if m=='counter': await ia('counter')
            elif m=='attic': await ia('stairs'); 
            elif m=='unpack': await ia('bag')
            elif m=='bed': await ia('bed')
            elif m=='morning': await go('inn1'); await phase(0); await ia('counter'); await walkout()
            elif m=='wella': await phase(0); await go('plaza'); await ia('wella')
            elif m=='school': await phase(0); await enter('school'); await ia('teacher')
            elif m=='candle': await ia('sdesk0')
            elif m=='explore':
                await go('attic'); await ia('bed')
            elif m=='breeze':
                await phase(0); await enter('school')
            elif m=='explore2': await go('attic'); await ia('window'); await ia('bed')
            elif m=='glow': await phase(0); await enter('school')
            elif m=='explore3': await go('attic'); await ia('bed')
            else:
                print('unhandled',m); break
        print(await info()); print(errs); await b.close()
asyncio.run(main())
