"""main app"""

from fastapi import FastAPI
from routers.banner import banner


app = FastAPI()

app.include_router(banner.router, prefix="/banner")
