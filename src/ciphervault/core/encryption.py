import os
import platform
import subprocess
from Cryptodome.Cipher import ChaCha20_Poly1305, AES
from Cryptodome.Protocol.KDF import PBKDF2, HKDF
from Cryptodome.Hash import SHA256
from zeroize import zeroize1

class ChaCha20Poly1305Cipher:
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits) long")
        self.key = key
    
    def encrypt(self, plaintext: bytes, associated_data: bytes = b'') -> bytes:
        cipher = ChaCha20_Poly1305.new(key=self.key)
        cipher.update(associated_data)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        return cipher.nonce + ciphertext + tag
    
    def decrypt(self, data: bytes, associated_data: bytes = b'') -> bytes:
        nonce = data[:12]
        ciphertext = data[12:-16]
        tag = data[-16:]
        cipher = ChaCha20_Poly1305.new(key=self.key, nonce=nonce)
        cipher.update(associated_data)
        return cipher.decrypt_and_verify(ciphertext, tag)

class AESGCMCipher:
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits) long")
        self.key = key
    
    def encrypt(self, plaintext: bytes, associated_data: bytes = b'') -> bytes:
        cipher = AES.new(self.key, AES.MODE_GCM)
        cipher.update(associated_data)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        return cipher.nonce + ciphertext + tag
    
    def decrypt(self, data: bytes, associated_data: bytes = b'') -> bytes:
        nonce = data[:16]
        ciphertext = data[16:-16]
        tag = data[-16:]
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        cipher.update(associated_data)
        return cipher.decrypt_and_verify(ciphertext, tag)

class HybridEncryptionManager:
    def __init__(self, password: str, salt: bytes, algorithm: str = "hybrid"):
        """
        Initialize with algorithm selection:
        - 'aes': Always use AES-256-GCM
        - 'chacha': Always use ChaCha20-Poly1305
        - 'hybrid': Auto-select based on hardware (default)
        """
        self.salt = salt
        self.key_deriver = KeyDerivation(password, self.salt)
        self.aes_cipher = AESGCMCipher(self.key_deriver.get_aes_key())
        self.chacha_cipher = ChaCha20Poly1305Cipher(self.key_deriver.get_chacha_key())
        self.algorithm = algorithm.lower()
        self.use_aes = self.has_aes_ni() if algorithm == "hybrid" else None
    
    @classmethod
    def from_keys(cls, aes_key: bytes, chacha_key: bytes, algorithm: str = "hybrid"):
        obj = cls.__new__(cls)  # bypass __init__
        obj.aes_cipher = AESGCMCipher(aes_key)
        obj.chacha_cipher = ChaCha20Poly1305Cipher(chacha_key)
        obj.algorithm = algorithm.lower()
        obj.use_aes = obj.has_aes_ni() if algorithm == "hybrid" else None
        return obj
    
    def has_aes_ni(self) -> bool:
        """Detect AES-NI hardware acceleration"""
        try:
            import cpufeature
            return cpufeature.CPUFeature.get('AES', False)
        except ImportError:
            os_name = platform.system()
            if os_name == "Linux":
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        return 'aes' in f.read().lower()
                except: return False
            elif os_name == "Darwin":  # macOS
                try:
                    result = subprocess.run(
                        ['sysctl', '-n', 'machdep.cpu.features'],
                        capture_output=True, text=True
                    )
                    return 'aes' in result.stdout.lower()
                except: return False
            elif os_name == "Windows":
                try:
                    result = subprocess.run(
                        ['powershell', '-Command', 
                         '(Get-WmiObject Win32_Processor).AESInstructionSet'],
                        capture_output=True, text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    return 'true' in result.stdout.lower()
                except: return False
        return False
    
    def encrypt(self, plaintext: bytes, context: bytes = b'') -> bytes:
        """Encrypt using selected algorithm with metadata prefix"""
        if self.algorithm == "aes":
            encrypted = self.aes_cipher.encrypt(plaintext, context)
            return b'AES' + encrypted
        elif self.algorithm == "chacha":
            encrypted = self.chacha_cipher.encrypt(plaintext, context)
            return b'CHA' + encrypted
        else:  # hybrid
            if self.use_aes:
                encrypted = self.aes_cipher.encrypt(plaintext, context)
                return b'AES' + encrypted
            else:
                encrypted = self.chacha_cipher.encrypt(plaintext, context)
                return b'CHA' + encrypted
    
    def decrypt(self, data: bytes, context: bytes = b'') -> bytes:
        """Decrypt based on metadata prefix with algorithm validation"""
        algo_prefix = data[:3]
        ciphertext = data[3:]
        
        # Validate algorithm selection matches data
        if self.algorithm == "aes" and algo_prefix != b'AES':
            raise ValueError("Data not encrypted with AES")
        if self.algorithm == "chacha" and algo_prefix != b'CHA':
            raise ValueError("Data not encrypted with ChaCha")
        
        if algo_prefix == b'AES':
            return self.aes_cipher.decrypt(ciphertext, context)
        elif algo_prefix == b'CHA':
            return self.chacha_cipher.decrypt(ciphertext, context)
        else:
            raise ValueError("Unsupported algorithm prefix")

class KeyDerivation:
    def __init__(self, password: str, salt: bytes, iterations: int = 120_000):
        self.password = password.encode('utf-8')
        self.salt = salt
        self.iterations = iterations
        self.master_key = self._derive_master_key()
    
    def _derive_master_key(self) -> bytes:
        return PBKDF2(
            self.password,
            self.salt,
            dkLen=32,
            count=self.iterations,
            hmac_hash_module=SHA256
        )
    def get_database_key(self) -> bytes:
        return HKDF(
            self.master_key,
            32,
            salt=None,
            hashmod=SHA256,
            context=b'db-encryption'
        )
    def get_aes_key(self) -> bytes:
        return HKDF(
            self.master_key,
            32,
            salt=None,
            hashmod=SHA256,
            context=b'aes-256-gcm'
        )
    
    def get_chacha_key(self) -> bytes:
        return HKDF(
            self.master_key,
            32,
            salt=None,
            hashmod=SHA256,
            context=b'chacha20'
        )

    def get_salt(self) -> bytes:
        return self.salt

    def clear_sensitive_data(self):
        """Securely wipe sensitive data from memory"""
        zeroize1(self.password)
        zeroize1(self.master_key)
        zeroize1(self.salt)