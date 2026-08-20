"""Encrypts datasource connection secrets at rest with Fernet (AES-128-CBC +
HMAC). `DATASOURCE_ENCRYPTION_KEY` must be a 32-byte urlsafe-base64 key
(rotate via a dual-read/single-write migration when needed — out of scope
for this skeleton, flagged here as the extension point).
"""
from __future__ import annotations

import json

from cryptography.fernet import Fernet

from src.config import Settings


class CredentialCipher:
    def __init__(self, settings: Settings) -> None:
        self._fernet = Fernet(settings.datasource_encryption_key.encode())

    def encrypt(self, credentials: dict[str, str]) -> bytes:
        return self._fernet.encrypt(json.dumps(credentials).encode())

    def decrypt(self, token: bytes) -> dict[str, str]:
        return json.loads(self._fernet.decrypt(token).decode())
