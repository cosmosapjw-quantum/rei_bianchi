"""Scalar-only C2d gates; no solver imports or physical evaluations.

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
    if set(parsed) not in (set(initial), allowed):
        raise ValueError(name + ': exact initial orders or complete registered fallback required')
    return [(q, parsed[q]) for q in sorted(parsed)[-3:]]


def _limits(contract, name):
    return {key: _positive(value, name + '.' + key)
            for key, value in contract[name].items()}


def _rkey(radius):
    return str(int(radius)) if radius.is_integer() else str(radius)


def _integer(value, label):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(label + ': integer required')
    return value


def _state_metadata(value, contract, radius):
    states, energies = value['states'], value['energies']
    if not isinstance(states, list) or len(states) != 2:
        raise ValueError('exactly two state metadata records required')
    if not isinstance(energies, list) or len(energies) != 2:
        raise ValueError('exactly two energies required')
    energies = [_number(e, 'energy') for e in energies]
    registered = [cfg for tier in ('profiles_by_R', 'fallback_profiles_by_R')
                  for cfg in contract[tier][_rkey(radius)].values()]
    edges_by_state, configurations, matching, residuals, phases = [], [], [], [], []
    for sector, state in enumerate(states):
        if (_integer(state['m'], 'state.m') != sector
                or _number(state['R'], 'state.R') != radius):
            raise ValueError('state sector/radius mismatch')
        if [_number(state['ZA'], 'ZA'), _number(state['ZB'], 'ZB')] != contract['charges']:
            raise ValueError('state charges differ from contract')
        if _number(state['energy'], 'state.energy') != energies[sector]:
            raise ValueError('state energy metadata mismatch')
        cfg = state['config']
        if not isinstance(cfg, dict) or cfg not in registered:
            raise ValueError('unregistered state configuration for radius')
        edges = state['actual_radial_edges']
        if not isinstance(edges, list) or len(edges) != cfg['radial_elements'] + 1:
            raise ValueError('radial edge count mismatch')
        edges = [_number(edge, 'radial edge') for edge in edges]
        if (edges[0] != 1 or any(a >= b for a, b in zip(edges, edges[1:]))
                or edges[-1] != 1 + 2 * cfg['radial_extent'] / radius
                or _number(state['xi_max'], 'xi_max') != edges[-1]
                or _integer(state['actual_radial_elements'], 'actual radial count') != len(edges) - 1):
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
        phase = state['phase']
        if phase['algorithm'] != contract['phase']['algorithm']:
            raise ValueError('phase algorithm differs from registered convention')
        for axis in ('radial', 'angular'):
            record = phase[axis]
            points = _integer(record['quadrature_points'], 'phase quadrature points')
            index = _integer(record['dominant_index'], 'phase dominant index')
            coordinate = _number(record['dominant_coordinate'], 'phase coordinate')
            dominant = _number(record['dominant_value'], 'phase dominant value')
            fraction = _number(record['negative_l2_fraction'], 'negative L2 fraction')
            lo, hi = (1., edges[-1]) if axis == 'radial' else (-1., 1.)
            if (points != cfg[axis + '_elements'] * cfg['quadrature_order']
                    or not 0 <= index < points or not lo < coordinate < hi
                    or not 0 <= fraction <= 1):
                raise ValueError('invalid phase sample metadata')
            phases.append({'m': sector, 'axis': axis, 'dominant_value': dominant,
                           'negative_l2_fraction': fraction})
        edges_by_state.append(edges)
        configurations.append(cfg)
    if configurations[0] != configurations[1] or edges_by_state[0] != edges_by_state[1]:
        raise ValueError('pair uses inconsistent meshes/configurations')
    return energies, states, edges_by_state, max(residuals), max(matching), phases


def _invalid(message):
    return {'pass': False, 'gates': {'input_valid': False},
            'failed_gates': ['input_valid'], 'checks': {},
            'input_error': str(message), 'selected_direct': None,
            'selected_force': None, 'scaled': None,
            'conditions': None, 'tail_knots': None}


def _condition(numerator, denominator):
    return numerator / abs(denominator) if denominator != 0 else None


def _finite_output(value):
    if isinstance(value, dict):
        for child in value.values():
            _finite_output(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _finite_output(child)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError('nonfinite derived scalar')
    return value


def _scaled_delta(lo, lb, radius):
    return {'Q_O': lo / radius, 'Q_B': lb * radius ** 2}


def pair_audit(value, contract):
    """Audit endpoint pair; archive all original records outside this evaluator.

    Registered frozen-state fallback selects its terminal three orders but never
    rewrites the initial records or represents a continuum error certificate.
    """
    try:
        radius = _positive(value['R'], 'R')
        if radius not in contract['new_R']:
            raise ValueError('pair radius not in registered new_R')
        raw, scaled = _limits(contract, 'raw_criteria'), _limits(contract, 'scaled_criteria')
        direct, force = _orders(value['direct'], 'direct', contract), _orders(value['force'], 'force', contract)
        energies, states, edges, residual, matching, phases = _state_metadata(value, contract, radius)
        dark = value['dark']
        if not isinstance(dark, dict) or set(dark) != {str(n) for n in contract['operators']['phi_nodes']}:
            raise ValueError('registered dark phi-node records required')
        dark_abs = max(abs(_number(row['L_dark_O_bar'], 'dark value')) for row in dark.values())
        gap = energies[1] - energies[0]
        for _, row in force:
            if _number(row['gap'], 'force gap') != gap:
                raise ValueError('force gap differs from state energies')
        increments, q_raw, q_scaled = {}, {}, {}
        for lane, sequence, keys in (('direct', direct, DIRECT_KEYS), ('force', force, FORCE_KEYS)):
            increments[lane] = []
            for (qa, a), (qb, b) in zip(sequence, sequence[1:]):
                by_quantity = {key: abs(b[key] - a[key]) for key in keys}
                increments[lane].append({'orders': [qa, qb], 'by_quantity_abs': by_quantity,
                    'scaled_abs': _scaled_delta(by_quantity['L_O_bar'], by_quantity['L_B_bar'], radius)})
            q_raw[lane] = max(d for inc in increments[lane] for d in inc['by_quantity_abs'].values())
            q_scaled[lane] = {q: max(inc['scaled_abs'][q] for inc in increments[lane]) for q in ('Q_O', 'Q_B')}
        # Every terminal direct/force combination: no favorable order pairing.
        lane_lo = max(abs(d['L_O_bar'] - f['L_O_bar']) for _, d in direct for _, f in force)
        lane_lb = max(abs(d['L_B_bar'] - f['L_B_bar']) for _, d in direct for _, f in force)
        lane_scaled = _scaled_delta(lane_lo, lane_lb, radius)
        norm = max(abs(d[key] - 1) for _, d in direct for key in ('norm_g', 'norm_b'))
        origin = max(abs(d['L_O_bar'] - d['L_B_bar'] - radius * d['p_x_bar'] / 3) for _, d in direct)
        momentum = max(abs(d['p_x_bar'] - gap * d['dipole_x']) for _, d in direct)
        origin_scaled = {'Q_O': origin / radius, 'Q_B': radius ** 2 * origin}
        momentum_scaled = {'Q_O': momentum / 3, 'Q_B': radius ** 3 * momentum / 3}
        selected_d, selected_f = dict(direct[-1][1]), dict(force[-1][1])
        selected_scaled = {'Q_O': {'direct': selected_d['L_O_bar'] / radius,
                                   'force': selected_f['L_O_bar'] / radius},
                           'Q_B': {'direct': -radius ** 2 * selected_d['L_B_bar'],
                                   'force': -radius ** 2 * selected_f['L_B_bar']}}
        phase_max = max(row['negative_l2_fraction'] for row in phases)
        checks = {'energy_gap': gap, 'energies': energies,
                  'direct_quadrature_max_abs': q_raw['direct'], 'force_quadrature_max_abs': q_raw['force'],
                  'quadrature_scaled_abs': q_scaled, 'quadrature_increments': increments,
                  'direct_force_L_O_abs': lane_lo, 'direct_force_L_B_abs': lane_lb,
                  'direct_force_scaled_abs': lane_scaled,
                  'direct_force_terminal_comparisons': len(direct) * len(force),
                  'norm_error_abs': norm, 'algebraic_residual_max': residual,
                  'scaled_matching_residual_max': matching, 'matching_residual_is_scientific_gate': False,
                  'origin_identity_abs': origin, 'origin_scaled_abs': origin_scaled,
                  'momentum_gap_dipole_abs': momentum, 'momentum_scaled_abs': momentum_scaled,
                  'dark_abs': dark_abs, 'phase_samples': phases,
                  'max_weighted_negative_L2_fraction': phase_max,
                  'bright_resolution_floor_scaled': {q: 10 * scaled[q + '_spatial_abs'] for q in selected_scaled},
                  'bright_legacy_absolute_floor': contract['bright_detectability']['original_absolute_LO_floor_retained']}
        gates = {'input_valid': True, 'negative_bound_state_energies': all(e < 0 for e in energies),
                 'positive_gap': gap > 0,
                 'positive_bright_Q_O': all(row['L_O_bar'] > 0 for _, row in direct + force),
                 'positive_bright_Q_B': all(row['L_B_bar'] < 0 for _, row in direct + force),
                 'bright_legacy_absolute_LO': min(selected_d['L_O_bar'], selected_f['L_O_bar']) > checks['bright_legacy_absolute_floor'],
                 'norm': norm <= raw['norm_error_abs'],
                 'algebraic_residual': residual <= raw['algebraic_residual_relative'],
                 'origin_raw': origin <= raw['origin_identity_abs'],
                 'momentum_raw': momentum <= raw['momentum_gap_dipole_abs'],
                 'direct_force_L_O_raw': lane_lo <= raw['direct_torque_abs'],
                 'direct_force_L_B_raw': lane_lb <= raw['direct_torque_abs'],
                 'phase_positive': all(row['dominant_value'] > 0 for row in phases),
                 'phase_negative_L2': phase_max <= contract['phase']['max_weighted_negative_L2_fraction'],
                 'dark': dark_abs <= raw['dark_abs']}
        for lane in ('direct', 'force'):
            gates[lane + '_quadrature_raw'] = q_raw[lane] <= raw['operator_quadrature_abs']
            for q in ('Q_O', 'Q_B'):
                gates[lane + '_quadrature_' + q + '_scaled'] = q_scaled[lane][q] <= scaled[q + '_quadrature_abs']
        for q in ('Q_O', 'Q_B'):
            gates['bright_resolved_' + q + '_scaled'] = min(selected_scaled[q].values()) > 10 * scaled[q + '_spatial_abs']
            gates['direct_force_' + q + '_scaled'] = lane_scaled[q] <= scaled[q + '_direct_force_abs']
            gates['origin_' + q + '_scaled'] = origin_scaled[q] <= scaled[q + '_origin_abs']
            gates['momentum_' + q + '_scaled'] = momentum_scaled[q] <= scaled[q + '_momentum_abs']
        return _finite_output({'pass': all(gates.values()), 'R': radius, 'gates': gates,
                'failed_gates': [key for key, passed in gates.items() if not passed], 'checks': checks,
                'selected_direct': selected_d, 'selected_force': selected_f,
                'selected_orders': {'direct': direct[-1][0], 'force': force[-1][0]},
                'terminal_orders': {'direct': [q for q, _ in direct], 'force': [q for q, _ in force]},
                'scaled': selected_scaled,
                'conditions': {'force_O': _condition(abs(selected_f['T_A']) + abs(selected_f['T_B']), selected_f['T_B'] - selected_f['T_A']),
                               'origin_B': _condition(abs(selected_d['L_O_bar']) + abs(radius * selected_d['p_x_bar'] / 3), selected_d['L_B_bar']),
                               'origin_B_leading': 1.5 * radius ** 3,
                               'certified_roundoff_bound': False},
                'tail_knots': {'states': [{'m': state['m'], 'config': dict(state['config']), 'actual_radial_edges': edge, 'xi_max': state['xi_max']}
                                         for state, edge in zip(states, edges)]},
                'continuum_error_enclosure': False})
    except (KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError, AttributeError) as exc:
        return _invalid(exc)


def quartet_audit(values, contract):
    """A single original or fallback quartet; no replacement of failed history."""
    try:
        if not isinstance(values, dict) or set(values) != set(PROFILES):
            raise ValueError('exact base/h/p/tail quartet required')
        pairs = {profile: pair_audit(values[profile], contract) for profile in PROFILES}
        gates = {'input_valid': all(row['gates'].get('input_valid', False) for row in pairs.values())}
        gates.update({profile + '_pair': row['pass'] for profile, row in pairs.items()})
        if not gates['input_valid']:
            return {'pass': False, 'gates': gates, 'failed_gates': [k for k, v in gates.items() if not v],
                    'checks': {}, 'pairs': pairs, 'input_error': 'invalid pair input', 'continuum_error_enclosure': False}
        radius = pairs['base']['R']
        if any(row['R'] != radius for row in pairs.values()):
            raise ValueError('quartet radii differ')
        raw, scaled = _limits(contract, 'raw_criteria'), _limits(contract, 'scaled_criteria')
        matching_tiers = [tier for tier in ('profiles_by_R', 'fallback_profiles_by_R')
                          if all(values[profile]['states'][sector]['config'] == contract[tier][_rkey(radius)][profile]
                                 for profile in PROFILES for sector in (0, 1))]
        gates['same_registered_profile_tier'] = len(matching_tiers) == 1
        tail_checks = []
        for sector in (0, 1):
            base_edges = values['base']['states'][sector]['actual_radial_edges']
            tail_edges = values['tail']['states'][sector]['actual_radial_edges']
            exact = len(tail_edges) > len(base_edges) and tail_edges[:len(base_edges)] == base_edges
            tail_checks.append({'m': sector, 'base_edge_count': len(base_edges), 'tail_edge_count': len(tail_edges),
                                'exact_inner_prefix_equal': exact})
        gates['tail_inner_knots_exact'] = all(row['exact_inner_prefix_equal'] for row in tail_checks)
        comparisons = {}
        for profile in ('h', 'p', 'tail'):
            energy = max(abs(a - b) for a, b in zip(values['base']['energies'], values[profile]['energies']))
            row = {'energy_delta_max_abs': energy}
            gates[profile + '_energy_raw'] = energy <= raw['energy_refinement_abs']
            for lane in ('direct', 'force'):
                base, refined = pairs['base']['selected_' + lane], pairs[profile]['selected_' + lane]
                lo, lb = abs(base['L_O_bar'] - refined['L_O_bar']), abs(base['L_B_bar'] - refined['L_B_bar'])
                delta = _scaled_delta(lo, lb, radius)
                row[lane] = {'L_O_delta_abs': lo, 'L_B_delta_abs': lb, 'scaled_abs': delta}
                gates[profile + '_' + lane + '_L_O_raw'] = lo <= raw['L_O_refinement_abs']
                gates[profile + '_' + lane + '_L_B_raw'] = lb <= raw['L_B_refinement_abs']
                for q in ('Q_O', 'Q_B'):
                    gates[profile + '_' + lane + '_' + q + '_scaled'] = delta[q] <= scaled[q + '_spatial_abs']
            comparisons[profile] = row
        return _finite_output({'pass': all(gates.values()), 'R': radius, 'gates': gates,
                'failed_gates': [key for key, passed in gates.items() if not passed],
                'checks': {'refinements': comparisons, 'tail_knots': tail_checks,
                           'matched_tier': matching_tiers[0] if len(matching_tiers) == 1 else None},
                'pairs': pairs, 'selected_direct': pairs['base']['selected_direct'],
                'selected_force': pairs['base']['selected_force'], 'scaled': pairs['base']['scaled'],
                'conditions': pairs['base']['conditions'], 'continuum_error_enclosure': False})
    except (KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError, AttributeError) as exc:
        return {'pass': False, 'gates': {'input_valid': False}, 'failed_gates': ['input_valid'],
                'checks': {}, 'pairs': {}, 'input_error': str(exc), 'continuum_error_enclosure': False}

