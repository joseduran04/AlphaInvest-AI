class AIError(Exception):
    """Excepción base del módulo de inteligencia artificial."""


class AIModelNotFoundError(AIError):
    """El modelo de inteligencia artificial solicitado no existe."""


class ModelVersionNotFoundError(AIError):
    """La versión del modelo solicitada no existe."""


class ActiveModelVersionNotFoundError(AIError):
    """No existe una versión activa disponible para el modelo."""


class ModelVersionAlreadyExistsError(AIError):
    """Ya existe una versión o checksum registrado."""


class AIModelUpdateError(AIError):
    """No fue posible actualizar el modelo de IA."""


class AIModelNotActiveError(AIError):
    """El modelo no está habilitado para utilizar versiones activas."""


class ModelVersionActivationError(AIError):
    """No fue posible activar la versión del modelo."""


class AIFeatureDataUnavailableError(AIError):
    """No existen datos suficientes para construir features de IA."""


class AIArtifactNotFoundError(AIError):
    """El artefacto registrado del modelo no existe."""


class AIArtifactIntegrityError(AIError):
    """El checksum del artefacto no coincide con el registrado."""


class AIArtifactLoadError(AIError):
    """El artefacto no pudo cargarse como modelo de IA."""


class AnalysisRequestNotFoundError(AIError):
    """La solicitud de análisis no existe."""


class AnalysisRequestPersistenceError(AIError):
    """No fue posible persistir la solicitud de análisis."""


class AnalysisRequestInvalidStateError(AIError):
    """La solicitud no se encuentra en un estado procesable."""


class AnalysisRequestInvalidParametersError(AIError):
    """Los parámetros de la solicitud de análisis son inválidos."""


class AnalysisRequestUnsupportedError(AIError):
    """La solicitud no es compatible con el procesador actual."""


class AnalysisRequestProcessingError(AIError):
    """La ejecución de la solicitud de análisis falló."""


class AnalysisResultNotReadyError(Exception):
    """La solicitud todavía no dispone de resultado."""


class AnalysisResultNotFoundError(Exception):
    """No existe resultado persistido para la solicitud."""