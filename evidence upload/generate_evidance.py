import os
import random
import struct

# Configuration
EVIDENCE_DIR = "evidence_locker"

def create_folder():
    if not os.path.exists(EVIDENCE_DIR):
        os.makedirs(EVIDENCE_DIR)
        print(f"[+] Created directory: {EVIDENCE_DIR}")

def create_safe_files():
    """Creates normal text and log files."""
    print("[*] Generating safe files...")
    
    # 1. Normal Text File
    with open(f"{EVIDENCE_DIR}/meeting_notes.txt", "w") as f:
        f.write("Team meeting at 10 AM. Discuss Q4 goals.")

    # 2. System Log (Clean)
    with open(f"{EVIDENCE_DIR}/system.log", "w") as f:
        f.write("2023-10-27 08:00:00 Service started.\n2023-10-27 08:05:00 Update check complete.")

def create_keyword_threats():
    """Creates files with suspicious keywords to trigger the Keyword Scanner."""
    print("[*] Generating keyword threats...")
    
    # 1. Passwords File
    with open(f"{EVIDENCE_DIR}/credentials.txt", "w") as f:
        f.write("SERVER_ADMIN: admin\nPASSWORD: SuperSecretPassword123!")

    # 2. Hidden Config
    with open(f"{EVIDENCE_DIR}/config.ini", "w") as f:
        f.write("[DATABASE]\nhost=localhost\nuser=root\nsecret_key=8492842")

def create_high_entropy_files():
    """Creates files with random data to trigger 'High Entropy' (Packed/Encrypted) detection."""
    print("[*] Generating high-entropy (encrypted/packed) files...")
    
    # 1. Random Binary Blob (High Entropy)
    with open(f"{EVIDENCE_DIR}/suspicious_blob.bin", "wb") as f:
        f.write(os.urandom(2048)) # 2KB of random noise

def create_fake_malware():
    """Creates files with executable extensions."""
    print("[*] Generating fake malware signatures...")
    
    # 1. Fake Exe
    with open(f"{EVIDENCE_DIR}/payload.exe", "wb") as f:
        f.write(b"MZ" + os.urandom(500)) # MZ header + random junk

    # 2. Fake Script
    with open(f"{EVIDENCE_DIR}/hack.bat", "w") as f:
        f.write("@echo off\ndel C:\\Windows\\System32")

def create_carvable_files():
    """Creates binary files with hidden headers to test File Carving."""
    print("[*] Generating carvable artifacts...")
    
    # 1. Corrupted file with hidden JPG header (FF D8 FF)
    with open(f"{EVIDENCE_DIR}/corrupted_disk.img", "wb") as f:
        # Junk + JPG Header + Junk
        data = os.urandom(100) + b'\xFF\xD8\xFF' + os.urandom(500)
        f.write(data)

    # 2. Corrupted file with hidden PDF header (%PDF-)
    with open(f"{EVIDENCE_DIR}/swap_memory.dmp", "wb") as f:
        data = os.urandom(50) + b'%PDF-1.4' + os.urandom(200)
        f.write(data)

if __name__ == "__main__":
    create_folder()
    create_safe_files()
    create_keyword_threats()
    create_high_entropy_files()
    create_fake_malware()
    create_carvable_files()
    print(f"\n[SUCCESS] Evidence Locker created at: {os.path.abspath(EVIDENCE_DIR)}")
    print("You can now run ShadowTrace and point it to this folder!")