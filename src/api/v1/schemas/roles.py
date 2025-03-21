from pydantic import BaseModel, Field

from .permissions import PermissionResponse


class RoleCreateOrUpdate(BaseModel):
    slug: str
    title: str
    description: str | None
    permissions: list[str] = Field(..., min_length=1)


class RoleResponse(BaseModel):
    slug: str
    title: str
    description: str | None
    permissions: list[PermissionResponse]


class AddOrDeleteRoleToUser(BaseModel):
    role_slug: str
    user_id: str
