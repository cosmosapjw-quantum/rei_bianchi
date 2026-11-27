"""Paper-derived clean-room ARSENY reimplementation seed.

NOT AUTHOR CODE.
"""
from .state_index import state_index, enumerate_states
from .transition import transition_block, ordered_probability_matrix
from .cross_section import integrate_probability_matrix
from .io_contract import ArsenyInput, parse_arseny_input

__all__ = [
    "state_index", "enumerate_states",
    "transition_block", "ordered_probability_matrix",
    "integrate_probability_matrix",
    "ArsenyInput", "parse_arseny_input",
]

from .term_real import TermPoint, solve_real_term, trace_real_curve, term_residuals

from .correlation import UnitedState, SeparatedState, cordir_heh, corinv_heh, asymptotic_electronic_energy

from .term_complex import ComplexTermPoint, BranchPointSolution, continue_complex_from_real, solve_branch_point

from .stueckelberg import StueckelbergResult, stueckelberg_delta, stueckelberg_probability, order_hidden_crossings
from .rotational import (
    RotationalBlockResult, RotationalConvergenceResult,
    angular_momentum_operators, epsilon_rotational, s_sigma_boundary,
    rotational_block, rotational_convergence, full_rotational_probability,
)

from .eq50_scoped import ScopedBranch, BRANCHES_NMAX3, ordered_scoped_branches, branch_probability_record, assemble_scoped_eq50
