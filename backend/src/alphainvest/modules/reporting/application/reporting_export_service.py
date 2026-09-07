import csv
from collections.abc import Sequence
from io import StringIO

from pydantic import BaseModel


class ReportingExportService:
    """Generación de reportes CSV en memoria."""

    @staticmethod
    def build_csv(
        *,
        items: Sequence[BaseModel],
        schema: type[BaseModel],
    ) -> str:
        field_names = list(
            schema.model_fields.keys()
        )

        output = StringIO(
            newline="",
        )

        # BOM UTF-8 para compatibilidad con Excel.
        output.write("\ufeff")

        writer = csv.DictWriter(
            output,
            fieldnames=field_names,
            extrasaction="ignore",
        )

        writer.writeheader()

        for item in items:
            writer.writerow(
                item.model_dump(
                    mode="json",
                )
            )

        return output.getvalue()