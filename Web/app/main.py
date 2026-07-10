from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router 
from app.web.router import web_router
from app.database import lifespan
from fastapi.responses import JSONResponse
from app.config import logger
from . import settings, ssl_options
from .api.v1.middlewares import user_middleware
from .api.v1.services import JWTService, CookieService
from celery import Celery

celery_app = Celery(
    "celery_worker",  # Имя приложения Celery
    broker=settings.REDIS_URL,  # URL брокера задач (Redis)
    backend=settings.REDIS_URL  # URL для хранения результатов выполнения задач
)

celery_app.conf.update(
    broker_use_ssl=ssl_options,
    redis_backend_use_ssl=ssl_options,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    enable_utc=True,  # Убедитесь, что UTC включен
    timezone='Europe/Moscow',  # Устанавливаем московское время
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

app = FastAPI(lifespan=lifespan)

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