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

from app.core.security import get_hash
from app.db.models import User

@pytest_asyncio.fixture
async def user_factory(db_session: AsyncSession):
    async def create_user(
        username: str,
        password: str,
        role: str
    ) -> dict:
        user = User(
            username=username,
            password=get_hash(password),
            role=role,
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        return {
            "id": user.id,
            "username": username,
            "password": password,
            "role": role,
        }

    return create_user

@pytest_asyncio.fixture
async def admin_user(user_factory) -> dict:
    return await user_factory(
        username="admin",
        password="admin-password",
        role="admin",
    )

@pytest_asyncio.fixture
async def manager_user(user_factory) -> dict:
    return await user_factory(
        username="manager",
        password="manager-password",
        role="manager",
    )

@pytest_asyncio.fixture
async def second_manager_user(user_factory) -> dict:
    return await user_factory(
        username="manager2",
        password="manager2-password",
        role="manager",
    )

@pytest_asyncio.fixture
async def regular_user(user_factory) -> dict:
    return await user_factory(
        username="regular",
        password="regular-password",
        role="user",
    )

# @pytest_asyncio.fixture
# async def registered_user(async_client: AsyncClient) -> dict:
#     response = await async_client.post("/users/register/", json=TEST_USER)
#     assert response.status_code == 201

#     user = response.json()
    
#     return {**user, "password": TEST_USER["password"]}


@pytest_asyncio.fixture
async def regular_user_headers(async_client: AsyncClient, regular_user: dict) -> dict:
    response = await async_client.post(
        "/users/login/",
        json={
            "username": regular_user["username"],
            "password": regular_user["password"],
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(async_client: AsyncClient, admin_user: dict) -> dict:
    response = await async_client.post(
        "/users/login/",
        json={
            "username": admin_user["username"],
            "password": admin_user["password"],
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def manager_headers(async_client: AsyncClient, manager_user: dict) -> dict:
    response = await async_client.post(
        "/users/login/",
        json={
            "username": manager_user["username"],
            "password": manager_user["password"],
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def second_manager_headers(async_client: AsyncClient, second_manager_user: dict) -> dict:
    response = await async_client.post(
        "/users/login/",
        json={
            "username": second_manager_user["username"],
            "password": second_manager_user["password"],
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


project_data = {"name": "new project", "description": "new_project_description"}

@pytest_asyncio.fixture
async def project(async_client: AsyncClient, manager_headers: dict) -> dict:
    response = await async_client.post("/projects/", json=project_data, headers=manager_headers)

    assert response.status_code == 200

    return response.json()


task_data = {"title": "new task", "description": "new_task_description"}

@pytest_asyncio.fixture
async def task(async_client: AsyncClient, manager_headers: dict, project: dict) -> dict:
    response = await async_client.post("/tasks/", json={ **task_data, "project_id": project["id"] }, headers=manager_headers)

    assert response.status_code == 200

    return response.json()
