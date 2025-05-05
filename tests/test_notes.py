import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession,
                                   expire_on_commit=False)


@pytest.fixture(scope="session")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_note(async_client):
    response = await async_client.post("/notes/",
                                       json={"title": "Test",
                                             "content": "Test content"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test"
    assert response.json()["content"] == "Test content"


@pytest.mark.asyncio
async def test_read_notes(async_client):
    await async_client.post("/notes/",
                            json={"title": "Note 1", "content": "Content 1"})
    await async_client.post("/notes/",
                            json={"title": "Note 2", "content": "Content 2"})

    response = await async_client.get("/notes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_update_existing_note(async_client):
    res = await async_client.post("/notes/",
                                  json={"title": "Old", "content": "Content"})
    note_id = res.json()["id"]

    update = await async_client.put(f"/notes/{note_id}",
                                    json={"title": "Updated",
                                          "content": "New content"})
    assert update.status_code == 200
    assert update.json()["title"] == "Updated"


@pytest.mark.asyncio
async def test_update_nonexistent_note(async_client):
    response = await async_client.put("/notes/9999",
                                      json={"title": "New",
                                            "content": "Updated"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


@pytest.mark.asyncio
async def test_delete_existing_note(async_client):
    res = await async_client.post("/notes/",
                                  json={"title": "Temp",
                                        "content": "To delete"})
    note_id = res.json()["id"]

    response = await async_client.delete(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Note deleted"


@pytest.mark.asyncio
async def test_delete_nonexistent_note(async_client):
    response = await async_client.delete("/notes/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


@pytest.mark.asyncio
async def test_delete_note_twice(async_client):
    res = await async_client.post("/notes/",
                                  json={"title": "Temp",
                                        "content": "Temp"})
    note_id = res.json()["id"]

    del_1 = await async_client.delete(f"/notes/{note_id}")
    assert del_1.status_code == 200

    del_2 = await async_client.delete(f"/notes/{note_id}")
    assert del_2.status_code == 404
