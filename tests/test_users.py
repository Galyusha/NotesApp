import pytest

async def test_register_user(client):
    response = client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"

@pytest.mark.asyncio
async def test_register_duplicate_user(async_client):
    await async_client.post("/register", json={"username": "testuser", "password": "testpass"})
    response =await async_client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(async_client):
    await async_client.post("/register", json={"username": "testuser", "password": "testpass"})
    response = await async_client.post("/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client):
    await async_client.post("/register", json={"username": "testuser", "password": "testpass"})
    response = await async_client.post("/login", json={"username": "testuser", "password": "wrong"})
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]