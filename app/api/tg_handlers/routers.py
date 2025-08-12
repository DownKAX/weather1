# -*- coding: utf-8 -*-

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import F, Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton as KB, ReplyKeyboardMarkup as KMB
from httpx import AsyncClient

from app.services.db_services import UserService, CitiesService
from app.utils.uow import Uow, AbstractUow

class NewCityState(StatesGroup):
    new_city = State()


async def get_user_service(uow: AbstractUow = Uow()):
    return UserService(uow)

async def get_city_service(uow: AbstractUow = Uow()):
    return CitiesService(uow)


router = Router()

@router.message(Command("weather"))
async def weather(message: types.Message):
    weather_keyboard = [[KB(text='Прогноз на сегодня'), KB(text='Прогноз на завтра')],
                        [KB(text='Прогноз на сегодня(кратко)'), KB(text='Прогноз на завтра(кратко)')],
                        [KB(text='Рассылка'), KB(text="Изменить город")]]
    keyboard = KMB(keyboard=weather_keyboard, resize_keyboard=True)
    await message.answer(text='Узнать прогноз погоды:', reply_markup=keyboard)

@router.message(F.text=='Прогноз на сегодня')
@router.message(F.text=='Прогноз на завтра')
@router.message(F.text=='Прогноз на сегодня(кратко)')
@router.message(F.text=='Прогноз на завтра(кратко)')
async def today(message: types.Message):
    user_service = await get_user_service()
    city_id = await user_service.select_user({'telegram_id': message.from_user.id}, return_value='city_id')
    body = {'city_id': city_id, 'forecast_range': message.text}
    if message.text.find('(кратко)') != -1:
        body.update({'short_flag': True})
        body['forecast_range'] = message.text.replace('(кратко)', '')
    async with AsyncClient() as client:
        forecast = await client.post('http://localhost:80/user/get_forecast', data=body)

    forecast = forecast.json().get('forecast')
    await message.answer(text=forecast)

@router.message(F.text=="Изменить город")
async def change_city(message: types.Message, state: FSMContext):
    await message.answer(text='Введите следующим сообщением название вашего города')
    await state.set_state(NewCityState.new_city)

@router.message(NewCityState.new_city)
async def change_new_city(message: types.Message, state: FSMContext):
    city_service = await get_city_service()
    city_id = await city_service.select_city({'city_name': message.text}, return_value='id')
    if not city_id:
        await message.answer(text='Такого города не существует/Нет в нашем сервисе, введи другой')
    else:
        user_service = await get_user_service()
        await user_service.update_data(col_name='telegram_id', col_value=message.from_user.id, data={'city_id': city_id})
        await message.answer(text=f'Город успешно изменён на: {message.text}')
        await state.clear()
        await state.set_state(None)

