from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import hashlib
import sqlite3

def derive_encryption_key(master, salt):
    # Set up key params
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(master.encode()))

    return key

def encrypt_password(password):
    connection = sqlite3.connect("credentials.db")
    cursor = connection.cursor()
    
    # Get master key
    key = cursor.execute("SELECT key FROM setup").fetchone()[0]
    
    connection.commit()
    cursor.close()
    connection.close()

    # Encrypt password
    fernet = Fernet(key)
    encrypt_password = fernet.encrypt(password.encode())
    return encrypt_password

def decrypt_password(encrypted_password):
    connection = sqlite3.connect("credentials.db")
    cursor = connection.cursor()
    
    # Get master key
    key = cursor.execute("SELECT key FROM setup").fetchone()[0]
    
    connection.commit()
    cursor.close()
    connection.close()

    # Decrypt password
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password).decode()
    return decrypted_password

def hash_password(password):
    # Create hash object
    hash_object = hashlib.sha256()
    
    # Update hash object with password
    hash_object.update(password.encode())
    
    # Get hexidecimal representation of hash
    hash_hex = hash_object.hexdigest()
    
    return hash_hex