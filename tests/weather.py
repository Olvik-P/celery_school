import time

from tasks.weather import get_weather


def test_weather_forecast(sity):
    """Тест 5: Прогноз погоды"""
    print('\n' + '='*50)
    print('5. ПРОГНОЗ ПОГОДы')
    print('='*50)
    res = get_weather.delay(sity)
    time.sleep(3)
    print(res.get())


if __name__ == '__main__':
    test_weather_forecast('Yekaterinburg')
