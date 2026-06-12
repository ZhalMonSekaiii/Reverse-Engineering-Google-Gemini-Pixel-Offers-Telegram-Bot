"""
Sigmax - AVD Setup Script
Creates and configures the Android Virtual Device with Pixel 10 Pro profile.
Run this AFTER install_sdk.py has completed successfully.
"""
import subprocess
import os
import sys
import configparser

from config import (
    SDK_ROOT, ADB, EMULATOR, AVDMANAGER, SDKMANAGER,
    AVD_NAME, SYSTEM_IMAGE, AVD_CONFIG, PIXEL_PROPS,
)


def run_cmd(cmd, check=True, timeout=60):
    """Run a command and return result."""
    print(f"  $ {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, shell=isinstance(cmd, str)
    )
    if result.stdout.strip():
        print(f"    {result.stdout.strip()[:200]}")
    if result.returncode != 0 and check:
        print(f"  [ERROR] {result.stderr.strip()[:300]}")
    return result


def check_prerequisites():
    """Verify SDK components are installed."""
    print("[1/5] Checking prerequisites...")
    
    checks = {
        "platform-tools": os.path.exists(ADB),
        "emulator": os.path.exists(EMULATOR),
        "system-image": os.path.exists(
            os.path.join(SDK_ROOT, "system-images", "android-35", 
                        "google_apis_playstore", "x86_64", "system.img")
        ),
        "platforms": os.path.exists(
            os.path.join(SDK_ROOT, "platforms", "android-35")
        ),
    }
    
    all_ok = True
    for name, ok in checks.items():
        status = "✓" if ok else "✗"
        print(f"  [{status}] {name}")
        if not ok:
            all_ok = False
    
    if not all_ok:
        print("\n[!] Missing components. Run install_sdk.py first!")
        sys.exit(1)
    
    print("  All prerequisites met!\n")


def delete_existing_avd():
    """Delete existing AVD if it exists."""
    result = run_cmd([AVDMANAGER, "list", "avd"], check=False)
    if AVD_NAME in (result.stdout or ""):
        print(f"  Deleting existing AVD '{AVD_NAME}'...")
        run_cmd([AVDMANAGER, "delete", "avd", "-n", AVD_NAME], check=False)


def create_avd():
    """Create the AVD with Pixel profile."""
    print(f"[2/5] Creating AVD '{AVD_NAME}'...")
    
    delete_existing_avd()
    
    # Create AVD - use 'no' to avoid custom hardware profile prompt
    cmd = [
        AVDMANAGER, "create", "avd",
        "-n", AVD_NAME,
        "-k", SYSTEM_IMAGE,
        "-d", "pixel_7_pro",  # Closest available device definition to Pixel 10 Pro
        "--force",
    ]
    
    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, text=True
    )
    out, _ = proc.communicate(input="no\n")
    print(f"  {out.strip()}")
    
    if proc.returncode != 0:
        print("[!] Failed to create AVD!")
        sys.exit(1)
    
    print(f"  AVD '{AVD_NAME}' created successfully!\n")


def get_avd_dir():
    """Get the AVD directory path."""
    avd_home = os.path.join(os.path.expanduser("~"), ".android", "avd")
    return os.path.join(avd_home, f"{AVD_NAME}.avd")


def configure_avd_hardware():
    """Configure AVD hardware settings."""
    print("[3/5] Configuring AVD hardware...")
    
    avd_dir = get_avd_dir()
    config_file = os.path.join(avd_dir, "config.ini")
    
    if not os.path.exists(config_file):
        print(f"  [!] Config not found: {config_file}")
        return
    
    # Read existing config
    with open(config_file, "r") as f:
        lines = f.readlines()
    
    # Parse into dict
    config = {}
    for line in lines:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()
    
    # Apply our settings
    for key, val in AVD_CONFIG.items():
        config[key] = val
    
    # Write back
    with open(config_file, "w") as f:
        for key, val in config.items():
            f.write(f"{key} = {val}\n")
    
    print(f"  Updated {len(AVD_CONFIG)} hardware settings")
    print(f"  Config: {config_file}\n")


def setup_pixel_spoofing():
    """Prepare Pixel 10 Pro spoofing script for runtime."""
    print("[4/5] Preparing Pixel 10 Pro device spoofing...")
    
    # Create a shell script that will run on emulator boot
    spoof_script = os.path.join(os.path.dirname(__file__), "spoof_pixel.sh")
    
    lines = ["#!/system/bin/sh", "# Pixel 10 Pro Device Spoofing"]
    for prop, value in PIXEL_PROPS.items():
        lines.append(f'setprop {prop} "{value}"')
    
    with open(spoof_script, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    
    print(f"  Created spoof script: {spoof_script}")
    print(f"  Contains {len(PIXEL_PROPS)} device properties to spoof")
    print("  Will be pushed to emulator at runtime\n")


def verify_avd():
    """Verify the AVD was created correctly."""
    print("[5/5] Verifying AVD...")
    
    result = run_cmd([AVDMANAGER, "list", "avd"])
    
    if AVD_NAME in (result.stdout or ""):
        print(f"\n{'='*60}")
        print(f"  ✅ AVD '{AVD_NAME}' ready!")
        print(f"  Next step: Run emulator_login.py to start emulator")
        print(f"{'='*60}")
    else:
        print(f"\n  [!] AVD '{AVD_NAME}' not found in list!")


if __name__ == "__main__":
    print("=" * 60)
    print("  Sigmax - AVD Setup")
    print("=" * 60)
    print()
    
    check_prerequisites()
    create_avd()
    configure_avd_hardware()
    setup_pixel_spoofing()
    verify_avd()
