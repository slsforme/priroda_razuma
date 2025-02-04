from models.models import Document
from .base import BaseRepository


class DocumentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Document)
