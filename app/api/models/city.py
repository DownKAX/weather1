from pydantic import BaseModel

class City(BaseModel):
    id: int = None
    city_name: str
    longitude: float
    latitude: float
    timezone: int
