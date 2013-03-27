import uuid, hashlib, base64
from passlib.hash import pbkdf2_sha512

def generate_key():
    return base64.urlsafe_b64encode(hashlib.sha256(uuid.uuid4().hex + uuid.uuid4().hex).digest()).strip(' =')

def hash_password(password=None):
    return pbkdf2_sha512.encrypt(password)

def check_password(password=None, hash=None):
    return pbkdf2_sha512.verify(password, hash)

def cookie(session_id=''):
    return 'session_id=%s; Path=/; Expires=Tue, 31-Dec-2019 23:59:59 GMT' % (session_id, )        
