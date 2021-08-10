from context import ddesigner
from ddesigner.model import *

import pytest


@pytest.fixture
def simple_node_data():
    arr = [SimpleNode("START", "", "", "2"), SimpleNode("2", "", "", "3"),
           SimpleNode("3", "", "", None)]

    return DialogueData(arr, {})


def test_simple_node(simple_node_data):
    start_node = simple_node_data.start_node

    assert start_node.get_next() == "2"
    assert start_node.get_next().get_next().get_next() is None
