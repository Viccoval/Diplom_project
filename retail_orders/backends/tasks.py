from celery import shared_task
from easy_thumbnails.files import get_thumbnailer
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


@shared_task
def generate_thumbnails(image_field, aliases):
    """
    Задача Celery для загрузки изображения.
    """
    thumbnailer = get_thumbnailer(image_field)
    for alias in aliases:
        thumbnail = thumbnailer.get_thumbnail(alias)
        print(f"Добавлена картинка: {thumbnail.url}")
