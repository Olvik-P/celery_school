"""Тестирование приоритетов выполнения"""
import time
from tasks.math import add
from tasks.users import process_user_data
from tasks.network import fetch_website_status
from tasks.weather import get_weather

print("=" * 60)
print("🎯 ТЕСТИРОВАНИЕ ПРИОРИТЕТОВ")
print("=" * 60)

# Отправляем задачи с разными приоритетами
print("\n📤 Отправка задач с приоритетами...")
time.sleep(3)
# 1. Критические задачи (users) - высокий приоритет в очереди
print(f"\n🔴 Отправляем 10 КРИТИЧЕСКИХ задач (users):")
for i in range(10):
    process_user_data.apply_async(
        args=(f"User{i}", 20+i, f"user{i}@mail.com"),
        priority=9  # максимальный приоритет внутри очереди
    )
    print(f"   ✓ User{i} отправлен (priority=9)")
time.sleep(3)
# 2. Важные задачи (math) - средний приоритет
print(f"\n🟡 Отправляем 10 ВАЖНЫХ задач (math):")
for i in range(10):
    add.apply_async(args=(i, i+1), priority=5)  # средний приоритет
    print(f"   ✓ add({i},{i+1}) отправлен (priority=5)")
time.sleep(3)
# 3. Обычные задачи (network) - низкий приоритет
print(f"\n🟢 Отправляем 5 ОБЫЧНЫХ задач (network):")
for i in range(5):
    fetch_website_status.apply_async(
        args=("https://google.com",),
        priority=2  # низкий приоритет
    )
    print(f"   ✓ network задача {i} отправлена (priority=2)")
time.sleep(3)
# 4. Фоновые задачи (weather) - самый низкий приоритет
print(f"\n🔵 Отправляем 5 ФОНОВЫХ задач (weather):")
for i in range(5):
    get_weather.apply_async(
        args=("Moscow",),
        priority=1  # самый низкий приоритет
    )
    print(f"   ✓ weather задача {i} отправлена (priority=1)")

print("\n" + "-" * 60)
print("✅ Все задачи отправлены!")
print("👀 Смотри в Flower, как users_worker обрабатывает быстрее всех!")
print("=" * 60)
