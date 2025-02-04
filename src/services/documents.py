from repositories.documents import DocumentRepository
from .base import BaseService


class DocumentService(BaseService):
    def __init__(self, repository: DocumentRepository):
        super().__init__(repository)
