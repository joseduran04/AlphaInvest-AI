from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from alphainvest.core.config import Settings
from alphainvest.modules.auth.infrastructure.security import (
    PasswordService,
    TokenService,
)


@pytest.mark.unit
def test_password_hash_and_verify() -> None:
    service = PasswordService()

    hashed = service.hash(
        "UnaClaveSegura2026!"
    )

    assert hashed != "UnaClaveSegura2026!"
    assert service.verify(
        "UnaClaveSegura2026!",
        hashed,
    )
    assert not service.verify(
        "incorrecta",
        hashed,
    )


@pytest.mark.unit
def test_access_token_contains_identity() -> None:
    settings = Settings(
        _env_file=None,
        jwt_secret_key="x" * 40,
    )

    service = TokenService(settings)

    user_id = uuid4()
    session_id = uuid4()

    token = service.create_access(
        user_id,
        session_id,
        ["INVERSIONISTA"],
        ["activos.leer"],
    )

    payload = service.decode(
        token,
        "access",
    )

    assert payload["sub"] == str(user_id)
    assert payload["sid"] == str(session_id)
    assert payload["type"] == "access"
    assert "activos.leer" in payload["permissions"]
    assert "jti" in payload


@pytest.mark.unit
def test_refresh_token_contains_required_claims() -> None:
    settings = Settings(
        _env_file=None,
        jwt_secret_key="x" * 40,
    )

    service = TokenService(settings)

    user_id = uuid4()
    session_id = uuid4()

    token, _ = service.create_refresh(
        user_id,
        session_id,
    )

    payload = service.decode(
        token,
        "refresh",
    )

    assert payload["sub"] == str(user_id)
    assert payload["sid"] == str(session_id)
    assert payload["type"] == "refresh"
    assert "iat" in payload
    assert "exp" in payload
    assert "jti" in payload


@pytest.mark.unit
def test_decode_rejects_wrong_token_type() -> None:
    settings = Settings(
        _env_file=None,
        jwt_secret_key="x" * 40,
    )

    service = TokenService(settings)

    token = service.create_access(
        uuid4(),
        uuid4(),
        [],
        [],
    )

    with pytest.raises(
        jwt.InvalidTokenError,
        match="Tipo de token inválido",
    ):
        service.decode(
            token,
            "refresh",
        )


@pytest.mark.unit
def test_decode_rejects_missing_required_claim() -> None:
    settings = Settings(
        _env_file=None,
        jwt_secret_key="x" * 40,
    )

    service = TokenService(settings)

    now = datetime.now(UTC)

    payload = {
        "sub": str(uuid4()),
        "sid": str(uuid4()),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=15),
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(
        jwt.MissingRequiredClaimError,
    ):
        service.decode(
            token,
            "access",
        )


@pytest.mark.unit
def test_decode_rejects_invalid_identity_claims() -> None:
    settings = Settings(
        _env_file=None,
        jwt_secret_key="x" * 40,
    )

    service = TokenService(settings)

    now = datetime.now(UTC)

    payload = {
        "sub": "invalid-user-id",
        "sid": str(uuid4()),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "jti": str(uuid4()),
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(
        jwt.InvalidTokenError,
        match="Claims de identidad inválidas",
    ):
        service.decode(
            token,
            "access",
        )


@pytest.mark.unit
def test_refresh_hash_is_deterministic() -> None:
    assert (
        TokenService.hash_refresh("abc")
        == TokenService.hash_refresh("abc")
    )

    assert TokenService.hash_refresh("abc") != "abc"
    