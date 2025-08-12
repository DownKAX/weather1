# -*- coding: utf-8 -*-

from aiogram import F, Router, types
from aiogram.types import KeyboardButton as KB, ReplyKeyboardMarkup as KMB, InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM

from app.utils.uow import Uow, AbstractUow
from app.services.db_services import UserService, CitiesService

async def get_user_service(uow: AbstractUow = Uow()):
    return UserService(uow)

news = Router()

newsletter_keyboard = [[IKB(text='Отказаться от рассылки', callback_data='news_refuse'), IKB(text='Подписаться на рассылку', callback_data='news_accept')]]
nk = IKM(inline_keyboard=newsletter_keyboard)

@news.message(F.text=='Рассылка')
async def newsletter(message: types.Message):
    await message.answer("Изменение настроек рассылки", reply_markup=nk)

@news.callback_query(F.data == 'news_refuse')
async def news_refuse(callback_data: types.CallbackQuery):
    user_service = await get_user_service()
    newsletter_sub = await user_service.select_user({'telegram_id': callback_data.from_user.id}, return_value='newsletter')
    if newsletter_sub:
        await user_service.update_data(col_name='telegram_id', col_value=callback_data.from_user.id, data={'newsletter': False})
        await callback_data.answer(text='Вы отказались от рассылки')
    else:
        await callback_data.answer(text='Вы и так не подписаны на рассылку')

@news.callback_query(F.data == 'news_accept')
async def news_accept(callback_data: types.CallbackQuery):
    user_service = await get_user_service()
    newsletter_sub = await user_service.select_user({'telegram_id': callback_data.from_user.id}, return_value='newsletter')
    if newsletter_sub:
        await callback_data.answer(text='Вы и так подписаны на рассылку')
    else:
        await user_service.update_data(col_name='telegram_id', col_value=callback_data.from_user.id, data={'newsletter': True})
        await callback_data.answer(text='Вы подписались на рассылку, теперь вы будете получать её каждый день в 7:00 по вашему времени')