"""Exact synthetic arithmetic examples for T2, not a proof checker or HH runner."""
from fractions import Fraction as F
import json


def dyadic_mesh(length, area, derivative_bound, epsilon):
    """The finite rational-comparison choice specified in T2.4."""
    assert length > 0 and area > 0 and derivative_bound >= 0 and epsilon > 0
    n = 1
    while derivative_bound and length / n > epsilon / (area * derivative_bound):
        n *= 2
    return n


def run():
    checks = []
    # Entire polynomial f(t,u)=t*u^2; H(t)=t/3 by exact antiderivative.
    midpoint_value = F(1, 6)
    assert F(0) != midpoint_value != F(1, 3)
    checks.append({"name": "midpoint_only_fails_whole_parameter_box",
                   "center_value": str(midpoint_value),
                   "excluded_exact_values": ["0", "1/3"], "passed": True})

    real_lo, real_hi = F(1, 3), F(2, 3)
    imag_lo, imag_hi = -F(1, 3), F(1, 3)
    real_radius = (real_hi - real_lo) / 2
    imag_radius = (imag_hi - imag_lo) / 2
    assert real_radius == F(1, 6) and imag_radius == F(1, 3)
    assert real_radius > F(1, 10) and imag_radius > F(1, 10)
    checks.append({"name": "intrinsic_complex_parameter_width",
                   "minimum_real_radius": str(real_radius),
                   "minimum_imag_radius": str(imag_radius),
                   "impossible_radius_cap": "1/10", "passed": True})

    # A direct exact quadrature sum is compared with an independent closed
    # form: sum midpoint^2 / N = 1/3 - 1/(12*N^2).
    tested_grids = 0
    for nt in (1, 2, 4):
        for nu in (1, 2, 4, 8):
            q = sum((F(2*i+1, 2*nt) * F(2*j+1, 2*nu)**2 / (nt*nu)
                     for i in range(nt) for j in range(nu)), F(0))
            exact = F(1, 6)
            error = exact - q
            assert error == F(1, 24*nu*nu)
            bound = F(1, 4*nt) + F(2, 4*nu)
            assert 0 <= error <= bound
            tested_grids += 1
    checks.append({"name": "midpoint_quadrature_exact_polynomial_examples",
                   "grids": tested_grids, "passed": True})

    # On K=[-1,2]+i[-1,1] in both variables, |t*u^2|<=5*sqrt(5)<=15.
    # With delta_t=delta_u=1, Cauchy's L_t=L_u=15 is a safe rational bound.
    epsilon, area, lt, lu = F(1, 32), F(1), F(15), F(15)
    nt = dyadic_mesh(F(1), area, lt, epsilon)
    nu = dyadic_mesh(F(1), area, lu, epsilon)
    eta = epsilon / (2*area)
    e = area * (lt/(4*nt) + lu/(4*nu) + eta)
    assert nt == nu == 512 and e == F(31, 1024) and e <= epsilon
    assert dyadic_mesh(F(3), F(7), F(0), F(1, 10)) == 1
    checks.append({"name": "constructive_mesh_and_evaluation_error_budget",
                   "nt": nt, "nu": nu, "point_evaluation_eta": str(eta),
                   "certified_component_radius_bound": str(e),
                   "requested_epsilon": str(epsilon), "passed": True,
                   "note": "mesh arithmetic only; these 262144 evaluations were not run"})

    # Additivity requires all panels, independently of how they were chosen.
    panels = [F(1, 2), F(1, 4), F(1, 8), F(1, 8)]
    assert sum(panels, F(0)) == 1
    assert sum(panels[:-1], F(0)) == F(7, 8)
    assert sum(panels + [panels[-1]], F(0)) == F(9, 8)
    checks.append({"name": "adaptive_coverage_is_not_optional",
                   "complete_constant_integral": "1",
                   "omitted_panel_result": "7/8",
                   "double_counted_panel_result": "9/8", "passed": True})

    # n=1 means the zeroth Taylor coefficient, not the derivative.
    assert F(3, 2)/3 == F(1, 2) and F(1, 2) != F(1, 3)
    checks.append({"name": "order_one_zeroth_coefficient_distinction",
                   "H_at_three_halves": "1/2", "H_derivative": "1/3",
                   "passed": True})

    assert nt * nu > 1000
    checks.append({"name": "finite_existence_does_not_imply_fixed_cap_success",
                   "constructed_point_count": nt*nu, "example_cap": 1000,
                   "proper_capped_result": "INCONCLUSIVE", "passed": True})
    return {"schema": "WU088_T2_EXACT_SYNTHETIC_ARITHMETIC_CHECKS_V1",
            "checks": checks, "passed": all(x["passed"] for x in checks),
            "actual_HH_runs": 0, "native_builds": 0,
            "theorem_proved_by_tests": False,
            "authority": "Proof text T2_UNIFORM_INTERIOR_THEOREM.md; examples only"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
