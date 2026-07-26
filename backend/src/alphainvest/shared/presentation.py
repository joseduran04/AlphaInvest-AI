from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    request_id: str | None = None


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class HealthData(BaseModel):
    status: str
    service: str
    version: str
    environment: str
