from .config import settings, ssl_options
from celery import Celery
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
def send_verify_email(self, email: str, code: int) -> bool:
    import logging
    logging.info(f"Sending verify email to {email} with code {code}")
    try:
        body = f"Здравствуйте!\n\nКод для подтверждения почты: {code}\n\nКод действителен 10 минут.\n\nЕсли вы не запрашивали подтверждение, проигнорируйте это письмо."
        send_msg(email, body, "Подтверждение почты")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

@celery_app.task(
    name='send_password_forgot_link',
    bind=True,
    max_retries=3,
    default_retry_delay=5
)
def send_verify_email(self, email: str, token: str) -> bool:
    import logging
    logging.info(f"Sending forgot email to {email} with token {token}")
    try:
        reset_link = f"{settings.BASE_URL}/password/change?token={token}"
        body = f"Здравствуйте!\n\nДля восстановления пароля перейдите по ссылке:\n{reset_link}\n\nСсылка действительна 10 минут.\n\nЕсли вы не запрашивали восстановление, проигнорируйте это письмо."
        send_msg(email, body, "Восстановление пароля")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def send_msg(email: str, body: str, subject: str):
    
    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_MAIL
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.starttls()
    smtpObj.login(settings.SMTP_MAIL, settings.SMTP_MAIL_PWD)
    smtpObj.sendmail(settings.SMTP_MAIL, email, msg.as_string())
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