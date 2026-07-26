from uuid import uuid4

import pytest

from alphainvest.core.config import Settings
from alphainvest.modules.auth.infrastructure.security import PasswordService, TokenService


@pytest.mark.unit
def test_password_hash_and_verify():
    service = PasswordService()
    hashed = service.hash("UnaClaveSegura2026!")
    assert hashed != "UnaClaveSegura2026!"
    assert service.verify("UnaClaveSegura2026!", hashed)
    assert not service.verify("incorrecta", hashed)


@pytest.mark.unit
def test_access_token_contains_identity():
    settings = Settings(_env_file=None, jwt_secret_key="x" * 40)
    svc = TokenService(settings)
    uid = uuid4()
    sid = uuid4()
    token = svc.create_access(uid, sid, ["INVERSIONISTA"], ["activos.leer"])
    payload = svc.decode(token, "access")
    assert payload["sub"] == str(uid)
    assert payload["sid"] == str(sid)
    assert "activos.leer" in payload["permissions"]


@pytest.mark.unit
def test_refresh_hash_is_deterministic():
    assert TokenService.hash_refresh("abc") == TokenService.hash_refresh("abc")
    assert TokenService.hash_refresh("abc") != "abc"
