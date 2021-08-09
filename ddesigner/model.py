"""The main model definitions."""
import enum
from dataclasses import *
from typing import Iterable


START_NODE_NAME = "START"


class VariableType(enum.Enum):
    """Supported variable types."""
    STRING = 0
    INTEGER = 1
    BOOLEAN = 2


@dataclass
class Node:
    """A dialogue designer node."""
    next: str
    node_name: str
    node_type: str
    title: str


# Dictionary mapping type names to actual type classes
NODE_TYPE_MAP = {
    "start": Node
}


class DialogueData:
    """Container of Nodes.

    Contains an organized set of Nodes and a dictionary of variables.
    """

    def __init__(self, nodes: Iterable[Node], variables: dict):
        self.variables = variables

        # Compute a map of nodes, in the form: {node_name: Node}
        self.nodes = {node.node_name: node for node in nodes}


class Dialogue:
    """A state machine encapsulating a DialogueData instance."""

    def __init__(self, data: DialogueData):
        self.data = data

        self.current_node = data.nodes[START_NODE_NAME]
