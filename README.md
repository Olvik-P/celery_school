# Пример работы с Celery

Представь, что твоя программа — это ресторан. Клиент (пользователь) делает 
заказ (запрос). Готовка сложного блюда (отправка email, обработка видео) 
занимает время. Если повар будет стоять у плиты 10 минут, пока готовится это 
блюдо, он не сможет принять следующий заказ. Это плохо.

- Celery — это помощник повара. Он забирает сложные заказы и готовит их на 
"кухне" (фоновые процессы), не отвлекая основного повара.

- RabbitMQ — это доска объявлений на кухне, куда вешаются заказы. Celery смотрит 
а доску и берет себе задания.

- Flower — это веб-камера, установленная на кухне, через которую менеджер (ты) 
может в реальном времени следить, сколько заказов готово, а сколько еще в процессе.

Наш стек:

- Брокер сообщений (доска объявлений): RabbitMQ (запустим в Docker).
- Обработчик задач (помощник): Celery (Python-библиотека).
- Хранилище результатов (итог готовки): Redis или база данных (RPC не подходит 
для Windows, будем использовать Redis в Docker).
- Мониторинг (камера): Flower (Python-библиотека).

## Установи окружение.

```
python -m venv venv
.\venv\Scripts\activate
```

## Установи необходимые пакеты. 
Создай файл requirements.txt:

```
celery==5.4.0
eventlet==0.36.1  # Обязательно для Windows!
redis==5.0.8      # Для хранения результатов
flower==2.0.1     # Для мониторинга
```

Запусти установку:

```
bash
pip install -r requirements.txt
```

## Запускаем инфраструктуру (Docker Compose).
Создай файл docker-compose.yml в корне проекта. Это золотой стандарт 
(best practice), чтобы не захламлять Windows-машину серверами.

```
yaml
services:
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: rabbitmq_school
    ports:
      - "5672:5672"      # Порт для подключения (AMQP)
      - "15672:15672"    # Порт для веб-интерфейса (Management UI)
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq

  redis:
    image: redis:7-alpine
    container_name: redis_school
    ports:
      - "6379:6379"      # Порт для подключения
    volumes:
      - redis_data:/data

volumes:
  rabbitmq_data:
  redis_data:
```

## Запусти контейнеры:

```
bash
docker-compose up -d
```

Теперь у тебя есть работающий RabbitMQ (доступен по адресу localhost:15672, 
логин/пароль guest/guest) и Redis.

- Что такое Celery? Это распределенная очередь задач. Ты говоришь программе: 
"сделай это", она кладет задание в очередь и сразу отвечает 
"ок, принято, иди дальше". Само задание выполняется позже в фоне.

- Роль RabbitMQ: Он хранит эти задания. Если Celery-работник (worker) занят или 
выключен, задание не пропадет, а будет ждать в RabbitMQ.

Задачи пишим в tasks/.

В celery_app.py cоздаем экземпляр приложения Celery
1. Имя модуля ('celery_school'')
2. Адрес брокера (RabbitMQ) - порт 5672
3. Адрес хранилища результатов (Redis) - порт 6379

```
from celery import Celery


app = Celery(
    'celery_school',  # Имя проекта
    broker='amqp://guest:guest@localhost:5672//',
    backend='redis://localhost:6379/0'
)

```
В app.conf.update описываем настройки приложения.

```
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Yekaterinburg',
    enable_utc=True,
    broker_connection_retry_on_startup=True,

    # Маршрутизация по очередям
    task_routes={
        'tasks.math.*': {'queue': 'math'},
        'tasks.network.*': {'queue': 'network'},
        'tasks.users.*': {'queue': 'users'},
        'tasks.weather.*': {'queue': 'weather'},
    }
)
```
В task_routes описываем маршрутизацию по очередям, которые будут использоваться в приложении.
Кроме этого старайся:
- Старайся давать осмысленные имена функциям, так как они будут отображаться в логах.

- Хранить конфигурацию отдельно: Жестко прописанный broker в коде — это ок для учебного проекта, но в реальности используй переменные окружения или отдельные конфигурационные файлы.

- Не злоупотреблять .get(): Этот метод ждет результата и убивает всю асинхронность. Обычно его используют только в тестах или в специальных местах.

- Всегда обрабатывай исключения внутри задач. Используй retry для временных сбоев (например, сеть недоступна). Это повышает отказоустойчивость.

- bind=True — мощный инструмент. Дает доступ к контексту задачи (ID, попытка выполнения и т.д.).

- Передавать данных: Celery сериализует аргументы в JSON (по умолчанию). Передавай простые типы: числа, строки, списки, словари. Не передавай объекты классов (например, сессию SQLAlchemy) — это приведет к ошибкам.

Для запуска приложения в Windows можно использовать команду для запуска воркеров по задачам:

```
celery -A tasks worker --loglevel=info -P eventlet -Q math  # Запуск воркера для очереди math
# И запускаем другие воркеры для очередей аналогичным образом
```

Но можно автоматировать запуск воркеров и создать файл run_workers.py:

```
import subprocess
import sys
from pathlib import Path

# Добавляем путь
sys.path.insert(0, str(Path(__file__).parent))

def run_worker(queue, name):
    """Запуск воркера для конкретной очереди"""
    cmd = [
        "celery", "-A", "celery_app", "worker",
        "--loglevel=info",
        "-P", "eventlet",
        "-Q", queue,
        "-n", f"{name}@%h"
    ]
    return subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)

if __name__ == "__main__":
    print("🚀 Запускаем воркеры...")
    
    # Запускаем воркеры в отдельных окнах
    workers = [
        run_worker("math", "math_worker"),
        run_worker("network", "network_worker"),
        run_worker("users", "users_worker"),
        run_worker("weather", "weather_worker"),
        run_worker("math,network,users,weather", "universal_worker"),
    ]
    
    print(f"✅ Запущено {len(workers)} воркеров")
    print("👀 Смотри в Flower: http://localhost:5555")
    
    # Ждем завершения
    for w in workers:
        w.wait()
```
Запуск одной командой:

```bash
python run_workers.py
```
### Но для продакшена так не делают, это для разработки.

## Запускаем Flower

```
celery -A celery_app flower --port=5555 --broker=amqp://guest:guest@localhost:5672//
```
Перейди в браузер и открой http://localhost:5555

Для проверки работы приложения в терминале выполни:
```
$ python
>>> from tasks.math import add  # импортируем задачу
>>> res = add.delay(1, 2)  # запускаем задачу
>>> print(f"ID задачи: {res.id}")  # получаем ID задачи
ID задачи: 958f185c-5e2d-49ef-97db-794f24a31996
>>> print(f"Готова? {res.ready()}")  #
Готова? True
>>> print(f"Результат: {res.get()}")  # получаем результат
Результат: 3
>>>
```
А в дашборде Flower можно увидеть статус задач по очередям и результаты выполнения.
В строке воркера math_worker@iTR будет видна 1 задача.

![alt text](media/image.png)

## Зачем нужен Flower?
Представь, что у тебя 10 воркеров и тысячи задач в день. Как понять:

- Кто чем занят?
- Какие задачи упали?
- Сколько задач в очереди?
- Не завис ли какой-то воркер?

Flower - это веб-интерфейс (как личный кабинет), который показывает ВСЁ в реальном времени!

## Зачем нужны разные очереди?
В реальном проекте задачи бывают разные:

- Срочные - отправить пароль по email (нужно быстро)
- Несрочные - сгенерировать годовой отчет (можно подождать)
- Фоновые - удалить старые файлы (можно ночью)

Если всё кидать в одну очередь, срочные задачи будут ждать, пока выполнятся долгие. Решение - разные очереди для разных типов задач!

## Протестим все наши задачи сразу:

```
python -m tests.all_test_run
```

## Расстановка приоритетов:
task_routes не определяет приоритеты выполнения задач — она определяет только то, в какую очередь попадет задача. Это называется маршрутизацией (routing), а не приоритезацией.

В run_workers.py мы можем добавить параметры, которые влияют на приоритет/скорость обработки задач!

### Погнали настраивать приоритеты!
Шаг 1: Обновим celery_app.py с поддержкой приоритетов

```
from celery import Celery
from kombu import Queue, Exchange

app = Celery(
    'celery_school',
    broker='amqp://guest:guest@localhost:5672//',
    backend='redis://localhost:6379/0'
)

# Конфигурация с приоритетами
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Yekaterinburg',
    enable_utc=True,
    broker_connection_retry_on_startup=True,

    # Маршрутизация по очередям
    task_routes={
        'tasks.math.*': {'queue': 'math'},
        'tasks.network.*': {'queue': 'network'},
        'tasks.users.*': {'queue': 'users'},
        'tasks.weather.*': {'queue': 'weather'},
    }
)

# === НАСТРОЙКА ПРИОРИТЕТОВ ===
# Объявляем очереди с поддержкой приоритетов (10 уровней)
app.conf.task_queues = (
    Queue('math', Exchange('math'), routing_key='math',
          queue_arguments={'x-max-priority': 10}),
    Queue('network', Exchange('network'), routing_key='network',
          queue_arguments={'x-max-priority': 10}),
    Queue('users', Exchange('users'), routing_key='users',
          queue_arguments={'x-max-priority': 10}),
    Queue('weather', Exchange('weather'), routing_key='weather',
          queue_arguments={'x-max-priority': 10}),
)

# Приоритет по умолчанию (средний)
app.conf.task_default_priority = 5

# Настройки для справедливого распределения
app.conf.worker_prefetch_multiplier = 1  # важно для приоритетов!

import tasks.math
import tasks.network
import tasks.users
import tasks.weather
```

Шаг 2: Создадим run_workers_priority.py с разными приоритетами воркеров

```
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

```
Шаг 3: Запустим run_workers_priority.py

```
python run_workers_priority.py
```
# Проверим, что все работает.

1. запускаем контейнеры:
```
docker-compose up -d
```
2. Открываем термина bash # 1 запускаем воркеры

```
python run_workers_priority.py
```
3. Открываем термина bash # 2 запускаем Flower:

```
celery -A celery_app flower --port=5555 --broker=amqp://guest:guest@localhost:5672//
```
4. Открываем термина bash # 3 где можем в консоли Python запускать задачи:

```
$ python
>>> from tasks.math import add  # импортируем задачу
>>> res = add.delay(1, 2)  # запускаем задачу
>>> print(f"ID задачи: {res.id}")  # получаем ID задачи
ID задачи: 958f185c-5e2d-49ef-97db-794f24a31996
>>> print(f"Готова? {res.ready()}")  #
Готова? True
>>> print(f"Результат: {res.get()}")  # получаем результат
Результат: 3
>>>
```

или запускать тесты, который находятся и tests/:

```
python -m tests.all_test_run
```



