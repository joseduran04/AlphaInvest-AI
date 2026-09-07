from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.infrastructure.database.session import (
    get_db_session,
)
from alphainvest.modules.ai.application.analysis_request_service import (
    AnalysisRequestService,
)
from alphainvest.modules.ai.application.service import (
    AIService,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.auth.presentation.dependencies import (
    AuthContext,
    require_permission,
)


def get_ai_service(
    session: AsyncSession = Depends(get_db_session),
) -> AIService:
    repository = AIRepository(session)

    return AIService(repository)


def get_analysis_request_service(
    session: AsyncSession = Depends(get_db_session),
) -> AnalysisRequestService:
    repository = AIRepository(session)

    return AnalysisRequestService(repository)


AnalysisRequestServiceDependency = Annotated[
    AnalysisRequestService,
    Depends(get_analysis_request_service),
]


AIServiceDependency = Annotated[
    AIService,
    Depends(get_ai_service),
]

AIModelReadContext = Annotated[
    AuthContext,
    Depends(require_permission("modelos.leer")),
]

ModelVersionReadContext = Annotated[
    AuthContext,
    Depends(
        require_permission("versiones_modelo.leer")
    ),
]

AIModelAdminContext = Annotated[
    AuthContext,
    Depends(
        require_permission("modelos.administrar")
    ),
]

ModelVersionAdminContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "versiones_modelo.administrar"
        )
    ),
]

ModelVersionActivateContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "versiones_modelo.activar"
        )
    ),
]


AnalysisRequestCreateContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "analisis.solicitar"
        )
    ),
]


AnalysisRequestReadContext = Annotated[
    AuthContext,
    Depends(
        require_permission(
            "analisis.leer"
        )
    ),
]