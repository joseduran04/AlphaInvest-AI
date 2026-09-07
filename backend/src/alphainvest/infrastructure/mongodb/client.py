from typing import Any

from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

from alphainvest.core.config import Settings

MongoClientType = AsyncMongoClient[
    dict[str, Any]
]


_client: MongoClientType | None = None


def create_mongo_client(
    settings: Settings,
) -> MongoClientType:
    """Construye el cliente documental sin abrir conexión aún."""

    return AsyncMongoClient[
        dict[str, Any]
    ](
        settings.mongodb_uri,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=(
            settings
            .mongodb_server_selection_timeout_ms
        ),
    )


def initialize_mongo_client(
    settings: Settings,
) -> None:
    """Inicializa el cliente para el event loop de la aplicación."""

    global _client

    if _client is not None:
        return

    _client = create_mongo_client(settings)


def get_mongo_client() -> MongoClientType:
    """Obtiene el cliente inicializado."""

    if _client is None:
        raise RuntimeError(
            "El cliente MongoDB no está inicializado"
        )

    return _client


async def close_mongo_client() -> None:
    """Cierra el cliente MongoDB de la aplicación."""

    global _client

    if _client is None:
        return

    await _client.close()

    _client = None