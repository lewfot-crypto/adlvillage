import asyncio,os,sys,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await (await b.new_context(viewport={'width':560,'height':1000})).new_page()
        errs=[]
        pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e)))
        await pg.goto('file://'+os.getcwd()+'/game_dbg.html'); await pg.wait_for_timeout(1500)
        ev=pg.evaluate
        await pg.wait_for_timeout(1500)
        await ev("(()=>{const s=__g.S();s.started=true;s.key=true;s.unpacked=true;s.day=2;s.phase=0;__g.SETo.timeMode='story';document.getElementById('dlg').hidden=true;document.getElementById('guide').hidden=true})()")
        SPN={'inn1':'inn1Door','attic':'atticWake','tavern':'tavernDoor','school':'schoolDoor','shop':'shopDoor'}
        async def advd(tag):
            last='';stuck=0
            for i in range(80):
                st=await ev("__g.st()")
                if st=='play': return True
                if st=='dialog':
                    t=await ev("(()=>{const d=document.getElementById('dlg');return d.querySelector('.nm').textContent+': '+d.querySelector('.tx').textContent})()")
                    if t!=last and len(t)>6: print('   ',t[:100],flush=True); last=t
                    ch=await ev("document.querySelectorAll('#dlg .ch > *').length")
                    if ch: await ev("[...document.querySelectorAll('#dlg .ch > *')].pop().click()")
                    else: await pg.mouse.click(280,880)
                await pg.wait_for_timeout(400)
            return False
        scenes=sys.argv[1].split(',')
        for sc in scenes:
            await ev("__g.go('%s','%s')"%(sc,SPN[sc]) if sc!='plaza' else "__g.go('plaza',Object.keys(__g.SP).find(k=>k.startsWith('plaza')))")
            await pg.wait_for_timeout(1500); await advd('enter')
            objs=await ev("JSON.stringify(__g.SC['%s'].objs.filter(o=>!o.solid||o.at).map(o=>o.id))"%sc)
            print('==',sc,objs,flush=True)
            await pg.screenshot(path=f'sc_{sc}.png')
            for o in json.loads(objs):
                await ev("__g.go('%s','%s')"%(sc,SPN[sc]) if sc!='plaza' else "__g.go('plaza',Object.keys(__g.SP).find(k=>k.startsWith('plaza')))")
                await pg.wait_for_timeout(900); await advd('e')
                n=await ev("__g.tapObj(__g.SC['%s'].objs.filter(x=>x.id=='%s')[0])"%(sc,o))
                print(' tap',o,'path',n,flush=True)
                for _ in range(40):
                    await pg.wait_for_timeout(300)
                    if await ev("__g.st()")!='play': break
                ok=await advd(o)
                if not ok: print('  !!STUCK',await ev("__g.st()"),flush=True)
        print(errs); await b.close()
asyncio.run(main())
