from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from dotenv import set_key

# jwt encryption
jwt_secret_key = os.environ.get('JWT_SECRET_KEY')
if not jwt_secret_key:
    jwt_secret_key = os.urandom(24).hex()
    set_key('.env', 'JWT_SECRET_KEY', jwt_secret_key)
    os.environ['JWT_SECRET_KEY'] = jwt_secret_key


# db encryption
encryption_key = os.environ.get('ENCRYPTION_KEY')
if not encryption_key:
    encryption_key = Fernet.generate_key().decode()
    set_key('.env', 'ENCRYPTION_KEY', encryption_key)
    os.environ['ENCRYPTION_KEY'] = encryption_key


salt = os.environ.get('SALT')
if not salt:
    salt = os.urandom(16).hex()
    set_key('.env', 'SALT', salt)
    os.environ['SALT'] = salt

salt = bytes.fromhex(salt)

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)

key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
fernet = Fernet(key)


def encrypt(secret_value):
    return fernet.encrypt(secret_value.encode()).decode()


def decrypt(encrypted_secret_value):
    return fernet.decrypt(encrypted_secret_value.encode()).decode()
