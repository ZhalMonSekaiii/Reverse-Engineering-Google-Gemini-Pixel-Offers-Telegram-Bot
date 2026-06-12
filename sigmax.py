import asyncio
import random
import pyotp
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import stealth_async

class GeminiOfferBot:
    def __init__(self, email: str, password: str, totp_secret: str, max_retries: int = 3):
        self.email = email
        self.password = password
        self.totp = pyotp.TOTP(totp_secret.strip().replace(" ", ""))
        self.max_retries = max_retries

    async def load_storage_state(self, playwright):
        """Load storage state dengan Pixel Spoofing Maksimal"""
        print("🔄 Loading storage state + Advanced Pixel Spoofing...")

        browser = await playwright.chromium.launch(
            headless=False,          # Ubah ke True setelah berhasil
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-web-security',
            ]
        )

        context = await browser.new_context(
            storage_state="google_state.json",
            viewport={"width": 412, "height": 915},
            user_agent="Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro XL Build/AP3A.241005.015) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36",
            device_scale_factor=3.0,
            is_mobile=True,
            has_touch=True,
            locale="id-ID",
            timezone_id="Asia/Jakarta",
        )

        page = await context.new_page()
        await stealth_async(page)

        # Spoofing mendalam
        await page.add_init_script("""
            () => {
                // Device Spoof
                Object.defineProperty(navigator, 'platform', {get: () => 'Android'});
                Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
                Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
                
                // WebGL & Canvas
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Google';
                    if (parameter === 37446) return 'ANGLE (Google, Vulkan 1.3.0)';
                    return getParameter.apply(this, arguments);
                };
            }
        """)

        print("✅ Storage + Pixel Spoofing Maksimal loaded")
        return browser, context, page

    async def safe_click(self, page, selector, timeout=15000):
        selectors = [s.strip() for s in selector.split(',')] if isinstance(selector, str) else [selector]
        for sel in selectors:
            try:
                await page.wait_for_selector(sel, timeout=timeout)
                await page.locator(sel).first.click(timeout=timeout)
                return True
            except:
                continue
        print(f"⚠️ Gagal klik: {selector}")
        return False

    async def claim_gemini_offer(self, page):
        print("🚀 Mencoba mengklaim Gemini Pixel Offer...")

        # === STEP 1: Buka halaman offers dan scan semua link ===
        offers_url = "https://one.google.com/offers"
        print(f"🌐 Membuka: {offers_url}")
        await page.goto(offers_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(random.randint(6000, 10000))

        # Scroll pelan ke bawah lalu balik (trigger lazy load)
        for i in range(3):
            await page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {(i+1)/3})")
            await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(2000)

        # Screenshot halaman offers untuk diagnostik
        await page.screenshot(path="offers_page.png", full_page=True)
        print("📸 Screenshot halaman offers disimpan")

        # === STEP 2: Scan semua link di halaman untuk partner-eft-onboard ===
        offer_links = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                return links
                    .map(a => ({ href: a.href, text: a.textContent.trim().substring(0, 100) }))
                    .filter(l => 
                        l.href.includes('partner-eft-onboard') || 
                        l.href.includes('/offer/') ||
                        l.href.includes('gemini') ||
                        l.text.toLowerCase().includes('gemini')
                    );
            }
        """)

        if offer_links:
            print(f"🔍 Ditemukan {len(offer_links)} link terkait:")
            for link in offer_links:
                print(f"   → {link['href']}  [{link['text'][:50]}]")

            # Prioritaskan partner-eft-onboard
            for link in offer_links:
                if "partner-eft-onboard" in link["href"]:
                    print(f"🎉 BERHASIL! Link offer spesifik ditemukan!")
                    print(f"🔗 {link['href']}")
                    await page.screenshot(path="SUCCESS_OFFER.png")
                    return link["href"]

            # Coba klik link yang ada /offer/
            for link in offer_links:
                if "/offer/" in link["href"]:
                    print(f"🖱️ Navigasi ke: {link['href']}")
                    await page.goto(link["href"], wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(8000)
                    if "partner-eft-onboard" in page.url:
                        print(f"🎉 Redirect ke offer link!")
                        print(f"🔗 {page.url}")
                        await page.screenshot(path="SUCCESS_OFFER.png")
                        return page.url
        else:
            print("⚠️ Tidak ada link terkait Gemini/offer ditemukan di halaman")

        # === STEP 3: Coba klik tombol/card offer ===
        print("🔍 Mencari tombol offer...")
        offer_selectors = [
            "a[href*='partner-eft-onboard']",
            "[data-offer-id]",
            "button:has-text('Claim')",
            "button:has-text('Aktifkan')",
            "button:has-text('Get Gemini')",
            "//a[contains(., 'Gemini Advanced')]",
            "//div[contains(., 'Gemini')]//button",
        ]

        for sel in offer_selectors:
            try:
                count = await page.locator(sel).count()
                if count > 0:
                    print(f"🖱️ Klik: {sel} ({count} match)")
                    await page.locator(sel).first.click()
                    await page.wait_for_timeout(10000)

                    if "partner-eft-onboard" in page.url or "/offer/" in page.url:
                        print(f"🎉 BERHASIL! Redirect ke: {page.url}")
                        await page.screenshot(path="SUCCESS_OFFER.png")
                        return page.url
            except:
                continue

        # === STEP 4: Coba direct URL patterns ===
        direct_urls = [
            "https://one.google.com/u/0/offer",
            "https://one.google.com/explore/gemini-advanced",
        ]
        for url in direct_urls:
            try:
                print(f"🌐 Direct: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(5000)
                if "partner-eft-onboard" in page.url:
                    print(f"🎉 Redirect ke: {page.url}")
                    return page.url
            except:
                continue

        # Fallback
        final_url = page.url
        print(f"⚠️ Offer spesifik tidak ditemukan. URL akhir: {final_url}")
        await page.screenshot(path="final_result.png")
        return final_url

    async def run_with_retry(self):
        for attempt in range(1, self.max_retries + 1):
            playwright = None
            browser = None
            try:
                print(f"\n🔄 === Attempt {attempt}/{self.max_retries} ===")
                
                playwright = await async_playwright().start()
                browser, context, page = await self.load_storage_state(playwright)
                
                await page.wait_for_timeout(5000)
                result = await self.claim_gemini_offer(page)
                
                print(f"🎉 Selesai di attempt {attempt}")
                return result

            except Exception as e:
                print(f"❌ Error: {e}")
            finally:
                if browser:
                    await browser.close()
                if playwright:
                    await playwright.stop()

            if attempt < self.max_retries:
                await asyncio.sleep(random.randint(10, 25))

        print("❌ Gagal semua attempt.")
        return None


# ================== JALANKAN ==================
if __name__ == "__main__":
    EMAIL = "X"      # tidak terlalu dipakai karena pakai state
    PASSWORD = "X"
    TOTP_SECRET = "X"   # tetap diisi sebagai cadangan

    bot = GeminiOfferBot(EMAIL, PASSWORD, TOTP_SECRET, max_retries=3)
    asyncio.run(bot.run_with_retry())