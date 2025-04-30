import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import Base, SessionLocal

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture()
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture()
def client(test_db):
    app.dependency_overrides[SessionLocal] = TestingSessionLocal
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_note(client):
    response = client.post("/notes/", json={"title": "Test", "content": "Test content"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test"


@pytest.mark.asyncio
async def test_update_note(client):
    create_res = client.post("/notes/", json={"title": "Test", "content": "Test content"})
    note_id = create_res.json()["id"]
    update_res = client.put(f"/notes/{note_id}", json={"title": "Updated", "content": "Updated"})
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated"

@pytest.mark.asyncio
async def test_update_nonexistent_note(client):
    response = client.put("/notes/999", json={"title": "Test", "content": "Test"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_note(client):
    create_res = client.post("/notes/", json={"title": "Test", "content": "Test content"})
    note_id = create_res.json()["id"]
    delete_res = client.delete(f"/notes/{note_id}")
    assert delete_res.status_code == 200
    assert delete_res.json() == {"detail": "Note deleted"}