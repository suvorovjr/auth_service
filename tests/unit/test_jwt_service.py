import asyncio
from datetime import timedelta

import jwt
import pytest

from src.domain.entities import User
from src.services.jwt import JWTService


@pytest.fixture
def secret_key() -> str:
    return "test_secret_key"


@pytest.fixture
def user() -> User:
    user = {
        "id": "user-1",
        "email": "test_email",
        "password": "test_password",
        "is_active": True,
    }
    return User(**user)


@pytest.fixture
def jwt_service(secret_key) -> JWTService:
    return JWTService(secret_key=secret_key)


def test_generate_and_decode_access_token(jwt_service, user):
    access_token = jwt_service.generate_access_token(user=user)
    token_obj = jwt_service.decode_token(access_token)

    assert token_obj.user_uuid == user.id
    assert isinstance(token_obj.scope, list)
    assert token_obj.exp - token_obj.iat == pytest.approx(15 * 60, abs=1)


def test_generate_and_decode_refresh_token(jwt_service, user):
    refresh_token = jwt_service.generate_refresh_token(user=user)
    token_obj = jwt_service.decode_token(refresh_token)

    assert token_obj.user_uuid == user.id
    assert isinstance(token_obj.scope, list)
    assert token_obj.exp - token_obj.iat == pytest.approx(60 * 24 * 60 * 60, abs=1)


@pytest.mark.asyncio
async def test_expired_token(secret_key, user):
    short_lived_jwt_service = JWTService(
        secret_key=secret_key,
        algorithm="HS256",
        access_token_lifetime=timedelta(seconds=1),
    )
    access_token = short_lived_jwt_service.generate_access_token(user)
    await asyncio.sleep(1.1)

    with pytest.raises(jwt.ExpiredSignatureError):
        short_lived_jwt_service.decode_token(access_token)


def test_invalid_token(jwt_service):
    invalid_token = "invalid.token.value"
    with pytest.raises(jwt.PyJWTError):
        jwt_service.decode_token(invalid_token)


def test_access_and_refresh_tokens_have_same_jti(jwt_service, user):
    access_token = jwt_service.generate_access_token(user=user)
    refresh_token = jwt_service.generate_refresh_token(user=user)
    access_token_obj = jwt_service.decode_token(access_token)
    refresh_token_obj = jwt_service.decode_token(refresh_token)

    assert access_token_obj.jti == refresh_token_obj.jti
