from sqlalchemy import (
    Integer, 
    String,
    ForeignKey,
    Column,
    Index, 
    UniqueConstraint

)

from sqlalchemy.orm import (
    relationship, 
    mapped_column, 
    Mapped, 
    declarative_base,
    validates
)
from app.store.models.base import Base


class GraphModel(Base):
    __tablename__ = "graphs"
    id = mapped_column(Integer, primary_key=True, index=True)
    nodes =relationship(back_populates="graph", cascade="all, delete-orphan")
    edges = relationship(back_populates="graph", cascade="all, delete-orphan")



class NodeModel(Base):
    __tablename__ = "nodes"
    __table_args__ = (
        UniqueConstraint('graph_id', 'name', name='uq_node_graph_name'),
        Index('idx_node_graph_name', 'graph_id', 'name'),
    )
    id = mapped_column(Integer, primary_key=True)
    graph_id = mapped_column(Integer, ForeignKey('graphs.id', ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    graph = relationship(back_populates="nodes")
    out_edges = relationship(
        foreign_keys="EdgeModel.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan"
    )



class EdgeModel(Base):
    __tablename__ = "edges"
    __table_args__ = (
        UniqueConstraint('graph_id', 'source_node_id', 'target_node_id', name='uq_edge_graph_source_target'),
        Index('idx_edge_source_target', 'source_node_id', 'target_node_id'),
        Index('idx_edge_graph', 'graph_id'),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    graph_id: Mapped[int] = mapped_column(Integer, ForeignKey('graphs.id', ondelete="CASCADE"))
    source_node_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('nodes.id', ondelete="CASCADE")
    )
    target_node_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('nodes.id', ondelete="CASCADE")
    )
    
    # Relationships
    graph: Mapped["GraphModel"] = relationship(back_populates="edges")
    source_node: Mapped["NodeModel"] = relationship(
        foreign_keys=[source_node_id],
        back_populates="out_edges"
    )