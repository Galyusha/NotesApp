from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.note import NoteCreate, NoteOut
from app.models.note import Note
from app.db import SessionLocal


router = APIRouter(prefix="/notes", tags=["notes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=NoteOut)
async def create_note(note: NoteCreate, db: AsyncSession = Depends(get_db)):
    new_note = Note(**note.dict(), owner_id=1)
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note

@router.get("/", response_model=list[NoteOut])
async def read_notes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note))
    return result.scalars().all()