from uuid import UUID

from sqlalchemy.exc import IntegrityError

from alphainvest.modules.ai.domain.enums import (
    AIModelStatus,
)
from alphainvest.modules.ai.domain.exceptions import (
    ActiveModelVersionNotFoundError,
    AIModelNotActiveError,
    AIModelNotFoundError,
    AIModelUpdateError,
    ModelVersionActivationError,
    ModelVersionAlreadyExistsError,
    ModelVersionNotFoundError,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.ai.presentation.schemas import (
    ActiveModelVersionResponse,
    AIModelListResponse,
    AIModelResponse,
    AIModelStatusUpdateRequest,
    AIModelSummaryResponse,
    ModelVersionCreateRequest,
    ModelVersionListResponse,
    ModelVersionResponse,
)


class AIService:
    """Casos de uso del catálogo de modelos de IA."""

    def __init__(
        self,
        repository: AIRepository,
    ) -> None:
        self._repository = repository

    async def list_models(
        self,
        *,
        search: str | None,
        model_type: str | None,
        status: AIModelStatus | None,
        limit: int,
        offset: int,
    ) -> AIModelListResponse:
        models, total = await self._repository.list_models(
            search=search,
            model_type=model_type,
            status=status.value if status else None,
            limit=limit,
            offset=offset,
        )

        return AIModelListResponse(
            items=[
                AIModelSummaryResponse.model_validate(
                    model
                )
                for model in models
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update_model_status(
        self,
        *,
        model_id: UUID,
        request: AIModelStatusUpdateRequest,
    ) -> AIModelResponse:
        model = await self._repository.get_model(
            model_id
        )

        if model is None:
            raise AIModelNotFoundError(
                "El modelo de inteligencia artificial "
                "solicitado no existe"
            )

        try:
            updated = (
                await self._repository.update_model_status(
                    model,
                    status=request.status.value,
                )
            )

            await self._repository.commit()

        except IntegrityError as error:
            await self._repository.rollback()

            raise AIModelUpdateError(
                "No fue posible actualizar "
                "el estado del modelo"
            ) from error

        return AIModelResponse.model_validate(
            updated
        )

    async def create_model_version(
        self,
        *,
        model_id: UUID,
        user_id: UUID,
        request: ModelVersionCreateRequest,
    ) -> ModelVersionResponse:
        model = await self._repository.get_model(
            model_id
        )

        if model is None:
            raise AIModelNotFoundError(
                "El modelo de inteligencia artificial "
                "solicitado no existe"
            )

        try:
            version = (
                await self._repository.create_model_version(
                    model_id=model.id,
                    version=request.version.strip(),
                    artifact_path=(
                        request.artifact_path.strip()
                    ),
                    checksum=request.checksum.strip(),
                    algorithm=request.algorithm.strip(),
                    framework=(
                        request.framework.strip()
                        if request.framework
                        else None
                    ),
                    hyperparameters=(
                        request.hyperparameters
                    ),
                    metrics=request.metrics,
                    training_dataset=(
                        request.training_dataset
                    ),
                    trained_at=request.trained_at,
                    created_by=user_id,
                )
            )

            await self._repository.commit()

        except IntegrityError as error:
            await self._repository.rollback()

            raise ModelVersionAlreadyExistsError(
                "Ya existe una versión con ese "
                "identificador o checksum"
            ) from error

        return ModelVersionResponse.model_validate(
            version
        )

    async def get_model(
        self,
        *,
        model_id: UUID,
    ) -> AIModelResponse:
        model = await self._repository.get_model(
            model_id
        )

        if model is None:
            raise AIModelNotFoundError(
                "El modelo de inteligencia artificial "
                "solicitado no existe"
            )

        return AIModelResponse.model_validate(model)

    async def get_model_by_code(
        self,
        *,
        code: str,
    ) -> AIModelResponse:
        model = await self._repository.get_model_by_code(
            code
        )

        if model is None:
            raise AIModelNotFoundError(
                "El modelo de inteligencia artificial "
                "solicitado no existe"
            )

        return AIModelResponse.model_validate(model)

    async def get_model_version(
        self,
        *,
        version_id: UUID,
    ) -> ModelVersionResponse:
        version = (
            await self._repository.get_model_version(
                version_id
            )
        )

        if version is None:
            raise ModelVersionNotFoundError(
                "La versión del modelo solicitada "
                "no existe"
            )

        return ModelVersionResponse.model_validate(
            version
        )

    async def list_model_versions(
        self,
        *,
        model_id: UUID,
    ) -> ModelVersionListResponse:
        model = await self._repository.get_model(
            model_id
        )

        if model is None:
            raise AIModelNotFoundError(
                "El modelo de inteligencia artificial "
                "solicitado no existe"
            )

        versions = (
            await self._repository.list_model_versions(
                model_id=model_id
            )
        )

        items = [
            ModelVersionResponse.model_validate(version)
            for version in versions
        ]

        return ModelVersionListResponse(
            model_id=model_id,
            items=items,
            total=len(items),
        )

    async def get_active_version(
        self,
        *,
        model_id: UUID,
    ) -> ActiveModelVersionResponse:
        model = await self._repository.get_model(
            model_id
        )

        if model is None:
            raise AIModelNotFoundError(
                "El modelo de inteligencia artificial "
                "solicitado no existe"
            )

        version = (
            await self._repository.get_active_version_for_model(
                model_id
            )
        )

        if version is None:
            raise ActiveModelVersionNotFoundError(
                "El modelo no tiene una versión activa "
                "disponible"
            )

        return ActiveModelVersionResponse(
            model=AIModelSummaryResponse.model_validate(
                model
            ),
            version=ModelVersionResponse.model_validate(
                version
            ),
        )

    async def get_active_version_by_code(
        self,
        *,
        code: str,
    ) -> ActiveModelVersionResponse:
        model = await self._repository.get_model_by_code(
            code
        )

        if model is None:
            raise AIModelNotFoundError(
                "El modelo de inteligencia artificial "
                "solicitado no existe"
            )

        version = (
            await self._repository
            .get_active_version_by_model_code(
                code
            )
        )

        if version is None:
            raise ActiveModelVersionNotFoundError(
                "El modelo no tiene una versión activa "
                "disponible"
            )

        return ActiveModelVersionResponse(
            model=AIModelSummaryResponse.model_validate(
                model
            ),
            version=ModelVersionResponse.model_validate(
                version
            ),
        )

    async def activate_model_version(
        self,
        *,
        version_id: UUID,
    ) -> ModelVersionResponse:
        version = (
            await self._repository.get_model_version(
                version_id
            )
        )

        if version is None:
            raise ModelVersionNotFoundError(
                "La versión del modelo solicitada "
                "no existe"
            )

        model = await self._repository.get_model(
            version.modelo_id
        )

        if model is None:
            raise AIModelNotFoundError(
                "El modelo asociado con la versión "
                "no existe"
            )

        if model.estado != AIModelStatus.ACTIVE.value:
            raise AIModelNotActiveError(
                "El modelo debe estar en estado ACTIVO "
                "antes de activar una versión"
            )

        try:
            activated = (
                await self._repository
                .activate_model_version(version)
            )

            await self._repository.commit()

        except IntegrityError as error:
            await self._repository.rollback()

            raise ModelVersionActivationError(
                "No fue posible activar la versión "
                "del modelo"
            ) from error

        return ModelVersionResponse.model_validate(
            activated
        )

    async def deactivate_model_version(
        self,
        *,
        version_id: UUID,
    ) -> ModelVersionResponse:
        version = (
            await self._repository.get_model_version(
                version_id
            )
        )

        if version is None:
            raise ModelVersionNotFoundError(
                "La versión del modelo solicitada "
                "no existe"
            )

        try:
            deactivated = (
                await self._repository
                .deactivate_model_version(version)
            )

            await self._repository.commit()

        except IntegrityError as error:
            await self._repository.rollback()

            raise ModelVersionActivationError(
                "No fue posible desactivar la versión "
                "del modelo"
            ) from error

        return ModelVersionResponse.model_validate(
            deactivated
        )