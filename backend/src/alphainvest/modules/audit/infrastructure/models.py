from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import CITEXT, INET, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from alphainvest.infrastructure.database.base import Base


class SecurityEventModel(Base):
    __tablename__ = "eventos_seguridad"
    __table_args__ = {"schema": "audit"}
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    usuario_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("auth.usuarios.id", ondelete="SET NULL")
    )
    correo_intentado: Mapped[str | None] = mapped_column(CITEXT)
    tipo_evento: Mapped[str] = mapped_column(String(50))
    severidad: Mapped[str] = mapped_column(String(20), server_default="BAJA")
    resultado: Mapped[str] = mapped_column(String(20))
    direccion_ip: Mapped[IPv4Address | IPv6Address | None] = mapped_column(INET)
    agente_usuario: Mapped[str | None] = mapped_column(Text)
    recurso: Mapped[str | None] = mapped_column(String(200))
    descripcion: Mapped[str] = mapped_column(Text)
    metadatos: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    fecha_evento: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    revisado: Mapped[bool] = mapped_column(Boolean, server_default="false")
    revisado_por: Mapped[UUID | None] = mapped_column(
        ForeignKey("auth.usuarios.id", ondelete="SET NULL")
    )
    fecha_revision: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    observaciones_revision: Mapped[str | None] = mapped_column(Text)
