from context import ddesigner
from ddesigner.default_model import *
from ddesigner.model import *

import pytest


@pytest.fixture
def default_model_data1():
    arr = (SimpleNode('START', '', '', '1'), SimpleNode('1', '', '', '2'),
           ShowMessageNode('2', '', '', '3', text={'ENG': 'hello world'}),
           SimpleNode('3', '', '', None))

    return DialogueData(arr, {})


def test_show_message_node(default_model_data1):
    dial = Dialogue(default_model_data1)

    assert dial.next_iter().text['ENG'] == 'hello world'
    assert dial.next_iter() is None
