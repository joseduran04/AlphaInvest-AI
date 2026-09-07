from datetime import date as DateType
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from alphainvest.modules.market.domain.enums import (
    AssetStatus,
)
from alphainvest.modules.market.domain.indicator_enums import (
    FinancialIndicatorType,
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
    execution_id: UUID
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


class IndicatorCalculationSpec(BaseModel):
    indicator_type: FinancialIndicatorType

    period: int | None = Field(
        default=None,
        ge=2,
        le=500,
    )

    fast_period: int | None = Field(
        default=None,
        ge=2,
        le=500,
    )

    slow_period: int | None = Field(
        default=None,
        ge=2,
        le=500,
    )

    signal_period: int | None = Field(
        default=None,
        ge=2,
        le=500,
    )

    @model_validator(mode="after")
    def validate_indicator_parameters(
        self,
    ) -> "IndicatorCalculationSpec":
        if self.indicator_type in {
            FinancialIndicatorType.MACD_SIGNAL,
            FinancialIndicatorType.MACD_HISTOGRAM,
        }:
            raise ValueError(
                "MACD_SIGNAL y MACD_HISTOGRAMA "
                "no se solicitan directamente"
            )

        if (
            self.indicator_type
            == FinancialIndicatorType.MACD
        ):
            if (
                self.fast_period is None
                or self.slow_period is None
                or self.signal_period is None
            ):
                raise ValueError(
                    "MACD requiere fast_period, "
                    "slow_period y signal_period"
                )

            if self.slow_period <= self.fast_period:
                raise ValueError(
                    "slow_period debe ser mayor "
                    "que fast_period"
                )

            if self.period is not None:
                raise ValueError(
                    "MACD no utiliza el campo period"
                )

            return self

        if self.period is None:
            raise ValueError(
                "El indicador requiere el campo period"
            )

        if any(
            value is not None
            for value in (
                self.fast_period,
                self.slow_period,
                self.signal_period,
            )
        ):
            raise ValueError(
                "Los periodos MACD solo pueden utilizarse "
                "con el indicador MACD"
            )

        return self


class IndicatorCalculationRequest(BaseModel):
    source_id: UUID
    calculations: list[IndicatorCalculationSpec] = Field(
        min_length=1,
        max_length=20,
    )

    @model_validator(mode="after")
    def validate_unique_calculations(
        self,
    ) -> "IndicatorCalculationRequest":
        keys = [
            (
                calculation.indicator_type,
                calculation.period,
                calculation.fast_period,
                calculation.slow_period,
                calculation.signal_period,
            )
            for calculation in self.calculations
        ]

        if len(keys) != len(set(keys)):
            raise ValueError(
                "No se permiten cálculos duplicados"
            )

        return self


class IndicatorCalculationItemResponse(BaseModel):
    indicator_type: FinancialIndicatorType
    period: str
    calculated: int
    created: int
    updated: int
    first_date: DateType | None
    last_date: DateType | None


class IndicatorCalculationResponse(BaseModel):
    asset_id: UUID
    symbol: str
    source_id: UUID
    source_name: str
    total_calculated: int
    total_created: int
    total_updated: int
    items: list[IndicatorCalculationItemResponse]
    calculated_at: datetime


class FinancialIndicatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: UUID = Field(
        validation_alias="activo_id"
    )
    indicator_type: FinancialIndicatorType = Field(
        validation_alias="tipo_indicador"
    )
    date: DateType = Field(
        validation_alias="fecha"
    )
    value: Decimal = Field(
        validation_alias="valor"
    )
    period: str = Field(
        validation_alias="periodo"
    )
    parameters: dict[str, object] | None = Field(
        default=None,
        validation_alias="parametros",
    )
    calculation_source: str | None = Field(
        default=None,
        validation_alias="fuente_calculo",
    )
    calculated_at: datetime = Field(
        validation_alias="fecha_calculo"
    )


class FinancialIndicatorListResponse(BaseModel):
    asset_id: UUID
    items: list[FinancialIndicatorResponse]
    total: int
    limit: int
    offset: int
    indicator_type: FinancialIndicatorType | None
    period: str | None
    start_date: DateType | None
    end_date: DateType | None