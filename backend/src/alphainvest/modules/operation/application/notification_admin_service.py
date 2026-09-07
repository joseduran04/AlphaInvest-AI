from uuid import UUID

from alphainvest.modules.operation.domain.enums import (
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)
from alphainvest.modules.operation.domain.exceptions import (
    InvalidNotificationStateTransitionError,
    NotificationNotFoundError,
)
from alphainvest.modules.operation.infrastructure.models import (
    NotificationModel,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)
from alphainvest.modules.operation.presentation.schemas import (
    AdminNotificationListResponse,
    NotificationResponse,
)


class NotificationAdminService:
    """Casos de uso administrativos de notificaciones."""

    _CANCELLABLE_STATUSES = {
        NotificationStatus.PENDING.value,
        NotificationStatus.SCHEDULED.value,
    }

    def __init__(
        self,
        repository: OperationRepository,
    ) -> None:
        self._repository = repository

    async def get_notification(
        self,
        *,
        notification_id: UUID,
    ) -> NotificationResponse:
        notification = (
            await self._get_notification(
                notification_id=notification_id
            )
        )

        return NotificationResponse.model_validate(
            notification
        )

    async def list_notifications(
        self,
        *,
        user_id: UUID | None,
        status: NotificationStatus | None,
        notification_type: NotificationType | None,
        channel: NotificationChannel | None,
        limit: int,
        offset: int,
    ) -> AdminNotificationListResponse:
        notifications, total = (
            await self._repository.list_notifications(
                user_id=user_id,
                status=status,
                notification_type=notification_type,
                channel=channel,
                limit=limit,
                offset=offset,
            )
        )

        return AdminNotificationListResponse(
            items=[
                NotificationResponse.model_validate(
                    notification
                )
                for notification in notifications
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def cancel_notification(
        self,
        *,
        notification_id: UUID,
    ) -> NotificationResponse:
        notification = (
            await self._get_notification(
                notification_id=notification_id
            )
        )

        if (
            notification.estado
            not in self._CANCELLABLE_STATUSES
        ):
            raise (
                InvalidNotificationStateTransitionError(
                    "Sólo pueden cancelarse "
                    "notificaciones PENDIENTES "
                    "o PROGRAMADAS"
                )
            )

        notification = (
            await self._repository
            .cancel_notification(
                notification
            )
        )

        await self._repository.commit()

        return NotificationResponse.model_validate(
            notification
        )

    async def _get_notification(
        self,
        *,
        notification_id: UUID,
    ) -> NotificationModel:
        notification = (
            await self._repository.get_notification(
                notification_id=notification_id
            )
        )

        if notification is None:
            raise NotificationNotFoundError(
                "La notificación solicitada no existe"
            )

        return notification