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
    print("Запускаем воркеры...")

    # Запускаем воркеры в отдельных окнах
    workers = [
        run_worker("math", "math_worker"),
        run_worker("network", "network_worker"),
        run_worker("users", "users_worker"),
        run_worker("weather", "weather_worker"),
        run_worker("math,network,users,weather", "universal_worker"),
    ]

    print(f"Запущено {len(workers)} воркеров")
    print("Смотри в Flower: http://localhost:5555")

    # Ждем завершения
    for w in workers:
        w.wait()
