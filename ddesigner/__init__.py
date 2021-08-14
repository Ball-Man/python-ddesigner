import json
from typing import TextIO

from . import model
from . import default_model
from . import conditional

from ddesigner.model import *


class UnsupportedNodeError(Exception):
    """Custom error for unsopported node types."""
    pass


def from_json(json_str, node_map=default_model.NODE_TYPE_MAP) -> DialogueData:
    """Import and return data from json.

    How the json is interpreted and the exact behaviour of the nodes
    highly depends on the given node_map.
    The default node_map will provide a basic implementation of all
    the nodes from the current DialogueDesigner version.

    NOTE: the 'repeat' nodes are not supported by the default mapping
    due to how the library internally works. If encountered,
    an UnsupportedNodeError will be rised.
    """
    ddesginer_dict = json.loads(json_str)[0]

    variables = {key: val['value'] for key, val
                 in ddesginer_dict['variables'].items()}
    nodes = []

    for node_dict in ddesginer_dict['nodes']:
        if node_dict['node_type'] not in node_map:
            raise UnsupportedNodeError(
                f"Unsupported node type {node_dict['node_type']} "
                "according to the used node type map")

        nodes.append(node_map[node_dict['node_type']](**node_dict))

    return DialogueData(nodes, variables)


def from_file(file: TextIO,
              node_map=default_model.NODE_TYPE_MAP) -> DialogueData:
    """Import and return data from file.

    The file content is assumed to be json.

    How the json is interpreted and the exact behaviour of the nodes
    highly depends on the given node_map.
    The default node_map will provide a basic implementation of all
    the nodes from the current DialogueDesigner version.

    NOTE: the 'repeat' nodes are not supported by the default mapping
    due to how the library internally works. If encountered,
    an UnsupportedNodeError will be rised.
    """
    return from_json(file.read(), node_map)
