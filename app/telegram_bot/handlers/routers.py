# -*- coding: utf-8 -*-

from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from httpx import AsyncClient
from app.telegram_bot.handlers.dependecies import user_dependency, cities_dependency
from app.telegram_bot.keyboards.common_keyboards import weather_markup

class NewCityState(StatesGroup):
    new_city = State()

async def weather(message: types.Message):
    await message.answer(text='Узнать прогноз погоды:', reply_markup=weather_markup)

async def today(message: types.Message,
                user_service: user_dependency):
    city_id = await user_service.select_user({'telegram_id': message.from_user.id}, return_value='city_id')
    body = {'city_id': city_id, 'forecast_range': message.text}
    if message.text.find('кратко') != -1:
        body.update({'short_flag': True})
        body['forecast_range'] = message.text.replace('(кратко)', '')
    async with AsyncClient() as client:
        forecast = await client.post('http://localhost:80/user/get_forecast', data=body)
        forecast = forecast.json().get('forecast')
    await message.answer(text=forecast)

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