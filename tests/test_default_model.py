from collections import Counter

from context import ddesigner
from ddesigner.default_model import *
from ddesigner.model import *

import pytest


@pytest.fixture
def default_model_data1():
    arr = (SetVariableNode('START', '', '', '1', 'var1', 1),
           SetVariableNode('1', '', '', '2', 'var1', 1,
                           operation_type=OperationType.ADD.value),
           SetVariableNode('2', '', '', '3', 'var1', 1,
                           operation_type=OperationType.SUBTRACT.value),
           SetVariableNode('3', '', '', '4', 'bool_ok', toggle=True),
           ShowMessageNode('4', '', '', '5', text={'ENG': 'hello world'}),
           SimpleNode('5', '', '', None))

    return DialogueData(arr, {'bool_ok': True})


@pytest.fixture
def default_model_data2():
    arr = SimpleNode('START', '', '', '1'), WaitNode('1', '', '', None, 10)

    return DialogueData(arr, {})


@pytest.fixture
def random_data_model1():
    arr = (SimpleNode('START', '', '', '1'),
           RandomBranchNode('1', '', '', possibilities=2,
                            branches={'1': '2', '2': '3'}),
           ShowMessageNode('2', '', '', '1', text={'ENG': 'branch1'}),
           ShowMessageNode('3', '', '', '1', text={'ENG': 'branch2'})
    )

    return DialogueData(arr, {})


@pytest.fixture
def random_data_model2():
    arr = (SimpleNode('START', '', '', '1'),
           ChanceBranchNode('1', '', '', chance_1=90, chance_2=10,
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


def test_random_branch_node(random_data_model1, rand):
    dial = Dialogue(random_data_model1)

    RandomBranchNode.rand = rand

    reached = Counter()

    for x in range(100):
        reached[dial.next_iter().text['ENG']] += 1

    assert reached['branch1'] > 0
    assert reached['branch2'] > 0


def test_chance_branch_node(random_data_model2, rand):
    dial = Dialogue(random_data_model2)

    ChanceBranchNode.rand = rand

    reached = Counter()

    for x in range(100):
        reached[dial.next_iter().text['ENG']] += 1

    assert reached['branch1'] > reached['branch2'] * 9


def test_set_variable_node(default_model_data1):
    dial = Dialogue(default_model_data1)

    dial.next()
    assert dial['var1'] == 1

    dial.next()
    assert dial['var1'] == 2

    dial.next()
    assert dial['var1'] == 1

    dial.next()
    assert not dial['bool_ok']


def test_wait_node(default_model_data2):
    dial = Dialogue(default_model_data2)

    assert dial.next_iter().time == 10
