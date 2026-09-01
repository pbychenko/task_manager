import os
from typing import AsyncGenerator

import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.database import Base
from app.utils.unitofwork import UnitOfWork
from main import app

load_dotenv()

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]


def _to_asyncpg_url(url: str) -> str:
    return make_url(url).set(drivername="postgresql+asyncpg")


test_engine = create_async_engine(
    _to_asyncpg_url(TEST_DATABASE_URL), poolclass=NullPool
)

test_async_session_maker = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

class TestUnitOfWork(UnitOfWork):
    """UnitOfWork, использующий тестовый session_factory вместо боевого."""

    def __init__(self):
        self.session_factory = test_async_session_maker


app.dependency_overrides[UnitOfWork] = TestUnitOfWork


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables() -> AsyncGenerator[None, None]:
    yield

    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Прямой доступ к сессии тестовой БД — удобно готовить/проверять данные в обход API."""
    async with test_async_session_maker() as session:
        yield session


TEST_USER = {"username": "user1", "password": "password1"}
task_data = {"title": "new task", "description": "new_task_description"}


@pytest_asyncio.fixture
async def registered_user(async_client: AsyncClient) -> dict:
    response = await async_client.post("/users/register/", json=TEST_USER)
    assert response.status_code == 201

    user = response.json()
    
    return {**user, "password": TEST_USER["password"]}


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient, registered_user: dict) -> dict:
    response = await async_client.post(
        "/users/login/",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def task(async_client: AsyncClient, auth_headers: dict) -> dict:
    response = await async_client.post("/tasks/", json=task_data, headers=auth_headers)

    assert response.status_code == 200

    return response.json()
