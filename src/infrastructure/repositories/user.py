import logging

from fastapi import Depends
from sqlalchemy import Result, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.domain.entities import User
from src.domain.exceptions import UserIsExists
from src.domain.repositories import AbstractUserRepository

logger = logging.getLogger(__name__)


class SQLAlchemyUserRepository(AbstractUserRepository):
    exclude_fields = ("roles", "created_at", "updated_at")

    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    async def create(self, email, password):
        insert_data = {"email": email, "password": password}
        query = insert(User).values(insert_data).returning(User)
        try:
            result: Result = await self._session.execute(query)
            await self._commit()
        except IntegrityError:
            logger.error("Пользователь с email %s уже существует.", email)
            raise UserIsExists
        return result.scalar_one()

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).filter_by(email=email)
        result: Result = await self._session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        """
        Получает запись из базы данных по ее идентификатору.

        :object_id: идентификатор записи.
        :return: объект модели или None, если запись не найдена.
        """

        query = select(User).filter_by(id=user_id)
        result: Result = await self._session.execute(query)
        return result.unique().scalar_one_or_none()

    async def update(self, user: User) -> User | None:
        """
        Обновляет запись в базе данных по ее идентификатору.

        :object_id: идентификатор записи.
        :schema: данные для обновления записи (Pydantic-схема).
        :return: обновленный объект модели или None, если запись не найдена.
        """

        await self._session.execute(update(User).filter_by(id=user.id).values(**user.to_dict(self.exclude_fields)))
        await self._commit()
        return

    async def _commit(self) -> None:
        await self._session.commit()


def get_user_repository(
    session: SQLAlchemyUserRepository = Depends(get_session),
) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session=session)
