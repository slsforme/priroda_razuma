from typing import Optional
from pydantic import BaseModel, constr

class DocumentBase(BaseModel):
    name: constr(min_length=3, max_length=255)
    data: bytes  

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    name: Optional[constr(min_length=3, max_length=255)]  
    data: Optional[bytes]  

class DocumentInDB(DocumentBase):
    id: int

    class Config:
        orm_mode = True