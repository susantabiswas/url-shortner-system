from fastapi import HTTPException


def bad_request_exception(msg: str):
    raise HTTPException(status_code=400, detail=msg)


def not_found_exception(url: str):
    raise HTTPException(status_code=404, detail=f"{url} not found")
