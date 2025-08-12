import logging
from fastapi import Request

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('info.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s %(levelname)s %(message)s',
#     datefmt='%d-%m-%Y %H:%M:%S',
#     handlers=[
#         logging.FileHandler('info.log'),
#         logging.StreamHandler()])
#
# logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    logger.info(f"Logging request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Logged response: {response.status_code}\n")
    return response