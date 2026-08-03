import asyncio
from playwright.async_api import async_playwright

URL = "https://gamefactory.zone/chess/app#cses=nhfJ44RzW9J6iON3XnVBaw&uid=5776831017%40telegram&ctype=chess&uname=Uraraka+Deku+san&domain=telegram&sign=IO7f6HC0ED1wWtnwab3lfrvXraI3zKhVKzkgugfqeOcKz5qFhJsoGCm%2BywrkdiIOcugsXkg84VYKondnhcG2hfbJ2hW2d12lWA%2BHs%2FFY1Cy0rt4SHATFjImriaOTNCfwu7lb8pSNXGsGexebyZhAGEGitpowvIuftWUtp%2FZKNRA%3D&subj=BQAAAPLn1iD_____MC8DAEsSctc-QTn8&logout=false"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        page = await browser.new_page()

        page.on("console", lambda msg: print(msg.text))

        await page.add_init_script("""
(() => {
    const NativeWS = window.WebSocket;

    window.WebSocket = function(...args) {
        console.log("[WS OPEN]", args[0]);

        const ws = new NativeWS(...args);

        const send = ws.send.bind(ws);

        ws.send = function(data) {
            console.log("[WS SEND]", data);
            return send(data);
        };

        ws.addEventListener("message", e => {
            console.log("[WS RECV]", e.data);
        });

        ws.addEventListener("open", () => {
            console.log("[WS CONNECTED]");
        });

        ws.addEventListener("close", () => {
            console.log("[WS CLOSED]");
        });

        return ws;
    };

    window.WebSocket.prototype = NativeWS.prototype;
})();
""")

        page.on(
            "request",
            lambda r: print(f">>> {r.method} {r.url}")
        )

        page.on(
            "response",
            lambda r: print(f"<<< {r.status} {r.url}")
        )

        print("Opening...")

        await page.goto(URL, wait_until="networkidle")

        print(await page.title())

        # Give the page plenty of time
        await page.wait_for_timeout(120000)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
