from os.path import exists as path_exists

from pymupdf import open as fitz_open

from app.core.logger import logger_info


def extract_file_pdf(file_path: str) -> str:
    if not path_exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    logger_info("Extractor", f"Extracting: {file_path}")

    doc = fitz_open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n\n"  # type: ignore
    doc.close()
    return full_text  # type: ignore
