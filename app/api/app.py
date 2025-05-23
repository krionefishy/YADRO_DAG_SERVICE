from fastapi import FastAPI
from fastapi.applications import AppType
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from app.store.database import Database
from app.web.config import settings
from app.web.middleware import setup_middleware
from app.web.routes import graph_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database(db_url=settings.POSTGRES_URL)
    await db.connect()
    app.state.db = db
    
    yield

    await db.disconnect()


def setup_app() -> FastAPI:
    app = FastAPI(title="DAG Service", lifespan=lifespan)

    setup_middleware(app)
    app.include_router(graph_router, prefix="/api")
    return app

app = setup_app()