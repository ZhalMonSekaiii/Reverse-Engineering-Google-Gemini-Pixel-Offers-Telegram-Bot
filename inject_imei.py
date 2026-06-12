import random
import telnetlib
import os

def calculate_luhn(imei_base):
    """Calculates the Luhn checksum digit for a 14-digit IMEI base."""
    digits = [int(c) for c in imei_base]
    for i in range(1, 14, 2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    total = sum(digits)
    return (10 - (total % 10)) % 10

def generate_pixel_9_pro_xl_imei():
    """Generates a random valid IMEI for Pixel 9 Pro XL (TAC: 35158285)."""
    tac = "35158285"
    serial = f"{random.randint(0, 999999):06d}"
    base = tac + serial
    checksum = calculate_luhn(base)
    return base + str(checksum)

def inject_imei_to_emulator(imei):
    print(f"[*] Trying to inject IMEI {imei} into emulator-5554...")
    try:
        auth_file = os.path.expanduser("~/.emulator_console_auth_token")
        with open(auth_file, "r") as f:
            auth_token = f.read().strip()
            
        tn = telnetlib.Telnet("localhost", 5554, timeout=5)
        tn.read_until(b"OK", timeout=2)
        
        # Authenticate
        tn.write(f"auth {auth_token}\n".encode('ascii'))
        tn.read_until(b"OK", timeout=2)
        
        # Set IMEI
        tn.write(f"gsm imei {imei}\n".encode('ascii'))
        tn.read_until(b"OK", timeout=2)
        
        tn.close()
        print("[+] Successfully injected IMEI to the live emulator!")
    except Exception as e:
        print(f"[-] Failed to inject IMEI via telnet: {e}")

if __name__ == "__main__":
    print("==================================================")
    print(" Pixel 9 Pro XL IMEI Generator & Emulator Checker")
    print("==================================================")
    
    new_imei = generate_pixel_9_pro_xl_imei()
    print(f"\n[>] Generated Valid IMEI: {new_imei}")
    
    print("\n[i] Injecting to running emulator...")
    inject_imei_to_emulator(new_imei)
    
    print("\n[!] CARA CEK (CHECKER):")
    print("1. Buka aplikasi Google One di emulator.")
    print("2. Tutup paksa (Force Stop) lalu buka lagi jika perlu.")
    print("3. Cek apakah offer muncul.")
    print("4. Jika belum, jalankan script ini lagi untuk mencoba IMEI baru!")
    print("==================================================")
