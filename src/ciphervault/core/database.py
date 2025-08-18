import os
import uuid
from contextlib import closing
import sqlcipher3.dbapi2 as sqlite

class SecurePasswordDatabase:
    def __init__(self, db_path: str, encryption_key: bytes):
        self.db_path = db_path
        self.encryption_key = encryption_key
        self.conn = self._create_connection()
        self._initialize_database()

    def _create_connection(self):
        conn = sqlite.connect(self.db_path)
        hex_key = self.encryption_key.hex()
        conn.execute(f"PRAGMA key = \"x'{hex_key}'\"")
        conn.execute("PRAGMA cipher_page_size = 4096")
        conn.execute("PRAGMA kdf_iter = 256000")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA secure_delete = ON")
        conn.execute("PRAGMA auto_vacuum = FULL")
        return conn

    def _initialize_database(self):
        with closing(self.conn.cursor()) as c:
            # Create main entries table
            c.execute("""
            CREATE TABLE IF NOT EXISTS vault_entries (
                id BLOB PRIMARY KEY,
                nonce BLOB NOT NULL,
                tag BLOB NOT NULL,
                ciphertext BLOB NOT NULL,
                algorithm TEXT NOT NULL CHECK(algorithm IN ('AES', 'CHA')),
                algorithm_mechanism TEXT NOT NULL CHECK(algorithm_mechanism IN ('aes', 'chacha', 'hybrid')),
                associated_data TEXT,
                created_at TIMESTAMP DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')),
                updated_at TIMESTAMP DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))
            ) WITHOUT ROWID;
            """)
            
            # Create configuration table
            c.execute("""
            CREATE TABLE IF NOT EXISTS vault_config (
                key TEXT PRIMARY KEY,
                value TEXT
            ) WITHOUT ROWID;
            """)
            
            # Create triggers
            c.execute("""
            CREATE TRIGGER IF NOT EXISTS update_timestamp
            AFTER UPDATE ON vault_entries
            FOR EACH ROW
            BEGIN
                UPDATE vault_entries SET updated_at = STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')
                WHERE id = OLD.id;
            END;
            """)
        self.conn.commit()

    def change_db_key(self, new_enc_key: bytes):
        c = self.conn.cursor()
        c.execute(f"PRAGMA key = \"x'{self.encryption_key.hex()}'\"")
        try:
            c.execute("SELECT count(*) FROM vault_config;")
        except Exception as e:
            c.close()
            raise RuntimeError("Old password is incorrect or database is not SQLCipher-encrypted.") from e
        # Change the encryption key
        c.execute(f"PRAGMA rekey = \"x'{new_enc_key.hex()}'\"")
        self.conn.commit()

    def add_entry(self, encrypted_data: bytes, context: str = "",
                 algorithm_mechanism: str = "hybrid") -> str:
        algo_id = encrypted_data[:3].decode()
        if algo_id not in ("AES", "CHA"):
            raise ValueError("Invalid algorithm identifier")
        
        if algo_id == "AES":
            nonce = encrypted_data[3:19]
            ciphertext = encrypted_data[19:-16]
            tag = encrypted_data[-16:]
        else:  # CHA
            nonce = encrypted_data[3:15]
            ciphertext = encrypted_data[15:-16]
            tag = encrypted_data[-16:]
        
        entry_id = uuid.uuid4().bytes
        with closing(self.conn.cursor()) as c:
            c.execute("""
            INSERT INTO vault_entries 
                (id, nonce, tag, ciphertext, algorithm, algorithm_mechanism, associated_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (entry_id, nonce, tag, ciphertext, algo_id, algorithm_mechanism, context))
        self.conn.commit()
        return entry_id.hex()

    def get_config(self, key: str) -> str:
        with closing(self.conn.cursor()) as c:
            c.execute("SELECT value FROM vault_config WHERE key = ?", (key,))
            result = c.fetchone()
        return result[0] if result else None

    def set_config(self, key: str, value: str):
        with closing(self.conn.cursor()) as c:
            c.execute("""
            INSERT OR REPLACE INTO vault_config (key, value)
            VALUES (?, ?)
            """, (key, value))
        self.conn.commit()

    def get_entries_by_service(self, service: str) -> list:
        """Get all entries for a service (non-unique)"""
        with closing(self.conn.cursor()) as c:
            c.execute("""
            SELECT hex(id), nonce, tag, ciphertext, algorithm, algorithm_mechanism, associated_data
            FROM vault_entries WHERE associated_data = ?
            """, (service,))
            results = c.fetchall()
        
        entries = []
        for row in results:
            entry_id, nonce, tag, ciphertext, algo_id, algo_mech, context = row
            algo_prefix = algo_id.encode()
            encrypted_data = algo_prefix + nonce + ciphertext + tag
            entries.append({
                'id': entry_id,
                'encrypted_data': encrypted_data,
                'algorithm': algo_id,
                'algorithm_mechanism': algo_mech,
                'context': context
            })
        return entries

    def get_entry(self, entry_id: str) -> dict:
        entry_id_bytes = bytes.fromhex(entry_id)
        with closing(self.conn.cursor()) as c:
            c.execute("""
            SELECT nonce, tag, ciphertext, algorithm, algorithm_mechanism, associated_data
            FROM vault_entries WHERE id = ?
            """, (entry_id_bytes,))
            result = c.fetchone()
        if not result:
            return None
        nonce, tag, ciphertext, algo_id, algo_mech, context = result
        algo_prefix = algo_id.encode()
        encrypted_data = algo_prefix + nonce + ciphertext + tag
        return {
            'id': entry_id,
            'encrypted_data': encrypted_data,
            'algorithm': algo_id,
            'algorithm_mechanism': algo_mech,
            'context': context
        }

    def get_all_entries(self) -> list:
        """Get all entries with encrypted data constructed for decryption"""
        with closing(self.conn.cursor()) as c:
            c.execute("""
                SELECT hex(id), associated_data, algorithm, nonce, ciphertext, tag, algorithm_mechanism
                FROM vault_entries
            """)
            entries = []
            for row in c.fetchall():
                id_hex, service, algo_id, nonce, ciphertext, tag, algo_mech = row
                # Construct encrypted_data in same format as get_entry()
                algo_prefix = algo_id.encode()
                encrypted_data = algo_prefix + nonce + ciphertext + tag
                entries.append({
                    'id': id_hex,
                    'service': service,
                    'encrypted_data': encrypted_data,
                    'algorithm_mechanism': algo_mech
                })
            return entries

    def update_entry(self, entry_id: str, encrypted_data: bytes, context: str,
                    algorithm_mechanism: str) -> None:
        entry_id_bytes = bytes.fromhex(entry_id)
        algo_id = encrypted_data[:3].decode()
        if algo_id not in ("AES", "CHA"):
            raise ValueError("Invalid algorithm identifier")
            
        if algo_id == "AES":
            nonce = encrypted_data[3:19]
            ciphertext = encrypted_data[19:-16]
            tag = encrypted_data[-16:]
        else:  # CHA
            nonce = encrypted_data[3:15]
            ciphertext = encrypted_data[15:-16]
            tag = encrypted_data[-16:]
        
        with closing(self.conn.cursor()) as c:
            c.execute("""
            UPDATE vault_entries
            SET nonce = ?, tag = ?, ciphertext = ?, algorithm = ?,
                algorithm_mechanism = ?, associated_data = ?
            WHERE id = ?
            """, (nonce, tag, ciphertext, algo_id, algorithm_mechanism, context, entry_id_bytes))
        self.conn.commit()

    def delete_entry(self, entry_id: str):
        entry_id_bytes = bytes.fromhex(entry_id)
        with closing(self.conn.cursor()) as c:
            c.execute("DELETE FROM vault_entries WHERE id = ?", (entry_id_bytes,))
        self.conn.commit()

    def close(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def vacuum(self):
        with closing(self.conn.cursor()) as c:
            c.execute("VACUUM")
        self.conn.commit()

    def export_backup(self, backup_path: str):
        with closing(self.conn.cursor()) as c:
            c.execute(f"VACUUM INTO '{backup_path}'")
        self.conn.commit()
