from tableaux_prover.propositional_logic_formula import parse_infix_formula, PropositionalLogicFormula, SYMBOL_TYPE, atomic_proposition_set
from tableaux_prover.tableaux_aggregator import both_lists_of_tableaux_branches

from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"


# Encoding that will store all of your constraints
E = Encoding()


# Need to have at least one formula that is long enough to create 50 branches.
CANDIDATE_FORMULAS = [
    # 0: simple tautology (LEM)
    "a | ~a",
    # 1: simplest contradiction
    "a & ~a",
    # 2: A simple contingent formula with 3 variables and 2 operators
    "(a & b) | c",
    # 3: A complicated looking formula using all the different connectives and variables
    "((a & b) | (c & d)) >> (x | y) & ~(z | (a & b) & (c & d) & (x | y) & ~(z | (a & b) & (c & d)))",
    # 4: An even more complicated and longer formula with even more variables and operators
    "((a & b) | (c & d)) >> (x | y) & ~(z | (a & b) & (c & d) & (x | y) & ~(z | (a & b) & (c & d))) | ((a & b) | (c & d)) >> (x | y) & ~(z | (a & b) & (c & d) & (x | y) & ~(z | (a & b) & (c & d)))",
    # 5: a long disjunction of all the variables (contingency)
    " | ".join([atom for atom in list(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")]),
    # 6: a long disjunction of all the variables plus a negation of one of them (tautology)
    " | ".join([atom for atom in list(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")]) + " | (~a)",
    # 7: a long disjunction of all the variables plus a negation of one of them (tautology)
    " | ".join([atom for atom in list(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")]) + " | (~a) | (~b)",
    # 8: a long conjunction of all the variables plus a negation of one of them (contradiction)
    " & ".join([atom for atom in list(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")]) + " & (~a)",
]

FORMULA_CLASSIFICATIONS = [
    "tautology",
    "contradiction",
    "contingency",
]

TABLEAUX_NAMES = [
    "regular_tablaux",
    "negated_tableaux",
]

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding


# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
@constraint.at_least_one(E)
@proposition(E)
class FancyPropositions:

    def __init__(self, data):
        self.data = data

    def _prop_name(self):
        return f"A.{self.data}"


# Call your variables whatever you want
a = FancyPropositions("a")
TAUTOLOGY = a | ~a
CONTRADICTION = a & ~a


@proposition(E)
class BranchContainsLiteral:

    def __init__(self, formula_id: int, tableaux_name: str, branch_number: int, proposition: PropositionalLogicFormula):
        self.formula_id = formula_id
        self.tableaux_name = tableaux_name
        self.branch_number = branch_number
        self.proposition_name = proposition
        assert formula_id in range(len(CANDIDATE_FORMULAS))
        assert tableaux_name in TABLEAUX_NAMES
        assert proposition.symbol == SYMBOL_TYPE.PROPOSITION or (
            proposition.symbol == SYMBOL_TYPE.NEGATION and proposition.children[0].symbol == SYMBOL_TYPE.PROPOSITION)

    def _prop_name(self):
        return f"formula.{self.formula_id}.tableaux.{self.tableaux_name}.branch.{self.branch_number}.contains.literal.{self.proposition_name}"


@proposition(E)
class BranchContingentOnLiteral:

    def __init__(self, formula_id: int, tableaux_name: str, branch_number: int, proposition: PropositionalLogicFormula):
        self.formula_id = formula_id
        self.tableaux_name = tableaux_name
        self.branch_number = branch_number
        self.proposition_name = proposition
        assert formula_id in range(len(CANDIDATE_FORMULAS))
        assert tableaux_name in TABLEAUX_NAMES
        assert proposition.symbol == SYMBOL_TYPE.PROPOSITION or (
            proposition.symbol == SYMBOL_TYPE.NEGATION and proposition.children[0].symbol == SYMBOL_TYPE.PROPOSITION)

    def _prop_name(self):
        return f"formula.{self.formula_id}.tableaux.{self.tableaux_name}.branch.{self.branch_number}.contingent_on.literal.{self.proposition_name}"


@proposition(E)
class BranchClosedOnVariable:

    def __init__(self, formula_id: int, tableaux_name: str, branch_number: int, variable: PropositionalLogicFormula):
        self.formula_id = formula_id
        self.tableaux_name = tableaux_name
        self.branch_number = branch_number
        self.variable = variable
        assert formula_id in range(len(CANDIDATE_FORMULAS))
        assert tableaux_name in TABLEAUX_NAMES
        assert variable.symbol == SYMBOL_TYPE.PROPOSITION

    def _prop_name(self):
        return f"formula.{self.formula_id}.tableaux.{self.tableaux_name}.branch.{self.branch_number}.closed_on.variable.{self.variable}"


@proposition(E)
class BranchClosed:

    def __init__(self, formula_id: int, tableaux_name: str, branch_number: int):
        self.formula_id = formula_id
        self.tableaux_name = tableaux_name
        self.branch_number = branch_number
        assert formula_id in range(len(CANDIDATE_FORMULAS))
        assert tableaux_name in TABLEAUX_NAMES

    def _prop_name(self):
        return f"formula.{self.formula_id}.tableaux.{self.tableaux_name}.branch.{self.branch_number}.closed"


@proposition(E)
class TableauxClosed:

    def __init__(self, formula_id: int, tableaux_name: str):
        self.formula_id = formula_id
        self.tableaux_name = tableaux_name
        assert formula_id in range(len(CANDIDATE_FORMULAS))
        assert tableaux_name in TABLEAUX_NAMES

    def _prop_name(self):
        return f"formula.{self.formula_id}.tableaux.{self.tableaux_name}.closed"


@proposition(E)
class FormulaClassification:

    def __init__(self, formula_id: int, classification: str):
        self.formula_id = formula_id
        self.classification = classification
        assert formula_id in range(len(CANDIDATE_FORMULAS))
        assert classification in FORMULA_CLASSIFICATIONS

    def _prop_name(self):
        return f"formula.{self.formula_id}.classification.{self.classification}"

# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.


def biconditional(a, b):
    return (a >> b) & (b >> a)


def example_theory(formula_id: int = 0):
    formula_str = CANDIDATE_FORMULAS[formula_id]
    parse_success, formula = parse_infix_formula(formula_str)
    assert parse_success
    global reg_branches, neg_branches
    reg_branches, neg_branches = both_lists_of_tableaux_branches(formula)
    # Set of all possible literals in the tableaus for the formula.
    global all_literal_pairs
    all_literal_pairs = {
        (atom, PropositionalLogicFormula(SYMBOL_TYPE.NEGATION, [atom])) for atom in atomic_proposition_set(formula)}
    # Iterate over each tableaux for an associated formula.
    for tableaux_name, branches in zip(TABLEAUX_NAMES, [reg_branches, neg_branches]):
        # Iterate over each branch in the tableaux.
        # Iteratively build the conjunction of all the branch closed propositions.
        conjunction_of_all_branches_closed = TAUTOLOGY
        for branch_number, branch in enumerate(branches):
            conjunction_of_all_branches_closed &= BranchClosed(
                formula_id, tableaux_name, branch_number)
            # Iterate over each pair of literals in the branch.
            # Iteratively build the disjunction of all the pairs of contradicting literals.
            disjunction_of_conjunct_literal_pairs = CONTRADICTION
            # Add constraints to specify the literals present in the branch.
            for atom, neg_atom in all_literal_pairs:
                disjunction_of_conjunct_literal_pairs |= BranchClosedOnVariable(
                    formula_id, tableaux_name, branch_number, atom)
                # Add constraints to specify the variables that the branch is closed on.
                E.add_constraint(biconditional(BranchClosedOnVariable(
                    formula_id, tableaux_name, branch_number, atom), BranchContainsLiteral(formula_id, tableaux_name, branch_number, atom) & BranchContainsLiteral(formula_id, tableaux_name, branch_number, neg_atom)))

                # Add constraints to specify the variables that the branch is contingent on.
                E.add_constraint(biconditional(
                    BranchContingentOnLiteral(formula_id, tableaux_name, branch_number, atom), BranchContainsLiteral(formula_id, tableaux_name, branch_number, atom) & ~BranchClosed(formula_id, tableaux_name, branch_number)))
                E.add_constraint(biconditional(
                    BranchContingentOnLiteral(formula_id, tableaux_name, branch_number, neg_atom), BranchContainsLiteral(formula_id, tableaux_name, branch_number, neg_atom) & ~BranchClosed(formula_id, tableaux_name, branch_number)))

                if atom in branch:
                    E.add_constraint(BranchContainsLiteral(
                        formula_id, tableaux_name, branch_number, atom))
                else:
                    E.add_constraint(~BranchContainsLiteral(
                        formula_id, tableaux_name, branch_number, atom))
                if neg_atom in branch:
                    E.add_constraint(BranchContainsLiteral(
                        formula_id, tableaux_name, branch_number, neg_atom))
                else:
                    E.add_constraint(~BranchContainsLiteral(
                        formula_id, tableaux_name, branch_number, neg_atom))

            # The branch is closed iff at least one pair of contradicting literals is in the branch.
            E.add_constraint(biconditional(BranchClosed(
                formula_id, tableaux_name, branch_number), disjunction_of_conjunct_literal_pairs))
        # The tableaux is closed iff all of it's branches are closed.
        E.add_constraint(biconditional(
            TableauxClosed(formula_id, tableaux_name), conjunction_of_all_branches_closed))

    regular_tableaux_closed = TableauxClosed(formula_id, "regular_tablaux")
    negated_tableaux_closed = TableauxClosed(formula_id, "negated_tableaux")
    # If both of the teablaux must be closed for this to work, then there must have been an error either
    # in the tableaux generation or in the constraints that represent it.
    constraint.add_at_most_one(
        E, regular_tableaux_closed, negated_tableaux_closed)
    tautology_classification = FormulaClassification(
        formula_id, "tautology")
    contradiction_classification = FormulaClassification(
        formula_id, "contradiction")
    contingency_classification = FormulaClassification(
        formula_id, "contingency")
    # These classifications are mutually exclusive.
    constraint.add_exactly_one(E, tautology_classification,
                               contradiction_classification, contingency_classification)
    # The formula is a tautology iff the regular tableaux is closed and the negated tableaux is closed.
    E.add_constraint(biconditional(tautology_classification, ~
                     regular_tableaux_closed & negated_tableaux_closed))
    # The formula is a contradiction iff the regular tableaux is closed and the negated tableaux is not closed.
    E.add_constraint(biconditional(contradiction_classification,
                     regular_tableaux_closed & ~negated_tableaux_closed))
    # The formula is a contingency iff the regular tableaux is not closed and the negated tableaux is not closed.
    E.add_constraint(biconditional(contingency_classification,
                     ~regular_tableaux_closed & ~negated_tableaux_closed))
    return E


if __name__ == "__main__":
    print("Creating the Semantic Tableau(s) and Representation as a SAT problem...")
    T = example_theory(2)

    print(all_literal_pairs)
    print(reg_branches)
    print(neg_branches)
    
    contradiction_factors = []
    contigency_factors = all_literal_pairs
    for branch in reg_branches:
        for atom, atom_neg in contigency_factors:
            if atom in branch and atom_neg in branch:
                contigency_factors.remove((atom, atom_neg))
                contradiction_factors.append((atom, atom_neg))
                break
    print(contradiction_factors)
    print(contigency_factors)

    # Don't compile until you're finished adding all your constraints!
    print("Computing the Solution...")
    T = T.compile()

    theory_satisfiable = T.satisfiable()
    theory_num_solutions = count_solutions(T)
    theory_solution = T.solve()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % theory_satisfiable)
    print("# Solutions: %d" % theory_num_solutions)
    # print("   Solution: %s" % theory_solution)
    print(f"# Variables: {len(T.vars())}")
    print(f"# Constraints: {T.size()}")

    print("\nFormula Classifications:")
    for formula_id, formula_str in enumerate(CANDIDATE_FORMULAS):
        if theory_solution.get(FormulaClassification(formula_id, FORMULA_CLASSIFICATIONS[0])) is None:
            continue
        encoded_formula = parse_infix_formula(formula_str)[1]
        regular_tableaux_branches, negated_tableaux_branches = both_lists_of_tableaux_branches(
            encoded_formula)
        num_regular_tableaux_branches = len(regular_tableaux_branches)
        num_negated_tableaux_branches = len(negated_tableaux_branches)
        # List of disjunctions of all conjunct literals, one for each branch in the regular tableaux. If at least one of these conjunctions is true, then the formula is true.
        all_formula_literals = [literal for literal in atomic_proposition_set(
            encoded_formula)] + [PropositionalLogicFormula(SYMBOL_TYPE.NEGATION, [literal]) for literal in atomic_proposition_set(encoded_formula)]
        contingently_true_conjuncts_of_literals = [
            [literal for literal in all_formula_literals if theory_solution.get(BranchContingentOnLiteral(formula_id, TABLEAUX_NAMES[0], branch_number, literal))] for branch_number in range(num_regular_tableaux_branches) if not theory_solution.get(BranchClosed(formula_id, TABLEAUX_NAMES[0], branch_number))]
        # List of disjunctions of all conjunct literals, one for each branch in the negated tableaux. If at least one of these conjunctions is true, then the formula is false.
        contingently_false_conjuncts_of_literals = [
            [literal for literal in all_formula_literals if theory_solution.get(BranchContingentOnLiteral(formula_id, TABLEAUX_NAMES[1], branch_number, literal))] for branch_number in range(num_negated_tableaux_branches) if not theory_solution.get(BranchClosed(formula_id, TABLEAUX_NAMES[1], branch_number))]
        # List of lists of variables for each branch in the negated tableaux. In each list contains the variables which have contradicting literal pairs.
        tautology_causing_variables = [[atom for atom in atomic_proposition_set(encoded_formula) if theory_solution.get(
            BranchClosedOnVariable(formula_id, "negated_tableaux", branch_number, atom))] for branch_number in range(num_negated_tableaux_branches)]
        # List of lists of variables for each branch in the regular tableaux. In each list contains the variables which have contradicting literal pairs.
        contradiction_causing_variables = [[atom for atom in atomic_proposition_set(encoded_formula) if theory_solution.get(
            BranchClosedOnVariable(formula_id, TABLEAUX_NAMES[0], branch_number, atom))] for branch_number in range(num_regular_tableaux_branches)]
        print(f"Formula {formula_id}: {formula_str}")
        for classification in FORMULA_CLASSIFICATIONS:
            formula_classification = FormulaClassification(
                formula_id, classification)
            print(
                f"\t{formula_classification}: {theory_solution.get(formula_classification, '?')}")
            # If tautology, then say which variables in the negated tableaux cause the contradiction.
            if classification == "tautology" and theory_solution.get(formula_classification):
                print(
                    f"\t\tTautology caused by: {tautology_causing_variables}")
            # If contradiction, then say which variables in the regular tableaux cause the contradiction.
            if classification == "contradiction" and theory_solution.get(formula_classification):
                print(
                    f"\t\tContradiction caused by: {contradiction_causing_variables}")
            # If contingency, then say which variables the formula is contingent on.
            if classification == "contingency" and theory_solution.get(formula_classification):
                print(
                    f"\t\tContingently true on: {contingently_true_conjuncts_of_literals}")
                print(
                    f"\t\tContingently false on: {contingently_false_conjuncts_of_literals}")

    print()
