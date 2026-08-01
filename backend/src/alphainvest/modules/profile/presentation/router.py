from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from alphainvest.modules.profile.domain.exceptions import (
    DuplicateAnswerError,
    IncompleteQuestionnaireError,
    InvalidAnswerError,
    QuestionnaireNotFoundError,
)
from alphainvest.modules.profile.presentation.dependencies import (
    AuthenticatedContext,
    ProfileServiceDependency,
)
from alphainvest.modules.profile.presentation.schemas import (
    CreateRiskEvaluationRequest,
    CurrentRiskProfileResponse,
    QuestionnaireResponse,
    RiskEvaluationResponse,
    RiskProfileHistoryResponse,
)

router = APIRouter(
    prefix="/profile",
    tags=["Perfil de riesgo"],
)


@router.get(
    "/questionnaire",
    response_model=QuestionnaireResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener cuestionario de perfil de riesgo",
    description=(
        "Obtiene el cuestionario publicado con sus preguntas "
        "y opciones de respuesta activas."
    ),
)
async def get_questionnaire(
    service: ProfileServiceDependency,
) -> QuestionnaireResponse:
    try:
        questionnaire = await service.get_active_questionnaire()
    except QuestionnaireNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return QuestionnaireResponse.model_validate(
        questionnaire
    )


@router.get(
    "/current",
    response_model=CurrentRiskProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener perfil de riesgo vigente",
    description=(
        "Obtiene el perfil de riesgo vigente del usuario "
        "autenticado."
    ),
)
async def get_current_risk_profile(
    context: AuthenticatedContext,
    service: ProfileServiceDependency,
) -> CurrentRiskProfileResponse:
    profile = await service.get_current_risk_profile(
        user_id=context.user.id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "El usuario no tiene un perfil de riesgo vigente"
            ),
        )

    return profile


@router.get(
    "/history",
    response_model=RiskProfileHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener historial de perfiles de riesgo",
    description=(
        "Obtiene todos los perfiles de riesgo del usuario "
        "autenticado, ordenados del más reciente al más antiguo."
    ),
)
async def get_risk_profile_history(
    context: AuthenticatedContext,
    service: ProfileServiceDependency,
) -> RiskProfileHistoryResponse:
    return await service.get_risk_profile_history(
        user_id=context.user.id,
    )


@router.post(
    "/evaluations",
    response_model=RiskEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear evaluación de perfil de riesgo",
    description=(
        "Valida las respuestas del cuestionario, calcula la "
        "clasificación y crea el perfil de riesgo vigente."
    ),
)
async def create_evaluation(
    data: CreateRiskEvaluationRequest,
    context: AuthenticatedContext,
    service: ProfileServiceDependency,
) -> RiskEvaluationResponse:
    try:
        return await service.create_evaluation(
            user_id=context.user.id,
            data=data,
        )

    except QuestionnaireNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except (
        DuplicateAnswerError,
        IncompleteQuestionnaireError,
        InvalidAnswerError,
        ValueError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    except IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No fue posible registrar la evaluación "
                "debido a un conflicto de datos"
            ),
        ) from error