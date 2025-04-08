from typing import Optional
from pydantic import BaseModel, constr

from datetime import datetime


class PatientBase(BaseModel):
    fio: constr(min_length=10, max_length=255)
    age: int


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    fio: Optional[constr(min_length=10, max_length=255)] = None
    age: Optional[int] = None


class PatientInDB(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

