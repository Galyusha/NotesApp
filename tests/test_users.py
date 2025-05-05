import pytest
import re


@pytest.mark.asyncio
async def test_register_user(async_client):
    response = await async_client.post("/users/register",
                                       json={"username": "testuser",
                                             "password": "testpass"})
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"


@pytest.mark.asyncio
async def test_register_duplicate_user(async_client):
    await async_client.post("/users/register",
                            json={"username": "testuser",
                                  "password": "testpass"})
    response = await async_client.post("/users/register",
                                       json={"username": "testuser",
                                             "password": "testpass"})
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(async_client):
    await async_client.post("/users/register",
                            json={"username": "testuser",
                                  "password": "testpass"})
    response = await async_client.post("/users/login",
                                       json={"username": "testuser",
                                             "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client):
    await async_client.post("/users/register",
                            json={"username": "testuser",
                                  "password": "testpass"})
    response = await async_client.post("/users/login",
                                       json={"username": "testuser",
                                             "password": "wrong"})
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client):
    response = await async_client.post("/users/login",
                                       json={"username": "nouser",
                                             "password": "nopass"})
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_token_format(async_client):
    await async_client.post("/users/register",
                            json={"username": "formatuser",
                                  "password": "secure123"})
    response = await async_client.post("/users/login",
                                       json={"username": "formatuser",
                                             "password": "secure123"})
    token = response.json().get("access_token")
    assert token and re.match(
        r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$', token)


@pytest.mark.asyncio
async def test_db_dependency(async_client):
    response = await async_client.get("/users/register")
    assert response.status_code == 405
