from pydantic import BaseModel, field_validator, model_validator
from typing import List, Dict, Any, Optional
from enum import Enum


class NodeSchema(BaseModel):
    name: str

    @field_validator("name")
    def validate_name(cls, value):
        if not value.isalpha():
            raise ValueError("Node name contains only latin letters")
        if len(value) > 255:
            raise ValueError("Node name must be less then 255 chars")
        return value


class EdgeSchema(BaseModel):
    source: str
    target: str


class GraphCreateSchema(BaseModel):
    nodes: List[NodeSchema]
    edges: List[EdgeSchema]

    @model_validator(mode="after")
    def check_nodes_not_empty(self):
        if not self.nodes:
            raise ValueError("Graph must contain at least one node")
        return self

    @model_validator(mode="after")
    def check_edges_not_empty(self):
        if not self.edges:
            raise ValueError("Graph must contain at least one edge")
        return self

    @model_validator(mode="after")
    def check_unique_node_names(self):
        names = [node.name for node in self.nodes]
        if len(names) != len(set(names)):
            raise ValueError("All node names must be unique within the graph")
        return self

    @model_validator(mode="after")
    def check_unique_edges(self):
        edge_pairs = [(edge.source, edge.target) for edge in self.edges]
        if len(edge_pairs) != len(set(edge_pairs)):
            raise ValueError("There are duplicate edges in the graph")
        return self


class GraphCreateResponseSchema(BaseModel):
    id: int


class GraphReadResponseSchema(BaseModel):
    id: int
    nodes: List[NodeSchema]
    edges: List[EdgeSchema]


class AdjacencyListResponseSchema(BaseModel):
    adjacency_list: Dict[str, List[str]]


class ErrorResponseSchema(BaseModel):
    message: str


class ValidationErrorSchema(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class HTTPValidationErrorSchema(BaseModel):
    detail: List[ValidationErrorSchema]