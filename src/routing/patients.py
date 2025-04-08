from .base import create_base_router
from schemas.patients import *
from depends import get_patient_service

router = create_base_router(
    prefix="/patients",
    tags=["patients"],
    service_dependency=get_patient_service,
    create_schema=PatientCreate,
    read_schema=PatientInDB,
    update_schema=PatientUpdate,
    object_name="пациент",
    gender='m',
)