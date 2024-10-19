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


# TODO: Could make this a regex pattern to allow for more than one letter symbols, this would be helpful so you don't have to type special characters.
atomic_proposition_strings = list(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
negation_strings = ["¬", "~", "!"]  # , "not"]
conjunction_strings = ["∧", "&", "/\\"]  # , "and"]
disjunction_strings = ["∨", "|", "\\/"]  # , "or"]
implication_strings = ["→", "->", ">>"]  # , "implies"]
# biconditional_strings = ["↔", "<->"]#, "iff", "if and only if"]
left_parenthesis_strings = ["(", "[", "{"]
right_parenthesis_strings = [")", "]", "}"]

# TODO: write test cases for this function.


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

# TODO: write test cases for this function.


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
