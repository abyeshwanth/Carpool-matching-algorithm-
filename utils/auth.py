"""
auth.py - Simple authentication helpers (SHA-256 password hashing).
For a production system, replace with bcrypt/argon2 + proper session tokens.
"""

import hashlib
from utils import db


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def signup(name, email, password, phone, role="rider"):
    hashed = hash_password(password)
    uid = db.create_user(name, email, hashed, phone, role)
    return uid


def login(email, password):
    user = db.get_user_by_email(email)
    if not user:
        return None
    if user["password"] == hash_password(password):
        return user
    return None
