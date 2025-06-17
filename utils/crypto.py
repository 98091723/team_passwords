import os
import secrets
import string
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class CryptoManager:
    """加密管理器，处理所有加密相关操作"""
    
    @staticmethod
    def generate_salt():
        """生成随机盐值"""
        return os.urandom(32)
    
    @staticmethod
    def derive_key(password, salt):
        """从密码和盐值派生加密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    @staticmethod
    def encrypt_data(data, key):
        """使用Fernet加密数据"""
        f = Fernet(key)
        return f.encrypt(data.encode())
    
    @staticmethod
    def decrypt_data(encrypted_data, key):
        """使用Fernet解密数据"""
        f = Fernet(key)
        return f.decrypt(encrypted_data).decode()
    
    @staticmethod
    def generate_password(length=16, include_symbols=True):
        """生成强密码"""
        characters = string.ascii_letters + string.digits
        if include_symbols:
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password
    
    @staticmethod
    def hash_password(password, salt):
        """使用PBKDF2HMAC哈希密码"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=64,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())