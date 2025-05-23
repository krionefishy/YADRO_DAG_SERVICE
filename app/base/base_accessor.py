from abc import ABC
from sqlalchemy.ext.asyncio import AsyncSession
from app.web.custom_exceptions import GraphNotFoundError

class BaseAccessor(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session