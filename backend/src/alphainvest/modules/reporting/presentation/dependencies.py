from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.infrastructure.database.session import (
    get_db_session,
)
from alphainvest.modules.auth.presentation.dependencies import (
    AuthContext,
    require_permission,
)
from alphainvest.modules.reporting.application.reporting_export_service import (
    ReportingExportService,
)
from alphainvest.modules.reporting.application.reporting_service import (
    ReportingService,
)
from alphainvest.modules.reporting.infrastructure.repository import (
    ReportingRepository,
)


def get_reporting_service(
    session: AsyncSession = Depends(get_db_session),
) -> ReportingService:
    repository = ReportingRepository(session)

    return ReportingService(repository)


def get_reporting_export_service() -> ReportingExportService:
    return ReportingExportService()


ReportingServiceDependency = Annotated[
    ReportingService,
    Depends(get_reporting_service),
]


ReportingExportServiceDependency = Annotated[
    ReportingExportService,
    Depends(get_reporting_export_service),
]


report_read_permission = require_permission(
    "reportes.leer"
)


ReportReadContext = Annotated[
    AuthContext,
    Depends(report_read_permission),
]


report_admin_permission = require_permission(
    "reportes.administrar"
)


ReportAdminContext = Annotated[
    AuthContext,
    Depends(report_admin_permission),
]


report_export_permission = require_permission(
    "reportes.exportar"
)


ReportExportContext = Annotated[
    AuthContext,
    Depends(report_export_permission),
]