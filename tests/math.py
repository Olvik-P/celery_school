from tasks.math import risky_division, add, multiply
import time


def test_add(x, y):
    """Тест 1: Сложение"""
    print("\n" + "="*50)
    print("1. СЛОЖЕНИЕ")
    print("="*50)
    res = add.delay(x, y)
    print(f"ID задачи: {res.id}")
    print(f"Статус (сразу): {res.status}")


def test_multiply(x, y):
    """Тест 2: Умножение"""
    print("\n" + "="*50)
    print("2. УМНОЖЕНИЕ")
    print("="*50)
    res = multiply.delay(x, y)
    print(f"ID задачи: {res.id}")
    print(f"Статус (сразу): {res.status}")


def test_successful_division():
    """Тест 3: Успешное деление"""
    print("\n" + "="*50)
    print("1. УСПЕШНОЕ ДЕЛЕНИЕ")
    print("="*50)

    res1 = risky_division.delay(10, 2)
    print(f"ID задачи: {res1.id}")
    print(f"Статус (сразу): {res1.status}")

    time.sleep(3)  # Ждем выполнения

    print(f"Готова? {res1.ready()}")
    print(f"Результат: {res1.get()}")
    print(f"Статус: {res1.status}")


def test_division_by_zero():
    """Тест 4: Деление на ноль (с повторными попытками)"""
    print("\n" + "="*50)
    print("2. ДЕЛЕНИЕ НА НОЛЬ (3 попытки)")
    print("="*50)

    res2 = risky_division.delay(10, 0)
    print(f"ID задачи: {res2.id}")

    # Следим за статусом
    for i in range(10):
        time.sleep(2)
        print(f"Проверка {i+1}: статус = {res2.status}")
        if res2.ready():
            break

    print(f"\nИтоговый результат: {res2.get()}")
    print(f"Финальный статус: {res2.status}")


if __name__ == "__main__":
    test_add(5, 3)
    test_multiply(4, 7)
    test_successful_division()
    test_division_by_zero()
