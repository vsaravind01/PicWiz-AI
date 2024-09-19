from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.sql_db_manager import SqlDatabaseManager, create_db_and_tables
from contextlib import asynccontextmanager
from routers import main_router
import logging

logging.getLogger("passlib").setLevel(logging.ERROR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager = SqlDatabaseManager()
    engine = db_manager.engine()
    create_db_and_tables(engine)
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(main_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
