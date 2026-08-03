import asyncio
from playwright.async_api import async_playwright

URL = "https://gamefactory.zone/chess/app#cses=nhfJ44RzW9J6iON3XnVBaw&uid=5776831017%40telegram&ctype=chess&uname=Uraraka+Deku+san&domain=telegram&sign=IO7f6HC0ED1wWtnwab3lfrvXraI3zKhVKzkgugfqeOcKz5qFhJsoGCm%2BywrkdiIOcugsXkg84VYKondnhcG2hfbJ2hW2d12lWA%2BHs%2FFY1Cy0rt4SHATFjImriaOTNCfwu7lb8pSNXGsGexebyZhAGEGitpowvIuftWUtp%2FZKNRA%3D&subj=BQAAAPLn1iD_____MC8DAEsSctc-QTn8&logout=false"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        page = await browser.new_page()

        page.on(
            "request",
            lambda r: print(f"\n>>> {r.method} {r.url}")
        )

        async def response(resp):
            try:
                ct = resp.headers.get("content-type", "")

                print(f"\n<<< {resp.status} {resp.url}")

                if (
                    "json" in ct
                    or "javascript" in ct
                    or "text" in ct
                ):
                    body = await resp.text()
                    print(body[:5000])

            except Exception as e:
                print(e)

        page.on(
            "response",
            lambda r: asyncio.create_task(response(r))
        )

        def websocket(ws):
            print("\n==============================")
            print("WEBSOCKET:", ws.url)
            print("==============================")

            ws.on(
                "framesent",
                lambda f: print("\n>> SENT\n", f.payload)
            )

            ws.on(
                "framereceived",
                lambda f: print("\n<< RECEIVED\n", f.payload)
            )

            ws.on(
                "close",
                lambda: print("\nWS CLOSED")
            )

        page.on("websocket", websocket)

        await page.goto(URL)

        print(await page.title())
        print(page.url)

        await page.wait_for_timeout(60000)

        html = await page.content()

        with open("rendered.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("Saved rendered.html")

        await browser.close()


asyncio.run(main())
