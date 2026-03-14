import time

from tasks.network import fetch_website_status


def test_website_check():
    """Тест 4: Проверка сайтов"""
    print('\n' + '='*50)
    print('4. ПРОВЕРКА САЙТОВ')
    print('='*50)

    # Работающий сайт
    res5 = fetch_website_status.delay('https://google.com')
    time.sleep(3)
    print(f'Google: {res5.get()}')

    # Несуществующий сайт
    res6 = fetch_website_status.delay('https://etot-sayt-ne-sushestvuet.ru')
    time.sleep(3)
    print(f'Несуществующий: {res6.get()}')


if __name__ == '__main__':
    test_website_check()
