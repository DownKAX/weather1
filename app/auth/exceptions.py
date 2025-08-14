from fastapi import HTTPException

class TokenNotFoundException(HTTPException):
    def __init__(self, status_code: int = 403, message: str = 'Token not found'):
        super().__init__(status_code, message)

class InvalidPasswordException(HTTPException):
    def __init__(self, status_code: int = 403, message: str = 'Invalid password'):
        super().__init__(status_code, message)

class ExpiredAccessToken(HTTPException):
    def __init__(self, status_code: int = 403, message: str = 'Expired access token'):
        super().__init__(status_code, message)

class InvalidTokenError(HTTPException):
    def __init__(self, status_code: int = 403, message: str = 'Invalid token'):
        super().__init__(status_code, message)

class InvalidRefreshTokenError(HTTPException):
    def __init__(self, status_code: int = 403, message: str = 'Invalid refresh token'):
        super().__init__(status_code, message)


class ExpiredRefreshToken(HTTPException):
    def __init__(self, status_code: int = 403, message: str = 'Expired refresh token'):
        super().__init__(status_code, message)

class InvalidRefreshToken(HTTPException):
    def __init__(self, status_code: int = 403, message: str = 'Invalid refresh token'):
        super().__init__(status_code, message)