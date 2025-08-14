from datetime import datetime, timedelta, UTC
from pydantic import BaseModel, Field

class Session(BaseModel):
    user: str
    useragent: str
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))
    exp: datetime = Field(default_factory=lambda: (datetime.now(UTC) + timedelta(days=5)))
    #У каждого экземляра будут правильные значения

class SessionForRedis(BaseModel):
    refresh_token: str
    session: Session

class Tokens(BaseModel):
    access_token: str
    refresh_token: str