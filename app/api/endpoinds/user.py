from fastapi import APIRouter, Form, Depends
from datetime import datetime, UTC

from app.api.models.city import City
from app.api.endpoinds.dependecies import city_dependency, user_dependency
from app.api.endpoinds.exceptions import NoDataException
from app.utils.forecast_api import forecast
from app.auth.register import check_token

user = APIRouter(prefix='/user')

@user.post('/update_telegram_city')
async def update_telegram_city(user_service: user_dependency, city_service: city_dependency,
                               user: str = Depends(check_token), city: str = Form(default=None),
                               telegram_id: int = Form(default=None)):
    if not (city or telegram_id):
        raise NoDataException
    data_to_update = {}
    if city:
        city_id: int = await city_service.select_city({'city_name': city}, return_value='id')
        data_to_update['city_id'] = city_id
    if telegram_id:
        data_to_update['telegram_id'] = telegram_id
    updated_data = await user_service.update_data(col_name='username', col_value=user.get('username'), data=data_to_update)
    return updated_data

@user.post("/get_forecast")
async def get_forecast(city_service: city_dependency,
                       city_id: int = Form(...), forecast_range: str = Form(...),
                       short_flag: bool = Form(default=False)
                       ):
    city_data: City = await city_service.select_city({'id': city_id})
    result = await forecast.get_forecast(latitude=city_data.latitude,
                                         longitude=city_data.longitude,
                                         forecast_range=forecast_range,
                                         current_hour=datetime.now(UTC).hour,
                                         analysis_mark=short_flag)
    return {"forecast": result}