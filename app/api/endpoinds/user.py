from fastapi import APIRouter, HTTPException, Form, Depends, Cookie
from datetime import datetime, UTC

from app.core.security import user_data_from_token
from app.utils.uow import Uow, AbstractUow
from app.services.db_services import UserService, CitiesService
from app.utils.forecast_api import forecast

async def get_user_service(uow: AbstractUow = Depends(Uow)):
    return UserService(uow)

async def get_city_service(uow: AbstractUow = Depends(Uow)):
    return CitiesService(uow)

user = APIRouter(prefix='/user')

@user.post('/update_telegram_city')
async def update_telegram_city(token: str = Cookie(), city: str = Form(default=None), telegram_id: int = Form(default=None),
                               user_service = Depends(get_user_service), city_service = Depends(get_city_service)):
    user: dict = await user_data_from_token(token)
    if not (city or telegram_id):
        raise HTTPException(status_code=401, detail='Nothing to change')

    data_to_update = {}
    if city:
        city_id: int = await city_service.select_city({'city_name': city}, return_value='id')
        data_to_update['city_id'] = city_id
    if telegram_id:
        data_to_update['telegram_id'] = telegram_id

    updated_data = await user_service.update_data(col_name='username', col_value=user.get('username'), data=data_to_update)
    return updated_data

@user.post("/get_forecast")
async def get_forecast(city_id: int = Form(...), forecast_range: str = Form(...), short_flag: bool = Form(default=False),
                       city_service = Depends(get_city_service)):
    city_data = await city_service.select_city({'id': city_id})
    result = await forecast.get_forecast(latitude=city_data.latitude, longitude=city_data.longitude, forecast_range=forecast_range, current_hour=datetime.now(UTC).hour, analysis_mark=short_flag)
    return {"forecast": result}
