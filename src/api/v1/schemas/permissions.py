from pydantic import BaseModel


class PermissionBase(BaseModel):
    slug: str
    description: str | None


class PermissionResponse(PermissionBase):
    pass


class PermissionCreate(PermissionBase):
    pass
