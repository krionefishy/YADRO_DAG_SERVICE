class CustomError(Exception):
    pass


class GraphCycleError(CustomError):
    def __init__(self):
        super().__init__("Failed to add graph")


class NodeNameNotUniqueError(CustomError):
    def __init__(self):
        super().__init__("Failed to add graph")


class EdgeAlreadyExistsError(CustomError):
    def __init__(self):
        super().__init__("Failed to add graph")


class GraphNotFoundError(CustomError):
    def __init__(self, graph_id: int):
        super().__init__(f"Graph entity not found")
