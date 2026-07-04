from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import HTTPException, status

def unauthorized_RedirectResponse():
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

def unauthorized_JSONResponse():
    return JSONResponse(content={"error": "unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED)