from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AppException(Exception):
    message: str
    code: str = "application_error"
    status_code: int = 400
    details: dict[str, Any] | None = None


class ResourceNotFoundError(AppException):
    def __init__(self, message: str = "Recurso no encontrado") -> None:
        super().__init__(message=message, code="resource_not_found", status_code=404)
