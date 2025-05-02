from fastapi.testclient import TestClient
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import httpx

from app.main import app
from app.db import Base
from app.routers.users import get_db
from app.models import user

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as client:
        yield client

@pytest_asyncio.fixture
async def async_client(test_db):
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(base_url="http://test", transport=httpx.ASGITransport(app=app)) as ac:
        yield ac

@pytest.fixture
def test_note_data():
    return {
        "title": "Test Note",
        "content": "Test content"
    }