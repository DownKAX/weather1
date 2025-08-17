from typing import Any
from pydantic import BaseModel

class QueryFilter(BaseModel):
    column: str
    value: Any
