import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.notes import create_note, read_notes, update_note, delete_note, translate_note_text
from app.models.note import Note
from app.schemas.note import NoteCreate, TranslationRequest
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_create_note():
    mock_db = AsyncMock(spec=AsyncSession)
    note_data = NoteCreate(title="Test Note", content="Test Content")

    result = await create_note(note=note_data, db=mock_db)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()
    assert result.title == "Test Note"
    assert result.content == "Test Content"
    assert result.owner_id == 1  # Default owner_id


@pytest.mark.asyncio
async def test_read_notes():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_note1 = Note(id=1, title="Note 1", content="Content 1", owner_id=1)
    mock_note2 = Note(id=2, title="Note 2", content="Content 2", owner_id=1)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        mock_note1, mock_note2]
    mock_db.execute.return_value = mock_result

    result = await read_notes(db=mock_db)

    mock_db.execute.assert_called_once()
    assert len(result) == 2
    assert result[0].title == "Note 1"
    assert result[1].title == "Note 2"


@pytest.mark.asyncio
async def test_update_note_success():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_note = MagicMock(spec=Note)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_note
    mock_db.execute.return_value = mock_result

    note_data = NoteCreate(title="Updated Title", content="Updated Content")

    result = await update_note(note_id=1, updated_note=note_data, db=mock_db)

    mock_db.execute.assert_called_once()
    assert mock_note.title == "Updated Title"
    assert mock_note.content == "Updated Content"
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_note_not_found():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None  # Note not found
    mock_db.execute.return_value = mock_result

    note_data = NoteCreate(title="Updated Title", content="Updated Content")

    with pytest.raises(HTTPException) as exc_info:
        await update_note(note_id=999, updated_note=note_data, db=mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Note not found"
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_note_success():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_note = MagicMock(spec=Note)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_note
    mock_db.execute.return_value = mock_result

    result = await delete_note(note_id=1, db=mock_db)

    mock_db.execute.assert_called_once()
    mock_db.delete.assert_awaited_once_with(mock_note)
    mock_db.commit.assert_awaited_once()
    assert result == {"detail": "Note deleted"}


@pytest.mark.asyncio
async def test_delete_note_not_found():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None  # Note not found
    mock_db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await delete_note(note_id=999, db=mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Note not found"
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_translate_note_text():
    translation_request = TranslationRequest(
        text="Привет мир",
        source_lang="ru",
        target_lang="en"
    )

    with patch("app.routers.notes.translate_text", return_value="Hello world") as mock_translate:
        result = await translate_note_text(translation_request=translation_request)

    mock_translate.assert_called_once_with(
        text="Привет мир",
        source_lang="ru",
        target_lang="en"
    )
    assert result.original_text == "Привет мир"
    assert result.translated_text == "Hello world"
