from tableaux_prover.propositional_logic_formula import parse_infix_formula
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
    # simple tautology (LEM)
    "a | ~a",
    # simplest contradiction
    "a & ~a",
    # A simple contingent formula with 3 variables and 2 operators
    "a & b | c",
    # A complicated looking formula with 50 operators, using all the different connectives and variables
    "((a & b) | (c & d)) >> (x | y) & ~(z | (a & b) & (c & d) & (x | y) & ~(z | (a & b) & (c & d)))",
    # An even more complicated and longer formula with even more variables and operators
    "((a & b) | (c & d)) >> (x | y) & ~(z | (a & b) & (c & d) & (x | y) & ~(z | (a & b) & (c & d))) | ((a & b) | (c & d)) >> (x | y) & ~(z | (a & b) & (c & d) & (x | y) & ~(z | (a & b) & (c & d)))",
]

FORMULA_CLASSIFICATIONS = [
    "is_tautology",
    "is_contradiction",
    "is_contingency",
]

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding


@proposition(E)
class BasicPropositions:

    def __init__(self, data):
        self.data = data

    def _prop_name(self):
        return f"A.{self.data}"


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
a = BasicPropositions("a")
b = BasicPropositions("b")
c = BasicPropositions("c")
d = BasicPropositions("d")
e = BasicPropositions("e")
# At least one of these will be true
x = FancyPropositions("x")
y = FancyPropositions("y")
z = FancyPropositions("z")


@proposition(E)
class AtomicProposition:

    def __init__(self, formula: str, tableaux_name: str, branch_number: int, proposition_name: str):
        self.formula = formula
        self.tableaux_name = tableaux_name
        self.branch_number = branch_number
        self.proposition_name = proposition_name

    def _prop_name(self):
        return f"formula.{self.formula}.tableaux.{self.tableaux_name}.branch.{self.branch_number}.atom.{self.data}"


@proposition(E)
class BranchClosed:

    def __init__(self, formula: str, tableaux_name: str, branch_number: int):
        self.formula = formula
        self.tableaux_name = tableaux_name
        self.branch_number = branch_number

    def _prop_name(self):
        return f"formula.{self.formula}.tableaux.{self.tableaux_name}.branch.{self.branch_number}.closed"


@proposition(E)
class TableauxClosed:

    def __init__(self, formula: str, tableaux_name: str):
        self.formula = formula
        self.tableaux_name = tableaux_name

    def _prop_name(self):
        return f"formula.{self.formula}.tableaux.{self.tableaux_name}.closed"


@proposition(E)
class FormulaClassification:

    def __init__(self, formula: str, classification: str):
        self.formula = formula
        self.classification = classification
        assert classification in FORMULA_CLASSIFICATIONS

    def _prop_name(self):
        return f"formula.{self.formula}.classification.{self.classification}"

# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.


def example_theory():
    # Add custom constraints by creating formulas with the variables you created.
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula
    E.add_constraint(~(x & y))
    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    constraint.add_exactly_one(E, a, b, c)

    return E


if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    print("\nVariable likelihoods:")
    for v, vn in zip([a, b, c, x, y, z], 'abcxyz'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()
