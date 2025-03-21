from uuid import uuid4

import pytest

from src.domain.entities import Session
from src.services.sessions import SessionService
from tests.unit.repositories import FakeSessionRepository


@pytest.fixture
def fake_session_repository() -> FakeSessionRepository:
    return FakeSessionRepository()


@pytest.fixture
def session_service(fake_session_repository) -> SessionService:
    return SessionService(fake_session_repository)


@pytest.fixture
def session() -> Session:
    session = Session(
        id=None,
        user_id=uuid4(),
        user_agent="pytest_user_agent",
        jti=uuid4(),
        refresh_token="test_refresh_token",
        user_ip="test_ip",
        is_active=True,
    )
    return session


@pytest.fixture
def current_session() -> Session:
    session = Session(
        id=None,
        user_id=uuid4(),
        user_agent="pytest_user_agent",
        jti=uuid4(),
        refresh_token="current_test_refresh_token",
        user_ip="test_ip",
        is_active=True,
    )
    return session


@pytest.mark.asyncio
async def test_create_new_session(session, session_service):
    new_session = await session_service.create_new_session(session=session)
    assert new_session.user_id == session.user_id
    assert new_session.is_active


@pytest.mark.asyncio
async def test_deactivate_current_session(session_service, session):
    created_session = await session_service.create_new_session(session)
    deactivate_session = await session_service.deactivate_current_session(created_session.refresh_token)
    assert created_session.jti == deactivate_session.jti
    assert created_session.refresh_token == deactivate_session.refresh_token
    assert not deactivate_session.is_active


@pytest.mark.asyncio
async def test_deactivate_all_without_current(session, current_session, session_service):
    created_session = await session_service.create_new_session(session=session)
    current_session.user_id = session.user_id
    current_session = await session_service.create_new_session(session=current_session)
    deactivate_sessions = await session_service.deactivate_all_without_current(current_session.refresh_token)

    first_deactivated_session = deactivate_sessions[0] if deactivate_sessions else None
    assert first_deactivated_session is not None
    assert first_deactivated_session.jti == created_session.jti
    assert not first_deactivated_session.is_active
    assert current_session.jti not in [s.jti for s in deactivate_sessions]
