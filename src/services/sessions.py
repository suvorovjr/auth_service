import logging
from uuid import UUID

from fastapi import Depends
from user_agents import parse

from src.domain.entities import Session
from src.domain.exceptions import SessionHasExpired
from src.domain.interfaces import AbstractSessionService
from src.domain.repositories import AbstractSessionRepository
from src.infrastructure.repositories.sessions import get_session_repository

logger = logging.getLogger(__name__)


class SessionService(AbstractSessionService):
    """Сервис для управления сессиями пользователей."""

    def __init__(self, session_repository: AbstractSessionRepository):
        """
        Инициализатор класса
        :param session_repository: Репозиторий для работы с объектами Session.
        """
        self._session_repository: AbstractSessionRepository = session_repository

    async def create_new_session(self, session: Session) -> Session:
        """
        Создаёт новую сессию пользователя.
        :param session: Объект сессии
        :return: Созданная сессия
        """
        device_type = self.get_user_device(user_agent=session.user_agent)
        session.device_type = device_type
        new_session = await self._session_repository.create(session)
        return new_session

    async def deactivate_current_session(self, refresh_token: str) -> Session | None:
        """
        Деактивирует текущую сессию пользователя.
        :param refresh_token: Refresh-токен пользователя
        :return: Обновлённая сессия (неактивная)
        :raises SessionHasExpired: Если сессия не найдена
        """
        current_session = await self._session_repository.get_by_refresh_token(refresh_token)
        if current_session is None:
            logger.error("Попытка деактивации несуществующей сессии (refresh_token=%s)", refresh_token)
            raise SessionHasExpired
        current_session.is_active = False
        updated_session = await self._session_repository.update(current_session)
        return updated_session

    async def deactivate_all_without_current(self, refresh_token: str) -> list[Session]:
        """
        Деактивирует все сессии пользователя, кроме текущей.
        :param refresh_token: Refresh-токен текущей сессии
        :return: Список деактивированных сессий
        :raises SessionHasExpired: Если сессия не найдена
        """
        current_session = await self._session_repository.get_by_refresh_token(refresh_token)
        if current_session is None:
            logger.warning("Попытка деактивации всех сессий без существующей текущей (refresh_token=%s)", refresh_token)
            raise SessionHasExpired
        user_sessions = await self._session_repository.get_sessions_by_user_id(current_session.user_id)
        deactivate_sessions = []
        for session in user_sessions:
            if session.id != current_session.id:
                session.is_active = False
                await self._session_repository.update(session)
                deactivate_sessions.append(session)
        return deactivate_sessions

    async def update_session_refresh_token(
        self, old_refresh_token: str, new_refresh_token: str, new_jti: str
    ) -> Session | None:
        """
        Обновляет refresh-токен текущей сессии.
        :param old_refresh_token: Старый refresh-токен
        :param new_refresh_token: Новый refresh-токен
        :param new_jti: Новый JTI
        :return: Обновлённая сессия
        :raises SessionHasExpired: Если сессия не активна или не найдена
        """
        current_session = await self._session_repository.get_by_refresh_token(old_refresh_token)
        if current_session is None:
            logger.error("Попытка обновления несуществующей сессии (refresh_token=%s)", old_refresh_token)
            raise SessionHasExpired
        if not current_session.is_active:
            logger.warning("Сессия с токеном %s истекла.", old_refresh_token)
            raise SessionHasExpired
        current_session.refresh_token = new_refresh_token
        current_session.jti = new_jti
        updated_session = await self._session_repository.update(session=current_session)
        return updated_session

    async def get_current_user_sessions(self, user_id: UUID | str) -> list[Session]:
        """
        Получает все сессии пользователя по user_id
        :param user_id: ID пользователя
        :return: Список сессий пользователя
        """
        sessions = await self._session_repository.get_sessions_by_user_id(user_id=user_id)
        return sessions

    @staticmethod
    def get_user_device(user_agent: str) -> str:
        """
        Получает тип устройства из отпечатка браузера (user_agent)
        :param user_agent: Отпечаток браузера пользователя
        :return: Тип устройства пользователя
        """
        ua = parse(user_agent)
        match (ua.is_mobile, ua.is_tablet, ua.is_pc):
            case (True, _, _):
                return "mobile"
            case (_, True, _):
                return "smart"
            case (_, _, True):
                return "desktop"
            case _:
                return "other"


def get_session_service(
    session_repository: AbstractSessionRepository = Depends(get_session_repository),
) -> AbstractSessionService:
    """
    Фабричный метод для получения экземпляра SessionService.
    :param session_repository: Репозиторий сессий
    :return: Экземпляр SessionService
    """
    return SessionService(session_repository=session_repository)
