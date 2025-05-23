from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession


def get_db():
    from app.api.app import app
    return app.state.db


async def get_db_session(app: FastAPI = Depends()) -> AsyncSession:
    async with app.state.db.get_db() as session:
        return session

        