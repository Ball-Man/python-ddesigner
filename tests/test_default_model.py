from collections import Counter

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


@pytest.fixture
def random_data_model():
    arr = (SimpleNode('START', '', '', '1'),
           RandomBranchNode('1', '', '', possibilities=2,
                            branches={'1': '2', '2': '3'}),
           ShowMessageNode('2', '', '', '1', text={'ENG': 'branch1'}),
           ShowMessageNode('3', '', '', '1', text={'ENG': 'branch2'})
    )

    return DialogueData(arr, {})


@pytest.fixture
def rand():
    return random.Random(10)


def test_show_message_node(default_model_data1):
    dial = Dialogue(default_model_data1)

    assert dial.next_iter().text['ENG'] == 'hello world'
    assert dial.next() is not None
    assert dial.next_iter() is None


def test_random_branch_node(random_data_model, rand):
    dial = Dialogue(random_data_model)

    RandomBranchNode.rand = rand

    reached = Counter()

    for x in range(100):
        reached[dial.next_iter().text['ENG']] += 1

    assert reached['branch1'] > 0
    assert reached['branch2'] > 0
