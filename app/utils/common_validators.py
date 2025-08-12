from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

def common_check(FuncException):
    async def wrapper(func, e_code, e_message, with_ermsg=False, *args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except FuncException as e:
            if with_ermsg:
                e = str(e)
                e_message = e[e.find('users.') + 6:e.find('\n')] + e_message
            raise HTTPException(status_code=e_code, detail=e_message)
    return wrapper

unique_check = common_check(IntegrityError)
exists_check = common_check(TypeError)