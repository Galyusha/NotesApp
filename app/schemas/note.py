from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteOut(NoteCreate):
    id: int

    class Config:
        from_attributes = True
        orm_mode = True


class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "ru"
    target_lang: str = "en"


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
