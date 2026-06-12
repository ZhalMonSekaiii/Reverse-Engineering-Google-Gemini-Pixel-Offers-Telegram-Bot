import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Pakai argumen agar lebih mirip Chrome biasa
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},  # ukuran desktop biasa
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            is_mobile=False,
        )
        
        page = await context.new_page()
        await page.goto("https://accounts.google.com/signin")
        
        print("🔴 LOGIN MANUAL sekarang di browser yang muncul.")
        print("   Login seperti biasa sampai berhasil masuk.")
        print("   Setelah masuk, tutup browser ini.")
        
        await page.pause()   # Pause sampai kamu tutup manual
        
        await context.storage_state(path="google_state.json")
        print("✅ Storage state berhasil disimpan!")
        
        await browser.close()

asyncio.run(main())