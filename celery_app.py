"""Основной Celery instance"""
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

import tasks.weather  # noqa: F401
import tasks.users  # noqa: F401
import tasks.network  # noqa: F401
import tasks.math  # noqa: F401

# Автоматически находим все задачи в папке tasks
# app.autodiscover_tasks(['tasks'])
