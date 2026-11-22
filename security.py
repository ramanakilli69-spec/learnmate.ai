"""
security.py - Password hashing and session tokens.

We use only Python's standard library:
  - hashlib.pbkdf2_hmac  -> slow hash that makes password guessing hard
  - secrets              -> cryptographically random salts and tokens
"""

import hashlib
import secrets

# More iterations = slower to hash = safer against guessing.
PBKDF2_ITERATIONS = 100_000


def hash_password(password):
    """Return a string 'salt$hash' (both parts are hex text)."""
    # A new random salt for every password, so equal passwords get different hashes.
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return salt + "$" + digest.hex()


def verify_password(password, stored):
    """Check a typed password against the stored 'salt$hash' string."""
    try:
        salt, expected_hex = stored.split("$", 1)
    except ValueError:
        # Stored value is not in the right format.
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    # compare_digest avoids timing attacks when comparing secrets.
    return secrets.compare_digest(digest.hex(), expected_hex)


def new_session_token():
    """Return a random, URL-safe token used as the login session id."""
    return secrets.token_urlsafe(32)
