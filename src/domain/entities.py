from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class BaseEntity:
    def to_dict(self, exclude: set[str]) -> dict[str, Any]:
        """
        Преобразует объект в словарь, исключая указанные поля.

        :param exclude: множество полей, которые нужно исключить
        :return: словарь с данными объекта
        """

        exclude = set(exclude) if exclude else set()
        return {key: value for key, value in asdict(self).items() if key not in exclude}


@dataclass
class User(BaseEntity):
    id: UUID | None
    email: str
    password: str
    is_active: bool
    roles: list = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Token:
    user_uuid: str
    iat: str
    exp: str
    jti: str
    scope: list[str]


@dataclass
class Permission:
    slug: str
    description: str


@dataclass
class Role:
    slug: str
    title: str
    description: str
    permissions: list[Permission] = field(default_factory=list)


@dataclass
class Session(BaseEntity):
    id: UUID | None
    user_id: UUID
    user_agent: str
    jti: UUID
    refresh_token: str
    user_ip: str | None
    is_active: bool
    device_type: str = "other"
    created_at: datetime | None = None
    updated_at: datetime | None = None
