from aiogram import Dispatcher, F
from aiogram.filters import Command

from app.telegram_bot.handlers.routers import (weather, today, change_city,
                                               change_new_city, NewCityState, registration_required)
from app.telegram_bot.handlers.newsletter import newsletter, news_refuse, news_accept
from app.telegram_bot.handlers.dependecies import RegisteredFilter


def register_handlers(dp: Dispatcher):
    F_texts = ['Прогноз на сегодня', 'Прогноз на завтра', 'Прогноз на сегодня(кратко)', 'Прогноз на завтра(кратко)',
               'Рассылка', "Изменить город"]
    F_datas = ['news_refuse', 'news_accept']

    # routers
    dp.message.register(weather, Command(commands=['start', 'weather']), RegisteredFilter())

    dp.message.register(today, F.text.in_({'Прогноз на сегодня', 'Прогноз на завтра',
                                           'Прогноз на сегодня(кратко)', 'Прогноз на завтра(кратко)'}),
                                            RegisteredFilter())

    dp.message.register(change_city, F.text == "Изменить город", RegisteredFilter())
    dp.message.register(change_new_city, NewCityState.new_city, RegisteredFilter())

    # newsletter
    dp.message.register(newsletter, F.text == 'Рассылка', RegisteredFilter())
    dp.callback_query.register(news_refuse, F.data == 'news_refuse', RegisteredFilter())
    dp.callback_query.register(news_accept, F.data == 'news_accept', RegisteredFilter())

    #access denied
    dp.message.register(registration_required, Command(commands=['start', 'weather']))
    dp.message.register(registration_required, F.text.in_(F_texts))
    dp.callback_query.register(registration_required, F.data.in_(F_datas))