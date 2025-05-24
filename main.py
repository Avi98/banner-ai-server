"""main app"""

from fastapi import FastAPI
from core.utils.logger import Logger
from routers.banner import banner

app = FastAPI()
logger = Logger.get_logger("banner_service", log_file="app.log")


def receive_signal(signalNumber, frame):
    print("Received:", signalNumber)
    sys.exit()


@app.on_event("startup")
async def startup_event():
    import signal

    signal.signal(signal.SIGINT, receive_signal)
    # startup tasks


app.include_router(banner.router, prefix="/banner")
