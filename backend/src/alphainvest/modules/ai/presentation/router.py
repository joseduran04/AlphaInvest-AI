from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisType,
)
from alphainvest.modules.ai.domain.enums import (
    AIModelStatus,
)
from alphainvest.modules.ai.domain.exceptions import (
    ActiveModelVersionNotFoundError,
    AIModelNotActiveError,
    AIModelNotFoundError,
    AIModelUpdateError,
    AnalysisRequestInvalidParametersError,
    AnalysisRequestInvalidStateError,
    AnalysisRequestNotFoundError,
    AnalysisRequestPersistenceError,
    AnalysisResultNotFoundError,
    AnalysisResultNotReadyError,
    ModelVersionActivationError,
    ModelVersionAlreadyExistsError,
    ModelVersionNotFoundError,
)
from alphainvest.modules.ai.presentation.dependencies import (
    AIModelAdminContext,
    AIModelReadContext,
    AIServiceDependency,
    AnalysisRequestCreateContext,
    AnalysisRequestReadContext,
    AnalysisRequestServiceDependency,
    ModelVersionActivateContext,
    ModelVersionAdminContext,
    ModelVersionReadContext,
)
from alphainvest.modules.ai.presentation.schemas import (
    ActiveModelVersionResponse,
    AIModelListResponse,
    AIModelResponse,
    AIModelStatusUpdateRequest,
    AnalysisRequestResponse,
    AssetAnalysisRequestCreate,
    AssetAnalysisResultResponse,
    IntegralAnalysisRequestCreate,
    ModelVersionCreateRequest,
    ModelVersionListResponse,
    ModelVersionResponse,
    RecommendationRequestCreate,
    RecommendationResultResponse,
    SentimentAnalysisRequestCreate,
)

router = APIRouter(
    prefix="/ai",
    tags=["Inteligencia artificial"],
)


@router.post(
    "/analysis-requests",
    response_model=AnalysisRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar análisis de un activo",
    description=(
        "Registra una solicitud de análisis de un activo "
        "para procesamiento posterior por el motor de IA."
    ),
)
async def create_asset_analysis_request(
    request: AssetAnalysisRequestCreate,
    context: AnalysisRequestCreateContext,
    service: AnalysisRequestServiceDependency,
) -> AnalysisRequestResponse:
    try:
        return await service.create_asset_request(
            user_id=context.user.id,
            request=request,
        )

    except AnalysisRequestPersistenceError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/analysis-requests/{request_id}",
    response_model=AnalysisRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar solicitud de análisis",
    description=(
        "Consulta una solicitud de análisis perteneciente "
        "al usuario autenticado."
    ),
)
async def get_asset_analysis_request(
    request_id: UUID,
    context: AnalysisRequestReadContext,
    service: AnalysisRequestServiceDependency,
) -> AnalysisRequestResponse:
    try:
        return await service.get_user_request(
            request_id=request_id,
            user_id=context.user.id,
        )

    except AnalysisRequestNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/models",
    response_model=AIModelListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar modelos de inteligencia artificial",
    description=(
        "Consulta el catálogo de modelos de inteligencia "
        "artificial registrados en AlphaInvest AI."
    ),
)
async def list_ai_models(
    _: AIModelReadContext,
    service: AIServiceDependency,
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=150,
    ),
    model_type: str | None = Query(
        default=None,
        min_length=1,
        max_length=50,
        alias="type",
    ),
    model_status: AIModelStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> AIModelListResponse:
    return await service.list_models(
        search=search,
        model_type=model_type,
        status=model_status,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/models/{model_id}/status",
    response_model=AIModelResponse,
    status_code=status.HTTP_200_OK,
    summary="Cambiar estado de un modelo de IA",
)
async def update_ai_model_status(
    model_id: UUID,
    request: AIModelStatusUpdateRequest,
    _: AIModelAdminContext,
    service: AIServiceDependency,
) -> AIModelResponse:
    try:
        return await service.update_model_status(
            model_id=model_id,
            request=request,
        )
    except AIModelNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except AIModelUpdateError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/models/{model_id}/versions",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar versión de modelo de IA",
    description=(
        "Registra los metadatos de una versión entrenada. "
        "El registro no activa automáticamente la versión."
    ),
)
async def create_ai_model_version(
    model_id: UUID,
    request: ModelVersionCreateRequest,
    context: ModelVersionAdminContext,
    service: AIServiceDependency,
) -> ModelVersionResponse:
    try:
        return await service.create_model_version(
            model_id=model_id,
            user_id=context.user.id,
            request=request,
        )
    except AIModelNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ModelVersionAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/models/code/{code}",
    response_model=AIModelResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar modelo de IA por código",
)
async def get_ai_model_by_code(
    code: str,
    _: AIModelReadContext,
    service: AIServiceDependency,
) -> AIModelResponse:
    try:
        return await service.get_model_by_code(
            code=code
        )
    except AIModelNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/models/code/{code}/active-version",
    response_model=ActiveModelVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar versión activa por código de modelo",
)
async def get_active_model_version_by_code(
    code: str,
    _: ModelVersionReadContext,
    service: AIServiceDependency,
) -> ActiveModelVersionResponse:
    try:
        return await service.get_active_version_by_code(
            code=code
        )
    except AIModelNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ActiveModelVersionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/models/{model_id}",
    response_model=AIModelResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar modelo de inteligencia artificial",
)
async def get_ai_model(
    model_id: UUID,
    _: AIModelReadContext,
    service: AIServiceDependency,
) -> AIModelResponse:
    try:
        return await service.get_model(
            model_id=model_id
        )
    except AIModelNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/models/{model_id}/versions",
    response_model=ModelVersionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar versiones de un modelo de IA",
)
async def list_ai_model_versions(
    model_id: UUID,
    _: ModelVersionReadContext,
    service: AIServiceDependency,
) -> ModelVersionListResponse:
    try:
        return await service.list_model_versions(
            model_id=model_id
        )
    except AIModelNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/models/{model_id}/active-version",
    response_model=ActiveModelVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar versión activa de un modelo de IA",
)
async def get_active_model_version(
    model_id: UUID,
    _: ModelVersionReadContext,
    service: AIServiceDependency,
) -> ActiveModelVersionResponse:
    try:
        return await service.get_active_version(
            model_id=model_id
        )
    except (
        AIModelNotFoundError,
        ActiveModelVersionNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/versions/{version_id}",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar versión de modelo de IA",
)
async def get_ai_model_version(
    version_id: UUID,
    _: ModelVersionReadContext,
    service: AIServiceDependency,
) -> ModelVersionResponse:
    try:
        return await service.get_model_version(
            version_id=version_id
        )
    except ModelVersionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/versions/{version_id}/activate",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Activar versión de modelo de IA",
    description=(
        "Activa una versión para inferencia y desactiva "
        "la versión activa anterior del mismo modelo."
    ),
)
async def activate_ai_model_version(
    version_id: UUID,
    _: ModelVersionActivateContext,
    service: AIServiceDependency,
) -> ModelVersionResponse:
    try:
        return await service.activate_model_version(
            version_id=version_id
        )
    except (
        AIModelNotFoundError,
        ModelVersionNotFoundError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except AIModelNotActiveError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except ModelVersionActivationError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/versions/{version_id}/deactivate",
    response_model=ModelVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Desactivar versión de modelo de IA",
)
async def deactivate_ai_model_version(
    version_id: UUID,
    _: ModelVersionActivateContext,
    service: AIServiceDependency,
) -> ModelVersionResponse:
    try:
        return await service.deactivate_model_version(
            version_id=version_id
        )
    except ModelVersionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ModelVersionActivationError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/analysis-requests/{request_id}/result",
    response_model=AssetAnalysisResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar resultado de análisis",
    description=(
        "Consulta el resultado financiero y de IA "
        "persistido para una solicitud ACTIVO completada."
    ),
)
async def get_asset_analysis_result(
    request_id: UUID,
    context: AnalysisRequestReadContext,
    service: AnalysisRequestServiceDependency,
) -> AssetAnalysisResultResponse:
    try:
        return await service.get_user_result(
            request_id=request_id,
            user_id=context.user.id,
        )

    except AnalysisRequestNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except AnalysisResultNotReadyError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except AnalysisResultNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/sentiment-analysis-requests",
    response_model=AnalysisRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar análisis de sentimiento",
    description=(
        "Registra una solicitud de análisis de "
        "sentimiento para una noticia financiera."
    ),
)
async def create_sentiment_analysis_request(
    request: SentimentAnalysisRequestCreate,
    context: AnalysisRequestCreateContext,
    service: AnalysisRequestServiceDependency,
) -> AnalysisRequestResponse:
    try:
        return await service.create_sentiment_request(
            user_id=context.user.id,
            request=request,
        )

    except AnalysisRequestPersistenceError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/recommendation-requests",
    response_model=AnalysisRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar recomendación inteligente",
    description=(
        "Registra una solicitud de recomendación "
        "a partir de una predicción ACTIVO completada."
    ),
)
async def create_recommendation_request(
    request: RecommendationRequestCreate,
    context: AnalysisRequestCreateContext,
    service: AnalysisRequestServiceDependency,
) -> AnalysisRequestResponse:
    try:
        return await service.create_recommendation_request(
            user_id=context.user.id,
            request=request,
        )

    except AnalysisRequestNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except (
        AnalysisRequestInvalidParametersError,
        AnalysisRequestInvalidStateError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except AnalysisResultNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except AnalysisRequestPersistenceError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/recommendation-requests/{request_id}",
    response_model=AnalysisRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar solicitud de recomendación",
    description=(
        "Consulta una solicitud de recomendación "
        "perteneciente al usuario autenticado."
    ),
)
async def get_recommendation_request(
    request_id: UUID,
    context: AnalysisRequestReadContext,
    service: AnalysisRequestServiceDependency,
) -> AnalysisRequestResponse:
    try:
        response = await service.get_user_request(
            request_id=request_id,
            user_id=context.user.id,
        )

        if (
            response.analysis_type
            != AnalysisType.RECOMMENDATION
        ):
            raise AnalysisRequestNotFoundError(
                "La solicitud de recomendación "
                "no existe"
            )

        return response

    except AnalysisRequestNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/recommendation-requests/{request_id}/result",
    response_model=RecommendationResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar resultado de recomendación",
    description=(
        "Consulta la recomendación persistida, "
        "sus activos asociados y sus evidencias."
    ),
)
async def get_recommendation_result(
    request_id: UUID,
    context: AnalysisRequestReadContext,
    service: AnalysisRequestServiceDependency,
) -> RecommendationResultResponse:
    try:
        return await service.get_user_recommendation_result(
            request_id=request_id,
            user_id=context.user.id,
        )

    except AnalysisRequestNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except AnalysisResultNotReadyError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except AnalysisResultNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post(
    "/integral-analysis-requests",
    response_model=AnalysisRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar análisis integral",
    description=(
        "Registra un análisis integral a partir "
        "de una predicción ACTIVO completada y, "
        "opcionalmente, análisis de SENTIMIENTO."
    ),
)
async def create_integral_analysis_request(
    request: IntegralAnalysisRequestCreate,
    context: AnalysisRequestCreateContext,
    service: AnalysisRequestServiceDependency,
) -> AnalysisRequestResponse:
    try:
        return await service.create_integral_request(
            user_id=context.user.id,
            request=request,
        )

    except AnalysisRequestNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except (
        AnalysisRequestInvalidParametersError,
        AnalysisRequestInvalidStateError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except AnalysisResultNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except AnalysisRequestPersistenceError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/integral-analysis-requests/{request_id}",
    response_model=AnalysisRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar solicitud de análisis integral",
    description=(
        "Consulta una solicitud INTEGRAL "
        "perteneciente al usuario autenticado."
    ),
)
async def get_integral_analysis_request(
    request_id: UUID,
    context: AnalysisRequestReadContext,
    service: AnalysisRequestServiceDependency,
) -> AnalysisRequestResponse:
    try:
        response = await service.get_user_request(
            request_id=request_id,
            user_id=context.user.id,
        )

        if (
            response.analysis_type
            != AnalysisType.INTEGRAL
        ):
            raise AnalysisRequestNotFoundError(
                "La solicitud de análisis integral "
                "no existe"
            )

        return response

    except AnalysisRequestNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/integral-analysis-requests/{request_id}/result",
    response_model=RecommendationResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar resultado de análisis integral",
    description=(
        "Consulta la recomendación final generada "
        "por una solicitud de análisis INTEGRAL, "
        "incluyendo activos y evidencias."
    ),
)
async def get_integral_analysis_result(
    request_id: UUID,
    context: AnalysisRequestReadContext,
    service: AnalysisRequestServiceDependency,
) -> RecommendationResultResponse:
    try:
        return await service.get_user_integral_result(
            request_id=request_id,
            user_id=context.user.id,
        )

    except AnalysisRequestNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except AnalysisResultNotReadyError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except AnalysisResultNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error