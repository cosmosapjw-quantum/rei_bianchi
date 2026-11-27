"""Scalar-only C2c gates; no solver imports or physical evaluations.

All deltas are empirical consistency checks, not continuum error enclosures.
Malformed inputs fail closed. Valid inputs with failed numerical gates retain
their selected values so the registered fallback can be decided externally.
"""
import math


DIRECT_KEYS = ('L_O_bar', 'L_B_bar', 'p_x_bar', 'dipole_x', 'norm_g', 'norm_b')
FORCE_KEYS = ('L_O_bar', 'L_B_bar', 'T_A', 'T_B')
RESIDUAL_KEYS = ('radial_discrete_relative', 'angular_discrete_relative')
PROFILES = ('base', 'h', 'p', 'tail')


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(label + ': finite real number required')
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(label + ': nonfinite number')
    return value


def _positive(value, label):
    value = _number(value, label)
    if value <= 0:
        raise ValueError(label + ': positive number required')
    return value


def _orders(mapping, name, contract):
    if not isinstance(mapping, dict):
        raise ValueError(name + ': order mapping required')
    initial = contract['operators'][name + '_orders']
    allowed = set(initial + contract['operators']['fallback_' + name + '_orders'])
    parsed = {}
    for key, record in mapping.items():
        if not isinstance(key, str) or not key.isdecimal() or str(int(key)) != key:
            raise ValueError(name + ': order keys must be canonical integers')
        order = int(key)
        if order not in allowed or order in parsed:
            raise ValueError(name + ': unregistered or duplicate order')
        if not isinstance(record, dict):
            raise ValueError(name + ': record mapping required')
        keys = DIRECT_KEYS if name == 'direct' else FORCE_KEYS
        for quantity in keys:
            _number(record[quantity], name + '.' + key + '.' + quantity)
        parsed[order] = record
    if len(parsed) < 3 or not set(initial).issubset(parsed):
        raise ValueError(name + ': three registered initial orders required')
    return [(q, parsed[q]) for q in sorted(parsed)[-3:]]


def _limits(contract, name):
    return {key: _positive(value, name + '.' + key)
            for key, value in contract[name].items()}


def _state_metadata(value, contract, radius):
    states = value['states']
    energies = value['energies']
    if not isinstance(states, list) or len(states) != 2:
        raise ValueError('exactly two state metadata records required')
    if not isinstance(energies, list) or len(energies) != 2:
        raise ValueError('exactly two energies required')
    energies = [_number(e, 'energy') for e in energies]
    edges_by_state = []
    configurations = []
    matching = []
    residuals = []
    for sector, state in enumerate(states):
        if (state['m'] != sector or isinstance(state['m'], bool)
                or _number(state['R'], 'state.R') != radius):
            raise ValueError('state sector/radius mismatch')
        if [_number(state['ZA'], 'ZA'), _number(state['ZB'], 'ZB')] != contract['charges']:
            raise ValueError('state charges differ from contract')
        if _number(state['energy'], 'state.energy') != energies[sector]:
            raise ValueError('state energy metadata mismatch')
        cfg = state['config']
        if not isinstance(cfg, dict):
            raise ValueError('state configuration required')
        registered = list(contract['profiles'].values()) + list(contract['fallback_profiles'].values())
        if cfg not in registered:
            raise ValueError('unregistered state configuration')
        edges = state['actual_radial_edges']
        if not isinstance(edges, list) or len(edges) != cfg['radial_elements'] + 1:
            raise ValueError('radial edge count mismatch')
        edges = [_number(edge, 'radial edge') for edge in edges]
        if (edges[0] != 1 or any(a >= b for a, b in zip(edges, edges[1:]))
                or edges[-1] != 1 + 2 * cfg['radial_extent'] / radius
                or _number(state['xi_max'], 'xi_max') != edges[-1]
                or state['actual_radial_elements'] != len(edges) - 1):
            raise ValueError('radial edges/domain metadata mismatch')
        for key in RESIDUAL_KEYS:
            residual = _number(state['residuals'][key], key)
            if residual < 0:
                raise ValueError('negative norm of discrete residual')
            residuals.append(residual)
        match = _number(state['residuals']['matching_absolute'], 'matching residual')
        if match < 0:
            raise ValueError('negative matching residual')
        denominator = max(1., abs(_number(state['separation_radial'], 'separation_radial'))
                          + abs(_number(state['separation_angular'], 'separation_angular')))
        matching.append(match / denominator)
        edges_by_state.append(edges)
        configurations.append(cfg)
    if configurations[0] != configurations[1] or edges_by_state[0] != edges_by_state[1]:
        raise ValueError('pair uses inconsistent meshes/configurations')
    return energies, states, edges_by_state, max(residuals), max(matching)


def _invalid(message):
    return {'pass': False, 'gates': {'input_valid': False},
            'failed_gates': ['input_valid'], 'checks': {},
            'input_error': str(message), 'selected_direct': None,
            'selected_force': None, 'scaled_LO': None,
            'conditions': None, 'tail_knots': None}


def _condition(numerator, denominator):
    # JSON-safe diagnostic. A zero denominator separately fails positivity.
    return numerator / abs(denominator) if denominator != 0 else None


def pair_audit(value, contract):
    """Audit one state pair at its final three available registered orders."""
    try:
        radius = _positive(value['R'], 'R')
        if radius not in contract['new_R']:
            raise ValueError('pair radius not in registered new_R')
        raw = _limits(contract, 'raw_criteria')
        scaled = _limits(contract, 'scaled_criteria')
        direct = _orders(value['direct'], 'direct', contract)
        force = _orders(value['force'], 'force', contract)
        energies, states, edges, residual, matching = _state_metadata(value, contract, radius)
        dark = value['dark']
        expected_dark = {str(n) for n in contract['operators']['phi_nodes']}
        if not isinstance(dark, dict) or set(dark) != expected_dark:
            raise ValueError('registered dark phi-node records required')
        dark_abs = max(abs(_number(record['L_dark_O_bar'], 'dark value')) for record in dark.values())
        gap = energies[1] - energies[0]
        # Force metadata gap is part of its value identity; do not silently use
        # a force evaluation produced from a different pair of energies.
        for _, record in force:
            if _number(record['gap'], 'force gap') != gap:
                raise ValueError('force gap differs from state energies')
        cubic = radius ** 3
        quadratic = radius ** 2
        increments = {}
        for name, sequence, keys in (('direct', direct, DIRECT_KEYS), ('force', force, FORCE_KEYS)):
            increments[name] = [
                {'orders': [qa, qb],
                 'by_quantity_abs': {key: abs(b[key] - a[key]) for key in keys},
                 'L_O_scaled_abs': abs(b['L_O_bar'] - a['L_O_bar']) / cubic}
                for (qa, a), (qb, b) in zip(sequence, sequence[1:])]
        q_direct = max(x for inc in increments['direct'] for x in inc['by_quantity_abs'].values())
        q_force = max(x for inc in increments['force'] for x in inc['by_quantity_abs'].values())
        q_direct_scaled = max(inc['L_O_scaled_abs'] for inc in increments['direct'])
        q_force_scaled = max(inc['L_O_scaled_abs'] for inc in increments['force'])
        # All 3x3 cross-lane combinations must pass. Different direct/force q
        # values are not paired by their numeric order or only by index.
        lane_lo = max(abs(d['L_O_bar'] - f['L_O_bar']) for _, d in direct for _, f in force)
        lane_lb = max(abs(d['L_B_bar'] - f['L_B_bar']) for _, d in direct for _, f in force)
        norm = max(abs(d[key] - 1) for _, d in direct for key in ('norm_g', 'norm_b'))
        origin = max(abs(d['L_O_bar'] - d['L_B_bar'] - radius * d['p_x_bar'] / 3)
                     for _, d in direct)
        momentum = max(abs(d['p_x_bar'] - gap * d['dipole_x']) for _, d in direct)
        bright_floor = 10 * cubic * scaled['L_O_spatial_abs']
        selected_bright_min = min(abs(direct[-1][1]['L_O_bar']), abs(force[-1][1]['L_O_bar']))
        checks = {
            'energy_gap': gap, 'energies': energies,
            'direct_quadrature_max_abs': q_direct,
            'force_quadrature_max_abs': q_force,
            'direct_L_O_quadrature_scaled_abs': q_direct_scaled,
            'force_L_O_quadrature_scaled_abs': q_force_scaled,
            'quadrature_increments': increments,
            'direct_force_L_O_abs': lane_lo,
            'direct_force_L_B_abs': lane_lb,
            'direct_force_L_O_scaled_abs': lane_lo / cubic,
            'norm_error_abs': norm, 'algebraic_residual_max': residual,
            'scaled_matching_residual_max': matching,
            'matching_residual_is_scientific_gate': False,
            'origin_identity_abs': origin,
            'origin_identity_scaled_abs': origin / cubic,
            'momentum_gap_dipole_abs': momentum,
            'momentum_induced_L_O_scaled_abs': momentum / (3 * quadratic),
            'bright_resolution_floor_raw': bright_floor,
            'selected_bright_min_abs': selected_bright_min,
            'dark_abs': dark_abs, 'dark_scaled_abs_diagnostic': dark_abs / cubic}
        gates = {
            'input_valid': True,
            'negative_bound_state_energies': all(e < 0 for e in energies),
            'positive_gap': gap > 0,
            'positive_bright_L_O': all(row['L_O_bar'] > 0 for _, row in direct + force),
            'bright_resolved_scaled': selected_bright_min > bright_floor,
            'direct_quadrature_raw': q_direct <= raw['operator_quadrature_abs'],
            'force_quadrature_raw': q_force <= raw['operator_quadrature_abs'],
            'direct_quadrature_scaled': q_direct_scaled <= scaled['L_O_quadrature_abs'],
            'force_quadrature_scaled': q_force_scaled <= scaled['L_O_quadrature_abs'],
            'direct_force_L_O_raw': lane_lo <= raw['direct_torque_abs'],
            'direct_force_L_B_raw': lane_lb <= raw['direct_torque_abs'],
            'direct_force_L_O_scaled': lane_lo / cubic <= scaled['L_O_direct_force_abs'],
            'norm': norm <= raw['norm_error_abs'],
            'algebraic_residual': residual <= raw['algebraic_residual_relative'],
            'origin_raw': origin <= raw['origin_identity_abs'],
            'origin_scaled': origin / cubic <= scaled['origin_identity_abs'],
            'momentum_raw': momentum <= raw['momentum_gap_dipole_abs'],
            'momentum_scaled': momentum / (3 * quadratic) <= scaled['momentum_induced_L_O_abs'],
            'dark': dark_abs <= raw['dark_abs']}
        selected_d = dict(direct[-1][1])
        selected_f = dict(force[-1][1])
        condition_force = _condition(abs(selected_f['T_A']) + abs(selected_f['T_B']),
                                     selected_f['T_B'] - selected_f['T_A'])
        condition_origin = _condition(abs(selected_d['L_B_bar']) + abs(radius * selected_d['p_x_bar'] / 3),
                                      selected_d['L_O_bar'])
        return {'pass': all(gates.values()), 'R': radius, 'gates': gates,
                'failed_gates': [name for name, passed in gates.items() if not passed],
                'checks': checks, 'selected_direct': selected_d, 'selected_force': selected_f,
                'selected_orders': {'direct': direct[-1][0], 'force': force[-1][0]},
                'terminal_orders': {'direct': [q for q, _ in direct], 'force': [q for q, _ in force]},
                'scaled_LO': {'direct': selected_d['L_O_bar'] / cubic,
                              'force': selected_f['L_O_bar'] / cubic},
                'conditions': {'force': condition_force, 'origin': condition_origin,
                               'certified_roundoff_bound': False},
                'tail_knots': {'states': [{'m': state['m'], 'config': dict(state['config']),
                                          'actual_radial_edges': edge,
                                          'xi_max': state['xi_max']}
                                         for state, edge in zip(states, edges)]},
                'continuum_error_enclosure': False}
    except (KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError) as exc:
        return _invalid(exc)


def quartet_audit(values, contract):
    """Compare a complete, same-tier base/h/p/tail quartet at one radius."""
    try:
        if not isinstance(values, dict) or set(values) != set(PROFILES):
            raise ValueError('exact base/h/p/tail quartet required')
        pairs = {profile: pair_audit(values[profile], contract) for profile in PROFILES}
        gates = {profile + '_pair': record['pass'] for profile, record in pairs.items()}
        if any(not record['gates'].get('input_valid', False) for record in pairs.values()):
            return {'pass': False, 'gates': gates, 'failed_gates': [k for k, v in gates.items() if not v],
                    'checks': {}, 'pairs': pairs, 'input_error': 'invalid pair input'}
        radius = pairs['base']['R']
        if any(record['R'] != radius for record in pairs.values()):
            raise ValueError('quartet radii differ')
        raw = _limits(contract, 'raw_criteria')
        scaled = _limits(contract, 'scaled_criteria')
        matching_tiers = [tier for tier in ('profiles', 'fallback_profiles')
                          if all(values[profile]['states'][sector]['config'] == contract[tier][profile]
                                 for profile in PROFILES for sector in (0, 1))]
        gates['same_registered_profile_tier'] = len(matching_tiers) == 1
        tail_checks = []
        for sector in (0, 1):
            base_edges = values['base']['states'][sector]['actual_radial_edges']
            tail_edges = values['tail']['states'][sector]['actual_radial_edges']
            exact = len(tail_edges) > len(base_edges) and tail_edges[:len(base_edges)] == base_edges
            tail_checks.append({'m': sector, 'base_edge_count': len(base_edges),
                                'tail_edge_count': len(tail_edges), 'exact_inner_prefix_equal': exact})
        gates['tail_inner_knots_exact'] = all(row['exact_inner_prefix_equal'] for row in tail_checks)
        comparisons = {}
        for profile in ('h', 'p', 'tail'):
            energy = max(abs(a - b) for a, b in zip(values['base']['energies'], values[profile]['energies']))
            row = {'energy_delta_max_abs': energy}
            gates[profile + '_energy_raw'] = energy <= raw['energy_refinement_abs']
            for lane in ('direct', 'force'):
                base = pairs['base']['selected_' + lane]
                refined = pairs[profile]['selected_' + lane]
                lo = abs(base['L_O_bar'] - refined['L_O_bar'])
                lb = abs(base['L_B_bar'] - refined['L_B_bar'])
                row[lane] = {'L_O_delta_abs': lo, 'L_B_delta_abs': lb,
                             'L_O_delta_scaled_abs': lo / radius ** 3}
                gates[profile + '_' + lane + '_L_O_raw'] = lo <= raw['L_O_refinement_abs']
                gates[profile + '_' + lane + '_L_B_raw'] = lb <= raw['L_B_refinement_abs']
                gates[profile + '_' + lane + '_L_O_scaled'] = lo / radius ** 3 <= scaled['L_O_spatial_abs']
            comparisons[profile] = row
        return {'pass': all(gates.values()), 'R': radius, 'gates': gates,
                'failed_gates': [name for name, passed in gates.items() if not passed],
                'checks': {'refinements': comparisons, 'tail_knots': tail_checks,
                           'matched_tier': matching_tiers[0] if len(matching_tiers) == 1 else None},
                'pairs': pairs, 'continuum_error_enclosure': False}
    except (KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError) as exc:
        return {'pass': False, 'gates': {'input_valid': False}, 'failed_gates': ['input_valid'],
                'checks': {}, 'pairs': {}, 'input_error': str(exc)}
