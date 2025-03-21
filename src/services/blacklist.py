from datetime import timedelta

from fastapi import Depends

from src.domain.interfaces import AbstractBlacklistService
from src.domain.repositories import AbstractBlacklistRepository
from src.infrastructure.repositories.blacklist import get_blacklist_repository


class BlacklistService(AbstractBlacklistService):
    """Сервис для работы с черным списком токенов."""

    def __init__(self, black_list_repository: AbstractBlacklistRepository):
        """
        Инициализация сервиса.
        :param black_list_repository: Репозиторий черного списка (реализация хранилища).
        """
        self._repository = black_list_repository

    async def is_exists(self, key: str) -> bool:
        """
        Проверяет, существует ли ключ в черном списке.
        :param key: Ключ (например, идентификатор токена).
        :return: True, если ключ существует, иначе False.
        """

        value = await self._repository.get_value(key=key)
        return value is not None

    async def set_one_value(self, key: str, value: str, exp: timedelta | None = None):
        """
        Добавляет один ключ в черный список.
        :param key: Ключ (например, идентификатор токена).
        :param value: Значение, связанное с ключом.
        :param exp: Время жизни ключа (если не указано, ключ будет без срока действия).
        """

        await self._repository.set_value(key=str(key), value=str(value), exp=exp)

    async def set_many_values(self, values: dict[str, str], exp: timedelta | None = None):
        """
        Добавляет несколько значений в храниРепозиторий для управления данными слище.
        :param values: Словарь {ключ: значение}.
        :param exp: Время жизни ключей (если указано, будет установлено время истечения).
        """

        values = {str(k): str(v) for k, v in values.items()}
        await self._repository.set_many_values(values=values, exp=exp)


def get_blacklist_service(
    repository: AbstractBlacklistRepository = Depends(get_blacklist_repository),
) -> AbstractBlacklistService:
    """
    Фабричный метод для получения экземпляра BlackListService.
    :param repository: Репозиторий черного списка.
    :return: Экземпляр сервиса черного списка.
    """
    black_list_service = BlacklistService(repository)
    return black_list_service
