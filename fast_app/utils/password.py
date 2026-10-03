from pwdlib import PasswordHash
Password_Hash=PasswordHash.recommended()

def hash_password(password:str):
    return Password_Hash.hash(password)

def verify_hash(password:str,hashed_password:str):
    return Password_Hash.verify(password,hashed_password)