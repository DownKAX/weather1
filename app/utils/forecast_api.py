# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Agg")
import asyncio
import pathlib
from datetime import datetime, timedelta, time
from fastapi import HTTPException
import matplotlib.pyplot as plt

import pandas as pd
import httpx




tfromiso = time.fromisoformat
fromiso = datetime.fromisoformat

class ForecastAPI:
    def __init__(self):
        self.ranges = {'Прогноз на сегодня': False, 'Прогноз на завтра': True}
        self.uvi_url = "https://currentuvindex.com/api/v1/uvi"
        self.weather_url = "https://api.open-meteo.com/v1/forecast"
        self.weather_vars = ("temperature_2m", "relative_humidity_2m", "precipitation", "precipitation_probability",
                             "cloud_cover", "surface_pressure", "wind_speed_10m",
                             "wind_direction_10m")

    async def get_external_data(self, latitude: float, longitude: float) -> tuple[list, dict]:
        forecast_url_params = {'latitude': latitude, 'longitude': longitude, 'hourly': self.weather_vars}
        async with httpx.AsyncClient(timeout=60) as client:
            forecast_uvi = await client.get(self.uvi_url, params=forecast_url_params)
            forecast_weather = await client.get(self.weather_url, params=forecast_url_params)

            if forecast_weather.status_code != 200:
                raise HTTPException(detail="Weather external service is not responding", status_code=403)

            if forecast_uvi.status_code != 200:
                raise HTTPException(detail="UVI external service is not responding", status_code=403)

        forecast_uvi: list = forecast_uvi.json()['forecast']  # [{'time': '2025-07-22T17:00:00Z', 'uvi': 0}, ...]
        forecast_weather.encoding = 'cp1251'
        forecast_weather: dict[str, list] = forecast_weather.json()['hourly']  # {"time": ["2025-07-22T00:00", ...], "temperature_2m": [16.7, ...], ...}
        return forecast_uvi, forecast_weather

    async def get_forecast(self, latitude: float, longitude: float, forecast_range: str, city_date: datetime, city_name: str, city_timezone: int) -> pathlib.Path:
        is_for_tomorrow = self.ranges[forecast_range]
        date = (city_date + timedelta(days=is_for_tomorrow)).strftime("%d-%m-%Y")
        path = pathlib.Path('app', 'utils', 'forecast_plots', f'{date}', f'{city_name}.png')

        if not path.exists():
            pathlib.Path(path.parent).mkdir(parents=True, exist_ok=True)
            try:
                forecast_uvi, forecast_weather = await self.get_external_data(latitude, longitude)
            except HTTPException as e:
                raise e

            await asyncio.to_thread(self.create_plot,forecast_weather, forecast_uvi, path, city_timezone, is_for_tomorrow)

        return path

    def create_plot(self, forecast_raw_data: dict, uvi_data: list, path, city_timezone: int, is_for_tomorrow: bool) -> None:
        forecast_df = pd.DataFrame(forecast_raw_data)
        uvi_df = pd.DataFrame(uvi_data)


        # Приводим время к общему dtype в обоих DataFrames; берем только нужный нам день
        forecast_df['time'] = forecast_df['time'].astype("datetime64[ns]")
        uvi_df['time'] = pd.to_datetime(uvi_df['time']).dt.tz_localize(None)
        forecast_df['time'] += timedelta(hours=city_timezone)
        uvi_df['time'] += timedelta(hours=city_timezone)
        forecast_df = forecast_df[forecast_df['time'].dt.day == forecast_df.loc[0, 'time'].day + is_for_tomorrow]

        # Соединяем графики в один и ограничиваем кол-во во избежание перегрузки графика
        df = forecast_df.merge(uvi_df, on='time')

        # Оптимизируем отображение в зависимости от количества данных
        step = 1 if len(df) <= 16 else 2
        df = df[::step]
        labels = df['time'].dt.strftime("%H:%M")
        ticks = range(0, len(df) * step, step)

        # отображаемые данные
        weather_icons = {'sun': chr(0x2600), 'cloud': chr(0x2601), 'sun_cloud': chr(0x2600) + chr(0x2601),
                         'rain': chr(0x2614)}
        humidity = f"{df['relative_humidity_2m'].mean():.1f}%"
        pressure = f"{df['surface_pressure'].mean():.0f}mm"
        wind_speed = f"{df['wind_speed_10m'].mean():.0f}m/s"

        precipitation = df['precipitation'].apply(lambda x: weather_icons['sun'] if x < 1 else weather_icons['rain'])
        precipitation[precipitation == weather_icons['sun']] = df['cloud_cover'].apply(
            lambda x: weather_icons['sun'] if x < 20 else weather_icons['sun_cloud'] if x < 60 else weather_icons[
                'cloud'])
        data = f'Влажность: {humidity}\nДавление: {pressure}\nСкорость ветра: {wind_speed}'

        # Отображаем данные так, чтобы все столбцы смотрели вверх, даже если есть отрицательные значения
        if (min_temp := min(df['temperature_2m'])) < 0:
            values_for_plot = df['temperature_2m'].apply(lambda x: x + abs(min_temp) + 1)
        else:
            values_for_plot = df['temperature_2m']

        # Строим график
        plt.figure(figsize=(max(len(df), 4), 5))
        figure_axes = plt.axes((0.1, 0.1, 0.8, 0.8))
        figure_axes.grid(alpha=0.2, color='y', which='both')
        bar_plot = plt.bar(df.index, values_for_plot, label=data)

        # Настройка отображения
        rang = int(max(abs(df['temperature_2m'])) - min(abs(df['temperature_2m']))) + 5
        rang = max(4, rang)
        plt.yticks([x for x in range(rang)])
        plt.xticks(ticks=ticks, labels=labels, rotation=45)
        plt.tick_params(axis='y', labelleft=False)

        # Информация
        plt.title(f"Погода на {path.parent.name}\n"
                  f"{path.name.strip('.png')}")
        plt.bar_label(bar_plot, labels=df['temperature_2m'], padding=1, fontsize=16)
        plt.bar_label(bar_plot, labels=precipitation, padding=15, fontsize=20)
        figure_axes.legend(fontsize=14)

        plt.savefig(pathlib.Path(path))



forecast = ForecastAPI()
