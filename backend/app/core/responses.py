from fastapi.responses import JSONResponse


def ok(data=None, message="success"):
    return {"code": 0, "message": message, "data": data}


def error(status_code: int, message: str):
    return JSONResponse(status_code=status_code, content={"code": status_code, "message": message, "data": None})
