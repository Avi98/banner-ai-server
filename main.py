"""main app"""

from fastapi import FastAPI
from core.utils.logger import Logger
from routers.banner import banner

app = FastAPI()
logger = Logger.get_logger("banner_service", log_file="app.log")

app.include_router(banner.router, prefix="/banner")
