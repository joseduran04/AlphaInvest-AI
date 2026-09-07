from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NewsPersistenceResult:
    document_id: str
    created: bool
    deduplication_key: str