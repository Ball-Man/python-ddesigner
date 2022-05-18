"""The main model definitions."""
import enum
from dataclasses import *
from typing import Iterable, Mapping, ClassVar, Any
from abc import abstractmethod, ABC
from collections import ChainMap


START_NODE_NAME = 'START'


class VariableType(enum.Enum):
    """Supported variable types."""
    STRING = 0
    INTEGER = 1
    BOOLEAN = 2


class NodeError(Exception):
    """Custom exception for faulty Node usage."""
    pass


class Blocking(enum.Enum):
    NON_BLOCKING = 0
    BLOCKING = 1


@dataclass
class Node(ABC):
    """A dialogue designer node."""
    node_name: str
    node_type: str
    title: str

    parent: ClassVar = None
    blocking: ClassVar = Blocking.NON_BLOCKING

    def get_next(self, variables: Mapping = {}, *args, **kwargs):
        """Get next node.

        Internally, self._compute is called (each time!).

        None is returned if there is currently no next node to go to.

        Any additional arguments (args, kwargs) will be passed to the
        _compute method.
        """
        if self.parent is None:
            raise NodeError(
                'Parent not set. This node is not part of a DialogueData.')

        # Compute
        next_ = self._compute(variables, *args, **kwargs)

        # If the value is None, return it otherwise return the next node
        return next_ and self.parent.nodes[next_]

    @abstractmethod
    def _compute(self, variables: Mapping, *args, **kwargs) -> str:
        """Make internal computation and return the next node's name.

        Override this method in subclasses to define custom behaviour
        for a Node.

        At the time of the call, it is safe to assume that self.parent
        is not None.

        If there is not next node to go to, return None.

        Additional arguments (args, kwargs) are passed from the get_next
        method.
        """
        pass


@dataclass
class SimpleNode(Node):
    """Basic node having a "next" field."""
    next: str = None

    def _compute(self, variables: Mapping) -> str:
        """Basic behaviour, return next node's name."""
        return self.next


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
    global_variables: Mapping[str, Any] = {}

    def __init__(self, data: DialogueData):
        self.data = data

        self.current_node = data.start_node
        self.variables = ChainMap({}, data.variables, self.global_variables)

    def __getitem__(self, index):
        """Access a local variable."""
        return self.variables[index]

    def __setitem__(self, index, value):
        """Set a local variable."""
        self.variables[index] = value

    def next(self, *args, **kwargs):
        """Update internal state to the next node and return it.

        If the next node is None, the state will not be updated.

        Any additional arguments (args, kwargs) will be passed to
        the node's get_next(...) method.
        """
        next_ = self.current_node.get_next(self.variables, *args, **kwargs)
        self.current_node = next_ or self.current_node

        return next_

    def next_iter(self, *args, **kwargs):
        """Update internal state to the next blocking node.

        All the non-blocking nodes found will be computed but
        immediately skipped. The first blocking node found will stop
        the iteration and return its value. The iteration will also
        stop if None is found (end of a branch).

        Nodes' blocking property can be changed via the class field
        Node.blocking (possible values come from the Blocking enum).

        Any additional arguments (args, kwargs) will be passed to
        the first computed node (to Node.get_next(...).
        Subsequent non-blocking nodes will receive no arguments.
        """
        node = self.next(*args, **kwargs)
        while node is not None and node.blocking == Blocking.NON_BLOCKING:
            node = self.next()

        return node
