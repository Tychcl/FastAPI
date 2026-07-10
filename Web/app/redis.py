import redis
from app import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT, 
    password=settings.REDIS_PASSWORD,
    ssl=True,  # Включаем SSL
    ssl_cert_reqs=None  # Отключаем проверку сертификата, если нужно
)

try:
    response = r.ping()
    if response:
        print("Подключение к Redis успешно!")
    else:
        print("Не удалось подключиться к Redis.")
except Exception as e:
    print(f"Произошла ошибка: {e}")