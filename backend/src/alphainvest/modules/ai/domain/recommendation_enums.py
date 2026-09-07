from enum import StrEnum


class RecommendationType(StrEnum):
    WATCH = "OBSERVAR"
    SIMULATED_BUY = "COMPRAR_SIMULADO"
    HOLD = "MANTENER"
    REDUCE = "REDUCIR"
    SIMULATED_SELL = "VENDER_SIMULADO"
    DIVERSIFY = "DIVERSIFICAR"
    REBALANCE = "REBALANCEAR"
    AVOID = "EVITAR"


class RecommendationRiskLevel(StrEnum):
    VERY_LOW = "MUY_BAJO"
    LOW = "BAJO"
    MEDIUM = "MEDIO"
    HIGH = "ALTO"
    VERY_HIGH = "MUY_ALTO"


class RecommendationStatus(StrEnum):
    GENERATED = "GENERADA"
    SHOWN = "MOSTRADA"
    ACCEPTED = "ACEPTADA"
    REJECTED = "RECHAZADA"
    EXPIRED = "EXPIRADA"
    WITHDRAWN = "RETIRADA"


class RecommendationAssetAction(StrEnum):
    WATCH = "OBSERVAR"
    ADD = "AGREGAR"
    HOLD = "MANTENER"
    INCREASE = "AUMENTAR"
    REDUCE = "REDUCIR"
    REMOVE = "RETIRAR"
    AVOID = "EVITAR"


class AnalysisEvidenceType(StrEnum):
    PRICE = "PRECIO"
    INDICATOR = "INDICADOR"
    SENTIMENT = "SENTIMIENTO"
    FUNDAMENTAL = "FUNDAMENTAL"
    RISK_PROFILE = "PERFIL_RIESGO"
    SIMULATION = "SIMULACION"
    PORTFOLIO = "PORTAFOLIO"
    MODEL = "MODELO"
    OTHER = "OTRA"


class EvidenceContribution(StrEnum):
    POSITIVE = "POSITIVA"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVA"