from initializers import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from routers import main_router
import logging

logging.getLogger("passlib").setLevel(logging.ERROR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = init_db()
    yield
    if engine:
        engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(main_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    from settings import Settings

    settings = Settings()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.app.log_level.value,
        reload=settings.app.debug,
    )
