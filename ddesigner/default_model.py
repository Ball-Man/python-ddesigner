"""Default model implementation for the current DD version."""
from ddesigner.model import *

from dataclasses import *

# Dictionary mapping type names to actual type classes
NODE_TYPE_MAP = {
    "start": SimpleNode
}
