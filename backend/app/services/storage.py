import uuid
from pathlib import Path

from app.core.config import settings


class LocalStorageService:
    def __init__(self, base_dir: str = settings.UPLOAD_DIR) -> None:
        self.base_path = Path(base_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_pdf(
        self,
        organization_id: uuid.UUID,
        document_id: uuid.UUID,
        content: bytes,
    ) -> str:
        org_dir = self.base_path / str(organization_id)
        org_dir.mkdir(parents=True, exist_ok=True)

        file_path = org_dir / f"{document_id}.pdf"
        file_path.write_bytes(content)

        # Store POSIX-style relative paths so DB records stay portable across Windows and Linux
        return file_path.as_posix()

    def delete_file(self, storage_path: str) -> None:
        file_path = Path(storage_path)
        if file_path.exists() and file_path.is_file():
            file_path.unlink()


storage_service = LocalStorageService()