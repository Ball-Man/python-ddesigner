"""The main model definitions."""
import enum
from dataclasses import *
from typing import Iterable, Mapping, Tuple, Union
from abc import abstractmethod, ABC
from collections import ChainMap


START_NODE_NAME = "START"


class VariableType(enum.Enum):
    """Supported variable types."""
    STRING = 0
    INTEGER = 1
    BOOLEAN = 2


class NodeError(Exception):
    """Custom exception for faulty Node usage."""
    pass


class NextNode(enum.Enum):
    """Special value for next node."""
    NOT_INITIALIZED = 0
    NONE = 1


@dataclass
class Node(ABC):
    """A dialogue designer node."""
    node_name: str
    node_type: str
    title: str

    parent = None

    def __post_init__(self):
        self._next: str = None    # Cache

    def get_next(self, variables: Mapping = {}):
        """Get next node.

        Internally, self._compute is called. Multiple calls will
        return the same cached value (hence _compute will not be called)
        unless the cached value is None.

        If the cached value is None when this method is invoked,
        the next node will be recalculated using self._compute.

        None is returned if there is currently no next node to go to.
        """
        if self.parent is None:
            raise NodeError(
                "Parent not set. This node is not part of a DialogueData.")

        # If not initialized, compute
        if self._next is None:
            self._next = self._compute(variables)

        # If the value is still None, return it
        if self._next is None:
            return None

        return self.parent.nodes[self._next]

    @abstractmethod
    def _compute(self, variables: Mapping) -> str:
        """Make internal computation and return the next node's name.

        Override this method in subclasses to define custom behaviour
        for a Node.

        The method is used by self.get_next to determine the name of the
        next node. The returned value will be cached, hence this method
        will ideally be called only once.

        At the time of the call, it is safe to assume that self.parent
        is not None.

        If there is not next node to go to, return None.
        """
        pass


@dataclass
class SimpleNode(Node):
    """Basic node having a "next" field."""
    next: str

    def _compute(self, variables: Mapping) -> str:
        """Basic behaviour, return next node's name."""
        return self.next


# Dictionary mapping type names to actual type classes
NODE_TYPE_MAP = {
    "start": SimpleNode
}


class DialogueData:
    """Container of Nodes.

    Contains an organized set of Nodes and a dictionary of variables.
    """

    def __init__(self, nodes: Iterable[Node], variables: dict):
        self.variables = variables

        # Compute a map of nodes, in the form: {node_name: Node}
        self.nodes = {node.node_name: node for node in nodes}

        # Link nodes to this instance
        for node in nodes:
            node.parent = self

    @property
    def start_node(self):
        return self.nodes[START_NODE_NAME]


class Dialogue:
    """A state machine encapsulating a DialogueData instance.

    Internal state keeps track of the current node (self.current_node)
    and variables (accessible as a mapping).

    Variables are looked up using a ChainMap, meaning that the
    contained DialogueData variables are kept constant. Do not manually
    modify DialogueData variables.
    """

    def __init__(self, data: DialogueData):
        self.data = data

        self.current_node = data.start_node
        self.variables = ChainMap({}, data.variables)

    def __getitem__(self, index):
        """Access a local variable."""
        return self.variables[index]

    def __setitem__(self, index, value):
        """Set a local variable."""
        self.variables[index] = value

    def next(self):
        """Update internal state to the next node and return it.

        If the next node is None, the state will not be updated.
        """
        next_ = self.current_node.get_next(self.variables)
        self.current_node = next_ or self.current_node

        return next_
