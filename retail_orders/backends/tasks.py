from celery import shared_task
import time


@shared_task
def send_email(to_email, subject, message):
    """
    Задача Celery для отправки email.
    """
    time.sleep(5)
    print("Отправлено {to_email}: {subject} - {message}")
    return f"{to_email}"

@shared_task
def do_import(data):
    """
    Задача Celery для импорта данных. Принимает данные в виде списка или словаря.
    """
    print(f"Импортировано: {data}")
    return f'Импорт произведен'