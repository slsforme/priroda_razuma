from typing import Optional
from pydantic import BaseModel, constr, validator
from datetime import datetime
from urllib.parse import quote

from models.models import SubDirectories
class DocumentBase(BaseModel):
    name: str
    patient_id: int
    subdirectory_type: SubDirectories
    author_id: Optional[int] = None


class DocumentCreate(DocumentBase):
    data: bytes


class DocumentUpdate(DocumentBase):
    name: Optional[str] = None
    patient_id: Optional[int] = None
    subdirectory_type: Optional[SubDirectories] = None
    author_id: Optional[int] = None
    data: Optional[bytes] = None

    @validator('name')
    def decode_name(cls, name: str) -> bytes:
        return quote(name)


class DocumentInDB(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
