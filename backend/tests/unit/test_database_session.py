import ssl

from alphainvest.core.config import Settings
from alphainvest.infrastructure.database.session import (
    build_database_connect_args,
    build_database_ssl_context,
)


def test_database_ssl_disabled_returns_no_context() -> None:
    settings = Settings(
        _env_file=None,
        database_ssl_mode="disable",
    )

    ssl_context = build_database_ssl_context(
        settings,
    )

    assert ssl_context is None


def test_database_ssl_require_encrypts_without_certificate_validation() -> None:
    settings = Settings(
        _env_file=None,
        database_ssl_mode="require",
    )

    ssl_context = build_database_ssl_context(
        settings,
    )

    assert ssl_context is not None
    assert ssl_context.check_hostname is False
    assert ssl_context.verify_mode == ssl.CERT_NONE


def test_database_ssl_verify_ca_validates_certificate() -> None:
    settings = Settings(
        _env_file=None,
        database_ssl_mode="verify-ca",
    )

    ssl_context = build_database_ssl_context(
        settings,
    )

    assert ssl_context is not None
    assert ssl_context.check_hostname is False
    assert ssl_context.verify_mode == ssl.CERT_REQUIRED


def test_database_ssl_verify_full_validates_hostname() -> None:
    settings = Settings(
        _env_file=None,
        database_ssl_mode="verify-full",
    )

    ssl_context = build_database_ssl_context(
        settings,
    )

    assert ssl_context is not None
    assert ssl_context.check_hostname is True
    assert ssl_context.verify_mode == ssl.CERT_REQUIRED


def test_database_connect_args_without_ssl() -> None:
    settings = Settings(
        _env_file=None,
        database_ssl_mode="disable",
        database_command_timeout=25,
    )

    connect_args = build_database_connect_args(
        settings,
    )

    assert connect_args == {
        "command_timeout": 25,
    }


def test_database_connect_args_with_ssl() -> None:
    settings = Settings(
        _env_file=None,
        database_ssl_mode="require",
    )

    connect_args = build_database_connect_args(
        settings,
    )

    assert "ssl" in connect_args
    assert isinstance(
        connect_args["ssl"],
        ssl.SSLContext,
    )