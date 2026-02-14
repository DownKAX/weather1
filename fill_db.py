import sqlalchemy
from dotenv import load_dotenv
import os
dotenv_path = os.path.join(os.path.dirname(__file__), 'app', '.env')
load_dotenv(dotenv_path)

from csv import DictReader
import asyncio
from app.utils.uow import Uow


async def fill_db():
    with open('app/utils/cities.csv', 'r', encoding='utf-8') as csvfile:
        row = DictReader(csvfile, delimiter=',')
        async with Uow() as uow:
            for x in row:
                try:
                    await uow.city_model.add_one({'city_name': x['Город'], 'latitude': float(x['Широта']), 'longitude': float(x['Долгота']), 'timezone': int((t := x['Часовой пояс'])[t.find("C") +1:])})
                except sqlalchemy.exc.IntegrityError:
                    print('1')
                    await uow.rollback()
            else:
                print('Города успешно записаны в базу данных')
            await uow.commit()

if __name__ == '__main__':
    asyncio.run(fill_db())