"""
Unit tests for password hashing, security, and verification.
"""
from werkzeug.security import generate_password_hash, check_password_hash


def test_password_hashing_and_verification():
    raw_password = "SecretPassword@123"
    hashed = generate_password_hash(raw_password)

    # 1. Plaintext must never equal hashed string
    assert hashed != raw_password
    assert len(hashed) > 40

    # 2. Correct password verifies to True
    assert check_password_hash(hashed, raw_password) is True

    # 3. Incorrect password verifies to False
    assert check_password_hash(hashed, "WrongPassword@123") is False


def test_hash_uniqueness_for_same_password():
    raw_password = "SamePassword@123"
    hash1 = generate_password_hash(raw_password)
    hash2 = generate_password_hash(raw_password)

    # Hashes generated with random salts must differ
    assert hash1 != hash2
    assert check_password_hash(hash1, raw_password) is True
    assert check_password_hash(hash2, raw_password) is True
