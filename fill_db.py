from dotenv import load_dotenv
import os
dotenv_path = os.path.join(os.path.dirname(__file__), 'app', '.env')
load_dotenv(dotenv_path)

from csv import DictReader
import asyncio
from app.api.models.city import City
from app.services.db_services import CitiesService
from app.utils.uow import Uow


async def fill_db():
    uow = Uow()
    cities_service = CitiesService(uow)
    with open('app/utils/cities.csv', 'r', encoding='utf-8') as csvfile:
        row = DictReader(csvfile, delimiter=',')
        for x in row:
            to_add = City(city_name=x.get('Город'), longitude=float(x.get('Долгота')), latitude=float(x.get('Широта')),
                          timezone=int((t := x.get('Часовой пояс'))[t.find('C') + 1:]))
            await cities_service.add_city(to_add)

if __name__ == '__main__':
    asyncio.run(fill_db())