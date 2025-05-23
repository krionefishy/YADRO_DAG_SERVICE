from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.web.custom_exceptions import (
    CustomError,
    GraphNotFoundError,
    GraphCycleError,
    NodeNameNotUniqueError,
    EdgeAlreadyExistsError
)


def setup_middleware(app: FastAPI):
    @app.exception_handler(GraphNotFoundError)
    async def handle_graph_not_found(request: Request, exc: GraphNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"message": str(exc)}
        )

    @app.exception_handler(GraphCycleError)
    async def handle_cycle_error(request: Request, exc: GraphCycleError):
        return JSONResponse(
            status_code=400,
            content={"message": str(exc)}
        )

    @app.exception_handler(NodeNameNotUniqueError)
    async def handle_node_name_unique_error(request: Request, exc: NodeNameNotUniqueError):
        return JSONResponse(
            status_code=400,
            content={"message": str(exc)}
        )

    @app.exception_handler(EdgeAlreadyExistsError)
    async def handle_edge_already_exists_error(request: Request, exc: EdgeAlreadyExistsError):
        return JSONResponse(
            status_code=400,
            content={"message": str(exc)}
        )

    @app.exception_handler(IntegrityError)
    async def handle_db_integrity_error(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=400,
            content={"message": "Failed to add graph"}
        )

    @app.middleware("http")
    async def error_middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except CustomError as e:
            raise e
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"message": "Internal server error"}
            )