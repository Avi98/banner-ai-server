"""main app"""

import sys
from fastapi import FastAPI
from config.get_db_session import init_db
from routers.banner import banner
from routers.vedio import routes
from middleware.cors import add_cors


app = FastAPI(
    root_path="/api/v1",
    title="Banner AI Server",
    description="Banner AI Server for generating banners using LLMs",
    version="0.1.0",
)


def receive_signal(signalNumber, frame):
    print("Received:", signalNumber)
    sys.exit()


# apply middleware
add_cors(app)


@app.on_event("startup")
async def startup_event():
    await init_db()

    import signal

    signal.signal(signal.SIGINT, receive_signal)
    # startup tasks


app.include_router(
    banner.router,
)
app.include_router(routes.router)
