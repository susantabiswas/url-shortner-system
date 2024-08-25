from fastapi import HTTPException


def bad_request_exception(msg: str):
    raise HTTPException(status_code=400, detail=msg)


def not_found_exception(id: str):
    raise HTTPException(status_code=404, detail=f"Id: {id} not found")
