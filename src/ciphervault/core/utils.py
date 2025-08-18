import secrets
import string
import time
import threading
import pyperclip
import requests
import hashlib
import warnings
import zxcvbn
from pyhibp import pwnedpasswords, set_user_agent
from datetime import datetime
import socket
import os, sys
import json
import shutil

def resource_path(relative_path):
    """Get absolute path to resource, works both during development and in PyInstaller bundle."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def generate_password(
    length=16,
    use_uppercase=True,
    use_digits=True,
    use_symbols=True
) -> str:
    alphabet = string.ascii_lowercase
    if use_uppercase:
        alphabet += string.ascii_uppercase
    if use_digits:
        alphabet += string.digits
    if use_symbols:
        alphabet += "!@#$%^&*()-_=+[]{};:,.<>?/\\|"

    if not alphabet:
        raise ValueError("Character set is empty. Enable at least one option.")

    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_strong_password(
    length=16,
    use_uppercase=True,
    use_digits=True,
    use_symbols=True,
    min_score=4,
    max_attempts=10
) -> str:
    for _ in range(max_attempts):
        pwd = generate_password(length, use_uppercase, use_digits, use_symbols)
        score = zxcvbn.zxcvbn(pwd).get("score", 0)
        if score >= min_score:
            return pwd
    # Fallback: return the best we found
    return pwd


def copy_clipboard(password: str, timeout_seconds: int = 30):
    """
    Copy password to clipboard and auto-clear after timeout_seconds.
    """
    pyperclip.copy(password)
    
    def clear_clipboard():
        time.sleep(timeout_seconds)
        # Clear clipboard
        pyperclip.copy("")
        print("Clipboard cleared.")

    t = threading.Thread(target=clear_clipboard, daemon=True)
    t.start()

def is_password_pwned(password: str) -> int:
    """Check if password has been found in data breaches using HaveIBeenPwned API."""
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_password[:5], sha1_password[5:]

    try:
        response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=5)
        if response.status_code != 200:
            warnings.warn(f"Failed to get response from HIBP API. Error: {response.status_code}.\n Skipping breach check!!")
            return False

        hashes = (line.split(":") for line in response.text.splitlines())
        return any(s == suffix for s, _ in hashes)
    except requests.RequestException:
        return False


def is_password_breached(password: str) -> bool:
    """
    Returns True if the given password has appeared in known data breaches.
    Uses the HaveIBeenPwned password API via k-anonymity.
    This feature requires an internet connection.
    """
    try:
        # Set a custom user agent (required by HIBP)
        set_user_agent(ua="CipherVaultApp")
        count = pwnedpasswords.is_password_breached(password=password)
        return count > 0
    except Exception:
        return False  # Assume not breached if offline or failed
        

def get_last_checked_timestamp() -> str:
    """
    Returns a timestamp string for 'Last Checked' label.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def is_connected_to_internet(host="8.8.8.8", port=53, timeout=3) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def get_vaults_dir():
    """
    Return absolute path to the application's managed vaults directory,
    works in dev and when frozen by PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller executable path
        exe_dir = os.path.dirname(sys.executable)
    else:
        # Running from script
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    vaults_dir = os.path.join(exe_dir, "vaults")
    os.makedirs(vaults_dir, exist_ok=True)
    return vaults_dir

def resolve_vault_path(filename):
    vaults_dir = get_vaults_dir()
    return os.path.join(vaults_dir, filename)

# def get_vaults_json_path():
#     return os.path.join(get_vaults_dir(), "vaults.json")

# def update_vault_metadata(meta):
#     """Add or update a vault entry in vaults.json"""
#     vaults_json_path = get_vaults_json_path()
#     try:
#         with open(vaults_json_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         data = {"vaults": []}

#     # Remove existing entry with same filename
#     data['vaults'] = [v for v in data['vaults'] if v.get("filename") != meta["filename"]]
#     data['vaults'].append(meta)
#     with open(vaults_json_path, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=4)

# def get_vault_metadata(vault_filename):
#     """Fetch metadata for a vault, fallback to defaults."""
#     vaults_json_path = get_vaults_json_path()
#     try:
#         with open(vaults_json_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         for v in data.get("vaults", []):
#             if v.get("filename") == vault_filename:
#                 return v
#     except Exception:
#         pass
#     # Fallback/defaults:
#     name = os.path.splitext(vault_filename)[0]
#     return {
#         "name": name,
#         "filename": vault_filename,
#         "totp_enabled": False
#     }