from abc import ABC, abstractmethod
from datetime import timedelta
from uuid import UUID

from src.domain.entities import Permission, Role, Session, User


class AbstractUserRepository(ABC):
    @abstractmethod
    async def create(self, email: str, password: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        raise NotImplementedError


class AbstractSessionRepository(ABC):
    @abstractmethod
    async def create(self, session: Session) -> Session:
        raise NotImplementedError

    @abstractmethod
    async def get_by_refresh_token(self, refresh_token: str) -> Session | None:
        raise NotImplementedError

    @abstractmethod
    async def get_sessions_by_user_id(self, user_id: str | UUID) -> list[Session]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, session: Session) -> Session | None:
        raise NotImplementedError


class AbstractPermissionRepository(ABC):
    @abstractmethod
    async def create_permission(self, slug: str, description: str | None) -> Permission:
        raise NotImplementedError

    @abstractmethod
    async def delete_permission(self, permission: Permission) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_permission(self, slug: str) -> Permission:
        raise NotImplementedError

    @abstractmethod
    async def get_all_permissions(self) -> list[Permission]:
        raise NotImplementedError

    @abstractmethod
    async def update_permission(self, permission: Permission) -> Permission:
        raise NotImplementedError


class AbstractRoleRepository(ABC):
    @abstractmethod
    async def create_role(
        self,
        slug: str,
        title: str,
        permissions: list[Permission],
        description: str | None,
    ) -> Role:
        raise NotImplementedError

    @abstractmethod
    async def delete_role(self, role: Role) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_role(self, slug: str) -> Role:
        raise NotImplementedError

    @abstractmethod
    async def get_all_roles(self) -> list[Role]:
        raise NotImplementedError

    @abstractmethod
    async def update_role(self, role: Role) -> Role:
        raise NotImplementedError

    @abstractmethod
    async def add_role_to_user(self, user_id: UUID, role_slug: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete_role_to_user(self, user_id: UUID, role_slug: str) -> bool:
        raise NotImplementedError


class AbstractBlacklistRepository(ABC):
    @abstractmethod
    def get_value(self, key: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def set_value(self, key: str, value: str, exp: timedelta) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_many_values(self, values: list[dict[str, str]], exp: timedelta) -> None:
        raise NotImplementedError
