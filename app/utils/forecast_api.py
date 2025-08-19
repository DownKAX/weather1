# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, time, UTC
import msgpack
import httpx
from redis import Redis

from app.my_redis_client import get_redis
import asyncio

tfromiso = time.fromisoformat
fromiso = datetime.fromisoformat

class ForecastAPI:
    def __init__(self):
        self.uvi_url = "https://currentuvindex.com/api/v1/uvi"
        self.weather_url = "https://api.open-meteo.com/v1/forecast"
        self.weather_vars = ("temperature_2m", "relative_humidity_2m", "precipitation", "precipitation_probability",
                             "cloud_cover", "surface_pressure", "wind_speed_10m",
                             "wind_direction_10m"
                             )
        self.weather_units = {"": "", '🌡': '°C | ', '💧': '%\n', '☔️': 'мм | ', '☔️％': '% | ',
                               '☁️': '%\n', '⏲️': 'гПа | ',
                               '💨': 'км/ч | ', '💨↗️': '°'
                             }
        self.weather_keys = tuple(self.weather_units.keys())[1:-1]
        self.advices = (
            ((-15, 0.001, 15, 25), ("Сильный мороз! Термобельё обязательно.", "Холодно. Наденьте пуховик и шапку.", "Прохладно. Легкая куртка не помешает.", "Идеально! футболка - отличный выбор.", "Жарко! Наденьте лёгкую одежду и головной убор.")),
            ((30, 60), ("Сухой воздух. Пейте больше воды.", "Комфортная влажность.", "Высокая влажность. Одежда из дышащих тканей.")),
            ((0.001, 2, 10),("Без осадков - можно без зонта.", "Лёгкий дождь. Возьмите зонт.", "Сильный дождь. Непромокаемая обувь обязательна.", "Ливень! Рекомендуем остаться дома.")),
            ((20, 50, 80), ("Дождь маловероятен.", "Возможен дождь. Имейте зонт под рукой.", "Высокая вероятность дождя.", "Точно будет дождь! Обязателен дождевик.")),
            ((20, 70), ("Ясно. Солнцезащитные очки обязательны.", "Переменная облачность.", "Пасмурно. Хороший день для музеев.")),
            ((990, 1020), ("Низкое давление. Возможна головная боль.", "Нормальное давление.", "Высокое давление. Отличный день для активности!")),
            ((5, 10, 15), ("Штиль. Идеально для пикника.", "Лёгкий ветер. Куртка не помешает.", "Сильный ветер. Закрепите незакреплённые предметы.", "Шторм! Будьте осторожны на улице."))
        )

    async def get_external_data(self, latitude: float, longitude: float) -> tuple[list, dict]:
        forecast_url_params = {'latitude': latitude, 'longitude': longitude, 'hourly': self.weather_vars}
        async with httpx.AsyncClient(timeout=60) as client:
            forecast_uvi = await client.get(self.uvi_url, params=forecast_url_params)
            forecast_weather = await client.get(self.weather_url, params=forecast_url_params)

        forecast_uvi: list = forecast_uvi.json()['forecast']  # [{'time': '2025-07-22T17:00:00Z', 'uvi': 0}, ...]
        forecast_weather.encoding = 'cp1251'
        forecast_weather: dict[str, list] = forecast_weather.json()['hourly']  # {"time": ["2025-07-22T00:00", ...], "temperature_2m": [16.7, ...], ...}
        return forecast_uvi, forecast_weather

    async def get_forecast(self, latitude: float, longitude: float, forecast_range: str, current_hour: int, analysis_mark = False):
        r = await get_redis()
        redis_key = f'{str(latitude)}-{str(longitude)}-{str(forecast_range)}-{str(current_hour)}'

        if cached_uvi := await r.get(f"{redis_key}:list"):
            cached_weather = await r.get(f"{redis_key}:dict")
            forecast_weather = msgpack.unpackb(cached_weather, raw=False)
            forecast_uvi = msgpack.unpackb(cached_uvi, raw=False)
        else:
            forecast_uvi, forecast_weather = await self.get_external_data(latitude, longitude)
            seconds_till_next_hour: int = (60 - datetime.now(UTC).minute) * 60
            await r.setex(name=f"{redis_key}:dict", value=msgpack.packb(forecast_weather), time=seconds_till_next_hour)
            await r.setex(name=f"{redis_key}:list", value=msgpack.packb(forecast_uvi), time=seconds_till_next_hour)


        ranges = {'Прогноз на сегодня': 0, 'Прогноз на завтра': 1}
        # Для "выравнивания" прогнозов находим самое раннее время из обоих сервисов
        # У прогноза с ультрафиолетом прогноз начинается позже по времени, поэтому берём его раннее время
        earliest_uvi_hour = fromiso(forecast_uvi[0]['time'][:-1])
        forecast_day = timedelta(days=ranges[forecast_range]) #
        start_point: datetime = earliest_uvi_hour + forecast_day
        if forecast_range == 'Прогноз на завтра': # Прогноз на завтра начинаем с полуночи
            start_point: datetime = start_point.replace(hour=0)

        end_point: datetime = start_point + timedelta(days=1, hours=-start_point.hour)

        start_point: int = list(map(lambda x: fromiso(x), forecast_weather['time'])).index(start_point)
        end_point: int = list(map(lambda x: fromiso(x), forecast_weather['time'])).index(end_point)

        forecast_weather = list(map(lambda x: x[start_point:end_point], forecast_weather.values()))

        if analysis_mark:
            forecast = await self.analyze_forecast(forecast_weather)
        else:
            forecast = await self.build_full_forecast(forecast_weather, forecast_uvi, r, redis_key)
        return forecast

    async def build_full_forecast(self, forecast_raw_data: list, uvi_data: list, r: Redis, redis_key: str) -> str:
        """Собирает строку, отображающую погодные данные на каждый час"""
        for_return = ''
        forecast_len = len(forecast_raw_data[0]) # Количество часов в прогнозе

        for num in range(forecast_len):
            for value, units in zip(forecast_raw_data, self.weather_units):
                val_raw = value[num]
                uvi = uvi_data[num]

                if isinstance(val_raw, str):
                    if fromiso(val_raw).timetuple().tm_hour == 0 or num == 0:
                        for_return += f"📅{fromiso(val_raw).date()}\n{len(val_raw) * '_'}\n\n"
                    for_return += f"{val_raw[val_raw.index('T')+1:]} - "
                    if fromiso(val_raw) == fromiso(uvi['time'][:-1]):
                        for_return += f"☀️UV {uvi['uvi']} | "
                else:
                    unit = f"{units}" if units else ""
                    for_return += f"{unit} {val_raw} {self.weather_units[unit.strip(' :')]}"

            for_return += '\n\n'

        seconds_till_next_hour: int = (60 - datetime.now(UTC).minute) * 60
        await r.setex(redis_key, seconds_till_next_hour, for_return)
        return for_return

    async def analyze_forecast(self, forecast: list) -> str:
        """Собирает советы на основе погодных данных, а также все минимальные и максимальные значения по времени"""
        analysis = '\n\nОсновные значения по прогнозу:\n'
        advices = ''
        for value, value_name, advice in zip(forecast[1:-1], self.weather_keys, self.advices):
            value_mark = self.weather_units[value_name.strip(': ')].strip('\n')
            max_val, min_val = max(value), min(value)
            max_val_ind, min_val_ind = value.index(max_val), value.index(min_val)
            max_val_time, min_val_time = forecast[0][max_val_ind], forecast[0][min_val_ind]
            max_val_time, min_val_time = max_val_time[max_val_time.index('T')+1:], min_val_time[min_val_time.index('T')+1:]
            analysis += f'max {value_name} - {max_val}{value_mark}({max_val_time})\n'
            analysis += f'min {value_name} - {min_val}{value_mark}({min_val_time})\n\n'
            for boundary, advice_text in zip(advice[0], advice[1]):
                if max_val < boundary:
                    advices += advice_text
                    break
            else:
                advices += advice[-1][-1]
        for_return = analysis + advices
        return for_return

forecast = ForecastAPI()
