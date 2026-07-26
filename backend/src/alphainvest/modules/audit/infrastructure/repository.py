from ipaddress import ip_address
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.modules.audit.infrastructure.models import SecurityEventModel


class SecurityAuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record(
        self,
        *,
        event_type: str,
        result: str,
        description: str,
        user_id: UUID | None = None,
        email: str | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
        severity: str = "BAJA",
        resource: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        parsed = None
        if ip:
            try:
                parsed = ip_address(ip)
            except ValueError:
                parsed = None
        self.session.add(
            SecurityEventModel(
                usuario_id=user_id,
                correo_intentado=email,
                tipo_evento=event_type,
                severidad=severity,
                resultado=result,
                direccion_ip=parsed,
                agente_usuario=user_agent,
                recurso=resource,
                descripcion=description,
                metadatos=metadata,
            )
        )
