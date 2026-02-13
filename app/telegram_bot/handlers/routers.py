# -*- coding: utf-8 -*-

from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from httpx import AsyncClient

from app.middleware.middleware import logger
from app.telegram_bot.handlers.dependecies import user_dependency, cities_dependency
from app.telegram_bot.keyboards.common_keyboards import weather_markup
import os

class NewCityState(StatesGroup):
    new_city = State()

async def weather(message: types.Message):
    await message.answer(text='Узнать прогноз погоды:', reply_markup=weather_markup)

async def today(message: types.Message,
                user_service: user_dependency):
    city_id = await user_service.select_user({'telegram_id': message.from_user.id}, return_value='city_id')
    body = {'city_id': city_id, 'forecast_range': message.text}
    async with AsyncClient() as client:
        environment = os.getenv('ENVIRONMENT', 'localhost')
        forecast = await client.post(f'http://{environment}:80/user/get_forecast', data=body, timeout=10)
        if forecast.status_code == 200:
            forecast = forecast.json().get('forecast')
            weather_plot = FSInputFile(forecast)
            await message.answer_photo(photo=weather_plot)
        else:
            await message.answer(text='Ошибка при получении погодных данных')
            logger.info(forecast.text)
            logger.info(f" status_code: {forecast.status_code}\n")


async def change_city(message: types.Message, state: FSMContext):
    await message.answer(text='Введите следующим сообщением название вашего города')
    await state.set_state(NewCityState.new_city)

async def change_new_city(message: types.Message, state: FSMContext,
                          city_service: cities_dependency, user_service: user_dependency):
    city_id = await city_service.select_city({'city_name': message.text}, return_value='id')
    if not city_id:
        await message.answer(text='Такого города не существует/Нет в нашем сервисе, введи другой')
    else:
        await user_service.update_data(col_name='telegram_id', col_value=message.from_user.id, data={'city_id': city_id})
        await message.answer(text=f'Город успешно изменён на: {message.text}')
        await state.clear()
        await state.set_state(None)

async def registration_required(message: types.Message):
    await message.answer(text='Вы не зарегистрированы в нашей системе, пройдите регистрацию')