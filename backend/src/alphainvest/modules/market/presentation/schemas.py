from datetime import date as DateType
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from alphainvest.modules.market.domain.enums import (
    AssetStatus,
)


class MarketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str = Field(validation_alias="codigo")
    name: str = Field(validation_alias="nombre")
    country: str = Field(validation_alias="pais")
    timezone: str = Field(
        validation_alias="zona_horaria"
    )
    currency: str = Field(validation_alias="moneda")
    active: bool = Field(validation_alias="activo")


class MarketListResponse(BaseModel):
    items: list[MarketResponse]
    total: int


class AssetTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str = Field(validation_alias="codigo")
    name: str = Field(validation_alias="nombre")
    description: str | None = Field(
        default=None,
        validation_alias="descripcion",
    )
    active: bool = Field(validation_alias="activo")


class AssetTypeListResponse(BaseModel):
    items: list[AssetTypeResponse]
    total: int


class AssetMarketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str = Field(validation_alias="codigo")
    name: str = Field(validation_alias="nombre")
    country: str = Field(validation_alias="pais")
    currency: str = Field(validation_alias="moneda")


class AssetTypeSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str = Field(validation_alias="codigo")
    name: str = Field(validation_alias="nombre")


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    symbol: str = Field(validation_alias="simbolo")
    name: str = Field(validation_alias="nombre")
    description: str | None = Field(
        default=None,
        validation_alias="descripcion",
    )
    currency: str = Field(validation_alias="moneda")
    sector: str | None
    industry: str | None = Field(
        default=None,
        validation_alias="industria",
    )
    isin: str | None
    status: AssetStatus = Field(
        validation_alias="estado"
    )
    listed_at: datetime = Field(
        validation_alias="fecha_alta"
    )
    updated_at: datetime = Field(
        validation_alias="fecha_actualizacion"
    )
    market: AssetMarketResponse = Field(
        validation_alias="mercado"
    )
    asset_type: AssetTypeSummaryResponse = Field(
        validation_alias="tipo_activo"
    )


class AssetListResponse(BaseModel):
    items: list[AssetResponse]
    total: int
    limit: int
    offset: int

class FinancialSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str = Field(validation_alias="nombre")
    provider: str = Field(validation_alias="proveedor")
    base_url: str | None = Field(
        default=None,
        validation_alias="url_base",
    )
    priority: int = Field(validation_alias="prioridad")
    active: bool = Field(validation_alias="activa")
    requires_api_key: bool = Field(
        validation_alias="requiere_api_key"
    )
    requests_per_minute: int | None = Field(
        default=None,
        validation_alias="limite_consultas_minuto",
    )
    last_request_at: datetime | None = Field(
        default=None,
        validation_alias="ultima_consulta",
    )


class FinancialSourceListResponse(BaseModel):
    items: list[FinancialSourceResponse]
    total: int


class PriceSourceSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str = Field(validation_alias="nombre")
    provider: str = Field(validation_alias="proveedor")


class HistoricalPriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: DateType = Field(validation_alias="fecha")
    open: Decimal | None = Field(
        default=None,
        validation_alias="apertura",
    )
    high: Decimal | None = Field(
        default=None,
        validation_alias="maximo",
    )
    low: Decimal | None = Field(
        default=None,
        validation_alias="minimo",
    )
    close: Decimal = Field(validation_alias="cierre")
    adjusted_close: Decimal | None = Field(
        default=None,
        validation_alias="cierre_ajustado",
    )
    volume: Decimal | None = Field(
        default=None,
        validation_alias="volumen",
    )
    currency: str = Field(validation_alias="moneda")
    registered_at: datetime = Field(
        validation_alias="fecha_registro",
    )
    source: PriceSourceSummaryResponse = Field(
        validation_alias="fuente",
    )


class HistoricalPriceListResponse(BaseModel):
    asset_id: UUID
    items: list[HistoricalPriceResponse]
    total: int
    limit: int
    offset: int
    start_date: DateType | None
    end_date: DateType | None


class LatestPriceResponse(BaseModel):
    asset_id: UUID
    symbol: str
    price: HistoricalPriceResponse


class PriceSynchronizationResponse(BaseModel):
    asset_id: UUID
    symbol: str
    source_id: UUID
    source_name: str
    received: int
    created: int
    updated: int
    synchronized_at: datetime
    first_date: DateType | None
    last_date: DateType | None