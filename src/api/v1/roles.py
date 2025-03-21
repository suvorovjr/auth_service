from fastapi import APIRouter, Depends

from src.api.v1.schemas import roles
from src.services.role import RoleService, get_role_service

roles_router = APIRouter()


@roles_router.get("/", response_model=list[roles.RoleResponse])
async def get_all_roles(role_service: RoleService = Depends(get_role_service)):
    return await role_service.get()


@roles_router.get("/{slug}/", response_model=roles.RoleResponse)
async def get_role(slug: str, role_service: RoleService = Depends(get_role_service)):
    return await role_service.get(slug=slug)


@roles_router.post("/", response_model=roles.RoleResponse)
async def create_role(data: roles.RoleCreateOrUpdate, role_service: RoleService = Depends(get_role_service)):
    return await role_service.create_or_update(data=data)


@roles_router.patch("/{slug}/", response_model=roles.RoleResponse)
async def change_role(
    slug: str,
    data: roles.RoleCreateOrUpdate,
    role_service: RoleService = Depends(get_role_service),
):
    return await role_service.create_or_update(data=data, slug=slug)


@roles_router.delete("/{slug}/", response_model=bool)
async def delete_role(slug: str, role_service: RoleService = Depends(get_role_service)):
    return await role_service.delete(slug=slug)


@roles_router.post("/add-role-to-user/", response_model=bool)
async def add_role_to_user(data: roles.AddOrDeleteRoleToUser, role_service: RoleService = Depends(get_role_service)):
    return await role_service.add_role_to_user(data=data)


@roles_router.post("/delete-role-from-user/", response_model=bool)
async def delete_role_from_user(
    data: roles.AddOrDeleteRoleToUser, role_service: RoleService = Depends(get_role_service)
):
    return await role_service.delete_role_from_user(data=data)
