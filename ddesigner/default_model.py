"""Default model implementation for the current DD version."""
from dataclasses import *
from typing import ClassVar
import random

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


@dataclass
class RandomBranchNode(Node):
    """Node used for the "random_branch" type.

    A non-blocking node that chooses randomly between a number of
    branches.
    """
    branches: dict = field(default_factory=lambda: {})
    possibilities: int = 2

    cache: ClassVar = False
    rand: ClassVar = random

    def _compute(self, variables):
        """Choose randomly between the given branches."""
        return self.rand.choice(
            [branch for key, branch in self.branches.items()
             if int(key) <= self.possibilities])
