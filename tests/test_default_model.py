import os.path as op

from collections import Counter

from context import ddesigner
from ddesigner.default_model import *
from ddesigner.model import *

import pytest

FILES_PATH = op.join(op.dirname(__file__), 'files')


@pytest.fixture
def default_model_data1():
    arr = (SetVariableNode('START', '', '', '1', 'var1', 1),
           SetVariableNode('1', '', '', '2', 'var1', 1,
                           operation_type=OperationType.ADD.value),
           SetVariableNode('2', '', '', '3', 'var1', 1,
                           operation_type=OperationType.SUBTRACT.value),
           SetVariableNode('3', '', '', '4', 'bool_ok', toggle=True),
           ShowMessageNode('4', '', '', None,
                           text={'ENG': 'hello world ${var1}',
                                 'ESP': 'hola mundo'},
                           choices=[{'is_condition': False, 'next': '5'}]),
           SimpleNode('5', '', '', None))

    return DialogueData(arr, {'bool_ok': True})


@pytest.fixture
def default_model_data2():
    arr = (ExecuteNode('START', '', '', '1', 'value'),
           WaitNode('1', '', '', '2', 10),
           ConditionBranchNode('2', '', '', 'var1 > 10',
                               {'True': '3', 'False': '4'}),
           ShowMessageNode('3', '', '', None))

    return DialogueData(arr, {'var1': 11})


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


@pytest.fixture
def chain1_file():
    file = open(op.join(FILES_PATH, 'chain1.json'))
    yield file

    file.close()


def test_show_message_node(default_model_data1):
    dial = Dialogue(default_model_data1)

    node = dial.next_iter()
    assert node.text['ENG'] == 'hello world ${var1}'

    variables = {'var1': 42}
    assert node.parse_text(variables=variables) == 'hello world 42'
    assert node.parse_text(
        language='ITA', variables=variables) == 'hello world 42'
    assert node.parse_text(
        language='ESP', variables=variables) == 'hola mundo'
    assert dial.next(0).node_name == '5'


def test_apply_parsers():
    def parser1(string, language, variables):
        return f'{string} {language} {variables}'

    def parser2(string, language, variables):
        return string + "1"

    result = apply_parsers([parser1, parser2], 'test', 'ENG', {})

    assert result == 'test ENG {}1'


def test_variables_text_parser():
    string = '${var1} this is a test ${var2}'

    result_novar = variables_text_parser(string, '', {})
    assert result_novar == 'var1 this is a test var2'

    result_onevar = variables_text_parser(string, '', {'var1': 42})
    assert result_onevar == '42 this is a test var2'

    result_fullvar = variables_text_parser(
        string, '', {'var1': 42, 'var2': 'ok', 'var3': 'useless'})
    assert result_fullvar == '42 this is a test ok'


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


class TestExecuteNode:

    @pytest.fixture
    def reset_execute(self):
        yield
        ExecuteNode.subscribers.clear()

    def test_subscriber_decorator(self, reset_execute):
        @ExecuteNode.subscriber
        def foo(command, variables):
            pass

        assert ExecuteNode.subscribers == {foo}

    def test_subscribe(self, reset_execute):
        def moo(command, variables):
            pass

        ExecuteNode.subscribe(moo)
        with pytest.raises(TypeError):
            ExecuteNode.subscribe(2)

        assert ExecuteNode.subscribers == {moo}

    def test_unsubscribe(self, reset_execute):
        def koo(command, variables):
            pass

        ExecuteNode.subscribe(koo)
        ExecuteNode.unsubscribe(koo)

        assert ExecuteNode.subscribers == set()

    def test_clear_subscribers(self):
        def doo(command, variables):
            pass

        def soo(command, variables):
            pass

        ExecuteNode.subscribe(doo)
        ExecuteNode.subscribe(soo)
        ExecuteNode.clear_subscribers()

        assert ExecuteNode.subscribers == set()

    def test_trigger_subscribers(self, default_model_data2, reset_execute):
        dial = Dialogue(default_model_data2)

        output = ''

        @ExecuteNode.subscriber
        def foo(command, variables):
            nonlocal output
            output = command

        dial.next_iter()

        assert output == 'value'


def test_condition_branch_node(default_model_data2):
    dial = Dialogue(default_model_data2)

    dial.next_iter()
    print(dial.next_iter())


def test_default_from_json(chain1_file):
    json = chain1_file.read()
    dial = Dialogue(ddesigner.from_json(json))

    while dial.next_iter() is not None:
        pass

    assert dial['var1'] == 0


def test_default_from_file(chain1_file):
    dial = Dialogue(ddesigner.from_file(chain1_file))

    while dial.next_iter() is not None:
        pass

    assert dial['var1'] == 0
