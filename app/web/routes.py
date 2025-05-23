from fastapi import APIRouter, Depends, HTTPException, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.store.accessors.graph_accessor import GraphAccessor
from app.web.custom_exceptions import GraphNotFoundError, GraphCycleError
from app.web.schemas import GraphCreateSchema
from app.web.dependencies import get_db_session

graph_router = APIRouter(prefix="/graph", tags=["Graph"])



@graph_router.post("/", status_code=201)
async def create_graph(
    schema: GraphCreateSchema,
    db: AsyncSession = Depends(get_db_session)
):
    accessor = GraphAccessor(db)

    if await accessor.has_cycle(schema.edges):
        raise GraphCycleError()

    graph_id = await accessor.create_graph(schema)
    return {"id": graph_id}


@graph_router.get("/{graph_id}", response_model=dict)
async def read_graph(graph_id: int, db: AsyncSession = Depends(get_db_session)):
    accessor = GraphAccessor(db)
    try:
        return await accessor.get_graph_by_id(graph_id)
    except GraphNotFoundError:
        raise HTTPException(status_code=404, detail={"message": "Graph entity not found"})


@graph_router.get("/{graph_id}/adjacency_list", response_model=dict)
async def get_adjacency_list(graph_id: int, db: AsyncSession = Depends(get_db_session)):
    accessor = GraphAccessor(db)
    try:
        return await accessor.get_adjacency_list(graph_id)
    except GraphNotFoundError:
        raise HTTPException(status_code=404, detail={"message": "Graph entity not found"})


@graph_router.get("/{graph_id}/reverse_adjacency_list", response_model=dict)
async def get_reverse_adjacency_list(graph_id: int, db: AsyncSession = Depends(get_db_session)):
    accessor = GraphAccessor(db)
    try:
        return await accessor.get_reverse_adjacency_list(graph_id)
    except GraphNotFoundError:
        raise HTTPException(status_code=404, detail={"message": "Graph entity not found"})


@graph_router.delete("/{graph_id}/node/{node_name}", status_code=204)
async def delete_node(graph_id: int, node_name: str, db: AsyncSession = Depends(get_db_session)):
    accessor = GraphAccessor(db)
    try:
        await accessor.delete_node_by_name(graph_id, node_name)
    except GraphNotFoundError:
        raise HTTPException(status_code=404, detail={"message": "Graph entity not found"})