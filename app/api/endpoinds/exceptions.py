from fastapi import HTTPException

class NoDataException(HTTPException):
    def __init__(self, status_code: int = 400, message: str = 'No data found'):
        super().__init__(status_code, message)
