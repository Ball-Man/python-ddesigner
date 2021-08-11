"""Module containing the logic for an arithmetic parser.

Lark is used as a parser generator.
"""
from typing import Mapping
import operator

import lark

# Default syntax for arithmetic expressions
ARITHM_EXPRESSIONS_SYNTAX = """
?start: or

?or: and
    | or "||" and -> or_
    | or "or" and -> or_

?and: comparison
    | and "&&" comparison -> and_
    | and "and" comparison -> and_

?comparison: sum
    | comparison "<" sum -> lt
    | comparison ">" sum -> gt
    | comparison "<=" sum -> lte
    | comparison ">=" sum -> gte
    | comparison "==" sum -> eq
    | comparison "!=" sum -> neq

?sum: product
    | sum "+" product   -> add
    | sum "-" product   -> sub

?product: not
    | product "*" not  -> mul
    | product "/" not  -> div
    | product "//" not -> floordiv

?not: atom
    | "!"atom           -> not_
    | "not" atom        -> not_

?atom: NUMBER           -> number
     | "-" atom         -> neg
     | "False"          -> false
     | "True"           -> true
     | NAME             -> var
     | STRING           -> string
     | "(" or ")"

%import common.ESCAPED_STRING -> STRING
%import common.CNAME -> NAME
%import common.NUMBER
%import common.WS_INLINE

%ignore WS_INLINE
"""


@lark.v_args(inline=True)
class ArithmExpressionTransformer(lark.Transformer):
    """Transformer used to calculate the result of arithmetic exp."""
    add = operator.add
    sub = operator.sub
    mul = operator.mul
    div = operator.truediv
    floordiv = operator.floordiv
    neg = operator.neg
    lt = operator.lt
    gt = operator.gt
    lte = operator.le
    gte = operator.ge
    eq = operator.eq
    neq = operator.ne

    def __init__(self, variables):
        self.variables = variables

    def and_(self, x, y):
        """Boolean and.

        For simplicity, an easy implementation of boolean operators
        which will NOT provide shot circuiting.
        """
        return x and y

    def or_(self, x, y):
        """Boolean or.

        For simplicity, an easy implementation of boolean operators
        which will NOT provide shot circuiting.
        """
        return x or y

    not_ = operator.not_
    number = float

    def string(self, string: str):
        return string.strip('"')

    def true(self):
        return True

    def false(self):
        return False

    def var(self, name):
        return self.variables[name]


# Default parser for arithmetic expressions (using the default syntax)
ARITHM_EXPRESSIONS_PARSER = lark.Lark(ARITHM_EXPRESSIONS_SYNTAX)


def arithm_expression_evaluate(
    expression: str, variables: Mapping,
    parser: lark.Lark = ARITHM_EXPRESSIONS_PARSER,
        transformer: lark.Transformer = ArithmExpressionTransformer):
    """Return the value of the given expression.

    Free variable names will be calculated using the 'variables'
    mapping.
    """
    return transformer(variables).transform(parser.parse(expression))
