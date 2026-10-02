import asyncio,os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await (await b.new_context(viewport={'width':560,'height':1000})).new_page()
        errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: m.type=='error' and errs.append(m.text))
        await pg.goto('file://'+os.getcwd()+'/game.html'); await pg.wait_for_timeout(2500)
        await pg.screenshot(path='b0.png')
        for i in range(1,9):
            await pg.mouse.click(280,600); await pg.wait_for_timeout(1500)
            await pg.screenshot(path=f'b{i}.png')
        print(errs)
        await b.close()
asyncio.run(main())
