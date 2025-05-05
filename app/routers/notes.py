from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.note import (
    NoteCreate,
    NoteOut,
    TranslationRequest,
    TranslationResponse,
)
from app.models.note import Note
from app.db import SessionLocal
from app.translation import translate_text


router = APIRouter(prefix="/notes", tags=["notes"])


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.post("/", response_model=NoteOut)
async def create_note(note: NoteCreate,
                      db: AsyncSession = Depends(get_db)):
    new_note = Note(
        **note.model_dump(), owner_id=1)
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note


@router.get("/", response_model=list[NoteOut])
async def read_notes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note))
    return result.scalars().all()


@router.put("/{note_id}", response_model=NoteOut)
async def update_note(note_id: int,
                      updated_note: NoteCreate,
                      db: AsyncSession = Depends(get_db)):
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
async def delete_note(note_id: int,
                      db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    await db.delete(note)
    await db.commit()
    return {"detail": "Note deleted"}


@router.post("/translate", response_model=TranslationResponse)
async def translate_note_text(translation_request:
                              TranslationRequest):
    translated = await translate_text(
        text=translation_request.text,
        source_lang=translation_request.source_lang,
        target_lang=translation_request.target_lang
    )

    return TranslationResponse(
        original_text=translation_request.text,
        translated_text=translated
    )
