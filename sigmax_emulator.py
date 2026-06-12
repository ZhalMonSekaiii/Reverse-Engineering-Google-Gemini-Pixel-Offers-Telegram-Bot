"""
Sigmax Emulator - Automated Gemini Pixel Offer Claimer
Uses Android Emulator + uiautomator2 to claim Gemini Advanced offers.

Prerequisites:
  1. Run install_sdk.py (one-time SDK setup)
  2. Run setup_avd.py (one-time AVD creation)
  3. Run emulator_login.py --spoof --accounts (first-time login)
  4. Run emulator_login.py --save (save login snapshot)
  5. Then run this script for automated claiming

Usage:
  python sigmax_emulator.py              # Full auto-claim flow
  python sigmax_emulator.py --check      # Just check for offers (no claim)
  python sigmax_emulator.py --screenshot # Take screenshot of offers page
"""
import subprocess
import time
import sys
import os
import re
import argparse

try:
    import uiautomator2 as u2
    HAS_U2 = True
except ImportError:
    HAS_U2 = False
    print("[!] uiautomator2 not installed. Install with: pip install uiautomator2")

from config import (
    ADB, EMULATOR, AVD_NAME, SNAPSHOT_NAME,
    PIXEL_PROPS, OFFERS_URL, GEMINI_OFFER_URL,
    EMULATOR_BOOT_TIMEOUT, PAGE_LOAD_TIMEOUT, ELEMENT_WAIT_TIMEOUT,
    SCREENSHOT_DIR,
)


class SigmaxEmulator:
    """Android Emulator-based Gemini offer claimer."""
    
    def __init__(self):
        self.device = None
        self.results = []
    
    def connect_device(self):
        """Connect to the running emulator via uiautomator2."""
        if not HAS_U2:
            print("[!] uiautomator2 required! pip install uiautomator2")
            return False
        
        print("[*] Connecting to emulator via uiautomator2...")
        try:
            self.device = u2.connect()
            info = self.device.info
            print(f"  Device: {info.get('productName', 'unknown')}")
            print(f"  Screen: {self.device.window_size()}")
            print(f"  SDK: {info.get('sdkInt', 'unknown')}")
            return True
        except Exception as e:
            print(f"[!] Failed to connect: {e}")
            return False
    
    def is_emulator_running(self):
        """Check if emulator is running."""
        try:
            result = subprocess.run(
                [ADB, "devices"], capture_output=True, text=True, timeout=10
            )
            return "emulator-" in result.stdout
        except:
            return False
    
    def start_emulator(self):
        """Start emulator from saved snapshot."""
        if self.is_emulator_running():
            print("[*] Emulator already running")
            return True
        
        print(f"[*] Starting emulator from snapshot '{SNAPSHOT_NAME}'...")
        cmd = [
            EMULATOR, "-avd", AVD_NAME,
            "-snapshot", SNAPSHOT_NAME,
            "-no-audio", "-no-boot-anim",
            "-writable-system",
        ]
        
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for boot
        start = time.time()
        subprocess.run([ADB, "wait-for-device"], timeout=EMULATOR_BOOT_TIMEOUT)
        
        while time.time() - start < EMULATOR_BOOT_TIMEOUT:
            result = subprocess.run(
                [ADB, "shell", "getprop", "sys.boot_completed"],
                capture_output=True, text=True, timeout=10,
            )
            if result.stdout.strip() == "1":
                elapsed = int(time.time() - start)
                print(f"[✓] Emulator booted in {elapsed}s")
                return True
            time.sleep(2)
        
        print("[✗] Boot timeout!")
        return False
    
    def apply_spoofing(self):
        """Apply Pixel 10 Pro identity spoofing."""
        print("[*] Applying Pixel 10 Pro spoofing...")
        subprocess.run([ADB, "root"], capture_output=True, timeout=10)
        time.sleep(2)
        
        for prop, value in PIXEL_PROPS.items():
            subprocess.run(
                [ADB, "shell", "setprop", prop, value],
                capture_output=True, timeout=10,
            )
        
        # Verify model
        result = subprocess.run(
            [ADB, "shell", "getprop", "ro.product.model"],
            capture_output=True, text=True, timeout=10,
        )
        model = result.stdout.strip()
        print(f"[✓] Device identity: {model}")
    
    def open_offers_page(self):
        """Open Google One offers page in Chrome."""
        print(f"[*] Opening offers page: {OFFERS_URL}")
        subprocess.run(
            [ADB, "shell", "am", "start", "-a", "android.intent.action.VIEW",
             "-d", OFFERS_URL, "com.android.chrome"],
            capture_output=True, timeout=10,
        )
        time.sleep(PAGE_LOAD_TIMEOUT // 2)  # Initial wait for page load
    
    def open_gemini_offer(self):
        """Navigate directly to Gemini offer URL."""
        print(f"[*] Opening Gemini offer: {GEMINI_OFFER_URL}")
        subprocess.run(
            [ADB, "shell", "am", "start", "-a", "android.intent.action.VIEW",
             "-d", GEMINI_OFFER_URL, "com.android.chrome"],
            capture_output=True, timeout=10,
        )
        time.sleep(PAGE_LOAD_TIMEOUT // 2)
    
    def take_screenshot(self, name="offer_check"):
        """Take and save screenshot."""
        timestamp = int(time.time())
        filename = f"{name}_{timestamp}.png"
        remote = f"/sdcard/{filename}"
        local = os.path.join(SCREENSHOT_DIR, filename)
        
        subprocess.run([ADB, "shell", "screencap", "-p", remote], timeout=10)
        subprocess.run([ADB, "pull", remote, local], timeout=10, capture_output=True)
        print(f"[*] Screenshot: {filename}")
        return local
    
    def find_offer_with_u2(self):
        """Use uiautomator2 to find and interact with Gemini offer."""
        if not self.device:
            print("[!] Not connected to device")
            return None
        
        print("[*] Scanning page for Gemini offer...")
        
        # Wait for page to load
        time.sleep(5)
        
        # Search for Gemini-related text on the page
        search_terms = [
            "Gemini Advanced",
            "Gemini",
            "Google One AI Premium",
            "AI Premium",
            "Claim",
            "Activate",
            "Get started",
        ]
        
        for term in search_terms:
            elements = self.device(textContains=term)
            if elements.exists:
                count = elements.count
                print(f"  Found '{term}' ({count} elements)")
                
                # Click the first matching element
                try:
                    elements[0].click()
                    print(f"  [✓] Clicked '{term}'")
                    time.sleep(3)
                    return term
                except Exception as e:
                    print(f"  [!] Click failed: {e}")
        
        # Also try by content-description
        for term in search_terms:
            elements = self.device(descriptionContains=term)
            if elements.exists:
                print(f"  Found by description: '{term}'")
                try:
                    elements[0].click()
                    print(f"  [✓] Clicked '{term}' (by description)")
                    time.sleep(3)
                    return term
                except Exception as e:
                    print(f"  [!] Click failed: {e}")
        
        print("  [!] No Gemini offer found on page")
        return None
    
    def extract_offer_url_from_chrome(self):
        """Extract the current URL from Chrome."""
        if not self.device:
            return None
        
        # Try to get URL from Chrome address bar
        url_bar = self.device(resourceId="com.android.chrome:id/url_bar")
        if url_bar.exists:
            url = url_bar.get_text()
            print(f"  Current URL: {url}")
            return url
        
        # Alternative: try getting URL via ADB
        result = subprocess.run(
            [ADB, "shell", "dumpsys", "activity", "activities"],
            capture_output=True, text=True, timeout=10,
        )
        
        # Search for partner-eft-onboard URL
        match = re.search(r'(https?://[^\s]*partner-eft-onboard[^\s]*)', result.stdout)
        if match:
            url = match.group(1)
            print(f"  Found offer URL: {url}")
            return url
        
        return None
    
    def find_offer_with_adb(self):
        """Fallback: use ADB-based page source inspection."""
        print("[*] Scanning with ADB dumpsys...")
        
        result = subprocess.run(
            [ADB, "shell", "dumpsys", "activity", "top"],
            capture_output=True, text=True, timeout=15,
        )
        
        output = result.stdout
        
        # Look for Gemini-related content
        gemini_indicators = ["gemini", "ai premium", "partner-eft-onboard"]
        found = []
        for indicator in gemini_indicators:
            if indicator.lower() in output.lower():
                found.append(indicator)
        
        if found:
            print(f"  Found indicators: {', '.join(found)}")
            return found
        
        return None
    
    def scroll_and_search(self):
        """Scroll the page and search for offers."""
        if not self.device:
            return None
        
        print("[*] Scrolling page to find offers...")
        
        for i in range(5):  # Scroll up to 5 times
            print(f"  Scroll {i+1}/5...")
            self.device.swipe_ext("up", scale=0.5)
            time.sleep(2)
            
            found = self.find_offer_with_u2()
            if found:
                return found
        
        return None
    
    def claim_offer_flow(self):
        """Full offer claim flow."""
        print("\n" + "=" * 60)
        print("  Starting Gemini Offer Claim Flow")
        print("=" * 60 + "\n")
        
        # Step 1: Open offers page
        self.open_offers_page()
        self.take_screenshot("offers_page")
        
        # Step 2: Try direct Gemini offer URL first
        self.open_gemini_offer()
        time.sleep(5)
        self.take_screenshot("gemini_offer")
        
        # Step 3: Try to find and click offer
        if HAS_U2 and self.device:
            found = self.find_offer_with_u2()
            if not found:
                found = self.scroll_and_search()
            
            if found:
                self.take_screenshot("offer_clicked")
                
                # Step 4: Try to extract the offer URL
                time.sleep(5)
                url = self.extract_offer_url_from_chrome()
                if url:
                    self.take_screenshot("offer_url")
                    return {
                        "status": "success",
                        "offer": found,
                        "url": url,
                    }
                else:
                    return {
                        "status": "partial",
                        "offer": found,
                        "message": "Offer found but URL not extracted",
                    }
        
        # Fallback: ADB inspection
        indicators = self.find_offer_with_adb()
        self.take_screenshot("final_state")
        
        if indicators:
            return {
                "status": "detected",
                "indicators": indicators,
                "message": "Gemini content detected, manual check needed",
            }
        
        return {
            "status": "not_found",
            "message": "No Gemini offer found",
        }
    
    def run(self, check_only=False, screenshot_only=False):
        """Main execution flow."""
        print("=" * 60)
        print("  Sigmax Emulator - Gemini Offer Claimer")
        print("=" * 60)
        print()
        
        # Step 1: Start emulator
        if not self.start_emulator():
            print("[!] Cannot start emulator. Exiting.")
            return
        
        # Step 2: Apply spoofing
        self.apply_spoofing()
        
        # Step 3: Connect uiautomator2
        if HAS_U2:
            self.connect_device()
        
        if screenshot_only:
            self.open_offers_page()
            time.sleep(10)
            self.take_screenshot("offers_check")
            print("[✓] Screenshot taken. Check the offers page manually.")
            return
        
        if check_only:
            self.open_offers_page()
            time.sleep(10)
            self.take_screenshot("offers_check")
            if HAS_U2 and self.device:
                self.find_offer_with_u2()
            else:
                self.find_offer_with_adb()
            return
        
        # Full claim flow
        result = self.claim_offer_flow()
        
        print("\n" + "=" * 60)
        print("  Results")
        print("=" * 60)
        for key, val in result.items():
            print(f"  {key}: {val}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Sigmax Emulator - Gemini Offer Claimer")
    parser.add_argument("--check", action="store_true", help="Only check for offers, don't claim")
    parser.add_argument("--screenshot", action="store_true", help="Just take a screenshot")
    args = parser.parse_args()
    
    claimer = SigmaxEmulator()
    claimer.run(check_only=args.check, screenshot_only=args.screenshot)


if __name__ == "__main__":
    main()
