from datetime import date, datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from alphainvest.modules.simulation.domain.enums import (
    ContributionFrequency,
    SimulationConfigurationStatus,
    SimulationExecutionStatus,
    SimulationType,
)


class SimulationConfigurationCreateRequest(
    BaseModel
):
    portafolio_id: UUID | None = None

    nombre: str = Field(
        min_length=1,
        max_length=150,
    )
    descripcion: str | None = Field(
        default=None,
        max_length=2000,
    )

    tipo_simulacion: SimulationType

    capital_inicial: Decimal = Field(
        gt=0,
        max_digits=24,
        decimal_places=8,
    )
    moneda_base: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
    )

    fecha_inicio: date
    fecha_fin: date

    aportacion_periodica: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        max_digits=24,
        decimal_places=8,
    )
    frecuencia_aportacion: (
        ContributionFrequency | None
    ) = None

    comision_porcentaje: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        le=100,
        max_digits=12,
        decimal_places=8,
    )
    inflacion_anual: Decimal | None = Field(
        default=None,
        gt=-100,
        max_digits=12,
        decimal_places=8,
    )
    tasa_libre_riesgo: Decimal | None = Field(
        default=None,
        gt=-100,
        max_digits=12,
        decimal_places=8,
    )

    numero_escenarios: int = Field(
        default=1,
        ge=1,
        le=1_000_000,
    )
    semilla_aleatoria: int | None = None
    parametros: dict[str, object] | None = None

    @field_validator(
        "nombre",
        "descripcion",
    )
    @classmethod
    def validate_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "El texto no puede estar vacío"
            )

        return normalized

    @field_validator("moneda_base")
    @classmethod
    def normalize_currency(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip().upper()

        if (
            len(normalized) != 3
            or not normalized.isalpha()
        ):
            raise ValueError(
                "La moneda debe usar tres letras"
            )

        return normalized

    @model_validator(mode="after")
    def validate_configuration(
        self,
    ) -> Self:
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError(
                "La fecha final debe ser posterior "
                "a la fecha inicial"
            )

        if self.aportacion_periodica == 0:
            if self.frecuencia_aportacion is not None:
                raise ValueError(
                    "No debe indicar una frecuencia "
                    "cuando la aportación es cero"
                )
        elif self.frecuencia_aportacion is None:
            raise ValueError(
                "Debe indicar la frecuencia de "
                "la aportación periódica"
            )

        if (
            self.tipo_simulacion
            == SimulationType.MONTE_CARLO
            and self.numero_escenarios <= 1
        ):
            raise ValueError(
                "Monte Carlo requiere más de "
                "un escenario"
            )

        return self


class SimulationConfigurationUpdateRequest(
    BaseModel
):
    portafolio_id: UUID | None = None

    nombre: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    descripcion: str | None = Field(
        default=None,
        max_length=2000,
    )

    tipo_simulacion: SimulationType | None = None

    capital_inicial: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=24,
        decimal_places=8,
    )
    moneda_base: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    fecha_inicio: date | None = None
    fecha_fin: date | None = None

    aportacion_periodica: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=24,
        decimal_places=8,
    )
    frecuencia_aportacion: (
        ContributionFrequency | None
    ) = None

    comision_porcentaje: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        max_digits=12,
        decimal_places=8,
    )
    inflacion_anual: Decimal | None = Field(
        default=None,
        gt=-100,
        max_digits=12,
        decimal_places=8,
    )
    tasa_libre_riesgo: Decimal | None = Field(
        default=None,
        gt=-100,
        max_digits=12,
        decimal_places=8,
    )

    numero_escenarios: int | None = Field(
        default=None,
        ge=1,
        le=1_000_000,
    )
    semilla_aleatoria: int | None = None
    parametros: dict[str, object] | None = None

    @field_validator(
        "nombre",
        "descripcion",
    )
    @classmethod
    def validate_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "El texto no puede estar vacío"
            )

        return normalized

    @field_validator("moneda_base")
    @classmethod
    def normalize_currency(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip().upper()

        if (
            len(normalized) != 3
            or not normalized.isalpha()
        ):
            raise ValueError(
                "La moneda debe usar tres letras"
            )

        return normalized

    @model_validator(mode="after")
    def validate_at_least_one_field(
        self,
    ) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo"
            )

        return self


class SimulationConfigurationResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    usuario_id: UUID
    portafolio_id: UUID | None

    nombre: str
    descripcion: str | None
    tipo_simulacion: SimulationType

    capital_inicial: Decimal
    moneda_base: str

    fecha_inicio: date
    fecha_fin: date

    aportacion_periodica: Decimal
    frecuencia_aportacion: (
        ContributionFrequency | None
    )

    comision_porcentaje: Decimal
    inflacion_anual: Decimal | None
    tasa_libre_riesgo: Decimal | None

    numero_escenarios: int
    semilla_aleatoria: int | None
    parametros: dict[str, object] | None

    estado: SimulationConfigurationStatus

    fecha_creacion: datetime
    fecha_actualizacion: datetime


class SimulationConfigurationListResponse(
    BaseModel
):
    items: list[
        SimulationConfigurationResponse
    ]
    total: int
    limit: int
    offset: int
    estado: (
        SimulationConfigurationStatus | None
    ) = None


class SimulationConfigurationArchiveResponse(
    BaseModel
):
    id: UUID
    estado: SimulationConfigurationStatus


class SimulationConfigurationAssetCreateRequest(
    BaseModel
):
    activo_id: UUID

    porcentaje_asignado: Decimal = Field(
        gt=0,
        le=100,
        max_digits=12,
        decimal_places=8,
    )

    monto_inicial: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=24,
        decimal_places=8,
    )

    precio_inicial: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=20,
        decimal_places=8,
    )

    orden: int = Field(
        gt=0,
    )

    parametros: dict[str, object] | None = None


class SimulationConfigurationAssetUpdateRequest(
    BaseModel
):
    porcentaje_asignado: Decimal | None = Field(
        default=None,
        gt=0,
        le=100,
        max_digits=12,
        decimal_places=8,
    )

    monto_inicial: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=24,
        decimal_places=8,
    )

    precio_inicial: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=20,
        decimal_places=8,
    )

    orden: int | None = Field(
        default=None,
        gt=0,
    )

    parametros: dict[str, object] | None = None

    @model_validator(mode="after")
    def validate_at_least_one_field(
        self,
    ) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo"
            )

        return self


class SimulationConfigurationAssetResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True
    )

    configuracion_id: UUID
    activo_id: UUID
    porcentaje_asignado: Decimal
    monto_inicial: Decimal | None
    precio_inicial: Decimal | None
    orden: int
    parametros: dict[str, object] | None
    fecha_agregado: datetime


class SimulationConfigurationAssetListResponse(
    BaseModel
):
    configuracion_id: UUID
    items: list[
        SimulationConfigurationAssetResponse
    ]
    total: int
    porcentaje_total: Decimal
    monto_total: Decimal
    distribucion_valida: bool


class SimulationDistributionStatusResponse(
    BaseModel
):
    configuracion_id: UUID
    estado: SimulationConfigurationStatus
    cantidad_activos: int
    porcentaje_total: Decimal
    monto_total: Decimal
    capital_inicial: Decimal
    distribucion_valida: bool


class SimulationConfigurationReadyResponse(
    BaseModel
):
    id: UUID
    estado: SimulationConfigurationStatus
    distribucion: SimulationDistributionStatusResponse


class SimulationExecutionCreateRequest(
    BaseModel
):
    configuracion_id: UUID

    version_modelo_id: UUID | None = None

    parametros_ejecucion: (
        dict[str, object] | None
    ) = None


class SimulationExecutionResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    configuracion_id: UUID
    usuario_id: UUID
    version_modelo_id: UUID | None

    estado: SimulationExecutionStatus
    porcentaje_progreso: Decimal

    fecha_solicitud: datetime
    fecha_inicio: datetime | None
    fecha_fin: datetime | None

    mensaje_error: str | None

    parametros_ejecucion: (
        dict[str, object] | None
    )

    identificador_proceso: str | None


class SimulationAssetResultResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    resultado_id: UUID
    activo_id: UUID

    porcentaje_asignado: Decimal
    capital_asignado: Decimal

    cantidad_inicial: Decimal | None

    precio_inicial: Decimal
    precio_final: Decimal

    valor_final: Decimal
    ganancia_perdida: Decimal
    rendimiento_porcentaje: Decimal

    volatilidad: Decimal | None
    maximo_drawdown_porcentaje: (
        Decimal | None
    )

    detalle: dict[str, object] | None

    fecha_registro: datetime


class SimulationResultResponse(
    BaseModel
):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    ejecucion_id: UUID

    capital_inicial: Decimal
    aportaciones_totales: Decimal
    capital_final: Decimal
    ganancia_perdida: Decimal

    rendimiento_total_porcentaje: Decimal
    rendimiento_anualizado_porcentaje: (
        Decimal | None
    )
    volatilidad_anualizada: Decimal | None
    indice_sharpe: Decimal | None
    maximo_drawdown_porcentaje: (
        Decimal | None
    )

    valor_en_riesgo: Decimal | None
    nivel_confianza_var: Decimal | None

    mejor_escenario: Decimal | None
    peor_escenario: Decimal | None
    mediana_escenarios: Decimal | None
    probabilidad_ganancia: Decimal | None

    moneda: str
    resumen: dict[str, object] | None

    fecha_registro: datetime

    activos: list[
        SimulationAssetResultResponse
    ]


class SimulationExecutionListResponse(
    BaseModel
):
    items: list[SimulationExecutionResponse]
    total: int
    limit: int
    offset: int
    estado: SimulationExecutionStatus | None = None
    configuracion_id: UUID | None = None


class SimulationExecutionCancelResponse(
    BaseModel
):
    id: UUID
    estado: SimulationExecutionStatus
    porcentaje_progreso: Decimal
    fecha_inicio: datetime | None
    fecha_fin: datetime