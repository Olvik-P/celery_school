# run_workers_priority.py
import subprocess
import time
from pathlib import Path


def run_worker(queue, name, concurrency=1, prefetch=4):
    """Запуск воркера с настраиваемыми параметрами приоритета"""
    print(f'Запуск {name}: очередь "{queue}", '
          f'concurrency={concurrency}, prefetch={prefetch}')

    cmd = [
        'celery', '-A', 'celery_app', 'worker',
        '--loglevel=info',
        '-P', 'eventlet',
        '-Q', queue,
        '-n', f'{name}@%h',
        '-c', str(concurrency),
        '--prefetch-multiplier', str(prefetch)
    ]

    # Запускаем в новом окне и сохраняем stdout/stderr в файл
    with open(f'logs/{name}.log', 'w') as log_file:
        return subprocess.Popen(
            cmd,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdout=log_file,
            stderr=subprocess.STDOUT
        )


if __name__ == '__main__':
    # Создаем папку для логов
    Path('logs').mkdir(exist_ok=True)

    print('=' * 60)
    print('ЗАПУСК ВОРКЕРОВ С ПРИОРИТЕТАМИ')
    print('=' * 60)
    print('\nЛегенда приоритетов:')
    print('КРИТИЧЕСКИЕ (users): 3 воркера, prefetch=10')
    print('ВАЖНЫЕ (math): 2 воркера, prefetch=4')
    print('ОБЫЧНЫЕ (network): 1 воркер, prefetch=2')
    print('ФОНОВЫЕ (weather): 1 воркер, prefetch=1')
    print('-' * 60)

    workers = []

    # КРИТИЧЕСКИЕ ЗАДАЧИ
    workers.append(run_worker(
        'users', 'users_priority_worker',
        concurrency=3, prefetch=10
    ))
    time.sleep(1)

    # ВАЖНЫЕ ЗАДАЧИ
    workers.append(run_worker(
        'math', 'math_priority_worker',
        concurrency=2, prefetch=4
    ))
    time.sleep(1)

    # ОБЫЧНЫЕ ЗАДАЧИ
    workers.append(run_worker(
        'network', 'network_priority_worker',
        concurrency=1, prefetch=2
    ))
    time.sleep(1)

    # ФОНОВЫЕ ЗАДАЧИ
    workers.append(run_worker(
        'weather', 'weather_priority_worker',
        concurrency=1, prefetch=1
    ))
    time.sleep(1)

    # Универсальный воркер
    workers.append(run_worker(
        'math,network,users,weather', 'universal_priority_worker',
        concurrency=1, prefetch=2
    ))

    print('\n' + '-' * 60)
    print(f'Запущено {len(workers)} воркеров с приоритетами')
    print('Смотри в Flower: http://localhost:5555')
    print('Смотри в RabbitMQ: http://localhost:15672')
    print('Логи в папке logs/')
    print('=' * 60)

    try:
        # Ждем завершения (по Ctrl+C)
        for w in workers:
            w.wait()
    except KeyboardInterrupt:
        print('\n Останавливаем воркеры...')
        for w in workers:
            w.terminate()
