from dataclasses import dataclass

from app.core.config import settings
from app.services.pdf_extractor import ExtractedDocument

DEFAULT_SEPARATORS: tuple[str, ...] = ("\n\n", "\n", ". ", " ", "")
#Defines the priority order for splitting text, ordered from coarsest structural boundary to finest.

@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    page_number: int
    content: str


# takes a block of text and guarantees every returned string is $\le$ chunk_size characters.
def _split_recursive( 
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    separators: tuple[str, ...] = DEFAULT_SEPARATORS,
) -> list[str]:
    
    cleaned = text.strip() #Strips leading/trailing whitespace.
    if not cleaned:
        return []
    if len(cleaned) <= chunk_size:
        return [cleaned]

    sep = "" #least priority separator 
    remaining_separators: tuple[str, ...] = () 

    for idx, candidate in enumerate(separators): # Loops through separators and picks the first one present in cleaned
        if candidate == "" or candidate in cleaned:
            sep = candidate
            remaining_separators = separators[idx + 1 :] #if any paragraph still too long, next recursive call automatically steps down to finer separators ("\n", then ". ", etc.).
            break

    # Base case: single continuous string with no whitespace/punctuation
    if sep == "":
        step = max(1, chunk_size - chunk_overlap)
        windows: list[str] = []
        for start in range(0, len(cleaned), step):
            windows.append(cleaned[start : start + chunk_size].strip())
            if start + chunk_size >= len(cleaned):
                break
        return [w for w in windows if w] #Uses a list comprehension to return the final list, filtering out any empty strings

    pieces = cleaned.split(sep)
    chunks: list[str] = []
    current_parts: list[str] = []
    current_len = 0

    for piece in pieces: # Greedy Merging & Recursive Sub-Splitting:
        # If a single piece exceeds chunk_size, flush current buffer and split deeper
        if len(piece) > chunk_size:
            if current_parts:
                chunks.append(sep.join(current_parts).strip())
                current_parts = []
                current_len = 0
            chunks.extend(
                _split_recursive(
                    piece, chunk_size, chunk_overlap, remaining_separators
                )
            )
            continue

        added_len = len(piece) + (len(sep) if current_parts else 0)
        if current_len + added_len > chunk_size and current_parts:
            chunks.append(sep.join(current_parts).strip())

            # Retain trailing parts within chunk_overlap budget for continuity
            overlap_parts: list[str] = []
            overlap_len = 0
            #Walking backwards to get overlap
            for prev_part in reversed(current_parts): #If keeping that overlap plus the next incoming piece would exceed chunk_size, it clears current_parts ([]) so the new piece starts cleanly without overflowing.
                extra = len(prev_part) + (len(sep) if overlap_parts else 0)
                if overlap_len + extra > chunk_overlap:
                    break
                overlap_parts.insert(0, prev_part)
                overlap_len += extra

            current_parts = overlap_parts
            current_len = overlap_len

            # If overlap + new piece still exceeds chunk_size, start fresh
            if (
                current_parts
                and current_len + len(sep) + len(piece) > chunk_size
            ):
                current_parts = []
                current_len = 0

        current_parts.append(piece)
        current_len += len(piece) + (len(sep) if len(current_parts) > 1 else 0)

    if current_parts:
        chunks.append(sep.join(current_parts).strip())

    return [c for c in chunks if c]


def chunk_document(
    extracted_doc: ExtractedDocument,
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP,
) -> list[TextChunk]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    all_chunks: list[TextChunk] = []
    chunk_counter = 0

    for page in extracted_doc.pages:
        page_chunks = _split_recursive(
            text=page.text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        for content in page_chunks:
            all_chunks.append(
                TextChunk(
                    chunk_index=chunk_counter,
                    page_number=page.page_number,
                    content=content,
                )
            )
            chunk_counter += 1

    return all_chunks