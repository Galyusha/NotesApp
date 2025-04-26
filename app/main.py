from fastapi import FastAPI
from app.routers import users, notes
from app.db import init_db

app = FastAPI(title="Simple Notes App")

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(users.router)
app.include_router(notes.router)