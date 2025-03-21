import logging

from fastapi import Depends
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.domain.entities import Permission
from src.domain.exceptions import PermissionIsExists
from src.domain.repositories import AbstractPermissionRepository

logger = logging.getLogger(__name__)


class SQLAlchemyPermissionRepository(AbstractPermissionRepository):
    """Репозиторий для управления разрешениями в базе данных"""

    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    async def create_permission(self, slug: str, description: str | None) -> Permission:
        """Создаёт новое разрешение"""
        insert_data = {"slug": slug, "description": description}
        query = insert(Permission).values(insert_data).returning(Permission)
        try:
            result: Result = await self._session.execute(query)
            await self._commit()
        except IntegrityError:
            logger.error("Разрешение с slug %s уже существует.", slug)
            raise PermissionIsExists
        return result.scalar_one()

    async def get_permission(self, slug: str) -> Permission | None:
        """Получает разрешение по slug"""
        query = select(Permission).filter_by(slug=slug)
        result: Result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_permissions(self) -> list[Permission]:
        """Получает список всех разрешений"""
        query = select(Permission)
        result: Result = await self._session.execute(query)
        return result.scalars().all()

    async def update_permission(self, permission: Permission) -> Permission | None:
        """Обновляет данные разрешения"""
        result: Result = await self._session.execute(
            update(Permission)
            .filter_by(slug=permission.slug)
            .values(description=permission.description)
            .returning(Permission)
        )
        await self._commit()
        return result.scalar_one_or_none()

    async def delete_permission(self, permission: Permission) -> bool:
        """Удаляет разрешение"""
        query = delete(Permission).filter_by(slug=permission.slug)
        await self._session.execute(query)
        await self._commit()
        return True

    async def _commit(self) -> None:
        """Фиксирует изменения в БД"""
        await self._session.commit()


def get_permission_repository(
    session: AsyncSession = Depends(get_session),
) -> SQLAlchemyPermissionRepository:
    """Функция для получения экземпляра репозитория"""
    return SQLAlchemyPermissionRepository(session=session)
