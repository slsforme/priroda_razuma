from typing import Optional
from pydantic import BaseModel, constr


class PatientBase(BaseModel):
    fio: constr(min_length=10, max_length=255)
    age: int


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    name: Optional[constr(min_length=10, max_length=255)]
    age: Optional[int]


class PatientInDB(PatientBase):
    id: int

    class Config:
        from_attributes = True
