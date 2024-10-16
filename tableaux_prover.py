from dataclasses import dataclass, field
from typing import List, Tuple, Literal, Callable
from enum import Enum
from collections import defaultdict

# Define the symbols that will be used in the propositional logic formulas.


class SYMBOLS(Enum):
    PROPOSITION = 0
    NEGATION = 1
    CONJUNCTION = 2
    DISJUNCTION = 3
    IMPLICATION = 4
    LEFT_PARENTHESIS = 5
    RIGHT_PARENTHESIS = 6
    # BICONDITIONAL = 7
    UNKNOWN = 999
    WILDCARD = 1000

    def __eq__(self, other):
        return other is SYMBOLS and (self.value == other.value or self is SYMBOLS.WILDCARD or other is SYMBOLS.WILDCARD)


# Types of symbols: connectives, parantheses, atomic propositions
CONNECTIVES = [
    SYMBOLS.NEGATION,
    SYMBOLS.CONJUNCTION,
    SYMBOLS.DISJUNCTION,
    SYMBOLS.IMPLICATION,
]
PARENTHESES = [SYMBOLS.LEFT_PARENTHESIS, SYMBOLS.RIGHT_PARENTHESIS]


@dataclass
class Symbol:
    symbol_enum: SYMBOLS = SYMBOLS.UNKNOWN
    default_representation: int = 0
    string_representations: list = field(default_factory=list)
    parse_symbol: Callable[[str], bool] = lambda x: False

    def __eq__(self, other):
        return other is Symbol and self.symbol_enum == other.symbol_enum

    def __str__(self) -> str:
        return self.string_representations[self.default_representation]


# Could make this a regex pattern to allow for more than one letter symbols, this would be helpful so you don't have to type special characters.
atomic_proposition_strings = list(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
negation_strings = ["¬", "~", "!", "not"]
conjunction_strings = ["∧", "&", "/\\", "and"]
disjunction_strings = ["∨", "|", "\\/", "or"]
implication_strings = ["→", "->", ">>", "implies"]
# biconditional_strings = ["↔", "<->", "iff", "if and only if"]
left_parenthesis_strings = ["(", "[", "{"]
right_parenthesis_strings = [")", "]", "}"]


def any_prefix(s: str, prefixes: List[str]) -> bool:
    return any([s.startswith(prefix) for prefix in prefixes])


NEGATION = Symbol(
    symbol_enum=SYMBOLS.NEGATION,
    default_representation=0,
    string_representations=negation_strings,
    parse_symbol=lambda s: any_prefix(s, negation_strings),
)
CONJUNCTION = Symbol(
    symbol_enum=SYMBOLS.CONJUNCTION,
    default_representation=0,
    string_representations=conjunction_strings,
    parse_symbol=lambda s: any_prefix(s, conjunction_strings),
)
DISJUNCTION = Symbol(
    symbol_enum=SYMBOLS.DISJUNCTION,
    default_representation=0,
    string_representations=disjunction_strings,
    parse_symbol=lambda s: any_prefix(s, disjunction_strings),
)
IMPLICATION = Symbol(
    symbol_enum=SYMBOLS.IMPLICATION,
    default_representation=0,
    string_representations=implication_strings,
    parse_symbol=lambda s: any_prefix(s, implication_strings),
)
LEFT_PARENTHESIS = Symbol(
    symbol_enum=SYMBOLS.LEFT_PARENTHESIS,
    default_representation=0,
    string_representations=left_parenthesis_strings,
    parse_symbol=lambda s: any_prefix(s, left_parenthesis_strings)
)
RIGHT_PARENTHESIS = Symbol(
    symbol_enum=SYMBOLS.RIGHT_PARENTHESIS,
    default_representation=0,
    string_representations=right_parenthesis_strings,
    parse_symbol=lambda s: any_prefix(s, right_parenthesis_strings)
)
PROPOSITION = Symbol(
    symbol_enum=SYMBOLS.PROPOSITION,
    default_representation=0,
    string_representations=atomic_proposition_strings,
    parse_symbol=lambda s: any_prefix(s, atomic_proposition_strings)
)


# Probably should have some test to show that the inference patterns are exhaustive and mutually exclusive.
non_branching_inference_patterns = [
    [SYMBOLS.NEGATION, SYMBOLS.NEGATION],
    [SYMBOLS.CONJUNCTION, SYMBOLS.WILDCARD],
    [SYMBOLS.NEGATION, SYMBOLS.DISJUNCTION],
    [SYMBOLS.NEGATION, SYMBOLS.IMPLICATION],
]
branching_inference_patterns = [
    [SYMBOLS.NEGATION, SYMBOLS.CONJUNCTION],
    [SYMBOLS.DISJUNCTION, SYMBOLS.WILDCARD],
    [SYMBOLS.IMPLICATION, SYMBOLS.WILDCARD],
]


class PropositionalLogicFormula(object):
    # this could be an immutable dataclass, but I'm not sure if that's necessary.
    def __init__(self, symbol: SYMBOLS, children: list['PropositionalLogicFormula'] = []):
        self.symbol = symbol
        self.children = children
        if symbol in CONNECTIVES:
            if symbol == SYMBOLS.NEGATION:
                assert len(children) == 1, "negation should have one child"
            else:
                assert len(
                    children) == 2, "connective should have two children"
        elif symbol == SYMBOLS.PROPOSITION:
            assert len(
                children) == 0, "atomic proposition should have no children"
        else:
            assert False, "invalid symbol"

    def __eq__(self, other):
        return other is PropositionalLogicFormula and self.symbol == other.symbol and self.children == other.children


# all lists are stacks, so we can use pop() to get the last element and append() to add a new element.
class AnalyticTableaux():
    def __init__(self,
                 new_formulas: list[PropositionalLogicFormula] = [],
                 literals: set[PropositionalLogicFormula] = {},
                 non_branching_formulas: list[PropositionalLogicFormula] = [],
                 branching_formulas: list[PropositionalLogicFormula] = []):
        self.new_formulas = new_formulas
        self.literals = literals
        self.non_branching_formulas = non_branching_formulas
        self.branching_formulas = branching_formulas

        # literals = set of literals reached so far in the tableaux (perhaps do dict of (literal, ENUM("found", ["positive", "negation"])) if that's somehow more efficient, maybe a lookup table is better if we restrict our formulas to have a fixed limit on the number of atomic propositions you can use)
        # non_branching_formulas = stack of formulas to be used to produce new inferences with non_branching_inference_patterns
        # braning_formulas = stack of formulas to be used to produce new inferences with branching inference patterns
        # new_formulas = formulas just produced from an inference, they need to be categorized as
        # we want to do the non_branching formulas first because if you branch first, then you have to apply the non_branching formulas twice (once for each branch)
        # there may be other ways to avoid repeated work with recognizing similar branches

# This idea of storing everything after each step seems like there is waste involved, currently doing this to simplify the implementation, but it may be possible to optimize this by doing more work in the same step.
# pos is position in the recursion tree, pos "1" is the first inference, pos "3r.1l" is in the right branch of the 3rd inference and the left branch of the 1st inference afterwards.


def is_contradiction_tableaux(tableaux: AnalyticTableaux) -> Tuple[bool, bool]:
    """
    Check if the formula is a contradiction.

    Args: 
    formula (list): The formula to check.

    Returns:
    success: True if the result was calculated correctly, False otherwise.

    result: True if the formula is a contradiction, False otherwise.
    """

    result = False
    success = False

    # could just loop while there are new formulas and non_branching_formulas, then recurse when there are only branching_formulas.

    # TODO: Recursively apply the rules of the tableaux method to formula in the Analytic Tableaux Data Structure until a contradiction is found or there are no more inference rules to apply. Return True if a contradiction is found, False otherwise.

    if tableaux is None:
        return success, result
    # Process the new formulas.
    if len(tableaux.new_formulas) > 0:
        # identify formula as literal, or branching, or non_branching
        new_formula = tableaux.new_formulas.pop()
        is_atomic = new_formula.symbol == SYMBOLS.PROPOSITION
        is_atomic_negation = new_formula.symbol == SYMBOLS.NEGATION and new_formula.children[
            0].symbol == SYMBOLS.PROPOSITION
        # if we kept track of depth, could check for parse tree of 1 or 2 nodes
        is_literal = is_atomic or is_atomic_negation
        if is_literal:
            # if we are creating the branches to be inputted into the logic encoding, at this point we would just add the literal as a positive or negative literal as a constraint for this branch.
            if is_atomic:
                opposite_formula = PropositionalLogicFormula(
                    SYMBOLS.NEGATION, [new_formula])
            else:  # is_atomic_negation
                opposite_formula = new_formula.children[0]
            if opposite_formula in tableaux.literals:
                # a contradiction has been reached, the branch is closed.
                success = True
                result = True
            else:
                tableaux.literals.add(new_formula)
                success, result = is_contradiction_tableaux(tableaux)
                tableaux.literals.remove(new_formula)
        # compound formula, need to categorize inference rule as branching or non_branching.
        else:
            pattern = [new_formula.symbol, new_formula.children[0].symbol]
            if pattern in branching_inference_patterns:
                tableaux.branching_formulas.append(new_formula)
                success, result = is_contradiction_tableaux(tableaux)
                tableaux.branching_formulas.pop(new_formula)
            elif pattern in non_branching_inference_patterns:
                tableaux.non_branching_formulas.append(new_formula)
                success, result = is_contradiction_tableaux(tableaux)
                tableaux.branching_formulas.pop(new_formula)
            else:
                success = False
                # assert False, "invalid formula"
    # Produce new formulas from non_branching_formulas
    elif len(tableaux.non_branching_formulas) > 0:
        formula = tableaux.non_branching_formulas.pop()
        pattern = [formula.symbol, formula.children[0].symbol]

        # apply inference rules
        # add new formulas to tableaux.new_formulas
        success = True
    # Produce new formulas from branching_formulas
    elif len(tableaux.branching_formulas) > 0:
        formula = tableaux.branching_formulas.pop()
        pattern = [formula.symbol, formula.children[0].symbol]

        # apply inference rules
        # add new formulas to tableaux.new_formulas
        success = True
    # No formulas to process.
    else:
        success = True
        result = False

    return success, result


# TODO: implement this function.
def stringify_formula(formula: PropositionalLogicFormula) -> Tuple[bool, str]:
    """
    Converts the formula from a list of integers to a string of symbols.

    Args:
    formula (list): The formula to convert.

    Returns:
    success: True if the formula was converted successfully, False otherwise.

    str: The formula as a string, if an error parsing occurred, the empty string `""` is returned.
    """
    result_formula = ""

    return (False, result_formula)


# TODO: implement this function.
def parse_infix_formula(formula: str) -> Tuple[bool, PropositionalLogicFormula]:
    """
    Parses the input formula, converts the string of symbols to a PropositionalLogicFormula.

    Args:
    formula (str): The formula to convert.

    Returns:
    success: True if the formula was parsed successfully, False otherwise.

    result: PropositionalLogicFormula object
    """
    result_formula = PropositionalLogicFormula
    success = False

    return (False, result_formula)


def classify_propositional_logic_formula(formula: str) -> Literal["contingency", "tautology", "contradiction", "invalid formula", "tableaux error"]:
    """
    Classify the propositional logic formula as a tautology, contradiction, or contingency.

    Args:
    formula (str): The formula to classify.

    Returns:
    str: The classification of the formula.
    """

    # Parse the formula provided using infix notation and convert it to postfix notation for easier processing.
    success_parsing, parsed_formula = parse_infix_formula(formula)
    if not success_parsing:
        return "invalid formula"
    else:
        negated_parsed_formula = PropositionalLogicFormula(
            symbol=SYMBOLS.NEGATION, children=[parsed_formula])

        # TODO: initialize Tableaux Data Structure which will contain all the relevant information (formulas) for the tableaux method.
        tableaux = None
        tableaux_negation = None

        (success1, is_contradiction) = is_contradiction_tableaux(tableaux)
        (success2, is_tautology) = is_contradiction_tableaux(tableaux_negation)

        # If either of the tableaux checks fail, return "tableaux error".
        # If the formula is neither a tautology nor a contradiction, then it is a contingency.
        # If the formula not a contradiction and it is a tautology, then it is a tautology.
        # If the formula is a contradiction and not a tautology, then it is a contradiction.
        # If the formula is a contradiction and a tautology, then there is an error in the tableaux method.

        if not success1 or not success2:
            return "tableaux error"
        elif not is_contradiction and not is_tautology:
            return "contingency"
        elif not is_contradiction and is_tautology:
            return "tautology"
        elif is_contradiction and not is_tautology:
            return "contradiction"
        else:  # is_contradiction and is_tautology
            return "tableaux error"

    return ""


def main():
    """
    This is where we can run test cases.
    """
    pass


if __name__ == "__main__":
    main()
    print(ord('¬'), '¬')
    print(NEGATION)
    list1 = [1]
    list2 = [1]
    print(list1 == list2)
