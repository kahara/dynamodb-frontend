import uuid, hashlib, base64
from datetime import datetime
from time import mktime

def generate_key():
    return hash(uuid.uuid4().hex)

def hash(plaintext):
    return base64.urlsafe_b64encode(hashlib.sha512(plaintext).digest()).strip(' =')

def salt_string(plaintext=None):
    salt = generate_key()
    cryptext = hash('%s%s' % (salt, plaintext))
    
    return '%s$%s' % (salt, cryptext)

def check_salted(plaintext=None, salted=None):
    salt = salted.split('$')[0]
    cryptext = '%s$%s' % (salt, hash('%s%s' % (salt, plaintext)))
    
    return cryptext == salted
