"""main app"""

from fastapi import FastAPI
from routers.banner import banner
from routers.vedio import routes

app = FastAPI()


def receive_signal(signalNumber, frame):
    print("Received:", signalNumber)
    sys.exit()


@app.on_event("startup")
async def startup_event():
    import signal

    signal.signal(signal.SIGINT, receive_signal)
    # startup tasks


app.include_router(
    banner.router,
)
app.include_router(routes.router)
