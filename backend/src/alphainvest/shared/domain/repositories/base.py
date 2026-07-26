from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

EntityT = TypeVar("EntityT")


class AbstractRepository(ABC, Generic[EntityT]):
    """Contrato mínimo; cada dominio ampliará únicamente lo que necesite."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> EntityT | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, entity: EntityT) -> EntityT:
        raise NotImplementedError
