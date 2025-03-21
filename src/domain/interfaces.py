from abc import ABC, abstractmethod
from datetime import timedelta
from uuid import UUID

from src.domain.entities import Session, Token, User


class AbstractJWTService(ABC):
    @abstractmethod
    def generate_access_token(self, user: User) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_refresh_token(self, user: User) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode_token(self, jwt_token: str) -> Token:
        raise NotImplementedError


class AbstractAuthService(ABC):
    @abstractmethod
    async def registration_new_user(self, email: str, password: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def login_user(self, email: str, password: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> User:
        raise NotImplementedError


class AbstractSessionService(ABC):
    @abstractmethod
    async def create_new_session(self, session: Session) -> Session:
        raise NotImplementedError

    @abstractmethod
    async def deactivate_current_session(self, refresh_token: str) -> Session | None:
        raise NotImplementedError

    @abstractmethod
    async def deactivate_all_without_current(self, refresh_token: str) -> list[Session]:
        raise NotImplementedError

    @abstractmethod
    async def update_session_refresh_token(self, old_refresh_token: str, new_refresh_token: str) -> Session | None:
        raise NotImplementedError

    @abstractmethod
    async def get_current_user_sessions(self, user_id: UUID | str) -> list[Session]:
        raise NotImplementedError


class AbstractBlacklistService(ABC):
    @abstractmethod
    async def is_exists(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def set_one_value(self, key: str, value: str, exp: timedelta) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set_many_values(self, values: list[dict[str, str]], exp: timedelta) -> None:
        raise NotImplementedError


class AbstractUserService(ABC):
    @abstractmethod
    async def get_current_user_profile(self, user_id: UUID | str) -> User:
        raise NotImplementedError


class AbstractOAuthService(ABC):
    @abstractmethod
    async def get_oauth_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_user_info(self, code: str) -> str:
        raise NotImplementedError
