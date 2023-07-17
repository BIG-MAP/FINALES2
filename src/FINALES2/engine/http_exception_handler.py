import logging

from fastapi import HTTPException


def http_exception_handler(message, status_code=400):
    logging.error(message)
    raise HTTPException(status_code=400, detail=message)
