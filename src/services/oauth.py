import logging
from json import JSONDecodeError
from urllib.parse import urlencode

from fastapi import Depends
from httpx import AsyncClient

from src.core.config import settings
from src.core.http_client import get_http_client
from src.domain.exceptions import (
    OAuthAccessTokenNotFound,
    OAuthResponseDecodeError,
    OAuthTokenExchangeError,
    OAuthUserInfoError,
)
from src.domain.interfaces import AbstractOAuthService

logger = logging.getLogger(__name__)


class YandexOAuthService(AbstractOAuthService):
    YANDEX_OAUTH_AUTHORIZE_URL = "https://oauth.yandex.ru/authorize"
    YANDEX_OAUTH_TOKEN_URL = "https://oauth.yandex.ru/token"
    YANDEX_USER_INFO_URL = "https://login.yandex.ru/info"
    SCOPE = "login:email login:info"

    def __init__(self, http_client: AsyncClient):
        self._client = http_client

    async def get_oauth_url(self) -> str:
        """
        Генерирует URL для перенаправления пользователя на страницу авторизации Яндекса.
        :return: Полный URL авторизации
        """
        params = {
            "response_type": "code",
            "client_id": settings.oauth.yandex_client_id,
            "redirect_uri": settings.oauth.yandex_callback_url,
            "scope": self.SCOPE,
        }
        url = f"{self.YANDEX_OAUTH_AUTHORIZE_URL}?{urlencode(params)}"
        logger.debug("Generated Yandex OAuth URL: %s", url)
        return url

    async def _get_oauth_token(self, code: str) -> str:
        """
        Получает access_token от Яндекса по коду авторизации.
        :param code: Код авторизации, полученный от Яндекса
        :return: access_token
        :raises: OAuthTokenExchangeError, OAuthResponseDecodeError, OAuthAccessTokenNotFound
        """
        request_data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.oauth.yandex_client_id,
            "client_secret": settings.oauth.yandex_client_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = await self._client.post(url=self.YANDEX_OAUTH_TOKEN_URL, data=request_data, headers=headers)

        if response.status_code != 200:
            logger.error("Ошибка при полчении access_token: status=%s, body=%s", response.status_code, response.text)
            raise OAuthTokenExchangeError

        try:
            token_data = response.json()
        except JSONDecodeError as e:
            logger.exception("Ошибка декодирования ответа при получении access_token")
            raise OAuthResponseDecodeError from e

        access_token = token_data.get("access_token")
        if access_token is None:
            logger.error("access_token не найден в ответе: %s", token_data)
            raise OAuthAccessTokenNotFound

        logger.info("Успешно получен access_token")
        return access_token

    async def get_user_info(self, code: str) -> dict[str, str]:
        """
        Получает информацию о пользователе от Яндекса используя access_token.
        :param code: Код авторизации от Яндекса
        :return: Словарь с информацией о пользователе
        :raises: OAuthUserInfoError, OAuthResponseDecodeError
        """
        access_token = await self._get_oauth_token(code)
        headers = {"Authorization": f"OAuth {access_token}"}
        params = {"format": "json"}

        response = await self._client.get(url=self.YANDEX_USER_INFO_URL, headers=headers, params=params)

        if response.status_code != 200:
            logger.error("Ошибка при получении user_info: status=%s, body=%s", response.status_code, response.text)
            raise OAuthUserInfoError

        try:
            user_info = response.json()
        except JSONDecodeError as e:
            logger.exception("Ошибка декодирования ответа user_info")
            raise OAuthResponseDecodeError from e

        logger.info("Успешно получены данные пользователя от Яндекса")
        return user_info


def get_yandex_oauth_service(http_client: AsyncClient = Depends(get_http_client)) -> AbstractOAuthService:
    return YandexOAuthService(http_client=http_client)
