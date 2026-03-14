import time
import sys
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_test_module(module_name):
    """Запуск конкретного тестового модуля"""
    print(f'\n{'='*60}')
    print(f'ЗАПУСК {module_name}')
    print(f'{'='*60}')
    module = __import__(f'tests.{module_name}', fromlist=[''])
    return module


if __name__ == '__main__':
    print('=' * 60)
    print('ЗАПУСК ВСЕХ ТЕСТОВ')
    print('=' * 60)
    print('Убедись, что воркер запущен!')
    print('-' * 60)

    # Даем время на проверку
    time.sleep(2)

    # Запускаем тесты по порядку
    math = run_test_module('math')
    math.add.delay(3, 2)
    math.risky_division.delay(6, 2)
    math.risky_division.delay(3, 0)
    math.multiply.delay(3, 2)
    time.sleep(2)
    weather = run_test_module('weather')
    weather.get_weather.delay('Yekaterinburg')
    weather.get_weather.delay('+++++++')
    time.sleep(2)
    network = run_test_module('network')
    network.fetch_website_status.delay('https://google.com')
    network.fetch_website_status.delay('https://etot-sayt-ne-sushestvuet.ru')
    time.sleep(2)
    users = run_test_module('users')
    users.process_user_data.delay('John Doe', 30, 'john@example.com')

    print('\n' + '=' * 60)
    print('ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ!')
    print('=' * 60)
