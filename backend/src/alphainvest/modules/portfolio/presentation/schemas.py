from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from alphainvest.modules.portfolio.domain.enums import (
    PortfolioStatus,
    PortfolioType,
    PositionStatus,
)


class PortfolioCreateRequest(BaseModel):
    nombre: str = Field(
        min_length=1,
        max_length=150,
    )
    descripcion: str | None = Field(
        default=None,
        max_length=2000,
    )
    moneda_base: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        pattern=r"^[A-Za-z]{3}$",
    )
    capital_inicial: Decimal = Field(
        ge=0,
        max_digits=24,
        decimal_places=8,
    )
    tipo: PortfolioType = PortfolioType.VIRTUAL
    fecha_inicio: date | None = None

    @field_validator(
        "nombre",
        "descripcion",
        mode="before",
    )
    @classmethod
    def strip_text(
        cls,
        value: object,
    ) -> object:
        if isinstance(value, str):
            stripped = value.strip()

            if not stripped:
                return None

            return stripped

        return value

    @field_validator("nombre")
    @classmethod
    def validate_name(
        cls,
        value: str | None,
    ) -> str:
        if value is None:
            raise ValueError(
                "El nombre no puede estar vacío"
            )

        return value

    @field_validator("moneda_base")
    @classmethod
    def normalize_currency(
        cls,
        value: str,
    ) -> str:
        return value.upper()


class PortfolioUpdateRequest(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    descripcion: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator(
        "nombre",
        mode="before",
    )
    @classmethod
    def strip_name(
        cls,
        value: object,
    ) -> object:
        if isinstance(value, str):
            stripped = value.strip()

            if not stripped:
                raise ValueError(
                    "El nombre no puede estar vacío"
                )

            return stripped

        return value

    @field_validator(
        "descripcion",
        mode="before",
    )
    @classmethod
    def strip_description(
        cls,
        value: object,
    ) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None

        return value

    @model_validator(mode="after")
    def validate_at_least_one_field(
        self,
    ) -> "PortfolioUpdateRequest":
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo"
            )

        return self


class PortfolioResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    usuario_id: UUID
    nombre: str
    descripcion: str | None
    moneda_base: str
    capital_inicial: Decimal
    saldo_efectivo: Decimal
    tipo: PortfolioType
    estado: PortfolioStatus
    fecha_inicio: date
    fecha_cierre: date | None
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class PortfolioListResponse(BaseModel):
    items: list[PortfolioResponse]
    total: int
    limit: int
    offset: int
    estado: PortfolioStatus | None


class PortfolioCloseResponse(BaseModel):
    id: UUID
    estado: PortfolioStatus
    fecha_cierre: date


class PositionCreateRequest(BaseModel):
    activo_id: UUID
    cantidad: Decimal = Field(
        gt=0,
        max_digits=24,
        decimal_places=8,
    )
    precio_promedio_compra: Decimal = Field(
        gt=0,
        max_digits=20,
        decimal_places=8,
    )
    fecha_apertura: datetime | None = None


class PositionUpdateRequest(BaseModel):
    cantidad: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=24,
        decimal_places=8,
    )
    precio_promedio_compra: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=20,
        decimal_places=8,
    )
    fecha_apertura: datetime | None = None

    @model_validator(mode="after")
    def validate_at_least_one_field(
        self,
    ) -> "PositionUpdateRequest":
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo"
            )

        return self


class PositionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    portafolio_id: UUID
    activo_id: UUID
    cantidad: Decimal
    precio_promedio_compra: Decimal
    costo_total: Decimal
    precio_actual: Decimal | None
    valor_actual: Decimal | None
    ganancia_perdida: Decimal | None
    rendimiento_porcentaje: Decimal | None
    moneda: str
    estado: PositionStatus
    fecha_apertura: datetime
    fecha_actualizacion: datetime
    fecha_cierre: datetime | None


class PositionListResponse(BaseModel):
    items: list[PositionResponse]
    total: int


class PortfolioSummaryResponse(BaseModel):
    portafolio_id: UUID
    usuario_id: UUID
    portafolio_nombre: str
    descripcion: str | None
    moneda_base: str
    capital_inicial: Decimal
    saldo_efectivo: Decimal
    tipo: PortfolioType
    estado: PortfolioStatus
    fecha_inicio: date
    fecha_cierre: date | None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    posiciones_abiertas: int
    posiciones_totales: int
    capital_invertido: Decimal
    valor_posiciones: Decimal
    valor_total_estimado: Decimal
    ganancia_perdida_posiciones: Decimal
    ganancia_perdida_total: Decimal
    rendimiento_estimado_porcentaje: Decimal | None


class PortfolioLatestValuationResponse(BaseModel):
    portafolio_id: UUID
    fecha_hora: datetime
    saldo_efectivo: Decimal
    valor_posiciones: Decimal
    valor_total: Decimal
    capital_invertido: Decimal
    ganancia_perdida: Decimal
    rendimiento_porcentaje: Decimal
    moneda: str
    fecha_registro: datetime


class PortfolioOverviewResponse(BaseModel):
    resumen: PortfolioSummaryResponse
    ultima_valoracion: (
        PortfolioLatestValuationResponse | None
    )


class AssetAllocationItemResponse(BaseModel):
    activo_id: UUID
    simbolo: str
    nombre: str
    sector: str | None
    industria: str | None
    cantidad: Decimal
    valor_referencia: Decimal
    porcentaje: Decimal


class AssetAllocationResponse(BaseModel):
    portafolio_id: UUID
    moneda_base: str
    valor_total_distribuido: Decimal
    items: list[AssetAllocationItemResponse]


class SectorAllocationItemResponse(BaseModel):
    sector: str
    posiciones: int
    valor_referencia: Decimal
    porcentaje: Decimal


class SectorAllocationResponse(BaseModel):
    portafolio_id: UUID
    moneda_base: str
    valor_total_distribuido: Decimal
    items: list[SectorAllocationItemResponse]


class PortfolioValuationCreateRequest(BaseModel):
    fecha_hora: datetime | None = None
    detalle: dict[str, object] | None = None


class PortfolioValuationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    portafolio_id: UUID
    fecha_hora: datetime
    saldo_efectivo: Decimal
    valor_posiciones: Decimal
    valor_total: Decimal
    capital_invertido: Decimal
    ganancia_perdida: Decimal
    rendimiento_porcentaje: Decimal | None
    moneda: str
    detalle: dict[str, object] | None
    fecha_registro: datetime


class PortfolioValuationListResponse(BaseModel):
    items: list[PortfolioValuationResponse]
    total: int
    limit: int
    offset: int