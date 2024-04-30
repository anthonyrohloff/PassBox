# https://www.linkedin.com/pulse/how-create-password-manager-python-yamil-garcia-rjxse/

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import hashlib

def derive_encryption_key(master, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(master.encode()))
    return key

def encrypt_password(password, key):
    fernet = Fernet(key)
    encrypt_password = fernet.encrypt(password.encode())
    return encrypt_password

def decrypt_password(encrypted_password, key):
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