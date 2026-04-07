from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions.app_exception import AppException
from app.core.logger import logger_error


def http_exception_handler(_request: Request, exception: Exception) -> JSONResponse:
    assert isinstance(exception, AppException)

    if exception.status_code >= 500:
        logger_error("System", exception.message)

    return JSONResponse(
        status_code=exception.status_code, content={"detail": exception.message}
    )
