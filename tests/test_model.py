from context import ddesigner
from ddesigner.model import *

import pytest


@pytest.fixture
def simple_node_data():
    arr = [SimpleNode("START", "", "", "2"), SimpleNode("2", "", "", "3"),
           SimpleNode("3", "", "", None)]

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
