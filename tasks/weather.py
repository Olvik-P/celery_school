import requests

from celery_app import app


def handle_weather_error(task, city, error_type, error_text):
    """
    Универсальный обработчик ошибок для погоды
    """
    print(f'Ошибка {error_type} для города {city}: {error_text}')

    # Разные стратегии для разных ошибок
    if error_type == 'connection_error':
        max_attempts = task.max_retries - 1  # Меньше попыток
        delay = task.default_retry_delay * 2  # Дольше ждать
    else:  # timeout
        max_attempts = task.max_retries  # Стандартные попытки
        delay = task.default_retry_delay  # Стандартная задержка

    # Проверяем, остались ли попытки
    if task.request.retries < max_attempts:
        print(
            f'Повтор через {
                delay
            } сек... (попытка {
                task.request.retries + 1
            }/{
                max_attempts
            })'
        )
        raise task.retry(exc=error_text, countdown=delay)
    else:
        print(f'Исчерпаны все попытки для {city}!')
        return {
            'city': city,
            'error': f'{error_type}: {error_text}',
            'status': 'failed',
            'attempts': task.request.retries + 1
        }


@app.task(bind=True, max_retries=2, default_retry_delay=5)
def get_weather(self, city):
    """
    Получение погоды в городе
    """
    if not city:
        return {'error': 'Не указан город'}

    print(f'Получаем погоду в городе {city}')

    url = f'https://wttr.in/{city}?format=%t+%c+%h'

    try:

        response = requests.get(url, timeout=5)
        raw_data = response.content.decode().strip()

        # Парсим ответ ' +6°C 🌫 70%'
        parts = raw_data.split()
        temp = parts[0] if len(parts) > 0 else 'N/A'
        condition = parts[1] if len(parts) > 1 else 'N/A'
        humidity = parts[2] if len(parts) > 2 else 'N/A'

        return {
            'city': city,
            'temperature': temp,
            'condition': condition,
            'humidity': humidity,
            'raw': raw_data,
            'success': True
        }

    except requests.exceptions.ConnectionError as exc:
        return handle_weather_error(self, city, 'connection_error', str(exc))
    except requests.exceptions.Timeout as exc:
        return handle_weather_error(self, city, 'timeout', str(exc))


if __name__ == '__main__':
    get_weather.delay('Moscow')
