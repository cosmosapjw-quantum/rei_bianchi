"""Single bounded PHYS89 primary. Dispatch only after controller ROOT_GO."""
import json
from evidence import UNIT, REPO, identity, main_args, publish, resume


def run():
    import numpy as np
    from fractions import Fraction as Q
    from decimal import Decimal
    from kernel import (parse_mf33, manufactured_fixture, native_bin, mapped_bin,
                        pullback, normalized, ratio_change, JointEvent, ClockDensity,
                        density_cm3_to_m3, capture_temperature_derivative)
    contract = json.loads((UNIT/'CONTRACT.json').read_text())
    table = parse_mf33(REPO/contract['source']['path'])
    a = np.array(table['float_matrix'])
    # This is the only eigen-decomposition in the entire prescribed campaign.
    eig, vectors = np.linalg.eigh(a)
    matrix = [[Q(x) for x in row] for row in table['matrix']]
    witness = None
    for i in range(153):
        for j in range(i+1, 153):
            minor = matrix[i][i]*matrix[j][j]-matrix[i][j]**2
            if minor < 0:
                witness = {'kind': 'EXACT_NEGATIVE_2X2_PRINCIPAL_MINOR', 'indices': [i, j],
                           'entries': [matrix[i][i], matrix[i][j], matrix[j][j]], 'determinant': minor}
                break
        if witness:
            break
    if witness is None and eig[0] < 0:
        # Fixed rationalization of the diagnostic eigenvector; retain all terms.
        v = [Q(float(x)).limit_denominator(10**12) for x in vectors[:, 0]]
        quadratic = sum((v[i]*matrix[i][j]*v[j] for i in range(153) for j in range(153)), Q(0))
        witness = {'kind': 'RATIONAL_QUADRATIC_WITNESS' if quadratic < 0 else 'RATIONALIZATION_NOT_NEGATIVE',
                   'vector': v, 'quadratic': quadratic}
    fixture = manufactured_fixture()
    checks = {}
    checks['raw_symmetry'] = bool(np.array_equal(a, a.T))
    checks['finite_raw'] = bool(np.isfinite(a).all())
    checks['event_energy_exact'] = all(sum(row) == 0 for row in fixture['energy_per_event'])
    checks['reward_group_conservation'] = all(sum(row[g] for row in fixture['reward_rows']) == 0 for g in range(3))
    checks['same_F_covariance_row_sum'] = all(sum(row) == 0 for row in fixture['statistics']['delta_covariance'])
    checks['same_F_linear_reward_sum'] = all(sum(row[1:]) == 0 for row in fixture['statistics']['linear_covariance'])
    checks['ratio_remainder'] = abs(fixture['ratio']['remainder']) <= fixture['ratio']['bound']
    boundaries = table['boundaries']
    checks['boundary_assignment'] = all(native_bin(x, boundaries) == i for i, x in enumerate(boundaries[:-1])
                                         if Decimal('0.00001') <= x <= Decimal('20000000'))
    checks['support_endpoints'] = native_bin(Decimal('0.00001'), boundaries) == 0 and native_bin(Decimal('20000000'), boundaries) == 152
    checks['mapped_boundary_guard'] = mapped_bin(Decimal('2'), [Decimal('0'), Decimal('2'), Decimal('4')], (Decimal('1'), Decimal('3'))) == 1
    checks['pullback_no_jacobian'] = pullback(Q(2), Q(3), 0, 1, fixture['F']) == 6*fixture['F'][0][1]
    checks['capture_Cv'] = capture_temperature_derivative(Q(12), [Q(2), Q(3)], [Q(3,2), Q(3,2)]) == Q(8,5)
    guards = {
        'below_support': lambda: native_bin(Decimal('0.000009999'), boundaries),
        'above_support': lambda: native_bin(Decimal('20000000.001'), boundaries),
        'nan_energy': lambda: native_bin(Decimal('NaN'), boundaries),
        'zero_normalizer': lambda: normalized([Q(0)]*3, [[Q(1)]*3], fixture['F']),
        'negative_intensity': lambda: normalized([Q(-1), Q(3), Q(5)], [[Q(1)]*3], fixture['F']),
        'ratio_denominator': lambda: ratio_change(fixture['r'], fixture['reward_rows'][0], [Q(-2)]*3, Q(1,2)),
        'ratio_rho': lambda: ratio_change(fixture['r'], fixture['reward_rows'][0], [Q(0)]*3, Q(1)),
        'invalid_partition': lambda: JointEvent(Q(1), Q(4), Q(1,2), Q(9,2), Q(2), Q(0)),
        'event_closure': lambda: JointEvent(Q(1), Q(4), Q(1), Q(1), Q(0), Q(0)),
        'energy_ownership': lambda: JointEvent(Q(1), Q(4), Q(1,2), Q(9,2), Q(0), Q(0), False, True).signed_energy(),
        'caloric_ownership': lambda: JointEvent(Q(1), Q(4), Q(1,2), Q(9,2), Q(0), Q(0), False, True).caloric(Q(1), Q(1), Q(1)),
        'nonpositive_Cv': lambda: capture_temperature_derivative(Q(1), [Q(0)], [Q(1)]),
        'negative_density': lambda: ClockDensity(Q(-1), Q(0), Q(0), Q(1)),
        'nonconserved_reference': lambda: ClockDensity(Q(1), Q(1), Q(0), Q(1)).yield_proper(Q(1), Q(1), conserved=True),
        'density_conversion': lambda: density_cm3_to_m3(Q(0))}
    for name, callback in guards.items():
        try:
            callback()
        except ValueError:
            checks['guard_'+name] = True
        else:
            checks['guard_'+name] = False
    if not all(checks.values()):
        raise AssertionError(checks)
    # Decimal quantum is based on each displayed token's last digit. This is
    # conditional on nearest rounding, never a physical or formatter guarantee.
    ulp = [str(Decimal(1).scaleb(x.as_tuple().exponent)) for x in table['packed']]
    float_stats = normalized([float(x) for x in fixture['r']],
                             [[float(x) for x in row] for row in fixture['reward_rows']],
                             [[float(x) for x in row] for row in fixture['F']])
    return {'SOURCE_TABLE.json': {'boundaries': table['boundaries'], 'packed': table['packed'],
                                 'matrix': table['matrix'], 'raw_tokens': table['raw_tokens']},
            'FIXTURE.json': fixture, 'CHECKS.json': checks,
            'FLOAT_FIXTURE.json': {'statistics': float_stats, 'capture_dotT': float(capture_temperature_derivative(12., [2., 3.], [1.5, 1.5]))},
            'MATRIX_DIAGNOSTIC.json': {'eigenvalues_binary64': eig.tolist(), 'eigh_calls': 1,
                'exact_witness': witness, 'raw_matrix_repaired': False,
                'stochastic_covariance_admission': 'DISALLOWED_DISPLAYED_MATRIX' if witness and witness['kind'] != 'RATIONALIZATION_NOT_NEGATIVE' else 'NOT_CERTIFIED_BY_DIAGNOSTIC',
                'strong_no_go': 'NOT_CLAIMED', 'physical_bound': False},
            'TOKEN_ROUNDING.json': {'ULP': ulp,
                'halfULP': [str(Decimal(x)/2) for x in ulp],
                'model': 'CONDITIONAL_NEAREST_ROUNDING_ONLY', 'formatter_guarantee': False, 'physical_bound': False}}


def main():
    args = main_args('primary')
    binding = identity()
    if args.resume:
        print(json.dumps(resume(args.output, 'primary', binding)))
        return
    if args.output.exists():
        raise FileExistsError('CREATE_ONLY_OUTPUT_ALREADY_EXISTS_BEFORE_SCIENCE')
    publish(args.output, 'primary', binding, run())
    print(json.dumps({'status': 'COMPLETE', 'kind': 'primary', 'identity': binding['sha256']}))


if __name__ == '__main__':
    main()
