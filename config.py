"""
Sigmax - Centralized Configuration
Android Emulator-based Gemini Pixel Offer Claimer
"""
import os

# ============================================================
# SDK & Emulator Paths
# ============================================================
SDK_ROOT = r"C:\AndroidSDK"
ADB = os.path.join(SDK_ROOT, "platform-tools", "adb.exe")
EMULATOR = os.path.join(SDK_ROOT, "emulator", "emulator.exe")
AVDMANAGER = os.path.join(SDK_ROOT, "cmdline-tools", "latest", "bin", "avdmanager.bat")
SDKMANAGER = os.path.join(SDK_ROOT, "cmdline-tools", "latest", "bin", "sdkmanager.bat")

# ============================================================
# AVD Configuration
# ============================================================
AVD_NAME = "PixelClaimer_API33"
SNAPSHOT_NAME = "logged_in"
SYSTEM_IMAGE = "system-images;android-33;google_apis_playstore;x86_64"

# AVD Hardware Config
AVD_CONFIG = {
    "hw.lcd.density": "420",         # Pixel DPI
    "hw.lcd.width": "1080",          # PC-friendly width
    "hw.lcd.height": "2400",         # PC-friendly height
    "hw.ramSize": "4096",            # 4 GB RAM for emulator
    "hw.keyboard": "yes",
    "hw.gpu.enabled": "yes",
    "hw.gpu.mode": "auto",
    "disk.dataPartition.size": "8G",
    "vm.heapSize": "576",
    "hw.camera.back": "none",
    "hw.camera.front": "none",
}

# ============================================================
# Pixel 10 Pro Device Identity (for spoofing)
# ============================================================
PIXEL_PROPS = {
    "ro.product.model": "Pixel 10 Pro",
    "ro.product.brand": "google",
    "ro.product.manufacturer": "Google",
    "ro.product.device": "frankel",
    "ro.product.name": "frankel",
    "ro.build.display.id": "BP1A.250505.005",
    "ro.build.fingerprint": "google/frankel/frankel:16/BP1A.250505.005/13209991:user/release-keys",
    "ro.build.description": "frankel-user 16 BP1A.250505.005 13209991 release-keys",
    "ro.build.product": "frankel",
    "ro.product.first_api_level": "36",
    "ro.hardware": "frankel",
    "ro.boot.hardware": "frankel",
    "persist.sys.timezone": "Asia/Jakarta",
    "persist.sys.language": "in",
    "persist.sys.country": "ID",
}

# ============================================================
# Google Account (for claiming offers)
# ============================================================
GOOGLE_EMAIL = "backupandrive693@gmail.com"
OFFERS_URL = "https://one.google.com/offers"
GEMINI_OFFER_URL = "https://one.google.com/explore/gemini/offer"

# ============================================================
# Timeouts (seconds)
# ============================================================
EMULATOR_BOOT_TIMEOUT = 120     # Max wait for emulator to boot
PAGE_LOAD_TIMEOUT = 30          # Max wait for page load
ELEMENT_WAIT_TIMEOUT = 15       # Max wait for UI element
SCREENSHOT_DIR = os.path.dirname(os.path.abspath(__file__))
