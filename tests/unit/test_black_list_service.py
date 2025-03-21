import asyncio
from datetime import timedelta

import pytest

from services.blacklist import BlacklistService
from tests.unit.repositories import FakeBlacklistRepository


@pytest.fixture
def fake_repository() -> FakeBlacklistRepository:
    return FakeBlacklistRepository()


@pytest.fixture
def black_list_service(fake_repository):
    return BlacklistService(fake_repository)


@pytest.mark.asyncio
async def test_blacklist_set_one(black_list_service):
    key = "token:jti_123"
    assert not await black_list_service.is_exists(key)
    await black_list_service.set_one_value(key, "blacklisted")
    assert await black_list_service.is_exists(key)


@pytest.mark.asyncio
async def test_blacklist_set_many(black_list_service):
    tokens = {
        "token:jti_456": "blacklisted",
        "token:jti_789": "blacklisted",
    }
    await black_list_service.set_many_values(tokens, exp=timedelta(seconds=1))

    assert await black_list_service.is_exists("token:jti_456")
    assert await black_list_service.is_exists("token:jti_789")

    await asyncio.sleep(1.1)

    assert not await black_list_service.is_exists("token:jti_456")
    assert not await black_list_service.is_exists("token:jti_789")
