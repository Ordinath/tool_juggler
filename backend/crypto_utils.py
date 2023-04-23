from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from dotenv import load_dotenv, set_key

load_dotenv()


# Get the encryption key from an environment variable or generate one
encryption_key = os.environ.get('ENCRYPTION_KEY')
if not encryption_key:
    encryption_key = Fernet.generate_key().decode()
    set_key('.env', 'ENCRYPTION_KEY', encryption_key)
    os.environ['ENCRYPTION_KEY'] = encryption_key

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=b'',
    iterations=100000,
)

key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
fernet = Fernet(key)


def encrypt(secret_value):
    return fernet.encrypt(secret_value.encode()).decode()


def decrypt(encrypted_secret_value):
    return fernet.decrypt(encrypted_secret_value.encode()).decode()
