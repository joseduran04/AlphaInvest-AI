from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from alphainvest.modules.profile.infrastructure.models import (
    QuestionModel,
    QuestionnaireModel,
    RiskEvaluationModel,
    RiskProfileModel,
    UserAnswerModel,
)


class ProfileRepository:
    """Acceso a datos del módulo de perfil de riesgo."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_published_questionnaire(
        self,
    ) -> QuestionnaireModel | None:
        statement = (
            select(QuestionnaireModel)
            .where(
                QuestionnaireModel.estado == "PUBLICADO",
            )
            .options(
                selectinload(
                    QuestionnaireModel.preguntas.and_(
                        QuestionModel.activa.is_(True),
                    )
                ).selectinload(QuestionModel.opciones)
            )
            .order_by(
                QuestionnaireModel.fecha_publicacion.desc(),
                QuestionnaireModel.fecha_creacion.desc(),
            )
            .limit(1)
        )

        result = await self._session.execute(statement)

        return result.scalars().first()

    async def get_questionnaire_for_evaluation(
        self,
        questionnaire_id: UUID,
    ) -> QuestionnaireModel | None:
        """Obtiene un cuestionario publicado para evaluarlo."""

        statement = (
            select(QuestionnaireModel)
            .where(
                QuestionnaireModel.id == questionnaire_id,
                QuestionnaireModel.estado == "PUBLICADO",
            )
            .options(
                selectinload(
                    QuestionnaireModel.preguntas.and_(
                        QuestionModel.activa.is_(True),
                    )
                ).selectinload(QuestionModel.opciones)
            )
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def add_evaluation(
        self,
        evaluation: RiskEvaluationModel,
    ) -> None:
        """Agrega una evaluación y obtiene su UUID."""

        self._session.add(evaluation)
        await self._session.flush()

    async def add_answers(
        self,
        answers: list[UserAnswerModel],
    ) -> None:
        """Agrega las respuestas pertenecientes a una evaluación."""

        self._session.add_all(answers)
        await self._session.flush()

    async def get_current_profile(
        self,
        user_id: UUID,
    ) -> RiskProfileModel | None:
        """Obtiene el perfil vigente del usuario."""

        statement = select(RiskProfileModel).where(
            RiskProfileModel.usuario_id == user_id,
            RiskProfileModel.vigente.is_(True),
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_profile_history(
        self,
        user_id: UUID,
    ) -> list[RiskProfileModel]:
        """Obtiene el historial de perfiles de riesgo del usuario."""

        statement = (
            select(RiskProfileModel)
            .where(
                RiskProfileModel.usuario_id == user_id,
            )
            .order_by(
                RiskProfileModel.fecha_inicio.desc(),
            )
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def close_current_profile(
        self,
        user_id: UUID,
    ) -> None:
        """Cierra cualquier perfil vigente del usuario."""

        await self._session.execute(
            update(RiskProfileModel)
            .where(
                RiskProfileModel.usuario_id == user_id,
                RiskProfileModel.vigente.is_(True),
            )
            .values(
                vigente=False,
                fecha_fin=datetime.now(UTC),
            )
        )

        await self._session.flush()

    async def add_risk_profile(
        self,
        profile: RiskProfileModel,
    ) -> None:
        """Agrega el nuevo perfil vigente."""

        self._session.add(profile)
        await self._session.flush()

    async def commit(self) -> None:
        """Confirma la transacción actual."""

        await self._session.commit()

    async def rollback(self) -> None:
        """Revierte la transacción actual."""

        await self._session.rollback()