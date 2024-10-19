from dataclasses import dataclass, field
from typing import List, Tuple, Literal, Callable
from enum import Enum

# Define the symbols that will be used in the propositional logic formulas.


class SYMBOL_TYPE(Enum):
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
        return isinstance(other, SYMBOL_TYPE) and (self.value == other.value or self.value == SYMBOL_TYPE.WILDCARD.value or other.value == SYMBOL_TYPE.WILDCARD.value)


# Types of symbols: connectives, parantheses, atomic propositions
CONNECTIVES = [
    SYMBOL_TYPE.NEGATION,
    SYMBOL_TYPE.CONJUNCTION,
    SYMBOL_TYPE.DISJUNCTION,
    SYMBOL_TYPE.IMPLICATION,
]
PARENTHESES = [SYMBOL_TYPE.LEFT_PARENTHESIS, SYMBOL_TYPE.RIGHT_PARENTHESIS]


@dataclass
class Symbol:
    symbol_enum: SYMBOL_TYPE = field(
        default_factory=lambda: SYMBOL_TYPE.UNKNOWN)
    default_representation: int = 0
    string_representations: list = field(default_factory=list)
    parse_symbol: Callable[[str], str | bool] = lambda x: False

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.symbol_enum == other.symbol_enum

    def __str__(self) -> str:
        return self.string_representations[self.default_representation]


# Could make this a regex pattern to allow for more than one letter symbols, this would be helpful so you don't have to type special characters.
atomic_proposition_strings = list(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
negation_strings = ["¬", "~", "!"]  # , "not"]
conjunction_strings = ["∧", "&", "/\\"]  # , "and"]
disjunction_strings = ["∨", "|", "\\/"]  # , "or"]
implication_strings = ["→", "->", ">>"]  # , "implies"]
# biconditional_strings = ["↔", "<->"]#, "iff", "if and only if"]
left_parenthesis_strings = ["(", "[", "{"]
right_parenthesis_strings = [")", "]", "}"]


def parenthesis_match(s: str) -> bool:
    """
    Check if the string is a parenthesis.

    if s is a parenthesis, return the matching parenthesis, otherwise return False.
    """
    if s in left_parenthesis_strings:
        return right_parenthesis_strings[left_parenthesis_strings.index(s)]
    elif s in right_parenthesis_strings:
        return left_parenthesis_strings[right_parenthesis_strings.index(s)]
    else:
        return False


def match_any_prefix(s: str, prefixes: List[str]) -> str:
    """
    Check if the string starts with any of the prefixes.

    If s starts with any of the prefixes, return the prefix, otherwise return an empty string.
    """
    return next((prefix for prefix in prefixes if s.startswith(prefix)), "")


NEGATION = Symbol(
    symbol_enum=SYMBOL_TYPE.NEGATION,
    default_representation=0,
    string_representations=negation_strings,
    parse_symbol=lambda s: match_any_prefix(s, negation_strings),
)
CONJUNCTION = Symbol(
    symbol_enum=SYMBOL_TYPE.CONJUNCTION,
    default_representation=0,
    string_representations=conjunction_strings,
    parse_symbol=lambda s: match_any_prefix(s, conjunction_strings),
)
DISJUNCTION = Symbol(
    symbol_enum=SYMBOL_TYPE.DISJUNCTION,
    default_representation=0,
    string_representations=disjunction_strings,
    parse_symbol=lambda s: match_any_prefix(s, disjunction_strings),
)
IMPLICATION = Symbol(
    symbol_enum=SYMBOL_TYPE.IMPLICATION,
    default_representation=0,
    string_representations=implication_strings,
    parse_symbol=lambda s: match_any_prefix(s, implication_strings),
)
LEFT_PARENTHESIS = Symbol(
    symbol_enum=SYMBOL_TYPE.LEFT_PARENTHESIS,
    default_representation=0,
    string_representations=left_parenthesis_strings,
    parse_symbol=lambda s: match_any_prefix(s, left_parenthesis_strings)
)
RIGHT_PARENTHESIS = Symbol(
    symbol_enum=SYMBOL_TYPE.RIGHT_PARENTHESIS,
    default_representation=0,
    string_representations=right_parenthesis_strings,
    parse_symbol=lambda s: match_any_prefix(s, right_parenthesis_strings)
)
PROPOSITION = Symbol(
    symbol_enum=SYMBOL_TYPE.PROPOSITION,
    default_representation=0,
    string_representations=atomic_proposition_strings,
    parse_symbol=lambda s: match_any_prefix(s, atomic_proposition_strings)
)


def default_symbol_represenation(symbol: SYMBOL_TYPE) -> str:
    """
    Get the default representation of the symbol.
    """
    if symbol == SYMBOL_TYPE.NEGATION:
        return NEGATION.string_representations[NEGATION.default_representation]
    elif symbol == SYMBOL_TYPE.CONJUNCTION:
        return CONJUNCTION.string_representations[CONJUNCTION.default_representation]
    elif symbol == SYMBOL_TYPE.DISJUNCTION:
        return DISJUNCTION.string_representations[DISJUNCTION.default_representation]
    elif symbol == SYMBOL_TYPE.IMPLICATION:
        return IMPLICATION.string_representations[IMPLICATION.default_representation]
    elif symbol == SYMBOL_TYPE.LEFT_PARENTHESIS:
        return LEFT_PARENTHESIS.string_representations[LEFT_PARENTHESIS.default_representation]
    elif symbol == SYMBOL_TYPE.RIGHT_PARENTHESIS:
        return RIGHT_PARENTHESIS.string_representations[RIGHT_PARENTHESIS.default_representation]
    elif symbol == SYMBOL_TYPE.PROPOSITION:
        return PROPOSITION.string_representations[PROPOSITION.default_representation]
    else:
        return ""


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


# Probably should have some test to show that the inference patterns are exhaustive and mutually exclusive.
non_branching_inference_patterns = [
    [SYMBOL_TYPE.NEGATION, SYMBOL_TYPE.NEGATION],
    [SYMBOL_TYPE.CONJUNCTION, SYMBOL_TYPE.WILDCARD],
    [SYMBOL_TYPE.NEGATION, SYMBOL_TYPE.DISJUNCTION],
    [SYMBOL_TYPE.NEGATION, SYMBOL_TYPE.IMPLICATION],
]
branching_inference_patterns = [
    [SYMBOL_TYPE.NEGATION, SYMBOL_TYPE.CONJUNCTION],
    [SYMBOL_TYPE.DISJUNCTION, SYMBOL_TYPE.WILDCARD],
    [SYMBOL_TYPE.IMPLICATION, SYMBOL_TYPE.WILDCARD],
]


@dataclass
class InferenceRule:
    symbol_pattern: List[SYMBOL_TYPE] = field(
        default_factory=lambda: [SYMBOL_TYPE.UNKNOWN, SYMBOL_TYPE.UNKNOWN])
    is_branching: bool = None
    inference: Callable[[List['PropositionalLogicFormula']],
                        List['PropositionalLogicFormula']] = lambda x: []

    def __post_init__(self):
        assert self.is_branching is not None, "is_branching should be a boolean"
        assert len(
            self.symbol_pattern) == 2, "inference rule should have two symbols"

    def __eq__(self, other):
        # An inference rule is uniquely defined by its symbol_pattern.
        return isinstance(other, InferenceRule) and self.symbol_pattern == other.symbol_pattern


def negation_negation_inference(formula: PropositionalLogicFormula) -> List[PropositionalLogicFormula]:
    assert formula.symbol == SYMBOL_TYPE.NEGATION and formula.children[
        0].symbol == SYMBOL_TYPE.NEGATION, "invalid formula"
    return [formula.children[0].children[0]]


def conjunction_inference(formula: PropositionalLogicFormula) -> List[PropositionalLogicFormula]:
    assert formula.symbol == SYMBOL_TYPE.CONJUNCTION, "invalid formula"
    return [formula.children[0], formula.children[1]]


def negation_disjunction_inference(formula: PropositionalLogicFormula) -> List[PropositionalLogicFormula]:
    assert formula.symbol == SYMBOL_TYPE.NEGATION and formula.children[
        0].symbol == SYMBOL_TYPE.DISJUNCTION, "invalid formula"
    return [PropositionalLogicFormula(SYMBOL_TYPE.NEGATION, [formula.children[0].children[0]]), PropositionalLogicFormula(SYMBOL_TYPE.NEGATION, [formula.children[0].children[1]])]


def negation_implication_inference(formula: PropositionalLogicFormula) -> List[PropositionalLogicFormula]:
    assert formula.symbol == SYMBOL_TYPE.NEGATION and formula.children[
        0].symbol == SYMBOL_TYPE.IMPLICATION, "invalid formula"
    return [formula.children[0].children[0], PropositionalLogicFormula(SYMBOL_TYPE.NEGATION, [formula.children[0].children[1]])]


def negation_conjunction_inference(formula: PropositionalLogicFormula) -> List[PropositionalLogicFormula]:
    assert formula.symbol == SYMBOL_TYPE.NEGATION and formula.children[
        0].symbol == SYMBOL_TYPE.CONJUNCTION, "invalid formula"
    return [PropositionalLogicFormula(SYMBOL_TYPE.NEGATION, [formula.children[0].children[0]]), PropositionalLogicFormula(SYMBOL_TYPE.NEGATION, [formula.children[0].children[1]])]


def disjunction_inference(formula: PropositionalLogicFormula) -> List[PropositionalLogicFormula]:
    assert formula.symbol == SYMBOL_TYPE.DISJUNCTION, "invalid formula"
    return [formula.children[0], formula.children[1]]


def implication_inference(formula: PropositionalLogicFormula) -> List[PropositionalLogicFormula]:
    assert formula.symbol == SYMBOL_TYPE.IMPLICATION, "invalid formula"
    return [PropositionalLogicFormula(SYMBOL_TYPE.NEGATION, [formula.children[0]]), formula.children[1]]


negation_negation_inference_rule = InferenceRule(
    symbol_pattern=[SYMBOL_TYPE.NEGATION, SYMBOL_TYPE.NEGATION],
    is_branching=False,
    inference=negation_negation_inference
)
conjunction_inference_rule = InferenceRule(
    symbol_pattern=[SYMBOL_TYPE.CONJUNCTION, SYMBOL_TYPE.WILDCARD],
    is_branching=False,
    inference=conjunction_inference
)
negation_disjunction_inference_rule = InferenceRule(
    symbol_pattern=[SYMBOL_TYPE.NEGATION, SYMBOL_TYPE.DISJUNCTION],
    is_branching=False,
    inference=negation_disjunction_inference
)
negation_implication_inference_rule = InferenceRule(
    symbol_pattern=[SYMBOL_TYPE.NEGATION, SYMBOL_TYPE.IMPLICATION],
    is_branching=False,
    inference=negation_implication_inference
)
non_branching_inference_rules = [
    negation_negation_inference_rule,
    conjunction_inference_rule,
    negation_disjunction_inference_rule,
    negation_implication_inference_rule,
]
negation_conjunction_inference_rule = InferenceRule(
    symbol_pattern=[SYMBOL_TYPE.NEGATION, SYMBOL_TYPE.CONJUNCTION],
    is_branching=True,
    inference=negation_conjunction_inference
)
disjunction_inference_rule = InferenceRule(
    symbol_pattern=[SYMBOL_TYPE.DISJUNCTION, SYMBOL_TYPE.WILDCARD],
    is_branching=True,
    inference=disjunction_inference
)
implication_inference_rule = InferenceRule(
    symbol_pattern=[SYMBOL_TYPE.IMPLICATION, SYMBOL_TYPE.WILDCARD],
    is_branching=True,
    inference=implication_inference
)
branching_inference_rules = [
    negation_conjunction_inference_rule,
    disjunction_inference_rule,
    implication_inference_rule,
]


# all lists are stacks, so we can use pop() to get the last element and append() to add a new element.
class AnalyticTableaux():
    def __init__(self,
                 new_formulas: list[PropositionalLogicFormula] = [],
                 literals: set[PropositionalLogicFormula] = set(),
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
        is_atomic = new_formula.symbol == SYMBOL_TYPE.PROPOSITION
        is_atomic_negation = new_formula.symbol == SYMBOL_TYPE.NEGATION and new_formula.children[
            0].symbol == SYMBOL_TYPE.PROPOSITION
        # if we kept track of depth, could check for parse tree of 1 or 2 nodes
        is_literal = is_atomic or is_atomic_negation
        if is_literal:
            # if we are creating the branches to be inputted into the logic encoding, at this point we would just add the literal as a positive or negative literal as a constraint for this branch.
            # obrain the opposite formula
            if is_atomic:
                opposite_literal = PropositionalLogicFormula(
                    SYMBOL_TYPE.NEGATION, [new_formula])
            else:  # is_atomic_negation
                opposite_literal = new_formula.children[0]

            # check if the opposite formula is in the literals, if so, then the branch is closed.
            if opposite_literal in tableaux.literals:
                # a contradiction has been reached, the branch is closed.
                success = True
                result = True
            # opposite formula is not in the literals, so add the new formula to the literals if it is not already there.
            elif new_formula in tableaux.literals:
                success, result = is_contradiction_tableaux(tableaux)
            else:
                tableaux.literals.add(new_formula)
                success, result = is_contradiction_tableaux(tableaux)
                tableaux.literals.remove(new_formula)
        # compound formula, need to categorize inference rule as branching or non_branching.
        elif new_formula.symbol in CONNECTIVES:
            pattern = [new_formula.symbol, new_formula.children[0].symbol]
            if pattern in branching_inference_patterns:
                tableaux.branching_formulas.append(new_formula)
                success, result = is_contradiction_tableaux(tableaux)
                # Remove the new formula from the tableaux in case of backtracking
                tableaux.branching_formulas.pop()
            elif pattern in non_branching_inference_patterns:
                tableaux.non_branching_formulas.append(new_formula)
                success, result = is_contradiction_tableaux(tableaux)
                # Remove the new formula from the tableaux in case of backtracking
                tableaux.non_branching_formulas.pop()
            else:
                success = False
                # assert False, "invalid formula"
        else:
            success = False
            # assert False, "invalid formula"
        # push the formula back onto the stack in case of backtracking
        tableaux.new_formulas.append(new_formula)
    # Produce new formulas from non_branching_formulas
    elif len(tableaux.non_branching_formulas) > 0:
        inference_formula = tableaux.non_branching_formulas.pop()
        pattern = [inference_formula.symbol,
                   inference_formula.children[0].symbol]
        # apply inference rules
        # add new formulas to tableaux.new_formulas and recurse
        rule = next(
            (rule for rule in non_branching_inference_rules if rule.symbol_pattern == pattern), None)
        if rule is not None:
            new_formulas = rule.inference(inference_formula)
            tableaux.new_formulas.extend(new_formulas)
            success, result = is_contradiction_tableaux(tableaux)
            # Remove the new formulas from the tableaux in case of backtracking
            tableaux.new_formulas = tableaux.new_formulas[:-len(new_formulas)]
        else:
            success = False
            # assert False, "invalid formula"
        # push the formula back onto the stack in case of backtracking
        tableaux.non_branching_formulas.append(inference_formula)
    # Produce new formulas from branching_formulas
    elif len(tableaux.branching_formulas) > 0:
        inference_formula = tableaux.branching_formulas.pop()
        pattern = [inference_formula.symbol,
                   inference_formula.children[0].symbol]
        # apply inference rules
        # add new formulas to tableaux.new_formulas
        rule = next(
            (rule for rule in branching_inference_rules if rule.symbol_pattern == pattern), None)
        if rule is not None:
            new_formulas = rule.inference(inference_formula)
            # If all branches are contradictions, then the formula is a contradiction.
            success = True
            result = True
            for new_formula in new_formulas:
                tableaux.new_formulas.append(new_formula)
                branch_success, branch_result = is_contradiction_tableaux(
                    tableaux)
                success = success and branch_success
                result = result and branch_result
                # Remove the new formula from the tableaux for backtracking
                tableaux.new_formulas.pop()
        else:
            success = False
            # assert False, "invalid formula"
        # push the formula back onto the stack in case of backtracking
        tableaux.branching_formulas.append(inference_formula)
    # No formulas to process.
    else:
        success = True
        result = False

    return success, result


def classify_propositional_logic_formula(formula: PropositionalLogicFormula) -> Literal["contingency", "tautology", "contradiction", "invalid formula", "tableaux error"]:
    """
    Classify the propositional logic formula as a tautology, contradiction, or contingency.

    Args:
    formula (PropositionalLogicFormula): The formula to classify.

    Returns:
    str: The classification of the formula.
    """

    negated_formula = PropositionalLogicFormula(
        SYMBOL_TYPE.NEGATION, [formula])
    # Initialize Tableaux Data Structure which contain all the relevant information (formulas) for the tableaux method.
    tableaux = AnalyticTableaux(new_formulas=[formula])
    tableaux_negation = AnalyticTableaux(new_formulas=[negated_formula])

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


def classify_propositional_logic_formula_str(formula: str) -> Literal["contingency", "tautology", "contradiction", "invalid formula", "tableaux error"]:
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
        return classify_propositional_logic_formula(parsed_formula)


def full_test_formula(formula: str) -> Tuple[bool, str]:
    results = f"testing formula: {formula}\n"
    parse_success, parsed_formula = parse_infix_formula(formula)
    results += f"{(parse_success, parsed_formula)}\n"
    stringify_success, stringified_formula = stringify_formula(
        parsed_formula, "infix")
    results += f"{(stringify_success, stringified_formula)}\n"
    classification = classify_propositional_logic_formula(
        parsed_formula)
    results += f"{classification}\n"
    return (parse_success and stringify_success and classification != "tableaux error", results)


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
    print([ord(c) for c in left_parenthesis_strings])
    print([ord(c) for c in right_parenthesis_strings])
    print(parse_infix_formula("()"))
    formula_string = "A&B"
    print(full_test_formula(formula_string)[1])
    formula_string = "A->B"
    print(full_test_formula(formula_string)[1])
    formula_string = "((A->B)&A)->B"
    print(full_test_formula(formula_string)[1])
    formula_string = "((A->B)&~B)->~A"
    print(full_test_formula(formula_string)[1])
    formula_string = "(A->~~A)"
    print(full_test_formula(formula_string)[1])
    formula_string = "((~~A)->A)"
    print(full_test_formula(formula_string)[1])
    formula_string = "(A->~~A)&((~~A)->A)"
    print(full_test_formula(formula_string)[1])
