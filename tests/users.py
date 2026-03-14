import time

from tasks.users import process_user_data


def test_user_data():
    """Тест 3: Обработка пользовательских данных"""
    print('\n' + '='*50)
    print('3. ОБРАБОТКА ПОЛЬЗОВАТЕЛЯ')
    print('='*50)

    # Передаем позиционные аргументы
    res3 = process_user_data.delay('Алиса', 25, 'alisa@example.com')
    time.sleep(4)
    result = res3.get()
    print(f'Результат (позиционные): {result}')
    print(f'Тип результата: {type(result)}')
    print(f'Имя из результата: {result['name']}')

    # Передаем именованные аргументы
    res4 = process_user_data.delay(
        name='Боб',
        age=30,
        email='bob@example.com'
    )
    time.sleep(4)
    print(f'\nРезультат (именованные): {res4.get()}')


if __name__ == '__main__':
    test_user_data()
