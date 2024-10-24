from dataclasses import dataclass, field
from typing import List, Tuple, Literal, Callable

from formula_symbols import SYMBOL_TYPE
from propositional_logic_formula import PropositionalLogicFormula


# TODO: Probably should have some test to show that the inference patterns are exhaustive and mutually exclusive.
# The "branching" vs "non-branching" is used in the Analytic Tableaux method.
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
