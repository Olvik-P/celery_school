import time

from celery_app import app


@app.task
def process_user_data(name, age, email=None):
    """
    Задача, принимающая сложные данные (словари, именованные аргументы)
    """
    print('👤 Обрабатываем пользователя:')
    print(f'   Имя: {name}')
    print(f'   Возраст: {age}')
    print(f'   Email: {email if email else 'не указан'}')

    # Имитация обработки
    time.sleep(3)

    # Возвращаем словарь с результатом
    return {
        'name': name,
        'age': age,
        'email': email,
        'status': 'processed',
        'timestamp': time.time()
    }


if __name__ == '__main__':
    process_user_data.delay('John Doe', 30, 'john@example.com')
    process_user_data.delay('Jane Doe', 25)
