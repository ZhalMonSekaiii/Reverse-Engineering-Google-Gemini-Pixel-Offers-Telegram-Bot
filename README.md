# 🕵️‍♂️ Reverse Engineering Google Gemini Pixel Offers

> [!WARNING]
> **DISCLAIMER: EDUCATIONAL PURPOSES ONLY**
> This repository is a Proof of Concept (PoC) documenting a reverse engineering experiment. This project is **NO LONGER MAINTAINED** and is archived. The methods described here may be patched by Google and will not work. Do not use this for malicious purposes.

## 📝 Overview
This repository contains scripts and documentation from an experiment attempting to automate and bypass Google's hardware verification for the Gemini Advanced Pixel 9 Pro promotion.

We explored two primary methods:
1. **Browser Automation:** Using Playwright and Stealth plugins to bypass browser-fingerprinting (Failed due to advanced React/ReCaptcha behavioral analysis).
2. **OS-Level Spoofing:** Downgrading an Android Emulator (API 33), patching Ramdisk via Magisk, and spoofing the OS Identity to a `Pixel 9 Pro XL` using PlayIntegrityFix.
3. **Hardware Spoofing:** Live injecting a Luhn-generated IMEI into the virtual modem via Telnet.

### 🏗️ Experiment Workflow Architecture
```mermaid
flowchart TD
    A[Start: Claim Attempt] --> B{Choose Method}
    B -->|Phase 1| C[Browser Automation / Playwright]
    C --> D[Modify User-Agent & Stealth Plugins]
    D --> E[ReCaptcha & React Behavioral Checks]
    E -->|Detected| F[Blocked by Google Anti-Bot]

    B -->|Phase 2 & 3| G[OS-Level Spoofing]
    G --> H[Android Emulator API 33]
    H --> I[rootAVD: Patch Ramdisk.img]
    I --> J[Install Magisk & Zygisk]
    J --> K[PlayIntegrityFix Module]
    K --> L[Spoof Fingerprint to Pixel 9 Pro XL]
    L --> M[Bypass Play Integrity & OS Checks]
    M --> N[Google One App - Request Offer]
    
    N --> O{Google Server Hardware Verification}
    O -->|Missing/Generic IMEI| P[Inject Random IMEI via Telnet]
    P --> N
    O -->|Check IMEI against Sales Database| Q{Does IMEI match a sold Pixel 9 Pro?}
    Q -->|No Match| R[Server Response: Offer Not Available]
    
    classDef success fill:#28a745,stroke:#fff,stroke-width:2px,color:#fff;
    classDef fail fill:#dc3545,stroke:#fff,stroke-width:2px,color:#fff;
    classDef spoof fill:#17a2b8,stroke:#fff,stroke-width:2px,color:#fff;
    
    M:::success
    F:::fail
    R:::fail
    K:::spoof
    P:::spoof
```

## 🛑 Why it failed (The Final Boss)
Despite fully spoofing the OS fingerprint and Play Integrity, Google's server-side verification checks the device's hardware identifiers (IMEI & Serial Number) against their **factory production and sales database**. 

Unless a valid, newly manufactured, and unsold Pixel 9 Pro IMEI is injected, the server will correctly reject the claim.

## 📚 Technical Learnings
- Playwright Stealth implementations
- Android API downgrades & AVD Ramdisk Kernel Patching
- Magisk / Zygisk root implementations
- Play Integrity API spoofing
- Live Modem RIL (Radio Interface Layer) Telnet manipulation

---
*Created for educational reverse-engineering purposes. Not intended for commercial use or exploitation.*
