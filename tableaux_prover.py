from typing import List, Tuple, Literal

# Define the symbols that will be used in the propositional logic formulas.
alternative_connectives1 = ["~", "/\\", "\\/", "->"]
alternative_connectives2 = ["~", "&", "|", "->"]
conectives = ["¬", "∧", "∨", "→"]
parentheses = ["(", ")"]
# Could make this a regex pattern to allow for more than one letter symbols, this would be helpful so you don't have to type special characters.
atomic_propositions = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
                       "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
symbols = conectives + parentheses + atomic_propositions

non_branching_inference_patterns = ["¬¬", "∧", "¬∨", "¬→"]
branching_inference_patterns = ["¬∧", "∨", "→"]


# TODO: determine the data structure to use for the Analytic Tableaux Method. This data structure should be able to store the formulas in a way that allows for easy manipulation and checking of the formulas. It should also consider the branching nature of the tableaux method.
def is_contradiction_tableaux(tableaux) -> Tuple[bool, bool]:
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

    # TODO: Recursively apply the rules of the tableaux method to formula in the Analytic Tableaux Data Structure until a contradiction is found or there are no more inference rules to apply. Return True if a contradiction is found, False otherwise.

    return (False, False)


# TODO: implement this function.
def stringify_formula(formula: List[int]) -> Tuple[bool, str]:
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
def parse_formula(formula: str) -> Tuple[bool, List[int]]:
    """
    Parses the input formula, converts the string of symbols to a list of consistent integer values and rearranges the formula from infix notation to postfix notation.

    Args:
    formula (str): The formula to convert.

    Returns:
    success: True if the formula was parsed successfully, False otherwise.

    list: The formula in postfix notation, also stored as an array of integers rather than string characters.
    """
    result_formula = []
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
    success_parsing, parsed_formula = parse_formula(formula)
    if not success_parsing:
        return "invalid formula"
    else:
        negated_parsed_formula = [ord("¬")] + parsed_formula

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
    print(ord('¬'))
