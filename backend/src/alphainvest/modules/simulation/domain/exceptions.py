class SimulationError(Exception):
    """Error base del módulo Simulation."""


class SimulationConfigurationNotFoundError(
    SimulationError
):
    """La configuración solicitada no existe."""


class SimulationConfigurationNameAlreadyExistsError(
    SimulationError
):
    """El usuario ya tiene una configuración con ese nombre."""


class SimulationConfigurationUnavailableError(
    SimulationError
):
    """La configuración no admite la operación solicitada."""


class SimulationPortfolioNotFoundError(
    SimulationError
):
    """El portafolio asociado no existe."""


class SimulationPortfolioUnavailableError(
    SimulationError
):
    """El portafolio no admite su uso en la simulación."""


class SimulationAssetNotFoundError(
    SimulationError
):
    """El activo solicitado no existe."""


class SimulationAssetUnavailableError(
    SimulationError
):
    """El activo no admite su uso en la simulación."""


class SimulationHistoricalSourceUnavailableError(
    SimulationError
):
    """La fuente histórica requerida no está disponible."""


class SimulationHistoricalPriceNotFoundError(
    SimulationError
):
    """No existen precios suficientes para el activo."""


class SimulationConfigurationAssetNotFoundError(
    SimulationError
):
    """El activo no está en la configuración."""


class SimulationConfigurationAssetAlreadyExistsError(
    SimulationError
):
    """El activo ya pertenece a la configuración."""


class SimulationDistributionInvalidError(
    SimulationError
):
    """La distribución de activos no es válida."""


class SimulationExecutionNotFoundError(
    SimulationError
):
    """La ejecución solicitada no existe."""


class SimulationExecutionUnavailableError(
    SimulationError
):
    """La ejecución no admite la operación solicitada."""


class SimulationExecutionAlreadyActiveError(
    SimulationError
):
    """La configuración ya tiene una ejecución activa."""


class SimulationModelVersionNotFoundError(
    SimulationError
):
    """La versión de modelo solicitada no existe."""


class SimulationModelVersionUnavailableError(
    SimulationError
):
    """La versión de modelo no admite su uso."""