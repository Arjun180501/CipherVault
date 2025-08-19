# CipherVault
COMP702 Final Dessertation

**CipherVault** is a modern, open-source standalone password manager built for advanced security, flexibility, and usability. It empowers users to store, generate, and manage passwords securely while offering strong multi-factor authentication and configurable encryption.  It offers a customizable GUI interface with user-configurable feature toggles,
allowing users to enable/disable or adjust specific functionality based on their security requirements
and usage preferences, and a command-line companion tool, making it accessible to both everyday
users and advanced technical professionals.

## Architecture Diagram

<img width="1000" height="600" alt="image" src="https://github.com/user-attachments/assets/dcbdda56-1383-4e24-b6d1-6c000ba42c36" />


## Architecture Overview

**Backend:**  
- Python 3.9+, encrypted SQLite storage  
- [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2) and [HKDF](https://en.wikipedia.org/wiki/HKDF) for key derivation with per-vault cryptographic salt  
- Encryption: AES-256-GCM, ChaCha20-Poly1305, Hybrid (Auto-select)

**Frontend:**  
- PyQt6 GUI with modular, professional workflow  
- CLI companion tool (`cvault`) for headless/server integrations

**Authentication:**  
- Master password  
- TOTP (RFC6238 standard, third-party auth app-friendly setup with QR and recovery codes)

**Security Toggles & Settings:**  
- Breach check enable/disable  
- Encryption algorithm selection
- Session and clipboard timeouts
- Recommended defaults and inline explanations for all settings


## Features

- **Configurable Encrypted SQLite Database:**  
  Client-side encryption using SQLCipher (wrapper) + SqLite DB. Users can choose from ChaCha20-Poly1305, AES-256-GCM, or        Hybrid (auto-select) data encryption mechanisms. The vault DB file along with salt file for new vaults needs to be stored     in a centralized vaults/ folder beside the exe files(GUI & CLI) in disk after installation.
  
  Please find documentation for the encryption algorithms below -
  
  **AES-GCM**
  https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Galois/counter_(GCM)

  **ChaCha20-Poly1305**
  https://en.wikipedia.org/wiki/ChaCha20-Poly1305
  
  Note: Hybrid mechanism recommended for usage if unsure as it picks the best algorithm based on device capabilities.
  
- **TOTP-based Multi-Factor Authentication:**  
  Two-factor authentication (OTP-based 2FA) can be enabled for additional security and registered with any 3rd party            authentication apps like Google authenticator, Microsoft authenticator etc.
  
- **Password Generator (Auto/Custom)**  
  Create strong, random passwords with customizable length and character sets. Users can either use auto generate option for    random generation of passwords or make use of custom configurations for generating strong passwords based on requirements     (Example - include/exclude [digits, capital letters])

- **Password Strength Meter**  
  Users can visualize real-time entropy-based strength and get feedback for weak passwords(powered by zxcvbn library).

- **Breach Detection:**  
  Users can check for password breaches either automatically on-login/after password updates/manually(one-click) against the    Have I Been Pwned database using a privacy-respecting k-anonymity model (To ensure whole passwords are not exposed to the     HIBP API).
  
- **Session Timeout & Clipboard Auto-Clear:**  
  Enhanced security with inactivity logout and secure clipboard management for passwords based on user-configurable timeout     settings.
  
- **User Customizable UI**:  
  Enable/disable features like TOTP (MFA), auto-breach check, clipboard timeout, and encryption method switch using user-       configurable toggles in settings.
  
- **Intuitive PyQt6 GUI and Command-Line Interface (CLI):**  
  Easy Interactive GUI for everyday users, powerful CLI access for professionals and automation.


## Screenshots
<img width="600" height="600" alt="image" src="https://github.com/user-attachments/assets/5dcffcbe-affe-47f0-880b-ae052f74b2d2" />
<img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/6a316d95-2232-4093-80a4-0a5fbf264832" />

<img width="200" height="400" alt="image" src="https://github.com/user-attachments/assets/2d97bcf7-e75c-484b-b0a0-92cdf394e36d" />


## Acknowledgements
- University of Liverpool, Department of Computer Science
- Supervisor: Dr. Karteek Sreenivasaiah
