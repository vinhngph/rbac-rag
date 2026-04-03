from logging import getLogger

logger = getLogger("uvicorn.error")


def logger_info(type: str, msg: str):
    logger.info(f"[-] {type}: {msg}")


def logger_error(type: str, msg: str):
    logger.error(f"[-] {type}: {msg}")


def logger_warning(type: str, msg: str):
    logger.warning(f"[-] {type}: {msg}")
