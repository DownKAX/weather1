from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

def common_check(FuncException):
    async def wrapper(func, e_code, e_message, *args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except FuncException as e:
            raise HTTPException(status_code=e_code, detail=e_message)
    return wrapper

unique_check = common_check(IntegrityError)
exists_check = common_check(TypeError)