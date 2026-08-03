import asyncio
from playwright.async_api import async_playwright


async def sniff(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        page = await browser.new_page()

        page.on(
            "request",
            lambda r: print(f"\n>>> REQUEST {r.method} {r.url}")
        )

        async def on_response(resp):
            try:
                print(f"\n<<< RESPONSE {resp.status} {resp.url}")

                ct = resp.headers.get("content-type", "")

                if any(
                    x in ct
                    for x in (
                        "json",
                        "javascript",
                        "text",
                        "xml",
                    )
                ):
                    body = await resp.text()
                    print(body[:5000])

            except Exception as e:
                print("Response error:", e)

        page.on(
            "response",
            lambda r: asyncio.create_task(on_response(r))
        )

        def on_websocket(ws):
            print("\n==============================")
            print("WEBSOCKET:", ws.url)
            print("==============================")

            ws.on(
                "framesent",
                lambda f: print(f"\n>> SENT\n{f.payload}")
            )

            ws.on(
                "framereceived",
                lambda f: print(f"\n<< RECEIVED\n{f.payload}")
            )

            ws.on(
                "close",
                lambda: print("\nWEBSOCKET CLOSED")
            )

        page.on("websocket", on_websocket)

        print("Opening:", url)

        await page.goto(
            url,
            wait_until="networkidle",
        )

        print("Title:", await page.title())
        print("Current URL:", page.url)

        html = await page.content()

        with open("rendered.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("Saved rendered.html")

        # Give sockets time to receive data
        await page.wait_for_timeout(60000)

        await browser.close()
