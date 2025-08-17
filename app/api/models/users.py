from pydantic import BaseModel, model_validator
from datetime import datetime
from fastapi import HTTPException

class User(BaseModel):
    username: str
    password: str
    register_time: datetime
    city_id: int
    telegram_id: int
    newsletter: bool = True

class RegistrationForm(BaseModel):
    username: str
    password: str
    password_confirmation: str
    telegram_id: int
    city: str


    @model_validator(mode='after')
    def validate_password_len(self):
        if 8 > (l :=len(self.password)) or l > 64:
            raise HTTPException(400, 'Password len must be between 8 and 64')
        if self.password != self.password_confirmation:
            raise HTTPException(400, 'Passwords do not match')
        return self


class City(BaseModel):
    id: int = None
    city_name: str
    longitude: float
    latitude: float
    timezone: int
