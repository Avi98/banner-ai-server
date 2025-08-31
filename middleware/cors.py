
from config.env_variables import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def add_cors(app:FastAPI):
    settings = get_settings()
    origin = [settings.ALLOWED_ORIGIN] if settings.ALLOWED_ORIGIN else settings.ALLOWED_ORIGIN

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origin,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

