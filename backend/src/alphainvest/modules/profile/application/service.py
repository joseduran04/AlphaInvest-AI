from uuid import UUID

from sqlalchemy.exc import IntegrityError

from alphainvest.modules.profile.domain.enums import (
    ClassificationMethod,
    EvaluationStatus,
    RiskClassification,
)
from alphainvest.modules.profile.domain.exceptions import (
    DuplicateAnswerError,
    IncompleteQuestionnaireError,
    InvalidAnswerError,
    QuestionnaireNotFoundError,
)
from alphainvest.modules.profile.domain.scoring import (
    RiskScoreResult,
    RiskScoringService,
    ScoredAnswer,
)
from alphainvest.modules.profile.infrastructure.models import (
    AnswerOptionModel,
    QuestionModel,
    QuestionnaireModel,
    RiskEvaluationModel,
    RiskProfileModel,
    UserAnswerModel,
)
from alphainvest.modules.profile.infrastructure.repository import (
    ProfileRepository,
)
from alphainvest.modules.profile.presentation.schemas import (
    CreateRiskEvaluationRequest,
    CurrentRiskProfileResponse,
    RiskEvaluationResponse,
    RiskProfileHistoryItemResponse,
    RiskProfileHistoryResponse,
)


class ProfileService:
    """Casos de uso del módulo de perfil de riesgo."""

    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    async def get_active_questionnaire(
        self,
    ) -> QuestionnaireModel:
        questionnaire = (
            await self._repository.get_published_questionnaire()
        )

        if questionnaire is None:
            raise QuestionnaireNotFoundError(
                "No existe un cuestionario publicado"
            )

        questionnaire.preguntas = [
            question
            for question in questionnaire.preguntas
            if question.activa
        ]

        for question in questionnaire.preguntas:
            question.opciones = [
                option
                for option in question.opciones
                if option.activa
            ]

        return questionnaire


    async def get_current_risk_profile(
        self,
        *,
        user_id: UUID,
    ) -> CurrentRiskProfileResponse | None:
        """Obtiene el perfil de riesgo vigente del usuario."""

        profile = await self._repository.get_current_profile(
            user_id
        )

        if profile is None:
            return None

        return CurrentRiskProfileResponse(
            id=profile.id,
            evaluation_id=profile.evaluacion_id,
            classification=RiskClassification(
                                profile.clasificacion
                            ),
            score=profile.puntuacion,
            confidence=profile.confianza,
            description=profile.descripcion,
            current=profile.vigente,
            started_at=profile.fecha_inicio,
        )

    
    async def get_risk_profile_history(
        self,
        *,
        user_id: UUID,
    ) -> RiskProfileHistoryResponse:
        """Obtiene el historial de perfiles de riesgo del usuario."""

        profiles = await self._repository.get_profile_history(
            user_id
        )

        items = [
            RiskProfileHistoryItemResponse(
                id=profile.id,
                evaluation_id=profile.evaluacion_id,
                classification=RiskClassification(
                    profile.clasificacion
                ),
                score=profile.puntuacion,
                confidence=profile.confianza,
                description=profile.descripcion,
                current=profile.vigente,
                started_at=profile.fecha_inicio,
                ended_at=profile.fecha_fin,
            )
            for profile in profiles
        ]

        return RiskProfileHistoryResponse(
            items=items,
            total=len(items),
        )

    async def create_evaluation(
        self,
        *,
        user_id: UUID,
        data: CreateRiskEvaluationRequest,
    ) -> RiskEvaluationResponse:
        questionnaire = (
            await self._repository.get_questionnaire_for_evaluation(
                data.questionnaire_id
            )
        )

        if questionnaire is None:
            raise QuestionnaireNotFoundError(
                "El cuestionario indicado no existe o no está publicado"
            )

        self._filter_active_content(questionnaire)

        submitted_answers = self._validate_request_answers(
            questionnaire=questionnaire,
            data=data,
        )

        scoring_answers = [
            ScoredAnswer(
                question_id=str(question.id),
                option_value=option.valor,
                weight=question.ponderacion,
            )
            for question, option in submitted_answers
        ]

        score_result = RiskScoringService.calculate(
            scoring_answers
        )

        evaluation = RiskEvaluationModel(
            usuario_id=user_id,
            cuestionario_id=questionnaire.id,
            version_cuestionario=questionnaire.version,
            puntuacion_total=score_result.normalized_score,
            clasificacion=score_result.classification.value,
            confianza=score_result.confidence,
            metodo_clasificacion=ClassificationMethod.RULES,
            estado=EvaluationStatus.COMPLETED,
            detalle_calculo=self._calculation_detail(
                score_result
            ),
        )

        try:
            await self._repository.add_evaluation(evaluation)

            answer_models = [
                UserAnswerModel(
                    evaluacion_id=evaluation.id,
                    pregunta_id=question.id,
                    opcion_id=option.id,
                    puntuacion_obtenida=(
                        option.valor * question.ponderacion
                    ),
                )
                for question, option in submitted_answers
            ]

            await self._repository.add_answers(answer_models)

            await self._repository.close_current_profile(
                user_id
            )

            profile = RiskProfileModel(
                usuario_id=user_id,
                evaluacion_id=evaluation.id,
                clasificacion=score_result.classification.value,
                puntuacion=score_result.normalized_score,
                confianza=score_result.confidence,
                descripcion=score_result.description,
                vigente=True,
            )

            await self._repository.add_risk_profile(profile)
            await self._repository.commit()

        except IntegrityError:
            await self._repository.rollback()
            raise

        return RiskEvaluationResponse(
            id=evaluation.id,
            questionnaire_id=questionnaire.id,
            questionnaire_version=questionnaire.version,
            raw_score=score_result.raw_score,
            normalized_score=score_result.normalized_score,
            classification=score_result.classification,
            confidence=score_result.confidence,
            method=ClassificationMethod.RULES,
            status=EvaluationStatus.COMPLETED,
            evaluated_at=evaluation.fecha_evaluacion,
            description=score_result.description,
        )


    @staticmethod
    def _filter_active_content(
        questionnaire: QuestionnaireModel,
    ) -> None:
        questionnaire.preguntas = [
            question
            for question in questionnaire.preguntas
            if question.activa
        ]

        for question in questionnaire.preguntas:
            question.opciones = [
                option
                for option in question.opciones
                if option.activa
            ]


    @staticmethod
    def _validate_request_answers(
        *,
        questionnaire: QuestionnaireModel,
        data: CreateRiskEvaluationRequest,
    ) -> list[tuple[QuestionModel, AnswerOptionModel]]:
        question_ids = [
            answer.question_id
            for answer in data.answers
        ]

        if len(question_ids) != len(set(question_ids)):
            raise DuplicateAnswerError(
                "No puede enviarse más de una respuesta "
                "para la misma pregunta"
            )

        questions_by_id = {
            question.id: question
            for question in questionnaire.preguntas
        }

        required_question_ids = {
            question.id
            for question in questionnaire.preguntas
            if question.obligatoria
        }

        submitted_question_ids = set(question_ids)

        missing_questions = (
            required_question_ids - submitted_question_ids
        )

        if missing_questions:
            raise IncompleteQuestionnaireError(
                "Faltan respuestas para preguntas obligatorias"
            )

        validated_answers = []

        for submitted in data.answers:
            question = questions_by_id.get(
                submitted.question_id
            )

            if question is None:
                raise InvalidAnswerError(
                    "Una pregunta no pertenece al "
                    "cuestionario publicado"
                )

            option = next(
                (
                    current_option
                    for current_option in question.opciones
                    if current_option.id == submitted.option_id
                ),
                None,
            )

            if option is None:
                raise InvalidAnswerError(
                    "Una opción no pertenece a la "
                    "pregunta indicada"
                )

            validated_answers.append(
                (question, option)
            )

        return validated_answers


    @staticmethod
    def _calculation_detail(
        result: RiskScoreResult,
    ) -> dict[str, str]:
        return {
            "puntuacion_bruta": str(result.raw_score),
            "puntuacion_minima": str(result.minimum_score),
            "puntuacion_maxima": str(result.maximum_score),
            "puntuacion_normalizada": str(
                result.normalized_score
            ),
            "clasificacion": result.classification.value,
            "metodo": ClassificationMethod.RULES.value,
        }