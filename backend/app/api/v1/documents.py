import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.pdf_extractor import PDFValidationError, extract_text_from_pdf
from app.services.storage import storage_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Bound memory usage by reading at most (MAX_UPLOAD_SIZE_MB + 1 byte)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    file_bytes = await file.read(max_bytes + 1)
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    # 2. Validate binary PDF signature, check encryption, and extract text
    try:
        extracted = extract_text_from_pdf(file_bytes)
    except PDFValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # 3. Strip any directory prefixes from client-supplied filename
    clean_filename = (
        Path(file.filename or "untitled.pdf").name.strip() or "untitled.pdf"
    )[:255]

    document_id = uuid.uuid4()
    storage_path = storage_service.save_pdf(
        organization_id=current_user.organization_id,
        document_id=document_id,
        content=file_bytes,
    )

    # 4. Commit metadata to PostgreSQL; roll back saved file if DB fails
    try:
        document = Document(
            id=document_id,
            organization_id=current_user.organization_id,
            uploaded_by=current_user.id,
            filename=clean_filename,
            storage_path=storage_path,
            file_size_bytes=len(file_bytes),
            page_count=extracted.page_count,
            status="EXTRACTED",
        )
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        storage_service.delete_file(storage_path)
        raise

    base_data = DocumentResponse.model_validate(document).model_dump()
    return DocumentUploadResponse(
        **base_data,
        extracted_characters=extracted.total_characters,
        message=f"Successfully extracted {extracted.total_characters} characters across {extracted.page_count} pages.",
    )


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Document)
        .where(Document.organization_id == current_user.organization_id)
        .order_by(Document.created_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.organization_id == current_user.organization_id,
        )
    )
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.organization_id == current_user.organization_id,
        )
    )
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    storage_path = document.storage_path
    db.delete(document)
    db.commit()

    # Delete the physical file only after the database deletion commits
    storage_service.delete_file(storage_path)
    return Response(status_code=status.HTTP_204_NO_CONTENT)