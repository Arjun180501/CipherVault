import os
import datetime
import pyotp
from ciphervault.core.vault import PasswordVault
from ciphervault.core.utils import resolve_vault_path

class AuthController:
    def __init__(self, parent_window=None):
        self.parent = parent_window

    def authenticate_user(self, vault_data, master_password):
        """
        Returns (success: bool, message: str, vault_obj: PasswordVault or None)
        """
        if not master_password:
            return False, "Master password is required.", None

        db_path = resolve_vault_path(vault_data["name"] + ".db")
        if not os.path.exists(db_path):
            return False, f"Vault database not found:\n{db_path}", None

        try:
            vault = PasswordVault(master_password, db_path=db_path)
            now = datetime.datetime.utcnow()
            vault.db.set_config("last_used", now.isoformat())

            return True, "Login successful!", vault

        except Exception as e:
            return False, f"Vault authentication failed:\n\n{e}", None

    def check_mfa_status(self, vault):
        totp_flag = vault.get_config("totp_enabled")
        if totp_flag == "true":
            return True
        else:
            return False
    
    def validate_totp(self, vault, totp_code):
        totp_key = vault.db.get_config("totp_key")
        totp_required = bool(totp_key)
        if totp_required:
            totp_key = vault.db.get_config("totp_key")
            if not totp_key:
                return False, "TOTP not configured. Please reinitialize the vault.", None
            totp = pyotp.TOTP(totp_key)
            if not totp.verify(totp_code):
                return False, "Invalid TOTP code. Access denied.", None
    