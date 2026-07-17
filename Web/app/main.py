from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router 
from app.web.router import web_router
from fastapi.responses import JSONResponse
from app.config import logger, settings
from .api.v1.middlewares import user_middleware
from .api.v1.services import JWTService, CookieService, PasswordHasherService
from app.redis import redis_client
from sqlalchemy import select
from contextlib import asynccontextmanager
from app.api.models import Base
from app.api.models import UserRoleBase
from app.database import context, AsyncSessionLocal
from fastapi import FastAPI
from .redis import redis_client 
from starlette.middleware.sessions import SessionMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with context.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        stmt = select(UserRoleBase)
        result = await session.execute(stmt)
        if result.scalars().first() is None:
            session.add_all([
                UserRoleBase.S_ADMIN(),
                UserRoleBase.ADMIN(),
                UserRoleBase.USER(),
            ])
            await session.commit()
    yield
    await redis_client.close()

app = FastAPI(lifespan=lifespan)

app.state.jwt_service = JWTService()
app.state.cookie_service = CookieService()
app.state.hash_service = PasswordHasherService()
app.state.redis = redis_client

app.middleware("http")(user_middleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,  # Обязательный параметр для подписи cookie
    session_cookie="session",     # Имя cookie
    max_age=None,            # Срок жизни сессии
    same_site="strict",                    # Защита от CSRF
    https_only=False                      # Только для HTTPS
)

app.include_router(api_router)
app.include_router(web_router)
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "path": request.url.path}
    )
    
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc), "path": request.url.path}
    )
    
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred"}
    )