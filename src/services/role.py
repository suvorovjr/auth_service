import logging

from fastapi import Depends

from src.api.v1.schemas.roles import AddOrDeleteRoleToUser, RoleCreateOrUpdate
from src.domain.entities import Role
from src.domain.exceptions import RoleNotFound, UserNotFound
from src.domain.repositories import AbstractPermissionRepository, AbstractRoleRepository, AbstractUserRepository
from src.infrastructure.repositories.permisson import get_permission_repository
from src.infrastructure.repositories.role import get_role_repository
from src.infrastructure.repositories.user import get_user_repository

logger = logging.getLogger(__name__)


class RoleService:
    def __init__(
        self,
        role_repository: AbstractRoleRepository,
        user_repository: AbstractUserRepository,
        permission_repository: AbstractPermissionRepository,
    ):
        self._role_repository: AbstractRoleRepository = role_repository
        self._user_repository: AbstractUserRepository = user_repository
        self._permission_repository: AbstractPermissionRepository = permission_repository

    async def create_or_update(self, data: RoleCreateOrUpdate, slug: str | None = None) -> Role:
        """Создаёт новую роль или обновляет существующую, связывая с разрешениями"""

        existing_role = await self._role_repository.get_role(slug)
        permissions = []
        for perm_slug in data.permissions:
            permission = await self._permission_repository.get_permission(perm_slug)
            if not permission:
                logger.warning(f"Разрешение {perm_slug} не найдено")
                continue
            permissions.append(permission)

        if existing_role:
            logger.info(f"Обновление роли: {data.slug}")
            existing_role.title = data.title
            existing_role.description = data.description
            existing_role.permissions = permissions
            return await self._role_repository.update_role(existing_role)
        else:
            logger.info(f"Создание новой роли: {data.slug}")
            return await self._role_repository.create_role(data.slug, data.title, permissions, data.description)

    async def delete(self, slug: str) -> bool:
        """Удаляет роль"""
        role = await self._role_repository.get_role(slug)
        if not role:
            logger.error(f"Роль {slug} не найдена для удаления")
            raise RoleNotFound(f"Роль '{slug}' не найдена")

        logger.info(f"Удаление роли: {slug}")
        return await self._role_repository.delete_role(role)

    async def get(self, slug: str | None = None) -> Role | list[Role]:
        """Получает одну роль по slug или список всех ролей"""
        if slug:
            role = await self._role_repository.get_role(slug)
            if not role:
                logger.error(f"Роль {slug} не найдена")
                raise RoleNotFound(f"Роль '{slug}' не найдена")
            return role
        else:
            return await self._role_repository.get_all_roles()

    async def add_role_to_user(self, data: AddOrDeleteRoleToUser) -> bool:
        """Добавляет роль пользователю"""

        result = await self._role_repository.add_role_to_user(data.user_id, data.role_slug)
        if result:
            logger.info(f"Роль {data.role_slug} добавлена пользователю {data.user_id}")
            return True
        logger.info(f"Пользователь {data.user_id} уже имеет роль {data.role_slug}")
        return False

    async def delete_role_from_user(self, data: AddOrDeleteRoleToUser) -> bool:
        """Удаляет роль у пользователя"""

        result = await self._role_repository.delete_role_to_user(data.user_id, data.role_slug)
        if result:
            logger.info(f"Роль {data.role_slug} удалена у пользователя {data.user_id}")
            return True
        logger.info(f"Пользователь {data.user_id} не имеет роли {data.role_slug}")
        return False

    async def check_role_for_user(self, user_id: str, role_slug: str) -> bool:
        """Проверяет, есть ли у пользователя определённая роль"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            logger.error(f"Пользователь {user_id} не найден")
            raise UserNotFound(f"Пользователь '{user_id}' не найден")

        role = await self._role_repository.get_role(role_slug)
        if not role:
            logger.error(f"Роль {role_slug} не найдена")
            raise RoleNotFound(f"Роль '{role_slug}' не найдена")

        return role in user.roles


def get_role_service(
    role_repository: AbstractRoleRepository = Depends(get_role_repository),
    user_repository: AbstractUserRepository = Depends(get_user_repository),
    permission_repository: AbstractPermissionRepository = Depends(get_permission_repository),
) -> RoleService:
    """Фабричная функция для получения экземпляра сервиса ролей"""
    return RoleService(
        role_repository=role_repository, user_repository=user_repository, permission_repository=permission_repository
    )
