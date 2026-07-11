from .config import settings, ssl_options
from celery import Celery
import smtplib

celery_app = Celery(
    "celery_worker",  # Имя приложения Celery
    broker=settings.REDIS_URL,  # URL брокера задач (Redis)
    backend=settings.REDIS_URL  # URL для хранения результатов выполнения задач
)

celery_app.conf.update(
    #broker_use_ssl=ssl_options,
    #redis_backend_use_ssl=ssl_options,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    enable_utc=True,  # Убедитесь, что UTC включен
    timezone='Europe/Moscow',  # Устанавливаем московское время
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

@celery_app.task(
    name='send_verify_email_code',
    bind=True,
    max_retries=3,
    default_retry_delay=5
)
def send_verify_email(self, user_email: str, code: int) -> bool:
    import logging
    logging.info(f"Sending email to {user_email} with code {code}")
    try:
        send_msg(user_email, str(code))
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False
    
def send_msg(email: str, msg: str):
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.starttls()
    smtpObj.login(settings.SMTP_MAIL,settings.SMTP_MAIL_PWD)
    smtpObj.sendmail(settings.SMTP_MAIL, email, msg)
    smtpObj.quit()
#broker_use_ssl: Указывает, следует ли использовать SSL для соединения с брокером сообщений (в данном случае Redis). Это повышает безопасность передачи данных или, как в нашем случае, отключает проверку.
#redis_backend_use_ssl: Аналогично предыдущему, эта настройка включает SSL для соединения с бэкендом результатов, что также улучшает безопасность.
#task_serializer: Определяет формат сериализации задач. В данном случае используется JSON, что позволяет легко передавать данные между процессами.
#result_serializer: Указывает формат сериализации результатов выполнения задач. Здесь также используется JSON, что обеспечивает совместимость с сериализацией задач.
#accept_content: Список типов контента, которые Celery будет принимать. Указание ['json'] означает, что Celery будет обрабатывать только сообщения в формате JSON.
#enable_utc: Включает использование времени по всемирному координированному времени (UTC). Это важно для синхронизации задач в распределенной системе.
#timezone: Устанавливает временную зону для задач. В нашем случае это "Europe/Moscow", что позволяет правильно обрабатывать временные метки в московском времени.
#broker_connection_retry_on_startup: Опция, которая указывает, следует ли повторно пытаться подключиться к брокеру сообщений при запуске приложения. Это полезно для обеспечения надежности.
#task_acks_late: Указывает, что задачи должны подтверждаться после их завершения. Это предотвращает потерю задач в случае сбоя рабочего процесса до завершения задачи.
#task_reject_on_worker_lost: Если рабочий процесс теряется, задачи не будут автоматически повторно назначены другим рабочим процессам. Это помогает избежать потери данных и дублирования работы.