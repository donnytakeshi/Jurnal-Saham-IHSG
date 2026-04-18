"""
User Authentication Module
Support untuk login/signup dengan password hashing
Integrasi dengan Firebase atau SQLite untuk user management
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
import json


class AuthManager:
    """User authentication & account management"""
    
    def __init__(self, db_path='data/users.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.init_db()
    
    def connect(self):
        """Connect to user database"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None
    
    def init_db(self):
        """Initialize user tables"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                profile_pic_path TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # User preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                theme TEXT DEFAULT 'light',
                currency TEXT DEFAULT 'IDR',
                auto_sync BOOLEAN DEFAULT 1,
                sync_interval INTEGER DEFAULT 3600,
                notifications_enabled BOOLEAN DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Cloud sync status
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_status (
                user_id INTEGER PRIMARY KEY,
                last_sync TIMESTAMP,
                sync_enabled BOOLEAN DEFAULT 1,
                cloud_storage TEXT DEFAULT 'none',
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        self.close()
    
    @staticmethod
    def hash_password(password, salt=None):
        """Hash password dengan salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return pwd_hash.hex(), salt
    
    @staticmethod
    def verify_password(password, pwd_hash, salt):
        """Verify password"""
        computed_hash, _ = AuthManager.hash_password(password, salt)
        return computed_hash == pwd_hash
    
    def signup(self, username, email, password):
        """Create new user account"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Validate input
            if len(password) < 6:
                return False, "Password harus minimal 6 karakter"
            
            if len(username) < 3:
                return False, "Username harus minimal 3 karakter"
            
            # Hash password
            pwd_hash, salt = self.hash_password(password)
            
            # Create user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt)
                VALUES (?, ?, ?, ?)
            ''', (username.lower(), email.lower(), pwd_hash, salt))
            
            user_id = cursor.lastrowid
            
            # Create user preferences
            cursor.execute('''
                INSERT INTO user_preferences (user_id)
                VALUES (?)
            ''', (user_id,))
            
            # Create sync status
            cursor.execute('''
                INSERT INTO sync_status (user_id)
                VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            self.close()
            
            return True, f"Akun berhasil dibuat! Selamat datang {username}"
        
        except sqlite3.IntegrityError:
            self.close()
            return False, "Username atau email sudah terdaftar"
        except Exception as e:
            self.close()
            return False, f"Error: {str(e)}"
    
    def login(self, username, password):
        """Verify user credentials"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, password_hash, salt, is_active 
                FROM users WHERE username = ? OR email = ?
            ''', (username.lower(), username.lower()))
            
            row = cursor.fetchone()
            
            if not row:
                self.close()
                return False, "Username tidak ditemukan"
            
            if not row['is_active']:
                self.close()
                return False, "Akun ini telah dinonaktifkan"
            
            # Verify password
            if not self.verify_password(password, row['password_hash'], row['salt']):
                self.close()
                return False, "Password salah"
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (row['id'],))
            conn.commit()
            
            self.close()
            return True, {"user_id": row['id'], "username": row['username']}
        
        except Exception as e:
            self.close()
            return False, f"Error login: {str(e)}"
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Get current password
            cursor.execute('''
                SELECT password_hash, salt FROM users WHERE id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            
            if not row:
                self.close()
                return False, "User tidak ditemukan"
            
            # Verify old password
            if not self.verify_password(old_password, row['password_hash'], row['salt']):
                self.close()
                return False, "Password lama salah"
            
            # Hash new password
            pwd_hash, salt = self.hash_password(new_password)
            
            # Update
            cursor.execute('''
                UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
            ''', (pwd_hash, salt, user_id))
            
            conn.commit()
            self.close()
            return True, "Password berhasil diubah"
        
        except Exception as e:
            self.close()
            return False, f"Error: {str(e)}"
    
    def get_user_info(self, user_id):
        """Get user profile info"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, created_at, last_login 
                FROM users WHERE id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            self.close()
            
            return dict(row) if row else None
        
        except Exception as e:
            self.close()
            return None
    
    def get_user_preferences(self, user_id):
        """Get user preferences"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM user_preferences WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            self.close()
            
            return dict(row) if row else None
        
        except Exception as e:
            self.close()
            return None
    
    def update_preferences(self, user_id, **kwargs):
        """Update user preferences"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            allowed_fields = ['theme', 'currency', 'auto_sync', 'sync_interval', 'notifications_enabled']
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not updates:
                self.close()
                return True, "Tidak ada perubahan"
            
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [user_id]
            
            cursor.execute(f'''
                UPDATE user_preferences SET {set_clause} WHERE user_id = ?
            ''', values)
            
            conn.commit()
            self.close()
            return True, "Preferensi berhasil diupdate"
        
        except Exception as e:
            self.close()
            return False, f"Error: {str(e)}"
    
    def enable_cloud_sync(self, user_id, storage_type='firebase'):
        """Enable cloud sync untuk user"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sync_status 
                SET sync_enabled = 1, cloud_storage = ?, last_sync = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (storage_type, user_id))
            
            conn.commit()
            self.close()
            return True, f"Cloud sync diaktifkan dengan {storage_type}"
        
        except Exception as e:
            self.close()
            return False, f"Error: {str(e)}"
    
    def get_sync_status(self, user_id):
        """Get user sync status"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sync_status WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            self.close()
            
            return dict(row) if row else None
        
        except Exception as e:
            self.close()
            return None
