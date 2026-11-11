import sys, asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for path, w, name, full in [(a.split(',')[0], int(a.split(',')[1]), a.split(',')[2], a.split(',')[3]=='1') for a in sys.argv[1:]]:
            pg = await b.new_page(viewport={"width": w, "height": 900})
            errs=[]; pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
            await pg.goto("http://localhost:8765" + path, wait_until="networkidle")
            await pg.evaluate("async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,80))}window.scrollTo(0,0)}")
            await pg.wait_for_timeout(1200)
            await pg.screenshot(path=f"/tmp/{name}.png", full_page=full)
            print(name, "errors:", errs)
        await b.close()
asyncio.run(main())
