"""Exact bounded HE31 polynomial/matrix checks using rational arithmetic.

SymPy was unavailable in this runtime. This standard-library implementation
introduces no package/environment change and performs no ODE integration.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json


def add(a, b):
    return [(a[i] if i < len(a) else Q(0)) +
            (b[i] if i < len(b) else Q(0)) for i in range(max(len(a), len(b)))]


def scale(a, k):
    return [k*x for x in a]


def mul(a, b):
    out = [Q(0)]*(len(a)+len(b)-1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i+j] += ai*bj
    return out


def integrate(a):
    return sum((2*a[i]/(i+1) for i in range(0, len(a), 2)), Q(0))


def mv(m, v):
    return [sum((mi*vi for mi, vi in zip(row, v)), Q(0)) for row in m]


polynomials = [[Q(1)], [Q(0), Q(1)]]
for n in range(1, 8):
    polynomials.append(scale(add(scale([Q(0)]+polynomials[-1], 2*n+1),
                                  scale(polynomials[-2], -n)), Q(1, n+1)))
kernel = [Q(3, 8), Q(0), Q(3, 8)]
eigenvalues = [integrate(mul(kernel, p)) for p in polynomials]
assert eigenvalues == [1, 0, Q(1, 10), 0, 0, 0, 0, 0, 0]
matrix = [[Q(-9, 10), Q(-2, 5)], [Q(-3, 20), Q(-2, 5)]]
fast = [Q(6, 7), Q(3, 14)]
slow = [Q(1, 7), Q(-3, 14)]
assert mv(matrix, fast) == scale(fast, Q(-1))
assert mv(matrix, slow) == scale(slow, Q(-3, 10))
assert add(fast, slow) == [1, 0]
assert mv(matrix, [Q(1), Q(0)]) == [Q(-9, 10), Q(-3, 20)]
second_derivative = mv(matrix, mv(matrix, [Q(1), Q(0)]))[0]
delta_quadratic = second_derivative/2 - Q(9, 10)**2/2
assert delta_quadratic == Q(3, 100)
f2 = scale(polynomials[2], Q(5))
df2 = [(i+1)*f2[i+1] for i in range(len(f2)-1)]
liouville_f2 = add(mul([Q(0), Q(3), Q(0), Q(-3)], df2),
                   mul([Q(4), Q(0), Q(-12)], f2))
A02 = integrate(liouville_f2)/2
assert A02 == -2
commutator_02 = A02*Q(9, 10)
assert commutator_02 == Q(-9, 5)
unit_ratio = Q(10**6, 100*10000)
assert unit_ratio == 1
out = dict(status="PASS_EXACT_ALGEBRA", engine="Python fractions.Fraction",
           ode_calls=0, benchmark_runs=0,
           initial_unavailable_dependency="SymPy; replaced by standard-library exact algebra",
           unpolarized_kernel_eigenvalues=[str(x) for x in eigenvalues],
           unpolarized_damping_coefficients=[str(1-x) for x in eigenvalues],
           polarized_i2_q_matrix=[[str(x) for x in row] for row in matrix],
           polarized_eigenvalues=["-1", "-3/10"],
           fast_mode_amplitude=[str(x) for x in fast],
           slow_mode_amplitude=[str(x) for x in slow],
           polarized_closed_form="(6 exp(-tau)+exp(-3 tau/10))/7; 3(exp(-tau)-exp(-3 tau/10))/14",
           polarized_closed_form_eigenvector_residuals="exact zero",
           initially_unpolarized_scalar_difference_tau2_coefficient=str(delta_quadratic),
           energy_matrix_A02=str(A02), commutator_AD_minus_DA_02=str(commutator_02),
           SI_to_cgs_collision_frequency_ratio=str(unit_ratio),
           source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
target = Path(__file__).with_name("THEORY_ALGEBRA_CHECK.json")
target.write_text(json.dumps(out, indent=2)+"\n")
print(json.dumps(out, indent=2))
