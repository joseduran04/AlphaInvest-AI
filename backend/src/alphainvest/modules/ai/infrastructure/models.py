from uuid import UUID

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from alphainvest.infrastructure.database.base import Base


class ModelVersionModel(Base):
    """
    Referencia ORM mínima para la tabla ai.versiones_modelo.

    Inicialmente se registra únicamente la llave primaria para que
    SQLAlchemy pueda resolver las relaciones y llaves foráneas desde
    otros módulos.
    """

    __tablename__ = "versiones_modelo"
    __table_args__ = {
        "schema": "ai",
    }

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )