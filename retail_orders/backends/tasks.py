from celery import shared_task
import time


@shared_task
def send_email(to_email, subject, message):
    time.sleep(5)
    print("Отправлено {to_email}: {subject} - {message}")
    return f"{to_email}"

@shared_task
def do_import(data):

    print(f"Импортировано: {data}")
    return f'Импорт произведен'