from typing import Any
from uuid import UUID

from alphainvest.modules.operation.domain.enums import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from alphainvest.modules.operation.domain.exceptions import (
    InvalidNotificationContentError,
    InvalidNotificationReferenceError,
    NotificationNotFoundError,
    NotificationNotSentError,
)
from alphainvest.modules.operation.infrastructure.models import (
    NotificationModel,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)
from alphainvest.modules.operation.presentation.schemas import (
    NotificationListResponse,
    NotificationResponse,
    UnreadNotificationCountResponse,
)


class NotificationService:
    """Casos de uso de notificaciones internas."""

    def __init__(
        self,
        repository: OperationRepository,
    ) -> None:
        self._repository = repository

    @staticmethod
    def is_channel_supported(
        channel: NotificationChannel,
    ) -> bool:
        return (
            channel
            == NotificationChannel.APPLICATION
        )

    @staticmethod
    def supported_channels(
    ) -> tuple[NotificationChannel, ...]:
        return (
            NotificationChannel.APPLICATION,
        )

    async def create_application_notification(
        self,
        *,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = (
            NotificationPriority.NORMAL
        ),
        data: dict[str, Any] | None = None,
        reference_type: str | None = None,
        reference_id: str | None = None,
    ) -> NotificationResponse:
        normalized_title = title.strip()
        normalized_message = message.strip()

        if (
            not normalized_title
            or len(normalized_title) > 200
        ):
            raise InvalidNotificationContentError(
                "El título de la notificación "
                "debe contener entre 1 y 200 caracteres"
            )

        if not normalized_message:
            raise InvalidNotificationContentError(
                "El mensaje de la notificación "
                "no puede estar vacío"
            )

        normalized_reference_type = (
            reference_type.strip()
            if reference_type is not None
            else None
        )

        normalized_reference_id = (
            reference_id.strip()
            if reference_id is not None
            else None
        )

        if (
            normalized_reference_type is None
        ) != (
            normalized_reference_id is None
        ):
            raise InvalidNotificationReferenceError(
                "El tipo y el identificador "
                "de referencia deben proporcionarse juntos"
            )

        if (
            normalized_reference_type == ""
            or normalized_reference_id == ""
        ):
            raise InvalidNotificationReferenceError(
                "La referencia de la notificación "
                "no puede estar vacía"
            )

        notification = (
            await self._repository.create_notification(
                user_id=user_id,
                notification_type=notification_type,
                channel=self._application_channel(),
                title=normalized_title,
                message=normalized_message,
                priority=priority,
                status=NotificationStatus.SENT,
                data=data,
                scheduled_at=None,
                reference_type=normalized_reference_type,
                reference_id=normalized_reference_id,
            )
        )

        await self._repository.commit()

        return NotificationResponse.model_validate(
            notification
        )

    async def create_application_notification_once(
        self,
        *,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = (
            NotificationPriority.NORMAL
        ),
        data: dict[str, Any] | None = None,
        reference_type: str,
        reference_id: str,
    ) -> NotificationResponse:
        normalized_reference_type = (
            reference_type.strip()
        )

        normalized_reference_id = (
            reference_id.strip()
        )

        if (
            not normalized_reference_type
            or not normalized_reference_id
        ):
            raise InvalidNotificationReferenceError(
                "La referencia de la notificación "
                "no puede estar vacía"
            )

        existing = (
            await self._repository
            .get_notification_by_reference(
                user_id=user_id,
                notification_type=notification_type,
                channel=self._application_channel(),
                reference_type=(
                    normalized_reference_type
                ),
                reference_id=(
                    normalized_reference_id
                ),
            )
        )

        if existing is not None:
            return NotificationResponse.model_validate(
                existing
            )

        return await (
            self.create_application_notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                data=data,
                reference_type=(
                    normalized_reference_type
                ),
                reference_id=(
                    normalized_reference_id
                ),
            )
        )

    async def get_notification(
        self,
        *,
        notification_id: UUID,
        user_id: UUID,
    ) -> NotificationResponse:
        notification = (
            await self._get_user_notification(
                notification_id=notification_id,
                user_id=user_id,
            )
        )

        self._ensure_sent(notification)

        return NotificationResponse.model_validate(
            notification
        )

    async def list_notifications(
        self,
        *,
        user_id: UUID,
        unread_only: bool,
        limit: int,
        offset: int,
    ) -> NotificationListResponse:
        notifications, total = (
            await self._repository
            .list_notifications_for_user(
                user_id=user_id,
                unread_only=unread_only,
                limit=limit,
                offset=offset,
            )
        )

        return NotificationListResponse(
            items=[
                NotificationResponse.model_validate(
                    notification
                )
                for notification in notifications
            ],
            total=total,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
        )

    async def count_unread(
        self,
        *,
        user_id: UUID,
    ) -> UnreadNotificationCountResponse:
        unread = (
            await self._repository
            .count_unread_notifications(
                user_id=user_id,
            )
        )

        return UnreadNotificationCountResponse(
            unread=unread
        )

    async def mark_as_read(
        self,
        *,
        notification_id: UUID,
        user_id: UUID,
    ) -> NotificationResponse:
        notification = (
            await self._get_user_notification(
                notification_id=notification_id,
                user_id=user_id,
            )
        )

        self._ensure_sent(notification)

        if notification.fecha_lectura is not None:
            return NotificationResponse.model_validate(
                notification
            )

        notification = (
            await self._repository
            .mark_notification_read(
                notification
            )
        )

        await self._repository.commit()

        return NotificationResponse.model_validate(
            notification
        )

    async def _get_user_notification(
        self,
        *,
        notification_id: UUID,
        user_id: UUID,
    ) -> NotificationModel:
        notification = (
            await self._repository
            .get_notification_for_user(
                notification_id=notification_id,
                user_id=user_id,
            )
        )

        if notification is None:
            raise NotificationNotFoundError(
                "La notificación solicitada no existe"
            )

        return notification

    @staticmethod
    def _ensure_sent(
        notification: NotificationModel,
    ) -> None:
        if (
            notification.estado
            != NotificationStatus.SENT.value
            or notification.fecha_envio is None
        ):
            raise NotificationNotSentError(
                "La notificación todavía "
                "no ha sido entregada"
            )

    @staticmethod
    def _application_channel() -> NotificationChannel:
        return NotificationChannel.APPLICATION