"""Диагностика проблем с autodiscover"""
import sys
from pathlib import Path

print('=' * 50)
print('ДИАГНОСТИКА ПРОЕКТА')
print('=' * 50)

# 1. Текущая директория
print(f'\n1. Текущая директория: {Path.cwd()}')

# 2. Содержимое текущей директории
print('\n2. Содержимое текущей директории:')
for item in Path.cwd().iterdir():
    prefix = '+' if item.is_dir() else '-'
    print(f'  {prefix} {item.name}')

# 3. Python path
print('\n3. Python path (sys.path):')
for i, path in enumerate(sys.path):
    print(f'  {i}: {path}')

# 4. Проверка импорта пакета tasks
print('\n4. Проверка импорта пакета "tasks":')
try:
    import tasks
    print('tasks найден!')
    print(f'     Путь: {tasks.__file__}')
    print(f'     Содержимое: {dir(tasks)}')
except ImportError as e:
    print(f'tasks НЕ найден: {e}')

# 5. Проверка импорта модулей внутри tasks
print('\n5. Проверка импорта модулей:')
modules_to_check = ['math', 'network', 'weather', 'users']
for module in modules_to_check:
    try:
        __import__(f'tasks.{module}')
        print(f'tasks.{module} найден!')
    except ImportError as e:
        print(f'tasks.{module} НЕ найден: {e}')

# 6. Проверка наличия __init__.py
print('\n6. Проверка __init__.py:')
tasks_init = Path.cwd() / 'tasks' / '__init__.py'
if tasks_init.exists():
    print('tasks/__init__.py существует')
    print(f'     Содержимое: {tasks_init.read_text() or 'пустой'}')
else:
    print('tasks/__init__.py НЕ существует!')

# 7. Проверка импорта app из celery_app
print('\n7. Проверка celery_app:')
try:
    from celery_app import app
    print('celery_app.app импортирован')

    # Попробуем принудительно выполнить autodiscover
    print('\n8. Пробуем autodiscover вручную:')
    try:
        app.autodiscover_tasks(['tasks'])
        print('autodiscover выполнен без ошибок')

        print('\n9. Найденные задачи:')
        tasks_found = []
        for task_name in sorted(app.tasks.keys()):
            if not task_name.startswith('celery.'):
                tasks_found.append(task_name)
                print(f'  • {task_name}')

        if not tasks_found:
            print('Задачи не найдены! Проверь декораторы @app.task')

    except Exception as e:
        print(f'autodiscover ошибка: {e}')

except ImportError as e:
    print(f'celery_app НЕ найден: {e}')

print('\n' + '=' * 50)
print('Диагностика завершена')
print('=' * 50)
