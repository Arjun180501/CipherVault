import os
import logging
from zeroize import zeroize1
import keyring
import base64
from ciphervault.core.encryption import KeyDerivation, HybridEncryptionManager
from ciphervault.core.database import SecurePasswordDatabase

class PasswordVault:
    def __init__(self, master_password: str = None, db_path: str = None, algorithm_mech: str = None):
        self.db_path = db_path
        self.salt_path = db_path + ".salt"
        self.master_password_ba = bytearray(master_password, 'utf-8') if master_password else None
        self._initialize_vault(algorithm_mech)
    
    def get_or_create_salt(self, salt_path: str) -> bytes:
        if os.path.exists(salt_path):
            with open(salt_path, "rb") as f:
                return f.read()
        salt = os.urandom(16)
        with open(salt_path, "wb") as f:
            f.write(salt)
        return salt
    
    def _initialize_vault(self, algorithm_mech: str = None):
        self.salt = self.get_or_create_salt(self.salt_path)
        if self.master_password_ba:
            password_str = self.master_password_ba.decode('utf-8')
            self.key_deriver = KeyDerivation(password_str, self.salt)
            self.db_key = self.key_deriver.get_database_key()
        else:
            self.db_key = base64.b64decode(keyring.get_password("database_key", "db_key"))
            password_str=None
        self.db = SecurePasswordDatabase(self.db_path, self.db_key)
        # Check if vault exists and get algorithm
        self.algorithm_mech = self._get_persisted_algorithm() or algorithm_mech or "hybrid"
        
        # Initialize encryption manager
        if password_str:
            self.encryption_manager = HybridEncryptionManager(password_str, self.salt, self.algorithm_mech)
            del password_str
            aes_key = self.key_deriver.get_aes_key()
            chacha_key = self.key_deriver.get_chacha_key()
            keyring.set_password("aes_key", "aes_key", base64.b64encode(aes_key).decode())
            keyring.set_password("chacha_key", "chacha_key", base64.b64encode(aes_key).decode())
        else:
            aes_key = base64.b64decode(keyring.get_password("aes_key", "aes_key"))
            chacha_key = base64.b64decode(keyring.get_password("chacha_key", "chacha_key"))
            self.encryption_manager = HybridEncryptionManager.from_keys(aes_key=aes_key, chacha_key=chacha_key, algorithm=self.algorithm_mech)
        # If new vault, persist algorithm
        if not self._vault_exists():
            if algorithm_mech == "aes":
                self.algorithm = "AES"
            elif algorithm_mech == "chacha":
                self.algorithm = "CHA"
            elif self.encryption_manager.has_aes_ni():
                self.algorithm = "AES"
            else:
                self.algorithm = "CHA"
            self.db.set_config("algorithm",  self.algorithm)
            logging.info(f"New vault created with algorithm: {self.algorithm}")
        
        self.locked = False
        logging.info("Vault initialized successfully")
        
    def _vault_exists(self) -> bool:
        """Check if vault has existing entries or config"""
        try:
            return bool(self.db.get_config("algorithm"))
        except:
            return False
    
    def _get_persisted_algorithm(self) -> str:
        """Get algorithm from persisted configuration"""
        return self.db.get_config("algorithm_mechanism")

    def update_config(self, key: str, value: str):
        self.db.set_config(key, value)

    def get_config(self, key: str, default=None):
        return self.db.get_config(key) or default

    def verify_master_password(self, password_to_test: str) -> bool:
        """
        Verify if the provided password matches the vault's master password.
        """
        try:
            # Use the existing salt
            with open(self.salt_path, "rb") as f:
                salt = f.read()
            # Derive a db key from the provided password
            key_deriver = KeyDerivation(password_to_test, salt)
            test_db_key = key_deriver.get_database_key()
            test_db = SecurePasswordDatabase(self.db_path, test_db_key)
            _ = test_db.get_config("algorithm")
            test_db.close()
            # If no exception, password is valid
            return True
        except Exception:
            return False

    
    def add_password_entry(self, service: str, username: str, password: str, notes: str = "") -> str:
        if self.locked:
            raise RuntimeError("Vault is locked")
        
        plaintext = f"{service}|{username}|{password}|{notes}".encode()
        plaintext_ba = bytearray(plaintext)
        
        try:
            encrypted_data = self.encryption_manager.encrypt(plaintext_ba, service.encode())
            _ = self.db.add_entry(
                encrypted_data, 
                context=service,
                algorithm_mechanism=self.algorithm_mech
            )
            logging.info(f"Added entry for {service} and {username}")
            return
        finally:
            zeroize1(plaintext_ba)
            del plaintext_ba

    def get_entries_by_service(self, service: str) -> list:
        if self.locked:
            raise RuntimeError("Vault is locked")
        db_entries = self.db.get_entries_by_service(service)
        user_entries = []
        for db_entry in db_entries:
            decrypted = self.encryption_manager.decrypt(
                db_entry['encrypted_data'],
                service.encode()
            )
            decrypted_ba = bytearray(decrypted)
            try:
                parts = decrypted_ba.decode().split('|', 3)
                user_entries.append({
                    'id': db_entry['id'],
                    'service': service,
                    'username': parts[1],
                    'notes': parts[3] if len(parts) > 3 else ""
                })
            finally:
                zeroize1(decrypted_ba)
                del decrypted_ba
        return user_entries

    def get_entry_details(self, entry_id: str) -> dict:
        if self.locked:
            raise RuntimeError("Vault is locked")
        db_entry = self.db.get_entry(entry_id)
        if not db_entry:
            return None
        decrypted = self.encryption_manager.decrypt(
            db_entry['encrypted_data'],
            db_entry['context'].encode()
        )
        decrypted_ba = bytearray(decrypted)
        try:
            parts = decrypted_ba.decode().split('|', 3)
            return {
                'id': entry_id,
                'service': parts[0],
                'username': parts[1],
                'password': parts[2],
                'notes': parts[3] if len(parts) > 3 else ""
            }
        finally:
            zeroize1(decrypted_ba)
            del decrypted_ba

    def find_entry(self, service: str, username: str) -> dict:
        """
        Find a password entry by service and username.
        Returns the entry dict if found, else None.
        """
        if self.locked:
            raise RuntimeError("Vault is locked")
        # Get all entries for the service
        entries = self.get_entries_by_service(service)
        # Search for the username within those entries
        for entry in entries:
            if entry['username'] == username:
                return entry
        return None
    
    def list_entries(self) -> list:
        if self.locked:
            raise RuntimeError("Vault is locked")
        db_entries = self.db.get_all_entries()
        user_entries = []
        for db_entry in db_entries:
            decrypted = self.encryption_manager.decrypt(
                db_entry['encrypted_data'],
                db_entry['service'].encode()
            )
            decrypted_ba = bytearray(decrypted)
            try:
                parts = decrypted_ba.decode().split('|', 3)
                user_entries.append({
                    'id': db_entry['id'],
                    'service': db_entry['service'],
                    'username': parts[1],
                    'notes': parts[3] if len(parts) > 3 else ""
                })
            finally:
                zeroize1(decrypted_ba)
                del decrypted_ba
        return user_entries
    
    def update_entry(self, entry_id: str, service: str = None, username: str = None, 
                    password: str = None, notes: str = None) -> bool:
        if self.locked:
            raise RuntimeError("Vault is locked")
        entry = self.get_entry_details(entry_id)
        if not entry:
            raise ValueError(f"No entry found with ID: {entry_id}")
        new_service = service or entry['service']
        new_username = username or entry['username']
        new_password = password or entry['password']
        new_notes = notes or entry['notes']
        new_plaintext = f"{new_service}|{new_username}|{new_password}|{new_notes}".encode()
        new_plaintext_ba = bytearray(new_plaintext)
        try:
            new_encrypted = self.encryption_manager.encrypt(
                new_plaintext_ba,
                new_service.encode()
            )
            self.db.update_entry(
                entry_id,
                new_encrypted,
                context=new_service,
                algorithm_mechanism=self.algorithm_mech
            )
            logging.info(f"Updated entry: {entry_id}")
            return True
        finally:
            zeroize1(new_plaintext_ba)
            del new_plaintext_ba

    def delete_entry(self, entry_id: str):
        if self.locked:
            raise RuntimeError("Vault is locked")
        self.db.delete_entry(entry_id)
        logging.info(f"Deleted entry: {entry_id}")

    def lock(self):
        if self.master_password_ba:
            zeroize1(self.master_password_ba)
            self.master_password_ba = bytearray()
            self.key_deriver.clear_sensitive_data()
        self.db.close()
        self.locked = True
        logging.info("Vault locked")

    def change_master_password(self, new_password: str):
        if self.locked:
            raise RuntimeError("Vault is locked")

        #Fetch all entries
        all_entries = []
        for entry_meta in self.db.get_all_entries():
            entry = self.get_entry_details(entry_meta['id'])
            if entry:
                all_entries.append(entry)

        #Generate new salt and db key
        new_salt = os.urandom(16)
        new_key_deriver = KeyDerivation(new_password, new_salt)
        new_db_key = new_key_deriver.get_database_key()

        #Create new encryption manager
        new_encryption_manager = HybridEncryptionManager(
            new_password,
            new_salt,
            self.algorithm_mech
        )

        #Update salt file on disk
        with open(self.salt_path, "wb") as f:
            f.write(new_salt)

        #Re-encrypt all entries
        for entry in all_entries:
            plaintext = f"{entry['service']}|{entry['username']}|{entry['password']}|{entry['notes']}".encode()
            plaintext_ba = bytearray(plaintext)
            try:
                new_encrypted_data = new_encryption_manager.encrypt(
                    plaintext_ba,
                    entry['service'].encode()
                )
                self.db.update_entry(
                    entry['id'],
                    new_encrypted_data,
                    context=entry['service'],
                    algorithm_mechanism=self.algorithm_mech
                )
            finally:
                zeroize1(plaintext_ba)
                del plaintext_ba

        self.db.change_db_key(new_db_key)
        logging.info("Master password changed successfully")

    def change_algorithm(self, new_algorithm_mech: str):
        if self.locked:
            raise RuntimeError("Vault is locked")
        if new_algorithm_mech not in ["aes", "chacha", "hybrid"]:
            raise ValueError("Invalid algorithm. Valid options: aes, chacha, hybrid")
        all_entries = []
        for entry_meta in self.db.get_all_entries():
            entry = self.get_entry_details(entry_meta['id'])
            if entry:
                all_entries.append(entry)
        
        old_algo_mech = self.get_config("algorithm_mechanism")
        if new_algorithm_mech == "aes":
            self.algorithm = "AES"
        elif new_algorithm_mech == "chacha":
            self.algorithm = "CHA"
        else:
            if self.encryption_manager.has_aes_ni():
                self.algorithm = "AES"
            else:
                self.algorithm = "CHA"
        self.db.set_config("algorithm",  self.algorithm)
        self.db.set_config("algorithm_mechanism", new_algorithm_mech)
        aes_key = base64.b64decode(keyring.get_password("aes_key", "aes_key"))
        chacha_key = base64.b64decode(keyring.get_password("chacha_key", "chacha_key"))
        encryption_manager = HybridEncryptionManager.from_keys(aes_key=aes_key, chacha_key=chacha_key, algorithm=new_algorithm_mech)
        for entry in all_entries:
            plaintext = f"{entry['service']}|{entry['username']}|{entry['password']}|{entry['notes']}".encode()
            plaintext_ba = bytearray(plaintext)
            try:
                encrypted_data = encryption_manager.encrypt(
                    plaintext_ba,
                    entry['service'].encode()
                )
                self.db.update_entry(
                    entry['id'],
                    encrypted_data,
                    context=entry['service'],
                    algorithm_mechanism=new_algorithm_mech
                )
            finally:
                zeroize1(plaintext_ba)
                del plaintext_ba
        logging.info(f"Algorithm changed from {old_algo_mech} to {new_algorithm_mech}. All entries re-encrypted.")

    def export_backup(self, backup_path: str):
        # Ensure destination folder exists
        os.makedirs(backup_path, exist_ok=True)
        self.db.export_backup(backup_path)
        logging.info(f"Backup created at {backup_path}")

    def close(self):
        self.lock()
        keyring.delete_password("database_key", "db_key")
        keyring.delete_password("aes_key", "aes_key")
        keyring.delete_password("chacha_key", "chacha_key")
        logging.info("Vault closed securely")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
