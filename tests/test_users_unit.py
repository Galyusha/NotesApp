import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.users import register, login
from app.models.user import User
from app.schemas.user import UserCreate
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_register_success():
    mock_db = AsyncMock(spec=AsyncSession)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    user_data = UserCreate(username="testuser", password="password123")

    with patch("app.routers.users.get_password_hash",
               return_value="hashed_password"):
        result = await register(user=user_data, db=mock_db)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()
    assert result == {"message": "User registered successfully"}


@pytest.mark.asyncio
async def test_register_username_taken():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_existing_user = User(
        username="testuser", hashed_password="hashed_password"
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_existing_user
    mock_db.execute.return_value = mock_result

    user_data = UserCreate(username="testuser", password="password123")

    with pytest.raises(HTTPException) as exc_info:
        await register(user=user_data, db=mock_db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Username already registered"
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_login_success():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.hashed_password = "hashed_password"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result

    user_data = UserCreate(username="testuser", password="password123")

    with patch("app.routers.users.verify_password",
               return_value=True) as mock_verify:
        with patch("app.routers.users.create_access_token",
                   return_value="test_token") as mock_create_token:
            result = await login(user=user_data, db=mock_db)

    mock_verify.assert_called_once_with("password123", "hashed_password")
    mock_create_token.assert_called_once_with({"sub": "testuser"})
    assert result == {"access_token": "test_token", "token_type": "bearer"}


@pytest.mark.asyncio
async def test_login_user_not_found():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    user_data = UserCreate(username="nonexistent", password="password123")

    with pytest.raises(HTTPException) as exc_info:
        await login(user=user_data, db=mock_db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_incorrect_password():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.hashed_password = "hashed_password"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result

    user_data = UserCreate(username="testuser", password="wrong_password")

    with patch("app.routers.users.verify_password",
               return_value=False) as mock_verify:
        with pytest.raises(HTTPException) as exc_info:
            await login(user=user_data, db=mock_db)

    mock_verify.assert_called_once_with("wrong_password", "hashed_password")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid credentials"
