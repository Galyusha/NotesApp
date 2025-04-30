from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
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

@router.put("/{note_id}", response_model=NoteOut)
async def update_note(note_id: int, updated_note: NoteCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.title = updated_note.title
    note.content = updated_note.content
    await db.commit()
    await db.refresh(note)
    return note

@router.delete("/{note_id}")
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    await db.delete(note)
    await db.commit()
    return {"detail": "Note deleted"}
