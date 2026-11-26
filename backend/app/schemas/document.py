import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    uploaded_by: uuid.UUID | None
    filename: str
    file_size_bytes: int
    page_count: int | None
    status: str
    error_message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(DocumentResponse):
    extracted_characters: int
    message: str