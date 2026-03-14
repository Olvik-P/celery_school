import time

from celery_app import app


@app.task
def add(x, y):
    """
    Простая функция сложения, которая 'спит' 5 секунд, имитируя долгую
    работу.
    """
    print(f'Задача add({x}, {y}) началась...')
    time.sleep(5)
    result = x + y
    print(f'Задача add завершена. Результат: {result}')
    return result


@app.task
def multiply(x, y):
    time.sleep(1)
    print('Задача multiply выполняется...')
    result = x * y
    print(f'Задача multiply завершена. Результат: {result}')
    return result


@app.task(bind=True, max_retries=3, default_retry_delay=5)
def risky_division(self, x, y):
    """
    Задача, которая может упасть с ошибкой.
    bind=True дает доступ к объекту задачи (self)
    max_retries=3 - максимум 3 попытки
    default_retry_delay=5 - ждать 5 секунд между попытками
    """
    print(f'🔄 Попытка #{self.request.retries + 1}: делим {x} на {y}')
    try:
        if y == 0:
            raise ValueError('Деление на ноль невозможно')
        time.sleep(1)
        result = x / y
        print(f'✅ Успех! {x}/{y} = {result}')
        return result
    except Exception as e:
        print('Error', e)

        if self.request.retries < self.max_retries:
            print(f'⏳ Повтор через {self.default_retry_delay} сек...')
            raise self.retry(e=e, countdown=self.default_retry_delay)
        else:
            print('💥 Исчерпаны все попытки!')
            # Больше не пытаемся, просто сообщаем об ошибке
            return {'error': str(e), 'status': 'failed'}


if __name__ == '__main__':
    add.delay(2, 3)
    multiply.delay(2, 3)
