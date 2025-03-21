from fastapi import APIRouter, Depends, status

from src.api.v1.schemas.permissions import PermissionCreate, PermissionResponse
from src.services.permission import PermissionService, get_permission_service

perm_router = APIRouter()


@perm_router.get("/", response_model=list[PermissionResponse], status_code=status.HTTP_200_OK)
async def get_all_permissions(
    permission_service: PermissionService = Depends(get_permission_service),
):
    return await permission_service.get()


@perm_router.get("/{slug}/", response_model=PermissionResponse, status_code=status.HTTP_200_OK)
async def get_permission(slug: str, permission_service: PermissionService = Depends(get_permission_service)):
    return await permission_service.get(slug=slug)


@perm_router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    data: PermissionCreate,
    permission_service: PermissionService = Depends(get_permission_service),
):
    return await permission_service.create_or_update(data=data)


@perm_router.patch("/{slug}/", response_model=PermissionResponse, status_code=status.HTTP_202_ACCEPTED)
async def change_permissions(
    slug: str,
    data: PermissionCreate,
    permission_service: PermissionService = Depends(get_permission_service),
):
    return await permission_service.create_or_update(data=data, slug=slug)


@perm_router.delete("/{slug}/", response_model=bool)
async def delete_permission(slug: str, permission_service: PermissionService = Depends(get_permission_service)):
    return await permission_service.delete(slug=slug)
