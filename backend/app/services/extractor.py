from os.path import exists as path_exists
from os import remove as os_remove
from marker.converters.pdf import PdfConverter  # type: ignore
from marker.models import create_model_dict  # type: ignore
from marker.output import text_from_rendered  # type: ignore
from fitz import open as fitz_open  # type: ignore
from gc import collect as gc_collect
from torch.cuda import (
    is_available as cuda_is_available,
    empty_cache as cuda_empty_cache,
)

from app.core.logger import logger_info

MAX_PAGES_PER_CHUNK = 1


def is_scanned_pdf(file_path: str) -> bool:
    doc = fitz_open(file_path)
    text_length = 0

    for page_num in range(min(3, len(doc))):
        page = doc[page_num]  # type: ignore
        text_length += len(page.get_text())  # type: ignore

    doc.close()

    return text_length < 50


def extract_file_pdf(file_path: str) -> str:
    if not path_exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    logger_info("Extractor", f"Extracting: {file_path}")

    if is_scanned_pdf(file_path):
        converter = PdfConverter(artifact_dict=create_model_dict())  # type: ignore

        full_extracted_text = ""

        try:
            pdf_document = fitz_open(file_path)
            total_pages = len(pdf_document)
        except Exception as e:
            raise ValueError(f"Cannot open file {file_path}: {str(e)}")

        logger_info("Extractor", f"Total pages - {file_path}: {total_pages}")

        if total_pages <= MAX_PAGES_PER_CHUNK:
            rendered = converter(file_path)  # type: ignore
            text, _, _ = text_from_rendered(rendered)  # type: ignore
            full_extracted_text = text
        else:
            for start_page in range(0, total_pages, MAX_PAGES_PER_CHUNK):
                end_page = min(start_page + MAX_PAGES_PER_CHUNK, total_pages) - 1

                temp_pdf_path = f"{file_path}_temp_{start_page}_{end_page}.pdf"

                try:
                    temp_pdf = fitz_open()
                    temp_pdf.insert_pdf(pdf_document, from_page=start_page, to_page=end_page)  # type: ignore
                    temp_pdf.save(temp_pdf_path)  # type: ignore
                    temp_pdf.close()

                    rendered = converter(temp_pdf_path)  # type: ignore
                    chunk_text, _, _ = text_from_rendered(rendered)  # type: ignore

                    full_extracted_text += chunk_text + "\n\n"
                except Exception as e:
                    raise e
                finally:
                    if path_exists(temp_pdf_path):
                        os_remove(temp_pdf_path)

                    gc_collect()
                    if cuda_is_available():
                        cuda_empty_cache()

        pdf_document.close()

        return full_extracted_text
    else:
        doc = fitz_open(file_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n\n"  # type: ignore
        doc.close()
        return full_text  # type: ignore
