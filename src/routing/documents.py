from .base import create_base_router
from schemas.documents import *
from depends import get_document_service

router = create_base_router(
    prefix="/documents",
    tags=["documents"],
    service_dependency=get_document_service,
    create_schema=DocumentCreate,
    read_schema=DocumentInDB,
    update_schema=DocumentUpdate,
    object_name="документ",
    has_file_field=True,  
    gender='m',
    file_field_name="data"  
)