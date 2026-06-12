import urllib.request
import json
import os
import subprocess
import time

PIF_URL = "https://github.com/KOWX712/PlayIntegrityFix/releases/download/v4.5-inject-s/PlayIntegrityFix_v4.5-inject-s.zip"
MAGISK_URL = "https://github.com/topjohnwu/Magisk/releases/download/v26.4/Magisk-v26.4.apk"

print("Downloading PlayIntegrityFix...")
urllib.request.urlretrieve(PIF_URL, "PlayIntegrityFix.zip")

print("Downloading Magisk...")
urllib.request.urlretrieve(MAGISK_URL, "Magisk.apk")

pif_data = {
  "MANUFACTURER": "Google",
  "MODEL": "Pixel 10 Pro",
  "FINGERPRINT": "google/google_pixel_10_pro/google_pixel_10_pro:15/AP3A.241005.015/12345678:user/release-keys",
  "BRAND": "google",
  "PRODUCT": "google_pixel_10_pro",
  "DEVICE": "google_pixel_10_pro",
  "RELEASE": "15",
  "ID": "AP3A.241005.015",
  "INCREMENTAL": "12345678",
  "TYPE": "user",
  "TAGS": "release-keys",
  "SECURITY_PATCH": "2024-10-05"
}

with open("custom.pif.json", "w") as f:
    json.dump(pif_data, f, indent=2)

print("Generated custom.pif.json")

print("Waiting for ADB device...")
subprocess.run(["C:\\AndroidSDK\\platform-tools\\adb.exe", "wait-for-device"])

# Wait a bit for boot complete
print("Waiting for boot to finish...")
time.sleep(15)

print("Installing Magisk...")
subprocess.run(["C:\\AndroidSDK\\platform-tools\\adb.exe", "install", "Magisk.apk"])

print("Pushing PIF and config...")
subprocess.run(["C:\\AndroidSDK\\platform-tools\\adb.exe", "push", "PlayIntegrityFix.zip", "/sdcard/Download/"])
subprocess.run(["C:\\AndroidSDK\\platform-tools\\adb.exe", "push", "custom.pif.json", "/sdcard/Download/"])

print("Done! Files are ready on device.")
