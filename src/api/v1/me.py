from fastapi import APIRouter, Depends, status

from src.api.v1.dependencies import AuthDep, SessionDep, UserServiceDep, get_access_token_data
from src.api.v1.schemas.me import ChangePasswordForm, ProfileResponse, Session
from src.domain.entities import Token

me_router = APIRouter()


@me_router.get("/", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def my_profile(user_service: UserServiceDep, payload: Token = Depends(get_access_token_data)):
    user_data = await user_service.get_current_user_profile(user_id=payload.user_uuid)
    return user_data


@me_router.get("/{uuid}/sessions/", response_model=list[Session], status_code=status.HTTP_200_OK)
async def my_sessions(session_service: SessionDep, payload: Token = Depends(get_access_token_data)):
    sessions = await session_service.get_current_user_sessions(user_id=payload.user_uuid)
    return sessions


@me_router.post("/change-password/", status_code=status.HTTP_200_OK)
async def change_password(
    change_password_form: ChangePasswordForm,
    auth_service: AuthDep,
    payload: Token = Depends(get_access_token_data),
):
    await auth_service.change_password(
        user_id=payload.user_uuid,
        old_password=change_password_form.current_password,
        new_password=change_password_form.new_password,
    )
    return {"ok": True}
