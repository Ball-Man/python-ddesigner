"""Default model implementation for the current DD version."""
from dataclasses import *
from typing import ClassVar, Any, Callable
import random
import enum

from ddesigner.model import *


# Dictionary mapping type names to actual type classes
NODE_TYPE_MAP = {
    "start": SimpleNode
}


@dataclass
class ShowMessageNode(SimpleNode):
    """Node used for the "show_message" type.

    It's a blocking node, with optional support to multiple conditioned
    choices (TODO).
    """
    character: list = field(default_factory=lambda: ["", 0])
    file: str = ""
    is_box: bool = False
    object_path: str = ""
    slide_camera: bool = True
    speaker_type: int = 0
    text: dict = field(default_factory=lambda: {"ENG": ""})
    choices: list = field(default_factory=lambda: [])

    blocking: ClassVar = Blocking.BLOCKING

    def _compute(self, variables, choice: int = None):
        """Simply go to next. TODO: support choices."""
        return super()._compute(variables)


class RandomNode(Node):
    """Abstract class for a Node based on a random generation.

    The random generator is kept in the RandomNode.rand attribute.
    """
    rand = random


@dataclass
class RandomBranchNode(RandomNode):
    """Node used for the "random_branch" type.

    A non-blocking node that chooses randomly between a number of
    branches.
    """
    branches: dict = field(default_factory=lambda: {'1': None})
    possibilities: int = 2

    def _compute(self, variables):
        """Choose randomly between the given branches."""
        return self.rand.choice(
            [branch for key, branch in self.branches.items()
             if int(key) <= self.possibilities])


@dataclass
class ChanceBranchNode(RandomNode):
    """Node used for the "chance_branch" type.

    A non-blocking node that chooses between two nodes (with different
    weights).
    """
    branches: dict = field(default_factory=lambda: {'1': None, '2': None})
    chance_1: int = 0
    chance_2: int = 100

    def _compute(self, variables):
        """Choose one of the two branches."""
        chance_tup = self.chance_1, self.chance_2
        branches_tup = self.branches['1'], self.branches['2']
        return self.rand.choices(branches_tup, weights=chance_tup)[0]


class OperationType(enum.Enum):
    """Supported operation types for SetVariableNodes."""
    SET = "SET"
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"


@dataclass
class SetVariableNode(SimpleNode):
    """Node used for the "set_local_variable" type.

    A non-blocking node that sets a local variable. Supported features:
    Set a value, increase/decrease a value, toggle a boolean.
    """
    var_name: str = ""
    value: Any = None
    toggle: bool = None
    operation_type: str = "SET"

    def _compute(self, variables):
        """Operate on the variables and return the next node."""
        # Check if it's a toggle
        if self.toggle:
            value = not variables[self.var_name]
        else:
            value = self.value

        # Calculate relative operations
        if self.operation_type == OperationType.ADD.value:
            value += variables[self.var_name]
        elif self.operation_type == OperationType.SUBTRACT.value:
            value = variables[self.var_name] - value

        variables[self.var_name] = value

        return super()._compute(variables)


@dataclass
class WaitNode(SimpleNode):
    """Node used for the "wait" type.

    A blocking node that carries a time value.
    """
    time: float = 0

    blocking: ClassVar = Blocking.BLOCKING


@dataclass
class ExecuteNode(SimpleNode):
    """Node used for the "execute" type.

    A non-blocking node.

    A subscribable class. Subscribers will be called and will receive
    the node's command (self.text) and the current variables state
    (a mapping). Any subscribers' return value will be ignored.
    Subscribers shall execute do whatever they want with the given data
    (eg. in gamedev cases: play a specific sound).
    NOTE: subscribers will be shared between all the instances of this
          class (for practical reasons, instance wide subscribers would
          be hard to manage in a real case scenario).

    No duplicate subscibers are allowed.

    Subscribe using ExecuteNode.subscribe method, or the
    ExecuteNode.subscriber decorator, like so:

    @ExecuteNode.subscriber
    def sub(command, variables):
        # ...

    The next node is given by the self.next attribute.
    """
    text: str = ""

    subscribers: ClassVar[set] = set()

    def _compute(self, variables):
        self._trigger_subscribers(variables)

        return super()._compute(variables)

    @classmethod
    def subscriber(cls, fun: Callable):
        """Decorator for subscribers.

        Decorate a function to automatically make it a subscruber.
        """
        cls.subscribe(fun)

        return fun

    @classmethod
    def subscribe(cls, fun: Callable):
        """Add a subscriber."""
        if not callable(fun):
            raise TypeError(f'{fun} is not callable')

        cls.subscribers.add(fun)

    @classmethod
    def unsubscribe(cls, fun):
        """Remove a subscriber."""
        cls.subscribers.remove(fun)

    @classmethod
    def clear_subscribers(cls):
        """Remove all subscribers."""
        cls.subscribers.clear()
