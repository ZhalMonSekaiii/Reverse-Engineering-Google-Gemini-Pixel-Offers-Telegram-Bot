import os
import subprocess

script = """#!/system/bin/sh
# Magisk post-fs-data.d script to spoof Pixel 10 Pro

resetprop ro.product.model "Pixel 10 Pro"
resetprop ro.product.brand "google"
resetprop ro.product.name "google_pixel_10_pro"
resetprop ro.product.device "google_pixel_10_pro"
resetprop ro.product.manufacturer "Google"
resetprop ro.board.platform "google_pixel_10_pro"
resetprop ro.build.product "google_pixel_10_pro"
resetprop ro.build.fingerprint "google/google_pixel_10_pro/google_pixel_10_pro:15/AP3A.241005.015/12345678:user/release-keys"
# Hide emulator traits disabled to prevent black screen
resetprop ro.boot.hardware "google_pixel_10_pro"
resetprop ro.boot.serialno "1234567890ABCDEF"
"""

# Write with explicit UNIX line endings
with open("spoof_magisk_unix.sh", "w", newline="\n") as f:
    f.write(script)

print("Created spoof_magisk_unix.sh with UNIX line endings.")
