"""Independent exact checks; no author implementation or molecular solver imports."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import itertools
import json
import os

checks = []

def record(name, actual, expected):
    assert actual == expected, (name, actual, expected)
    checks.append({'name': name, 'actual': str(actual),
                   'expected': str(expected), 'passed': True})

# Derive dimensions by enumerating hydrogenic angular quantum numbers.
for n in (1, 2, 3):
    states = [(l, m) for l in range(n) for m in range(-l, l+1)]
    record(f'UA_n{n}_full_dimension', len(states), n*n)
    for m in (0, 1):
        record(f'UA_n{n}_m{m}_dimension', sum(mm == m for _, mm in states),
               max(0, n-m))
ua_energy = lambda n: -F(9, 2*n*n)
record('UA_ground_to_n2_gap_EA', ua_energy(2)-ua_energy(1), F(27, 8))
record('UA_n2_to_n3_gap_EA', ua_energy(3)-ua_energy(2), F(5, 8))
record('large_R_rank5_external_gap_limit_EA',
       min(F(3,2), -F(2,9)+F(1,2), -F(1,8)+F(1,2), F(1,2)), F(5,18))
# n>=3 full shells individually exceed either rank 5 or 6. Enumerating
# the only eligible complete shells proves the finite integer obstruction.
def allowed_shell_sums(first_n, max_rank):
    eligible = [n*n for n in range(first_n, max_rank+1) if n*n <= max_rank]
    return sorted({sum(rank for rank, selected in zip(eligible, selection) if selected)
                   for selection in itertools.product((False, True), repeat=len(eligible))
                   if sum(rank for rank, selected in zip(eligible, selection) if selected) <= max_rank})
record('excited_complete_shell_ranks_leq6', allowed_shell_sums(2, 6), [0, 4])
record('all_complete_shell_ranks_leq6', allowed_shell_sums(1, 6), [0, 1, 4, 5])

# Independent mass/energy bookkeeping in artificial consistent units.
Mp, Mt, velocity = F(4), F(1), F(3)
mu = Mp*Mt/(Mp+Mt)
lab, relative = Mp*velocity**2/2, mu*velocity**2/2
record('target_rest_energy_conversion', relative/lab, Mt/(Mp+Mt))
record('A4_lab_per_unit_to_relative_energy', relative/(lab/4), F(4,5))

# A rational positive turning point constructed from energy conservation.
E, K, b, turning = F(2), F(12), F(4), F(8)
J2 = 2*mu*E*b*b
record('Rutherford_quadratic_residual', E*turning**2-K*turning-E*b*b, F(0))
record('Rutherford_radial_energy_at_turning', J2/(2*mu*turning**2)+K/turning, E)
record('Rutherford_head_on_positive_turning', K/E, F(6))

# Straight-line geometry with a 5-12-13 triangle, including angular sign.
b, velocity, time, radius = F(5), F(3), F(4), F(13)
radial_velocity = velocity**2*time/radius
theta_dot = -b*velocity/radius**2  # theta = atan2(b, v*t).
record('straight_line_radius_squared', b*b+(velocity*time)**2, radius**2)
record('straight_line_speed_decomposition',
       radial_velocity**2+(radius*theta_dot)**2, velocity**2)
record('straight_line_theta_dot_sign', theta_dot < 0, True)

report = {
    'scope': 'Independent rational arithmetic and quantum-number counting only; '
             'not an eigensolve or functional-analytic proof by computation',
    'author_code_imported': False,
    'old_scientific_suites_rerun': 0,
    'new_physical_evaluations': 0,
    'checks': checks,
    'passed': all(c['passed'] for c in checks),
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
destination = Path(__file__).with_suffix('.json')
with destination.open('xb') as stream:
    stream.write((json.dumps(report, indent=2, sort_keys=True)+'\n').encode())
    stream.flush()
    os.fsync(stream.fileno())
directory = os.open(destination.parent, os.O_DIRECTORY)
os.fsync(directory)
os.close(directory)
print(json.dumps({'passed': report['passed'], 'exact_checks': len(checks),
                  'output': str(destination)}))
