from typing import List, Tuple, Literal, Callable

from tableaux_prover.formula_symbols import *
from tableaux_prover.propositional_logic_formula import PropositionalLogicFormula, parse_infix_formula, stringify_formula
from tableaux_prover.inference_rules import *
from tableaux_prover.tableaux_classifier import AnalyticTableaux, classify_propositional_logic_formula


def isAtomic(symbol: SYMBOL_TYPE) -> bool:
    return symbol == SYMBOL_TYPE.PROPOSITION


def isAtomicNegation(formula: PropositionalLogicFormula) -> bool:
    return formula.symbol == SYMBOL_TYPE.NEGATION and formula.children[0].symbol == SYMBOL_TYPE.PROPOSITION


def isLiteral(formula: PropositionalLogicFormula) -> list[bool]:
    atomic = isAtomic(formula.symbol)
    atomicNegation = isAtomicNegation(formula)
    # returns [isLiteral, isAtomic]
    return [(atomic or atomicNegation), atomic]


def generateNegation(formula: PropositionalLogicFormula) -> PropositionalLogicFormula:
    return PropositionalLogicFormula(SYMBOL_TYPE.NEGATION, [formula])


def generatePattern(formula: PropositionalLogicFormula) -> list[SYMBOL_TYPE]:
    return [formula.symbol, formula.children[0].symbol]


def isBranching(pattern: list[SYMBOL_TYPE]) -> bool:
    return pattern in branching_inference_patterns


def tableaux_aggregator(tableaux: AnalyticTableaux) -> list[set[PropositionalLogicFormula]]:
    branches = []

    if tableaux is None:
        return branches

    if len(tableaux.new_formulas) > 0:
        curr_formula = tableaux.new_formulas.pop()
        is_literal: list[bool] = isLiteral(curr_formula)
        if is_literal[0]:
            if curr_formula in tableaux.literals:
                branches = tableaux_aggregator(tableaux)
            else:
                tableaux.literals.add(curr_formula)
                branches = tableaux_aggregator(tableaux)
                tableaux.literals.remove(curr_formula)

        elif not is_literal[0]:  # isComplex
            pattern = generatePattern(curr_formula)
            if isBranching(pattern):

                tableaux.branching_formulas.append(curr_formula)
                branches = tableaux_aggregator(tableaux)
                tableaux.branching_formulas.pop()

            elif not isBranching(pattern):

                tableaux.non_branching_formulas.append(curr_formula)
                branches = tableaux_aggregator(tableaux)
                tableaux.non_branching_formulas.pop()
            else:
                assert False, "204 -> Invalid Formula"
        else:
            assert False, "204 -> Invalid Formula"

        tableaux.new_formulas.append(curr_formula)

    elif len(tableaux.non_branching_formulas) > 0:
        curr_formula = tableaux.non_branching_formulas.pop()
        pattern = generatePattern(curr_formula)

        rule = next(
            (rule for rule in non_branching_inference_rules if rule.symbol_pattern == pattern), None)
        if rule is not None:
            curr_formulas = rule.inference(curr_formula)
            tableaux.new_formulas.extend(curr_formulas)
            branches = tableaux_aggregator(tableaux)
            tableaux.new_formulas = tableaux.new_formulas[:-len(curr_formulas)]
        else:
            assert False, "204 -> Error"

        tableaux.non_branching_formulas.append(curr_formula)
    elif len(tableaux.branching_formulas) > 0:
        curr_formula = tableaux.branching_formulas.pop()
        pattern = generatePattern(curr_formula)
        rule = next(
            (rule for rule in branching_inference_rules if rule.symbol_pattern == pattern), None)

        if rule is not None:
            new_formulas = rule.inference(curr_formula)

            for formula in new_formulas:
                tableaux.new_formulas.append(formula)
                branches.extend(tableaux_aggregator(tableaux))
                tableaux.new_formulas.pop()
        else:
            assert False, "204 -> Invalid Formula"

        tableaux.branching_formulas.append(curr_formula)

    else:
        branches = [set(tableaux.literals)]

    return branches


def both_lists_of_tableaux_branches(formula: PropositionalLogicFormula) -> Tuple[list[set[PropositionalLogicFormula]], list[set[PropositionalLogicFormula]]]:
    """
    Given a formula, return the branches of the tableaux for the formula and the branches for the tableaux of its negation.
    """
    negated_formula = PropositionalLogicFormula(
        SYMBOL_TYPE.NEGATION, [formula])
    branches = tableaux_aggregator(AnalyticTableaux(new_formulas=[formula]))
    neg_branches = tableaux_aggregator(
        AnalyticTableaux(new_formulas=[negated_formula]))
    return branches, neg_branches


def test_aggregator(formula: str):
    results = f"testing formula: {formula}\n"
    parse_success, parsed_formula = parse_infix_formula(formula)
    classification = classify_propositional_logic_formula(parsed_formula)
    branches, neg_branches = both_lists_of_tableaux_branches(parsed_formula)
    results += f"{classification}\n"
    results += f"original formula branches: {branches}\n"
    results += f"negated formula branches: {neg_branches}\n"
    return results


def main():
    # law of excluded middle
    formula_string = "A|~A"
    print(test_aggregator(formula_string))
    # law of noncontradiction
    formula_string = "A&~A"
    print(test_aggregator(formula_string))
    # contingencies
    formula_string = "A&B"
    print(test_aggregator(formula_string))
    # modus ponens
    formula_string = "((A->B)&A)->B"
    print(test_aggregator(formula_string))
    # modus tollens
    formula_string = "((A->B)&~B)->~A"
    print(test_aggregator(formula_string))
    # contrapositive
    formula_string = "(A->B) -> ((~B) -> (~A))"
    print(test_aggregator(formula_string))
    # double negation
    formula_string = "(A->~~A)&((~~A)->A)"
    print(test_aggregator(formula_string))
    # de morgan's laws
    formula_string = "((~(A&B))->((~A)|(~B))) & (((~A)|(~B))->(~(A&B)))"
    print(test_aggregator(formula_string))


if __name__ == "__main__":
    main()
