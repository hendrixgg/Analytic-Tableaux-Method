from dataclasses import dataclass, field
from typing import List, Tuple, Literal, Callable

from tableaux_prover.formula_symbols import *


@dataclass
class PropositionalLogicFormula:
    symbol: SYMBOL_TYPE = field(default_factory=lambda: SYMBOL_TYPE.UNKNOWN)
    children: list['PropositionalLogicFormula'] = field(default_factory=list)
    id: str | None = None

    def __post_init__(self):
        if self.symbol in CONNECTIVES:
            # assert self.id is None, "connective should not have an id"
            if self.symbol == SYMBOL_TYPE.NEGATION:
                assert len(
                    self.children) == 1, "negation should have one child"
            else:
                assert len(
                    self.children) == 2, "connective should have two children"
        elif self.symbol == SYMBOL_TYPE.PROPOSITION:
            assert self.id is not None, "atomic proposition should have an id"
            assert len(
                self.children) == 0, "atomic proposition should have no children"
        elif self.symbol == SYMBOL_TYPE.UNKNOWN:
            assert self.id is None, "unknown symbol should not have an id"
            assert len(
                self.children) == 0, "unknown symbol should have no children"
        else:
            print(self.symbol, self.id, self.children)
            assert False, "invalid symbol"

    def __eq__(self, other):
        return isinstance(other, PropositionalLogicFormula) and self.symbol == other.symbol and self.children == other.children and self.id == other.id

    def __hash__(self):
        return hash(stringify_formula(self, "prefix")[1])

    def __repr__(self):
        return stringify_formula(self, "prefix")[1]


def stringify_formula(formula: PropositionalLogicFormula, format: Literal["prefix", "infix", "postfix"]) -> Tuple[bool, str]:
    """
    Converts the formula from a list of integers to a string of symbols.

    Args:
    formula (list): The formula to convert.

    Returns:
    success: True if the formula was converted successfully, False otherwise.

    str: The formula as a string, if an error parsing occurred, the empty string `""` is returned.
    """
    result_formula = ""
    success = False
    # recursively build the string
    if formula.symbol == SYMBOL_TYPE.PROPOSITION:
        result_formula = formula.id
        success = True
    elif formula.symbol == SYMBOL_TYPE.NEGATION:
        success_child, child_formula = stringify_formula(
            formula.children[0], format)
        if success_child:
            if format == "prefix":
                result_formula = f"{NEGATION.string_representations[NEGATION.default_representation]}{child_formula}"
            elif format == "infix":
                result_formula = f"({NEGATION.string_representations[NEGATION.default_representation]}{child_formula})"
            elif format == "postfix":
                result_formula = f"{child_formula}{NEGATION.string_representations[NEGATION.default_representation]}"
            success = True
        else:
            result_formula = ""
            success = False
    elif formula.symbol in CONNECTIVES:
        success_child1, child_formula1 = stringify_formula(
            formula.children[0], format)
        success_child2, child_formula2 = stringify_formula(
            formula.children[1], format)
        if success_child1 and success_child2:
            symbol_representation = default_symbol_represenation(
                formula.symbol)
            if format == "prefix":
                result_formula = f"{symbol_representation} {child_formula1} {child_formula2}"
            elif format == "infix":
                result_formula = f"({child_formula1} {symbol_representation} {child_formula2})"
            elif format == "postfix":
                result_formula = f"{child_formula1} {child_formula2} {symbol_representation}"
            else:
                result_formula = ""
                success = False
            success = True
    else:
        result_formula = ""
        success = False

    return (success, result_formula)


def parse_infix_formula(formula: str) -> Tuple[bool, PropositionalLogicFormula]:
    """
    Parses the input formula, converts the string of symbols to a PropositionalLogicFormula.
    There is no notion of operator precedence in this parser, so all operators are treated as having the same precedence.

    Args:
    formula (str): The formula to convert.

    Returns:
    success: True if the formula was parsed successfully, False otherwise.

    result: PropositionalLogicFormula object
    """
    result_formula = PropositionalLogicFormula()
    success = False
    # first convert the formula to postfix notation
    # then convert the postfix notation to a PropositionalLogicFormula object

    operator_stack = []
    postfix_formula = []
    i = 0
    while i < len(formula):
        # exactly one of these must be true. Or there's a space. Or it's an invalid character.
        left_parenthesis_match = LEFT_PARENTHESIS.parse_symbol(formula[i:])
        right_parenthesis_match = RIGHT_PARENTHESIS.parse_symbol(formula[i:])
        proposition_match = PROPOSITION.parse_symbol(formula[i:])
        negation_match = NEGATION.parse_symbol(formula[i:])
        conjunction_match = CONJUNCTION.parse_symbol(formula[i:])
        disjunction_match = DISJUNCTION.parse_symbol(formula[i:])
        implication_match = IMPLICATION.parse_symbol(formula[i:])
        # biconditional_match = BICONDITIONAL.parse_symbol(formula[i])
        # check parenthesis
        if left_parenthesis_match:
            operator_stack.append(left_parenthesis_match)
            i += len(left_parenthesis_match)
        elif right_parenthesis_match:
            left_parenthesis_match = parenthesis_match(right_parenthesis_match)
            while operator_stack and operator_stack[-1] not in left_parenthesis_strings:
                postfix_formula.append(operator_stack.pop())
            # check if the parenthesis match, if not, return an error
            if not operator_stack or operator_stack[-1] != left_parenthesis_match:
                return (False, result_formula)
            else:  # operator_stack[-1] == left_parenthesis_match
                operator_stack.pop()
            i += len(right_parenthesis_match)
        # check proposition
        elif proposition_match:
            postfix_formula.append(proposition_match)
            i += len(proposition_match)
        # check operator
        elif negation_match:
            operator_stack.append(negation_match)
            i += len(negation_match)
        elif conjunction_match:
            operator_stack.append(conjunction_match)
            i += len(conjunction_match)
        elif disjunction_match:
            operator_stack.append(disjunction_match)
            i += len(disjunction_match)
        elif implication_match:
            operator_stack.append(implication_match)
            i += len(implication_match)
        # elif biconditional_match:
        #     operator_stack.append(biconditional_match)
        elif formula[i] == " ":
            i += 1
        else:
            # invalid formula
            return (False, result_formula)
    while operator_stack:
        postfix_formula.append(operator_stack.pop())

    # convert postfix_formula to PropositionalLogicFormula object
    stack = []
    for symbol in postfix_formula:
        # exactly one of these must be true.
        proposition_match = PROPOSITION.parse_symbol(symbol)
        negation_match = NEGATION.parse_symbol(symbol)
        conjunction_match = CONJUNCTION.parse_symbol(symbol)
        disjunction_match = DISJUNCTION.parse_symbol(symbol)
        implication_match = IMPLICATION.parse_symbol(symbol)
        # biconditional_match = BICONDITIONAL.parse_symbol(symbol)
        if proposition_match:
            formula = PropositionalLogicFormula(
                symbol=SYMBOL_TYPE.PROPOSITION, children=[], id=proposition_match)
            stack.append(formula)
        elif negation_match:
            if len(stack) < 1:
                return (False, result_formula)
            formula = PropositionalLogicFormula(
                symbol=SYMBOL_TYPE.NEGATION, children=[stack.pop()])
            stack.append(formula)
        elif conjunction_match:
            if len(stack) < 2:
                return (False, result_formula)
            # reverse order of children since we are popping from the stack
            child2 = stack.pop()
            child1 = stack.pop()
            formula = PropositionalLogicFormula(
                symbol=SYMBOL_TYPE.CONJUNCTION, children=[child1, child2])
            stack.append(formula)
        elif disjunction_match:
            if len(stack) < 2:
                return (False, result_formula)
            child2 = stack.pop()
            child1 = stack.pop()
            formula = PropositionalLogicFormula(
                symbol=SYMBOL_TYPE.DISJUNCTION, children=[child1, child2])
            stack.append(formula)
        elif implication_match:
            if len(stack) < 2:
                return (False, result_formula)
            child2 = stack.pop()
            child1 = stack.pop()
            formula = PropositionalLogicFormula(
                symbol=SYMBOL_TYPE.IMPLICATION, children=[child1, child2])
            stack.append(formula)
        else:
            return (False, result_formula)

    if len(stack) != 1:
        success = False
    else:
        result_formula = stack.pop()
        success = True

    return (success, result_formula)

# TODO: create test cases for the parser.
