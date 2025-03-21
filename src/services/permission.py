import logging

from fastapi import Depends

from src.api.v1.schemas.permissions import PermissionBase
from src.domain.entities import Permission
from src.domain.exceptions import PermissionNotFound
from src.domain.repositories import AbstractPermissionRepository
from src.infrastructure.repositories.permisson import get_permission_repository

logger = logging.getLogger(__name__)


class PermissionService:
    def __init__(self, permission_repository: AbstractPermissionRepository):
        self._permission_repository: AbstractPermissionRepository = permission_repository

    async def create_or_update(self, data: PermissionBase, slug: str | None = None) -> Permission:
        """Создаёт новое разрешение или обновляет существующее"""
        existing_permission = await self._permission_repository.get_permission(slug)

        if existing_permission:
            logger.info(f"Обновление разрешения: {data.slug}")
            existing_permission.description = data.description
            return await self._permission_repository.update_permission(existing_permission)
        else:
            logger.info(f"Создание нового разрешения: {data.slug}")
            return await self._permission_repository.create_permission(data.slug, data.description)

    async def delete(self, slug: str) -> bool:
        """Удаляет разрешение"""
        permission = await self._permission_repository.get_permission(slug)
        if not permission:
            logger.error(f"Разрешение {slug} не найдено для удаления")
            raise PermissionNotFound(f"Разрешение '{slug}' не найдено")

        logger.info(f"Удаление разрешения: {slug}")
        return await self._permission_repository.delete_permission(permission)

    async def get(self, slug: str | None = None) -> Permission | list[Permission]:
        """Получает одно разрешение по slug или список всех разрешений"""
        if slug:
            permission = await self._permission_repository.get_permission(slug)
            if not permission:
                logger.error(f"Разрешение {slug} не найдено")
                raise PermissionNotFound(f"Разрешение '{slug}' не найдено")
            return permission
        else:
            return await self._permission_repository.get_all_permissions()


def get_permission_service(
    permission_repository: AbstractPermissionRepository = Depends(get_permission_repository),
) -> PermissionService:
    """Фабричная функция для получения экземпляра сервиса разрешений"""
    return PermissionService(permission_repository=permission_repository)
