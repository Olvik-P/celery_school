import requests
import time

from celery_app import app


@app.task(bind=True, max_retries=1, default_retry_delay=10)
def fetch_website_status(self, url):
    """
    Проверки доступности сайта
    """
    print(f'Проверяем сайт: {url}')

    try:

        start = time.time()
        response = requests.get(url, timeout=5, allow_redirects=True)
        duration = time.time() - start

        result = {
            'url': url,
            'status_code': response.status_code,
            'duration': round(duration, 2),
            'success': response.status_code < 400,
            'content_length': len(response.text)
        }

        print(f'📊 Результат: {result}')
        return result

    except requests.exceptions.ConnectionError:
        error_msg = f'❌ Не удалось подключиться к {url}'
        print(error_msg)

        if self.request.retries < self.max_retries:
            print(f'⏳ Повтор через {self.default_retry_delay} сек...')
            # Повторяем задачу
            raise self.retry(exc=error_msg, countdown=self.default_retry_delay)
        else:
            print('💥 Исчерпаны все попытки!')
            # Больше не пытаемся, просто сообщаем об ошибке
            return {'error': str(error_msg), 'status': 'failed'}


if __name__ == '__main__':
    fetch_website_status.delay('https://www.google.com')
    fetch_website_status.delay('https:// velosipedov.her')
