from context import ddesigner
from ddesigner.conditional import *

import pytest


@pytest.fixture
def variables():
    return {'var1': 10, 'var2': False, 'var3': 120, 'var4': 'hello'}


def test_basic_algebra():
    assert arithm_expression_evaluate('2 + 2', {}) == 4
    assert arithm_expression_evaluate('2 - 2', {}) == 0
    assert arithm_expression_evaluate('2 * 3', {}) == 6
    assert arithm_expression_evaluate('2 * 3 + 2', {}) == 8
    assert arithm_expression_evaluate('2 * (3 + 2)', {}) == 10
    assert arithm_expression_evaluate('2 * -(3 + 2)', {}) == -10
    assert arithm_expression_evaluate('2 // 3 + 2', {}) == 2
    assert arithm_expression_evaluate('10 / 10 + 1', {}) == 2


def test_booeal_algebra():
    assert arithm_expression_evaluate('True or False', {})
    assert arithm_expression_evaluate('True || False', {})
    assert not arithm_expression_evaluate('False or False', {})
    assert not arithm_expression_evaluate('True and False', {})
    assert not arithm_expression_evaluate('True && False', {})
    assert arithm_expression_evaluate('True or False && False', {})
    assert not arithm_expression_evaluate('(True or False) && False', {})
    assert not arithm_expression_evaluate('not True', {})
    assert not arithm_expression_evaluate('!True', {})
    assert not arithm_expression_evaluate('not True or False', {})


def test_comparisons():
    assert arithm_expression_evaluate('1 == 1', {})
    assert arithm_expression_evaluate('1 != 2', {})
    assert arithm_expression_evaluate('1 + 1 == 2', {})
    assert arithm_expression_evaluate('10 > 0', {})
    assert arithm_expression_evaluate('0 > -1', {})
    assert arithm_expression_evaluate('2 > -1 > -100', {})
    assert not arithm_expression_evaluate('2 > -1 > 100', {})
    assert not arithm_expression_evaluate('-1 > 2', {})
    assert arithm_expression_evaluate('-1 >= -1', {})
    assert arithm_expression_evaluate('-1 <= -1', {})


def test_variables(variables):
    assert arithm_expression_evaluate('var1 + 2', variables) == 12
    assert arithm_expression_evaluate('var3 / var1', variables) == 12
    assert arithm_expression_evaluate('!var2', variables)
    assert arithm_expression_evaluate('(var3 + (var1 - 1) * 2) + 10',
                                      variables) == 148
    assert arithm_expression_evaluate('var2 or 3 > 2', variables)
    assert not arithm_expression_evaluate('var2 or var1 > var3', variables)


def test_strings(variables):
    assert arithm_expression_evaluate('var4 == "hello"', variables)
    assert arithm_expression_evaluate('var4 != "hell"', variables)
    assert arithm_expression_evaluate('var4 + "o" == "helloo"', variables)
