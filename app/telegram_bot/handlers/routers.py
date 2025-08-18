# -*- coding: utf-8 -*-

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import F, Router, types
from aiogram.fsm.state import StatesGroup, State
from datetime import UTC, datetime

from app.utils.forecast_api import forecast
from app.telegram_bot.handlers.dependecies import user_dependency, cities_dependency
from app.telegram_bot.keyboards.common_keyboards import weather_markup

class NewCityState(StatesGroup):
    new_city = State()

router = Router()

@router.message(Command("weather"))
async def weather(message: types.Message):
    await message.answer(text='Узнать прогноз погоды:', reply_markup=weather_markup)

@router.message(F.text=='Прогноз на сегодня')
@router.message(F.text=='Прогноз на завтра')
@router.message(F.text=='Прогноз на сегодня(кратко)')
@router.message(F.text=='Прогноз на завтра(кратко)')
async def today(message: types.Message,
                user_service: user_dependency, city_service: cities_dependency, short_flag = False):
    city_id = await user_service.select_user({'telegram_id': message.from_user.id}, return_value='city_id')
    city_data = await city_service.select_city({'id': city_id})
    day = message.text
    if message.text.find('(кратко)') != -1:
        short_flag = True
        day = message.text.replace('(кратко)', '')

    forecast_data = await forecast.get_forecast(latitude=city_data.latitude,
                                          longitude=city_data.longitude,
                                          forecast_range=day,
                                          current_hour=datetime.now(UTC).hour,
                                          analysis_mark=short_flag)
    await message.answer(text=forecast_data)

@router.message(F.text=="Изменить город")
async def change_city(message: types.Message, state: FSMContext):
    await message.answer(text='Введите следующим сообщением название вашего города')
    await state.set_state(NewCityState.new_city)

@router.message(NewCityState.new_city)
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