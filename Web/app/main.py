from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router 
from app.web.router import web_router
from .database import lifespan
from fastapi.responses import JSONResponse
from .config import logger
from .api.v1.middlewares import user_middleware
from .api.v1.services import JWTService, CookieService

app = FastAPI(lifespan=lifespan)

from app.api.v1.services import JWTService, CookieService

app.state.jwt_service = JWTService()
app.state.cookie_service = CookieService()

app.middleware("http")(user_middleware)

app.include_router(api_router)
app.include_router(web_router)
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "path": request.url.path}
    )
    
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred"}
    )