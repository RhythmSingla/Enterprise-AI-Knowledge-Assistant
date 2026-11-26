from dataclasses import dataclass

import pymupdf


class PDFValidationError(Exception):
    """Raised when an uploaded file fails PDF security or content checks."""


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class ExtractedDocument:
    page_count: int
    pages: list[ExtractedPage]

    @property
    def total_characters(self) -> int:
        return sum(len(page.text) for page in self.pages)


def extract_text_from_pdf(file_bytes: bytes) -> ExtractedDocument:
    if not file_bytes:
        raise PDFValidationError("Uploaded file is empty.")

    # Verify the binary PDF file signature (magic bytes), not just the .pdf extension
    if not file_bytes.startswith(b"%PDF-"):
        raise PDFValidationError(
            "Invalid file format. Only genuine PDF documents are accepted."
        )

    try:
        pdf_doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFValidationError("Corrupted or unreadable PDF file.") from exc

    with pdf_doc:
        if pdf_doc.is_encrypted:
            raise PDFValidationError(
                "Password-protected PDFs are not supported. Please upload an unlocked PDF."
            )

        page_count = len(pdf_doc)
        if page_count == 0:
            raise PDFValidationError("PDF contains zero pages.")

        extracted_pages: list[ExtractedPage] = []
        for index, page in enumerate(pdf_doc, start=1):
            raw_text = page.get_text("text")
            cleaned_text = "\n".join(
                line.strip()
                for line in raw_text.splitlines()
                if line.strip()
            )
            if cleaned_text:
                extracted_pages.append(
                    ExtractedPage(page_number=index, text=cleaned_text)
                )

    if not extracted_pages:
        raise PDFValidationError(
            "No selectable text found in PDF. Scanned image-only PDFs require OCR."
        )

    return ExtractedDocument(
        page_count=page_count,
        pages=extracted_pages,
    )