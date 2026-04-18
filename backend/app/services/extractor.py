from os.path import exists as path_exists
from marker.converters.pdf import PdfConverter  # type: ignore
from marker.models import create_model_dict  # type: ignore
from marker.output import text_from_rendered  # type: ignore

from app.core.logger import logger_info


def extract_file_with_marker(file_path: str) -> str:
    if not path_exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    logger_info("Extractor", f"Extracting: {file_path}")

    converter = PdfConverter(artifact_dict=create_model_dict())  # type: ignore

    rendered = converter(file_path)  # type: ignore

    full_text, _, _ = text_from_rendered(rendered)  # type: ignore

    return full_text
