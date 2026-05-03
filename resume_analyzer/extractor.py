"""PDF text extraction utilities."""

import io
import PyPDF2


def extract_text_from_pdf(file_stream) -> str:
    """Extract plain text from a PDF file stream.

    Args:
        file_stream: A file-like object containing PDF data.

    Returns:
        The extracted text as a single string.

    Raises:
        ValueError: If the file cannot be read as a PDF or yields no text.
    """
    try:
        reader = PyPDF2.PdfReader(file_stream)
    except Exception as exc:
        raise ValueError(f"Could not read PDF file: {exc}") from exc

    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    if not pages_text:
        raise ValueError(
            "No text could be extracted from the PDF. "
            "The file may be scanned or image-based."
        )

    return "\n".join(pages_text)
