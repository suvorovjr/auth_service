from uuid import UUID

from fastapi import Depends

from src.domain.entities import User
from src.domain.interfaces import AbstractUserService
from src.domain.repositories import AbstractUserRepository
from src.infrastructure.repositories.user import get_user_repository


class UserService(AbstractUserService):
    def __init__(self, user_repository: AbstractUserRepository):
        self._repository: AbstractUserRepository = user_repository

    async def get_current_user_profile(self, user_id: UUID | str) -> User:
        user = await self._repository.get_by_id(user_id=user_id)
        return user


def get_user_service(user_repository: AbstractUserRepository = Depends(get_user_repository)):
    user_service = UserService(user_repository=user_repository)
    return user_service
