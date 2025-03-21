import pytest

from src.domain.entities import User
from src.domain.exceptions import UserIsExists, WrongEmailOrPassword, WrongOldPassword
from src.services.auth import AuthService
from tests.unit.repositories import FakeUserRepository


@pytest.fixture
def fake_user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def auth_service(fake_user_repository) -> AuthService:
    return AuthService(user_repository=fake_user_repository)


@pytest.fixture
def user() -> User:
    user = {
        "id": "user-1",
        "email": "test_email",
        "password": "test_password",
        "is_active": True,
    }
    return User(**user)


@pytest.mark.asyncio
async def test_create_new_user(auth_service, user):
    new_user = await auth_service.registration_new_user(email=user.email, password=user.password)

    assert user.email == new_user.email
    assert user.password != new_user.password


@pytest.mark.asyncio
async def test_register_existing_user(auth_service, user):
    new_user = await auth_service.registration_new_user(email=user.email, password=user.password)

    with pytest.raises(UserIsExists):
        await auth_service.registration_new_user(email=new_user.email, password=new_user.password)


@pytest.mark.asyncio
async def test_successful_login(auth_service, user):
    await auth_service.registration_new_user(email=user.email, password=user.password)

    assert await auth_service.login_user(email=user.email, password=user.password)


@pytest.mark.asyncio
async def test_login_with_nonexistent_user(auth_service):
    email = "unknown@example.com"
    password = "password"

    with pytest.raises(WrongEmailOrPassword):
        await auth_service.login_user(email=email, password=password)


@pytest.mark.asyncio
async def test_login_with_invalid_password(auth_service):
    email = "test@example.com"
    correct_password = "securepassword"
    wrong_password = "wrongpassword"

    await auth_service.registration_new_user(email=email, password=correct_password)

    with pytest.raises(WrongEmailOrPassword):
        await auth_service.login_user(email=email, password=wrong_password)


@pytest.mark.asyncio
async def test_change_password(auth_service):
    email = "test@example.com"
    old_password = "oldpassword"
    new_password = "newpassword"

    user = await auth_service.registration_new_user(email=email, password=old_password)
    updated_user = await auth_service.change_password(
        user_id=user.id, old_password=old_password, new_password=new_password
    )

    assert auth_service._verify_password(new_password, updated_user.password)


@pytest.mark.asyncio
async def test_change_password_with_invalid_old_password(auth_service):
    email = "test@example.com"
    old_password = "oldpassword"
    new_password = "newpassword"
    wrong_old_password = "wrongoldpassword"

    user = await auth_service.registration_new_user(email=email, password=old_password)

    with pytest.raises(WrongOldPassword):
        await auth_service.change_password(user_id=user.id, old_password=wrong_old_password, new_password=new_password)
