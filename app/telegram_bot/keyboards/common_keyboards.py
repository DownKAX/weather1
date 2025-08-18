from aiogram.types import (InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM,
                           KeyboardButton as KB, ReplyKeyboardMarkup as KMB)

newsletter_keyboard = [[IKB(text='Отказаться от рассылки', callback_data='news_refuse'), IKB(text='Подписаться на рассылку', callback_data='news_accept')]]
newsletter = IKM(inline_keyboard=newsletter_keyboard)

weather_keyboard = [[KB(text='Прогноз на сегодня'), KB(text='Прогноз на завтра')],
                    [KB(text='Прогноз на сегодня(кратко)'), KB(text='Прогноз на завтра(кратко)')],
                    [KB(text='Рассылка'), KB(text="Изменить город")]]
weather_markup = KMB(keyboard=weather_keyboard, resize_keyboard=True)