import asyncio
from playwright.async_api import async_playwright


DUMP_SCRIPT = r"""
(() => {
    if (window.__pgnx_installed) return;
    window.__pgnx_installed = true;

    const seen = new WeakSet();

    function dump(value, label = "root", depth = 0) {
        const pad = "  ".repeat(depth);

        try {
            if (value === null) {
                console.log(`${pad}${label}: null`);
                return;
            }

            if (value === undefined) {
                console.log(`${pad}${label}: undefined`);
                return;
            }

            const t = typeof value;
            if (t === "string" || t === "number" || t === "boolean" || t === "bigint") {
                console.log(`${pad}${label}:`, value);
                return;
            }

            if (t === "function") {
                console.log(`${pad}${label}: [Function ${value.name || "anonymous"}]`);
                return;
            }

            if (seen.has(value)) {
                console.log(`${pad}${label}: [Circular]`);
                return;
            }

            seen.add(value);

            if (Array.isArray(value)) {
                console.log(`${pad}${label}: [Array(${value.length})]`);
                for (let i = 0; i < value.length && i < 40; i++) {
                    dump(value[i], `[${i}]`, depth + 1);
                }
                return;
            }

            const ctor = value && value.constructor ? value.constructor.name : "Object";
            console.log(`${pad}${label}: [${ctor}]`);

            const keys = Object.keys(value);
            for (const k of keys) {
                try {
                    const v = value[k];
                    if (depth >= 4 && typeof v === "object" && v !== null) {
                        console.log(`${pad}  ${k}: [Object]`);
                    } else {
                        dump(v, k, depth + 1);
                    }
                } catch (e) {
                    console.log(`${pad}  ${k}: [unreadable: ${e}]`);
                }
            }
        } catch (e) {
            console.log(`${pad}${label}: [dump error: ${e}]`);
        }
    }

    function wrapWhenReady(name) {
        const original = window[name];
        if (typeof original !== "function" || original.__pgnx_wrapped) return false;

        const wrapped = function(...args) {
            const result = original.apply(this, args);
            try {
                console.log(`[[${name} RESULT]]`);
                dump(result, name);
            } catch (e) {
                console.log(`[[${name} DUMP ERROR]] ${e}`);
            }
            return result;
        };

        wrapped.__pgnx_wrapped = true;
        window[name] = wrapped;
        console.log(`[[PNGX]] wrapped ${name}`);
        return true;
    }

    function tick() {
        wrapWhenReady("MK");
        wrapWhenReady("Vbb");
    }

    tick();
    const timer = setInterval(tick, 25);
    window.addEventListener("beforeunload", () => clearInterval(timer));
})();
"""


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

        page.on("console", lambda msg: print(msg.text))

        await page.add_init_script(DUMP_SCRIPT)

        page.on("request", lambda r: print(f">>> {r.method} {r.url}"))
        page.on("response", lambda r: print(f"<<< {r.status} {r.url}"))

        print("Opening...")
        await page.goto(url, wait_until="networkidle")
        print(await page.title())

        await page.wait_for_timeout(120000)
        await browser.close()


async def main():
    # Backward-compatible fallback for the old hardcoded test flow.
    url = "https://gamefactory.zone/chess/app#cses=nhfJ44RzW9J6iON3XnVBaw&uid=5776831017%40telegram&ctype=chess&uname=Uraraka+Deku+san&domain=telegram&sign=IO7f6HC0ED1wWtnwab3lfrvXraI3zKhVKzkgugfqeOcKz5qFhJsoGCm%2BywrkdiIOcugsXkg84VYKondnhcG2hfbJ2hW2d12lWA%2BHs%2FFY1Cy0rt4SHATFjImriaOTNCfwu7lb8pSNXGsGexebyZhAGEGitpowvIuftWUtp%2FZKNRA%3D&subj=BQAAAPLn1iD_____MC8DAEsSctc-QTn8&logout=false"
    await sniff(url)


if __name__ == "__main__":
    asyncio.run(main())
