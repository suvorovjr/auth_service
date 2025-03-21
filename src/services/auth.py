import logging

from fastapi import Depends
from passlib.context import CryptContext

from src.domain.entities import User
from src.domain.exceptions import WrongEmailOrPassword, WrongOldPassword
from src.domain.repositories import AbstractUserRepository
from src.infrastructure.repositories.user import get_user_repository

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repository: AbstractUserRepository):
        self._user_repository: AbstractUserRepository = user_repository
        self._context: CryptContext = CryptContext(schemes=["bcrypt"])

    async def registration_new_user(self, email: str, password: str) -> User:
        """
        Регистрирует нового пользователя, хешируя его пароль перед сохранением.

        :param email: Email пользователя.
        :param password: Открытый пароль пользователя.
        :return: Созданный объект User.
        """

        hashed_password = self._get_password_hash(password)
        new_user = await self._user_repository.create(email=email, password=hashed_password)
        return new_user

    async def login_user(self, email: str, password: str) -> User | None:
        """
        Проверяет учетные данные пользователя при входе.

        :param email: Email пользователя.
        :param password: Открытый пароль пользователя.
        :return: True, если аутентификация успешна.
        :raises WrongEmailOrPassword: Если учетные данные неверны.
        """

        user = await self._user_repository.get_by_email(email=email)
        if user is None or not self._verify_password(password, user.password):
            logger.error("Неверный логин для пользователя %s", email)
            raise WrongEmailOrPassword
        return user

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> User:
        """
        Изменяет пароль пользователя.

        :param user_id: Идентификатор пользователя.
        :param old_password: Старый пароль пользователя.
        :param new_password: Новый пароль пользователя.
        :return: Обновленный объект User.
        :raises WrongOldPassword: Если старый пароль неверен.
        """

        user = await self._user_repository.get_by_id(user_id=user_id)
        if not self._verify_password(old_password, user.password):
            logger.error("Неверный пароль для пользоавтеля %s.", str(user.id))
            raise WrongOldPassword
        hashed_new_password = self._get_password_hash(new_password)
        user.password = hashed_new_password
        updated_user = await self._user_repository.update(user=user)
        return updated_user

    def _get_password_hash(self, password) -> str:
        """
        Генерирует хеш пароля с использованием bcrypt.

        :param password: Открытый пароль.
        :return: Захешированный пароль.
        """

        return self._context.hash(password)

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Проверяет соответствие пароля и его хеша.

        :param password: Открытый пароль.
        :param hashed_password: Захешированный пароль.
        :return: True, если пароль корректен.
        """

        return self._context.verify(password, hashed_password)


def get_auth_service(
    user_repository: AbstractUserRepository = Depends(get_user_repository),
) -> AuthService:
    auth_service: AuthService = AuthService(user_repository=user_repository)
    return auth_service
