import ssl
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alphainvest.core.config import Settings, get_settings


def build_database_ssl_context(
    settings: Settings,
) -> ssl.SSLContext | None:
    """Construye el contexto SSL utilizado por asyncpg."""

    mode = settings.database_ssl_mode

    if mode == "disable":
        return None

    if mode == "require":
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        return context

    context = ssl.create_default_context(
        cafile=settings.database_ssl_ca_file,
    )

    if mode == "verify-ca":
        context.check_hostname = False

    return context


def build_database_connect_args(
    settings: Settings,
) -> dict[str, Any]:
    """Construye argumentos específicos de conexión para asyncpg."""

    connect_args: dict[str, Any] = {
        "command_timeout": settings.database_command_timeout,
    }

    ssl_context = build_database_ssl_context(
        settings,
    )

    if ssl_context is not None:
        connect_args["ssl"] = ssl_context

    return connect_args


def create_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.database_url_string,
        echo=settings.database_echo,
        pool_pre_ping=True,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
        pool_recycle=settings.database_pool_recycle,
        connect_args=build_database_connect_args(
            settings,
        ),
    )


settings = get_settings()
engine = create_engine(settings)
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Una sesión y una transacción independiente por petición HTTP."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine() -> None:
    await engine.dispose()

