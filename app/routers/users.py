from fastapi import APIRouter, Depends, HTTPException
from app.db import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.user import UserCreate
from app.models.user import User
from app.auth import get_password_hash, create_access_token, verify_password


router = APIRouter(prefix="/users", tags=["users"])


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.post("/register")
async def register(user: UserCreate,
                   db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(
        User.username == user.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400,
                            detail="Username already registered")

    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "User registered successfully"}


@router.post("/login")
async def login(user: UserCreate,
                db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(
        User.username == user.username))
    db_user = result.scalar_one_or_none()
    if not db_user or not verify_password(user.password,
                                          db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}
