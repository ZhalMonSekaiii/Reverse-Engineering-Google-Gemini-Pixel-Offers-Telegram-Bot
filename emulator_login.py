"""
Sigmax - Emulator Login Manager
Starts the emulator, applies Pixel spoofing, and manages login snapshots.

Usage:
  python emulator_login.py           # Start emulator for manual login
  python emulator_login.py --spoof   # Start + apply Pixel spoofing
  python emulator_login.py --save    # Save snapshot after login
  python emulator_login.py --load    # Load saved snapshot (auto mode)
"""
import subprocess
import time
import sys
import os
import argparse

from config import (
    SDK_ROOT, ADB, EMULATOR, AVD_NAME, SNAPSHOT_NAME,
    PIXEL_PROPS, EMULATOR_BOOT_TIMEOUT,
)


def is_emulator_running():
    """Check if emulator is already running."""
    try:
        result = subprocess.run(
            [ADB, "devices"], capture_output=True, text=True, timeout=10
        )
        return "emulator-" in result.stdout
    except Exception:
        return False


def wait_for_boot(timeout=EMULATOR_BOOT_TIMEOUT):
    """Wait until emulator is fully booted."""
    print("[*] Waiting for emulator to boot...")
    start = time.time()
    
    # First wait for device to appear
    subprocess.run([ADB, "wait-for-device"], timeout=timeout)
    
    while time.time() - start < timeout:
        result = subprocess.run(
            [ADB, "shell", "getprop", "sys.boot_completed"],
            capture_output=True, text=True, timeout=10,
        )
        if result.stdout.strip() == "1":
            elapsed = int(time.time() - start)
            print(f"[OK] Emulator booted in {elapsed}s")
            return True
        time.sleep(2)
        remaining = int(timeout - (time.time() - start))
        print(f"  Still booting... ({remaining}s remaining)")
    
    print("[FAIL] Boot timeout!")
    return False


def start_emulator(snapshot=None, writable_system=True):
    """Start the emulator."""
    if is_emulator_running():
        print("[*] Emulator already running")
        return True
    
    cmd = [EMULATOR, "-avd", AVD_NAME, "-no-audio", "-no-boot-anim", "-gpu", "host"]
    
    if writable_system:
        pass # Disabling writable-system as it causes boot loops with Magisk on Play Store images
        

    if snapshot:
        cmd.extend(["-snapshot", snapshot])
        print(f"[*] Starting emulator from snapshot '{snapshot}'...")
    else:
        cmd.append("-no-snapshot-load")
        print(f"[*] Starting emulator (fresh boot)...")
    
    # Start emulator in background
    proc = subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    
    return wait_for_boot()


def apply_pixel_spoofing():
    """Apply Pixel 10 Pro device properties."""
    print("\n[*] Applying Pixel 10 Pro spoofing...")
    
    # Need root access to modify system props
    subprocess.run([ADB, "root"], capture_output=True, timeout=10)
    time.sleep(2)
    
    success = 0
    failed = 0
    
    for prop, value in PIXEL_PROPS.items():
        result = subprocess.run(
            [ADB, "shell", "setprop", prop, value],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            success += 1
        else:
            failed += 1
            print(f"  [!] Failed: {prop}")
    
    print(f"[OK] Spoofing applied: {success} success, {failed} failed")
    
    # Verify key props
    print("\n[*] Verifying identity:")
    for prop in ["ro.product.model", "ro.product.brand", "ro.product.device", "ro.build.fingerprint"]:
        result = subprocess.run(
            [ADB, "shell", "getprop", prop],
            capture_output=True, text=True, timeout=10,
        )
        print(f"  {prop} = {result.stdout.strip()}")


def save_snapshot(name=SNAPSHOT_NAME):
    """Save emulator snapshot."""
    print(f"\n[*] Saving snapshot '{name}'...")
    result = subprocess.run(
        [ADB, "emu", "avd", "snapshot", "save", name],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode == 0:
        print(f"[OK] Snapshot '{name}' saved!")
    else:
        print(f"[FAIL] Failed to save snapshot: {result.stderr.strip()}")


def open_chrome(url=None):
    """Open Chrome browser, optionally navigate to URL."""
    if url:
        print(f"\n[*] Opening Chrome → {url}")
        subprocess.run(
            [ADB, "shell", "am", "start", "-a", "android.intent.action.VIEW",
             "-d", url, "com.android.chrome"],
            capture_output=True, timeout=10,
        )
    else:
        print("\n[*] Opening Chrome...")
        subprocess.run(
            [ADB, "shell", "am", "start", "com.android.chrome"],
            capture_output=True, timeout=10,
        )


def open_settings_accounts():
    """Open Google Account settings for manual login."""
    print("\n[*] Opening Settings -> Accounts...")
    subprocess.run(
        [ADB, "shell", "am", "start", "-a", "android.settings.ADD_ACCOUNT_SETTINGS"],
        capture_output=True, timeout=10,
    )
    print("  -> Please add your Google account manually in the emulator window")
    print("  -> After login, run: python emulator_login.py --save")


def take_screenshot(filename="emulator_screenshot.png"):
    """Take a screenshot from the emulator."""
    remote_path = f"/sdcard/{filename}"
    local_path = os.path.join(os.path.dirname(__file__), filename)
    
    subprocess.run([ADB, "shell", "screencap", "-p", remote_path], timeout=10)
    subprocess.run([ADB, "pull", remote_path, local_path], timeout=10)
    print(f"[*] Screenshot saved: {local_path}")
    return local_path


def main():
    parser = argparse.ArgumentParser(description="Sigmax Emulator Login Manager")
    parser.add_argument("--spoof", action="store_true", help="Apply Pixel 10 Pro spoofing")
    parser.add_argument("--save", action="store_true", help="Save login snapshot")
    parser.add_argument("--load", action="store_true", help="Load saved snapshot")
    parser.add_argument("--screenshot", action="store_true", help="Take screenshot")
    parser.add_argument("--accounts", action="store_true", help="Open accounts settings")
    parser.add_argument("--chrome", type=str, nargs="?", const="", help="Open Chrome [optional URL]")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Sigmax - Emulator Login Manager")
    print("=" * 60)
    print()
    
    if args.save:
        # Just save snapshot (emulator must be running)
        if not is_emulator_running():
            print("[!] Emulator not running!")
            return
        save_snapshot()
        return
    
    if args.screenshot:
        if not is_emulator_running():
            print("[!] Emulator not running!")
            return
        take_screenshot()
        return
    
    # Start emulator
    snapshot = SNAPSHOT_NAME if args.load else None
    if not start_emulator(snapshot=snapshot):
        print("[!] Failed to start emulator")
        return
    
    # Verify identity via OS level
    print("\n[*] Verifying OS-level identity (Magisk Spoofed):")
    for prop in ["ro.product.model", "ro.product.brand", "ro.product.device", "ro.build.fingerprint"]:
        result = subprocess.run(
            [ADB, "shell", "getprop", prop],
            capture_output=True, text=True, timeout=10,
        )
        print(f"  {prop} = {result.stdout.strip()}")
    
    # Open accounts or Chrome
    if args.accounts:
        open_settings_accounts()
    elif args.chrome is not None:
        url = args.chrome if args.chrome else None
        open_chrome(url)
    else:
        # Default: open account settings for first-time login
        if not args.load:
            open_settings_accounts()
    
    print("\n[*] Emulator is running. Use Ctrl+C to exit (emulator stays open)")


if __name__ == "__main__":
    main()
