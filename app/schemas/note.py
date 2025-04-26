from pydantic import BaseModel

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteOut(NoteCreate):
    id: int

    class Config:
        orm_mode = True