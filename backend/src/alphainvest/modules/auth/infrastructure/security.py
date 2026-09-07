from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from alphainvest.core.config import Settings


class PasswordService:
    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except (VerifyMismatchError, InvalidHashError):
            return False


class TokenService:
    REQUIRED_CLAIMS = (
        "sub",
        "sid",
        "type",
        "iat",
        "exp",
        "jti",
    )

    def __init__(self, settings: Settings):
        self.settings = settings

    def create_access(
        self,
        user_id: UUID,
        session_id: UUID,
        roles: list[str],
        permissions: list[str],
    ) -> str:
        now = datetime.now(UTC)
        exp = now + timedelta(
            minutes=self.settings.access_token_minutes
        )

        payload = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": "access",
            "roles": roles,
            "permissions": permissions,
            "iat": now,
            "exp": exp,
            "jti": str(uuid4()),
        }

        return jwt.encode(
            payload,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )

    def create_refresh(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> tuple[str, datetime]:
        now = datetime.now(UTC)
        exp = now + timedelta(
            days=self.settings.refresh_token_days
        )

        payload = {
            "sub": str(user_id),
            "sid": str(session_id),
            "type": "refresh",
            "iat": now,
            "exp": exp,
            "jti": str(uuid4()),
        }

        return (
            jwt.encode(
                payload,
                self.settings.jwt_secret_key,
                algorithm=self.settings.jwt_algorithm,
            ),
            exp,
        )

    def decode(
        self,
        token: str,
        expected_type: str,
    ) -> dict[str, Any]:
        payload = jwt.decode(
            token,
            self.settings.jwt_secret_key,
            algorithms=[
                self.settings.jwt_algorithm,
            ],
            options={
                "require": list(self.REQUIRED_CLAIMS),
            },
        )

        if payload.get("type") != expected_type:
            raise jwt.InvalidTokenError(
                "Tipo de token inválido"
            )

        try:
            UUID(str(payload["sub"]))
            UUID(str(payload["sid"]))
            UUID(str(payload["jti"]))
        except (TypeError, ValueError) as exc:
            raise jwt.InvalidTokenError(
                "Claims de identidad inválidas"
            ) from exc

        return payload

    @staticmethod
    def hash_refresh(token: str) -> str:
        return sha256(token.encode()).hexdigest()
    