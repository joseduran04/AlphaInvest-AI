from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class NewsStorageResult:
    reference_id: UUID
    mongo_document_id: str
    mongo_created: bool