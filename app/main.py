from fastapi import FastAPI
from app.routers import users, notes
from app.db import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Simple Notes App")

app.include_router(users.router)
app.include_router(notes.router)