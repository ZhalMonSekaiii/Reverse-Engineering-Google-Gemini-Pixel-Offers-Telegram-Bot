import json
import subprocess
import time

pif_data = {
  "MANUFACTURER": "Google",
  "MODEL": "Pixel 9 Pro XL",
  "FINGERPRINT": "google/komodo/komodo:14/AD1A.240530.047.U1/12108848:user/release-keys",
  "BRAND": "google",
  "PRODUCT": "komodo",
  "DEVICE": "komodo",
  "RELEASE": "14",
  "ID": "AD1A.240530.047.U1",
  "INCREMENTAL": "12108848",
  "TYPE": "user",
  "TAGS": "release-keys",
  "SECURITY_PATCH": "2024-08-05"
}

with open("custom.pif.json", "w") as f:
    json.dump(pif_data, f, indent=2)

subprocess.run(["C:\\AndroidSDK\\platform-tools\\adb.exe", "push", "custom.pif.json", "/sdcard/Download/"])
subprocess.run(["C:\\AndroidSDK\\platform-tools\\adb.exe", "shell", "su", "-c", "cp /sdcard/Download/custom.pif.json /data/adb/pif.json"])
print("Fingerprint updated to Pixel 9 Pro XL!")

print("Stopping Google Services to apply changes...")
subprocess.run(["C:\\AndroidSDK\\platform-tools\\adb.exe", "shell", "am", "force-stop", "com.google.android.gms"])
subprocess.run(["C:\\AndroidSDK\\platform-tools\\adb.exe", "shell", "am", "force-stop", "com.android.vending"])
subprocess.run(["C:\\AndroidSDK\\platform-tools\\adb.exe", "shell", "pm", "clear", "com.google.android.apps.subscriptions.red"])
print("Google One data cleared!")
