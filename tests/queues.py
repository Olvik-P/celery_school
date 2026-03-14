"""Тестирование маршрутизации по очередям"""
import time
from tasks.math import add, multiply, risky_division
from tasks.network import fetch_website_status
from tasks.weather import get_weather
from tasks.users import process_user_data

print("=" * 60)
print("🚀 ТЕСТИРОВАНИЕ ОЧЕРЕДЕЙ")
print("=" * 60)
time.sleep(3)
# Математика - пойдет в очередь 'math'
print("\n📐 Математические задачи -> очередь 'math'")
add.delay(5, 3)
multiply.delay(4, 7)
risky_division.delay(10, 0)
time.sleep(3)
# Сеть - пойдет в очередь 'network'
print("\n🌐 Сетевые задачи -> очередь 'network'")
fetch_website_status.delay("https://google.com")
fetch_website_status.delay("https://velospedov_net_v_cnegu.ky")
time.sleep(3)
# Погода - пойдет в очередь 'weather'
print("\n☁️ Погодные задачи -> очередь 'weather'")
get_weather.delay("Moscow")
get_weather.delay("Yekaterinburg")
time.sleep(3)
# Пользователи - пойдет в очередь 'users'
print("\n👤 Задачи пользователей -> очередь 'users'")
process_user_data.delay("Alice", 25, "alice@example.com")
process_user_data.delay("Bob", 30, "bob@example.com")

print("\nОтправляем 100 задач в очередь 'math'")
for i in range(100):
    add.delay(i, i+1)
    print(f"  Задача {i+1} отправлена")

print("\n" + "=" * 60)
print("✅ Все задачи отправлены по очередям!")
print("👀 Смотри в Flower: http://localhost:5555")
print("👀 Смотри в RabbitMQ: http://localhost:15672")
print("=" * 60)
