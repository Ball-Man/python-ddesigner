from context import ddesigner
from ddesigner.model import *

import pytest


class SimpleBlockingNode(SimpleNode):
    blocking = Blocking.BLOCKING


class ToggleNode(Node):
    current_val = None

    def _compute(self, variables, val: bool):
        self.current_val = val

        return None


@pytest.fixture
def simple_node_data():
    arr = [SimpleNode("START", "", "", "2"), SimpleNode("2", "", "", "3"),
           SimpleNode("3", "", "", None)]

    return DialogueData(arr, {'var1': 'default', 'var2': 'default'})


@pytest.fixture
def simple_blocked_data():
    arr = [SimpleNode("START", "", "", "2"), SimpleNode("2", "", "", "3"),
           SimpleBlockingNode("3", "", "", "4"), SimpleNode("4", "", "", "5"),
           SimpleNode("5", "", "", None)]

    return DialogueData(arr, {'var1': 'default', 'var2': 'default'})


def test_simple_node(simple_node_data):
    start_node = simple_node_data.start_node

    assert start_node.get_next().node_name == "2"
    assert start_node.get_next().get_next().get_next() is None


class TestDialogue:

    def test_variables(self, simple_node_data):
        dial = Dialogue(simple_node_data)

        dial['var1'] = 'not default'

        assert dial['var1'] == 'not default'
        assert dial.data.variables['var1'] == 'default'
        assert dial['var2'] == 'default'

    def test_next(self, simple_node_data):
        dial = Dialogue(simple_node_data)

        dial.next()
        assert dial.current_node.node_name == "2"

        dial.next()
        assert dial.current_node.node_name == "3"

        assert dial.next() is None
        assert dial.current_node.node_name == "3"

    def test_next_iter(self, simple_node_data):
        dial = Dialogue(simple_node_data)

        assert dial.next_iter() is None

    def test_arguments_pass(self):
        dial = Dialogue(DialogueData([ToggleNode("START", "", "")], {}))

        dial.next_iter(True)
        assert dial.current_node.current_val
