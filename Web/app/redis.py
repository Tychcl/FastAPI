import redis.asyncio as redis
from app.config import settings
from typing import Optional

redis_client = redis.Redis(host=settings.REDIS_HOST,
                           port=settings.REDIS_PORT,
                           db=0, password=settings.REDIS_PASSWORD,
                           #ssl=True, 
                           #ssl_cert_reqs=None
                           )

async def set_reset_token(token: str, email: str, ttl_seconds: int = 300) -> None:
    """
    Сохраняет токен для сброса пароля с временем жизни (TTL).
    По умолчанию 15 минут.
    """
    key = f"reset_token:{token}"
    await redis_client.setex(key, ttl_seconds, email)

async def get_email_by_reset_token(token: str) -> Optional[str]:
    """Получает email по токену сброса. Возвращает None, если токен не найден или истёк."""
    key = f"reset_token:{token}"
    return await redis_client.get(key)

async def delete_reset_token(token: str) -> None:
    """Удаляет токен сброса (используется после успешной смены пароля)."""
    key = f"reset_token:{token}"
    await redis_client.delete(key)

async def check_redis_connection() -> bool:
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False