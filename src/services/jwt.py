import logging
import uuid
from datetime import datetime, timedelta

import jwt

from src.core.config import settings
from src.domain.entities import Token, User
from src.domain.exceptions import SessionHasExpired
from src.domain.interfaces import AbstractJWTService

logger = logging.getLogger(__name__)


class JWTService(AbstractJWTService):
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_lifetime: timedelta = timedelta(minutes=15),
        refresh_token_lifetime: timedelta = timedelta(days=60),
    ) -> None:
        """
        Инициализирует JWT сервис с заданными параметрами.

        :param secret_key: Секретный ключ для подписи токенов.
        :param algorithm: Алгоритм шифрования (по умолчанию "H256").
        :param access_token_lifetime: Время жизни access токена.
        :param refresh_token_lifetime: Время жизни refresh токена.
        """

        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_lifetime = access_token_lifetime
        self._refresh_token_lifetime = refresh_token_lifetime
        self._jti = str(uuid.uuid4())

    def _generate_token(self, user: User, token_lifetime: timedelta) -> str:
        """
        Генерирует JWT токен для указанного пользователя с заданным временем жизни.

        :param user: Объект пользователя, для которого создаётся токен.
        :param token_lifetime: Время жизни токена.
        :return: Сгенерированный JWT токен в виде строки.
        """

        now = datetime.now()
        payload = {
            "user_uuid": str(user.id),
            "iat": now.timestamp(),
            "exp": (now + token_lifetime).timestamp(),
            "jti": self._jti,
            "scope": [perm.slug for role in user.roles for perm in role.permissions],
        }
        return jwt.encode(payload=payload, key=self._secret_key, algorithm=self._algorithm)

    def generate_access_token(self, user: User) -> str:
        """
        Генерирует access токен для указанного пользователя.

        :param user: Объект пользователя, для которого создаётся access токен.
        :return: Сгенерированный access JWT токен в виде строки.
        """

        return self._generate_token(user=user, token_lifetime=self._access_token_lifetime)

    def generate_refresh_token(self, user: User) -> str:
        """
        Генерирует refresh токен для указанного пользователя.

        :param user: Объект пользователя, для которого создаётся refresh токен.
        :return: Сгенерированный refresh JWT токен в виде строки.
        """

        return self._generate_token(user=user, token_lifetime=self._refresh_token_lifetime)

    def decode_token(self, jwt_token: str) -> Token:
        """
        Декодирует и валидирует JWT токен.

        :param jwt_token: JWT токен в виде строки.
        :return: Объект Token с полезной нагрузкой из токена.
        :raises SessionHasExpired: Если токен просрочен.
        """

        try:
            payload = jwt.decode(jwt=jwt_token, key=self._secret_key, algorithms=[self._algorithm])
            token = Token(**payload)
        except jwt.ExpiredSignatureError:
            logger.error("Токен %s просрочен.", jwt_token)
            raise SessionHasExpired
        except (jwt.PyJWTError, TypeError):
            logger.error("Ошибка декодирования токена %s", jwt_token)
            raise SessionHasExpired
        return token

    @property
    def jti(self):
        return self._jti


def get_jwt_service() -> JWTService:
    jwt_service = JWTService(
        secret_key=settings.service.secret_key.get_secret_value(),
        algorithm=settings.service.jwt_algorithm,
        access_token_lifetime=timedelta(minutes=30),
        refresh_token_lifetime=timedelta(days=30),
    )
    return jwt_service
