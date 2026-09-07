class PortfolioError(Exception):
    """Error base del módulo Portfolio."""


class PortfolioNotFoundError(PortfolioError):
    """El portafolio solicitado no existe."""


class PortfolioNameAlreadyExistsError(PortfolioError):
    """El usuario ya tiene un portafolio con ese nombre."""


class PortfolioUnavailableError(PortfolioError):
    """El portafolio no admite la operación solicitada."""


class PositionNotFoundError(PortfolioError):
    """La posición solicitada no existe."""


class PositionAlreadyExistsError(PortfolioError):
    """El activo ya tiene una posición en el portafolio."""


class PortfolioAssetNotFoundError(PortfolioError):
    """El activo solicitado no existe."""


class PortfolioAssetUnavailableError(PortfolioError):
    """El activo solicitado no está disponible."""


class WatchlistNotFoundError(PortfolioError):
    """La lista de seguimiento solicitada no existe."""


class WatchlistNameAlreadyExistsError(PortfolioError):
    """El usuario ya tiene una lista con ese nombre."""