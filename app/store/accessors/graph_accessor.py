from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete, update
from app.store.models.base import Base
from sqlalchemy.ext.asyncio import AsyncSession
from app.web.custom_exceptions import GraphNotFoundError, GraphCycleError
from app.store.models.models import GraphModel, NodeModel, EdgeModel
from sqlalchemy.exc import IntegrityError
class GraphAccessor:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_graph(self, schema) -> int:
        try:
            if await self.has_cycle(schema.edges):
                raise GraphCycleError()

            result = await self.session.execute(insert(GraphModel).returning(GraphModel.id))
            graph_id = result.scalar_one()

            for node in schema.nodes:
                await self.session.execute(
                    insert(NodeModel).values(name=node.name, graph_id=graph_id)
                )

            for edge in schema.edges:
                source_id = await self.get_node_id_by_name(graph_id, edge.source)
                target_id = await self.get_node_id_by_name(graph_id, edge.target)

                await self.session.execute(
                    insert(EdgeModel).values(
                        source_node_id=source_id,
                        target_node_id=target_id,
                        graph_id=graph_id
                    )
                )

            await self.session.commit()
            return graph_id

        except GraphCycleError as e:
            await self.session.rollback()
            raise  

        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("Database integrity violation") from e

        except Exception as e:
            await self.session.rollback()
            raise  

    async def get_graph_by_id(self, graph_id: int) -> dict:
        try:
            query = select(GraphModel).where(GraphModel.id == graph_id)
            result = await self.session.execute(query)
            graph = result.scalars().first()

            if not graph:
                raise GraphNotFoundError(graph_id)

            nodes = [{"name": node.name} for node in graph.nodes]
            edges = [
                {"source": edge.source_node.name, "target": edge.target_node.name}
                for edge in graph.edges
            ]

            return {
                "id": graph.id,
                "nodes": nodes,
                "edges": edges
            }

        except GraphNotFoundError:
            await self.session.rollback()
            raise

        except Exception as e:
            await self.session.rollback()
            raise

    async def get_adjacency_list(self, graph_id: int) -> dict:
        try:
            query = (
                select(NodeModel.name, EdgeModel)
                .join(EdgeModel, NodeModel.id == EdgeModel.source_node_id)
                .where(NodeModel.graph_id == graph_id)
            )

            result = await self.session.execute(query)
            rows = result.all()

            adjacency_list = {}

            for node_name, edge in rows:
                adjacency_list.setdefault(node_name, []).append(edge.target_node.name)

            all_nodes_query = select(NodeModel.name).where(NodeModel.graph_id == graph_id)
            all_nodes = (await self.session.execute(all_nodes_query)).scalars().all()

            for node in all_nodes:
                if node not in adjacency_list:
                    adjacency_list[node] = []

            return {"adjacency_list": adjacency_list}

        except Exception as e:
            await self.session.rollback()
            raise

    async def get_reverse_adjacency_list(self, graph_id: int) -> dict:
        try:
            query = (
                select(NodeModel.name, EdgeModel)
                .join(EdgeModel, NodeModel.id == EdgeModel.target_node_id)
                .where(NodeModel.graph_id == graph_id)
            )

            result = await self.session.execute(query)
            rows = result.all()

            reverse_adjacency_list = {}

            for node_name, edge in rows:
                reverse_adjacency_list.setdefault(node_name, []).append(edge.source_node.name)

            all_nodes_query = select(NodeModel.name).where(NodeModel.graph_id == graph_id)
            all_nodes = (await self.session.execute(all_nodes_query)).scalars().all()

            for node in all_nodes:
                if node not in reverse_adjacency_list:
                    reverse_adjacency_list[node] = []

            return {"adjacency_list": reverse_adjacency_list}

        except Exception as e:
            await self.session.rollback()
            raise

    async def delete_node_by_name(self, graph_id: int, node_name: str) -> None:
        try:
            node_query = select(NodeModel).where(
                NodeModel.graph_id == graph_id,
                NodeModel.name == node_name
            ).limit(1)

            result = await self.session.execute(node_query)
            node = result.scalars().first()

            if not node:
                raise GraphNotFoundError(graph_id)

            await self.session.delete(node)
            await self.session.commit()

        except GraphNotFoundError:
            await self.session.rollback()
            raise

        except Exception as e:
            await self.session.rollback()
            raise

    async def has_cycle(self, edges: list) -> bool:
        try:
            from collections import defaultdict

            graph_map = defaultdict(list)
            all_nodes = set()

            for edge in edges:
                src = edge["source"]
                tgt = edge["target"]
                graph_map[src].append(tgt)
                all_nodes.add(src)
                all_nodes.add(tgt)

            visited = set()
            recursion_stack = set()

            def dfs(node):
                if node in recursion_stack:
                    return True
                if node in visited:
                    return False

                visited.add(node)
                recursion_stack.add(node)

                for neighbor in graph_map.get(node, []):
                    if dfs(neighbor):
                        return True

                recursion_stack.remove(node)
                return False

            for node in all_nodes:
                if node not in visited:
                    if dfs(node):
                        return True

            return False

        except Exception as e:
            await self.session.rollback()
            raise RuntimeError("Failed to check cycles due to internal error") from e

    async def get_node_id_by_name(self, graph_id: int, name: str) -> int:
        try:
            query = select(NodeModel.id).where(
                NodeModel.graph_id == graph_id,
                NodeModel.name == name
            ).limit(1)

            result = await self.session.execute(query)
            row = result.first()

            if not row:
                raise GraphNotFoundError(graph_id)

            return row[0]

        except GraphNotFoundError:
            await self.session.rollback()
            raise

        except Exception as e:
            await self.session.rollback()
            raise