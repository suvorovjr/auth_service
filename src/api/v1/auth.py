from fastapi import APIRouter, Depends, Request, Response, status

from src.api.v1.dependencies import (
    AuthDep,
    BlacklistDep,
    JWTDep,
    SessionDep,
    get_current_user,
    get_refresh_token,
    set_refresh_token,
)
from src.api.v1.schemas.auth_schemas import LoginForm, LoginResponse, RegisterForm, UserResponse
from src.core.config import settings
from src.domain.entities import User
from src.domain.exceptions import PasswordsNotMatch
from src.domain.factories.session import SessionFactory

auth_router = APIRouter()


@auth_router.post("/register/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(register_form: RegisterForm, auth_service: AuthDep) -> UserResponse:
    if register_form.password != register_form.confirm_password:
        raise PasswordsNotMatch
    user = await auth_service.registration_new_user(register_form.email, register_form.password)
    return user


@auth_router.post("/login/", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def login(
    request: Request,
    response: Response,
    login_form: LoginForm,
    auth_service: AuthDep,
    jwt_service: JWTDep,
    session_service: SessionDep,
) -> LoginResponse:
    user = await auth_service.login_user(email=login_form.email, password=login_form.password)
    access_token = jwt_service.generate_access_token(user)
    refresh_token = jwt_service.generate_refresh_token(user)
    session = SessionFactory.create(
        user_id=user.id,
        jti=jwt_service.jti,
        user_agent=request.headers["user-agent"],
        refresh_token=refresh_token,
        user_ip=request.headers["host"],
    )
    await session_service.create_new_session(session=session)
    set_refresh_token(response=response, refresh_token=refresh_token)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@auth_router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    session_service: SessionDep,
    blacklist_service: BlacklistDep,
    refresh_token: str = Depends(get_refresh_token),
):
    deactivate_session = await session_service.deactivate_current_session(refresh_token)
    await blacklist_service.set_one_value(
        deactivate_session.jti,
        deactivate_session.user_id,
        settings.service.access_token_expire,
    )
    return


@auth_router.post("/refresh/", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def refresh(
    response: Response,
    session_service: SessionDep,
    jwt_service: JWTDep,
    refresh_token: str = Depends(get_refresh_token),
    current_user: User = Depends(get_current_user),
) -> LoginResponse:
    new_refresh_token = jwt_service.generate_refresh_token(user=current_user)
    new_access_token = jwt_service.generate_access_token(user=current_user)
    new_jti = jwt_service.jti
    _ = await session_service.update_session_refresh_token(refresh_token, new_refresh_token, new_jti)
    set_refresh_token(response=response, refresh_token=new_refresh_token)
    return LoginResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@auth_router.post("/logout-others/", status_code=status.HTTP_204_NO_CONTENT)
async def logout_others(
    session_service: SessionDep,
    black_list_service: BlacklistDep,
    current_refresh_token: str = Depends(get_refresh_token),
):
    deactivate_sessions = await session_service.deactivate_all_without_current(current_refresh_token)
    jti_tokens = {session.jti: session.user_id for session in deactivate_sessions}
    await black_list_service.set_many_values(jti_tokens, settings.service.access_token_expire)
    return
