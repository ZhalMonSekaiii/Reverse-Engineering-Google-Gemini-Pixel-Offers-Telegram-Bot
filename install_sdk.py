"""
Android SDK Component Installer
Installs platforms;android-35 and system-images with proper license acceptance.
"""
import subprocess
import sys
import os
import time

SDK_ROOT = r"C:\AndroidSDK"
SDKMANAGER = os.path.join(SDK_ROOT, "cmdline-tools", "latest", "bin", "sdkmanager.bat")

PACKAGES = [
    "platforms;android-35",
    "system-images;android-35;google_apis_playstore;x86_64",
]

def run_sdk_install(packages):
    """Install SDK packages with auto-license acceptance."""
    cmd = [SDKMANAGER, f"--sdk_root={SDK_ROOT}"] + packages
    print(f"[*] Running: {' '.join(cmd)}")
    print(f"[*] This may take 5-15 minutes for system image download (~2 GB)...")
    print()
    
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    
    output_lines = []
    while True:
        line = proc.stdout.readline()
        if not line and proc.poll() is not None:
            break
        if line:
            line = line.rstrip()
            output_lines.append(line)
            print(line, flush=True)
            # Auto-accept licenses
            if "Accept?" in line or "y/N" in line or "(y/N)" in line:
                proc.stdin.write("y\n")
                proc.stdin.flush()
                print("  >> Auto-accepted license")
    
    rc = proc.wait()
    return rc, output_lines

def accept_licenses():
    """Accept all SDK licenses first."""
    print("[*] Accepting all SDK licenses...")
    cmd = [SDKMANAGER, f"--sdk_root={SDK_ROOT}", "--licenses"]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    # Send many y's to accept all
    try:
        out, _ = proc.communicate(input="y\ny\ny\ny\ny\ny\ny\ny\ny\ny\n", timeout=60)
        print(out)
    except subprocess.TimeoutExpired:
        proc.kill()
        print("[!] License acceptance timed out, continuing anyway...")

def verify_installation():
    """Verify installed packages."""
    print("\n[*] Verifying installation...")
    cmd = [SDKMANAGER, f"--sdk_root={SDK_ROOT}", "--list_installed"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

if __name__ == "__main__":
    print("=" * 60)
    print("  Android SDK Component Installer")
    print("=" * 60)
    print()
    
    # Step 1: Accept licenses
    accept_licenses()
    
    # Step 2: Install packages
    print("\n" + "=" * 60)
    print(f"  Installing: {', '.join(PACKAGES)}")
    print("=" * 60)
    print()
    
    rc, output = run_sdk_install(PACKAGES)
    
    if rc == 0:
        print("\n[✓] Installation completed successfully!")
    else:
        print(f"\n[✗] Installation failed with code {rc}")
        # Try installing one at a time
        print("[*] Retrying packages individually...")
        for pkg in PACKAGES:
            print(f"\n[*] Installing {pkg}...")
            rc2, _ = run_sdk_install([pkg])
            if rc2 == 0:
                print(f"[✓] {pkg} installed successfully!")
            else:
                print(f"[✗] {pkg} failed!")
    
    # Step 3: Verify
    verify_installation()
