"""Default model implementation for the current DD version."""
from ddesigner.model import *

from dataclasses import *
from typing import ClassVar

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
        super()._compute(variables)
