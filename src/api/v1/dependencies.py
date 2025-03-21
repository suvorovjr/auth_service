import logging
from typing import Annotated

from fastapi import Depends, Request, Response, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.config import settings
from src.domain.entities import Token, User
from src.domain.exceptions import Forbidden, SessionHasExpired, UserNotFound
from src.domain.interfaces import (
    AbstractAuthService,
    AbstractBlacklistService,
    AbstractJWTService,
    AbstractOAuthService,
    AbstractSessionService,
    AbstractUserService,
)
from src.domain.repositories import AbstractUserRepository
from src.infrastructure.repositories.user import get_user_repository
from src.services.auth import get_auth_service
from src.services.blacklist import get_blacklist_service
from src.services.jwt import get_jwt_service
from src.services.oauth import get_yandex_oauth_service
from src.services.sessions import get_session_service
from src.services.user import get_user_service

SessionDep = Annotated[AbstractSessionService, Depends(get_session_service)]
AuthDep = Annotated[AbstractAuthService, Depends(get_auth_service)]
JWTDep = Annotated[AbstractJWTService, Depends(get_jwt_service)]
BlacklistDep = Annotated[AbstractBlacklistService, Depends(get_blacklist_service)]
UserServiceDep = Annotated[AbstractUserService, Depends(get_user_service)]
YandexOAuthDep = Annotated[AbstractOAuthService, Depends(get_yandex_oauth_service)]

UserRepoDep = Annotated[AbstractUserRepository, Depends(get_user_repository)]

security = HTTPBearer()


logger = logging.getLogger(__name__)


def set_refresh_token(response: Response, refresh_token: str) -> None:
    """
    Устанавливает refresh-токен в cookies ответа.
    :param response: Объект ответа FastAPI
    :param refresh_token: Строка refresh-токена
    """

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.service.debug,
        samesite="Strict",
        max_age=settings.service.refresh_token_expire,
    )


def get_refresh_token(request: Request) -> str | None:
    """
    Извлекает refresh-токен из cookies.
    :param request: Объект запроса FastAPI
    :return: Строка refresh-токена
    :raises SessionHasExpired: Если токен отсутствует
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        logger.warning("Refresh токен не обнаружен")
        raise SessionHasExpired
    request.state.refresh_token = refresh_token
    return refresh_token


def get_refresh_token_data(
    request: Request,
    jwt_service: JWTDep,
    refresh_token: str = Depends(get_refresh_token),
) -> Token:
    """
    Декодирует refresh-токен и сохраняет его данные в request.state.
    :param request: Объект запроса FastAPI
    :param jwt_service: Сервис для работы с JWT
    :param refresh_token: Строка refresh-токена
    :return: Декодированный объект Token
    """
    payload = jwt_service.decode_token(refresh_token)
    request.state.payload = payload
    return payload


async def get_current_user(user_repository: UserRepoDep, payload: Token = Depends(get_refresh_token_data)) -> User:
    """
    Получает пользователя из базы по UUID из токена.
    :param user_repository: Репозиторий пользователей
    :param payload: Декодированный refresh-токен
    :return: Объект User
    :raises UserNotFound: Если пользователь не найден
    """
    user: User = await user_repository.get_by_id(payload.user_uuid)
    if user is None:
        logger.error("Ошибка при получении пользователя с id %s из БД", payload.user_uuid)
        raise UserNotFound
    return user


def get_access_token_data(
    request: Request,
    jwt_service: JWTDep,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Token:
    access_token = credentials.credentials
    access_token_payload: Token = jwt_service.decode_token(access_token)
    request.state.access_token_payload = access_token_payload
    return access_token_payload


def require_permissions(required_permissions: list[str] | None = None):
    """
    Фабрика зависимостей (dependencies),
    которая возвращает функцию проверки прав на основе access-токена.
    :param required_permissions: Список требуемых прав
    :return: Асинхронная функция check_permission
    """

    async def check_permission(
        request: Request,
        jwt_service: JWTDep,
        blacklist_service: BlacklistDep,
        credentials: HTTPAuthorizationCredentials = Security(security),
    ):
        logger.debug("Проверяем access-токен и права доступа...")
        access_token = credentials.credentials
        payload: Token = jwt_service.decode_token(access_token)

        if await blacklist_service.is_exists(payload.jti):
            raise SessionHasExpired

        if required_permissions and not set(required_permissions).issubset(set(payload.scope)):
            raise Forbidden

        request.state.user = payload.user_uuid
        return payload

    return check_permission
