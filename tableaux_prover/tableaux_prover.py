from typing import List, Tuple, Literal, Callable

from formula_symbols import *
from propositional_logic_formula import PropositionalLogicFormula, parse_infix_formula, stringify_formula
from inference_rules import *


# all lists are stacks, so we can use pop() to get the last element and append() to add a new element.
# TODO: find a way to store the branches as a list of constraints for the logic encoding, so that we can check if the branch is closed by checking if the opposite literal is in the list of constraints.
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

    # Recursively apply the rules of the tableaux method to formula in the Analytic Tableaux Data Structure until a contradiction is found or there are no more inference rules to apply. Return True if a contradiction is found, False otherwise.

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
    formula_string = "A|~A"
    print(full_test_formula(formula_string)[1])
    formula_string = "A&~A"
    print(full_test_formula(formula_string)[1])
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
    formula_string = "((A->B)&(B->C))->(A->C)"
    print(full_test_formula(formula_string)[1])
    formula_string = "(A->(B->A))"
    print(full_test_formula(formula_string)[1])
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
