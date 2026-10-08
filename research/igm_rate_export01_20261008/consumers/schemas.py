"""Schema-only BASS/REC intake. No solver, history inference or donor calls."""
from fractions import Fraction


class SchemaError(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def require(value, code):
    if not value:
        raise SchemaError(code)


def number(value, code):
    require(isinstance(value, (int, str)) and not isinstance(value, bool), code)
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError):
        raise SchemaError(code) from None


def authority(packet, key):
    require(isinstance(packet.get(key), str) and bool(packet[key].strip()), 'MISSING_' + key.upper())
    return packet[key]


def identity(packet):
    return {key: authority(packet, key) for key in ('source_identity', 'state_identity', 'clock_authority', 'frame_authority')}


def fraction_state(state):
    require(state.get('species_denominators') == {'x_HII': 'H nuclei', 'x_HeII': 'He nuclei', 'x_HeIII': 'He nuclei'}, 'SPECIES_DENOMINATOR_MISMATCH')
    require(state.get('density_units') == 'proper cm^-3', 'DENSITY_CONVENTION_MISMATCH')
    require(state.get('density_conversion_count') == 0, 'DOUBLE_DENSITY_CONVERSION')
    nh, nhe = (number(state.get(k), 'MISSING_NUCLEAR_DENSITY') for k in ('n_H', 'n_He'))
    hii, heii, heiii = (number(state.get(k), 'MISSING_SPECIES_FRACTION') for k in ('x_HII', 'x_HeII', 'x_HeIII'))
    require(nh >= 0 and nhe >= 0, 'NEGATIVE_DENSITY')
    require(0 <= hii <= 1 and heii >= 0 and heiii >= 0 and heii + heiii <= 1, 'INVALID_SPECIES_FRACTION')
    return nh, nhe, hii, heii, heiii, nh * hii + nhe * (heii + 2 * heiii)


def absent(schema):
    return {'schema': schema, 'payload_status': 'NOT_PROVIDED', 'physical_admission': 'HOLD', 'observer_calls': 0, 'provider_calls': 0}


def bass_observable(packet=None):
    """Validate prescribed data; return exact unit conversion, never integrate it."""
    if packet is None:
        return absent('BASS-OBS-SCHEMA01/v1')
    ids = identity(packet)
    require(packet.get('payload_scope') == 'schema_fixture', 'ACTUAL_HISTORY_ADMISSION_NOT_IMPLEMENTED')
    require(packet.get('time_units') == 'normal seconds', 'MISSING_NORMAL_TIME_MAPPING')
    edges = [number(v, 'INVALID_NORMAL_TIME') for v in packet.get('normal_time_edges', [])]
    require(len(edges) >= 2 and all(b > a for a, b in zip(edges, edges[1:])), 'NONINCREASING_NORMAL_TIME_EDGES')
    epochs = packet.get('epoch_ln_a_exact', [])
    require(len(epochs) == len(edges), 'MISSING_EXACT_EPOCHS')
    epochs = [number(v, 'INVALID_EXACT_EPOCH') for v in epochs]
    tail = number(packet.get('caller_observer_tail'), 'MISSING_OBSERVER_TAIL')
    require(tail >= 0, 'INVALID_OBSERVER_TAIL')
    authority(packet, 'observer_tail_authority')
    mode = packet.get('reconstruction')
    if mode == 'endpoint_linear_density':
        states = packet.get('endpoint_states', [])
        require(len(states) == len(edges), 'ENDPOINT_COUNT_MISMATCH')
        ne = [fraction_state(s)[-1] * 1000000 for s in states]
        require(packet.get('doppler_applied_count') == 0, 'DOUBLE_DOPPLER_APPLICATION')
        d = number(packet.get('fixed_doppler_D'), 'MISSING_FRAME_DOPPLER')
        require(d > 0, 'INVALID_FRAME_DOPPLER')
        c = number(packet.get('c_m_s'), 'MISSING_RATE_CONSTANT')
        sigma = number(packet.get('sigma_T_m2'), 'MISSING_RATE_CONSTANT')
        require(c > 0 and sigma > 0, 'INVALID_RATE_CONSTANT')
        constants_owner = authority(packet, 'rate_constants_authority')
        rates = [c * sigma * n * d for n in ne]
        values = {'proper_ne_m3': [str(v) for v in ne], 'endpoint_q_t_s1': [str(v) for v in rates], 'density_units': 'proper m^-3', 'rate_units': 's^-1 normal time', 'fixed_doppler_D': str(d), 'density_conversion_factor': 1000000, 'c_m_s': str(c), 'sigma_T_m2': str(sigma), 'rate_constants_authority': constants_owner, 'density_conversion_count': 1, 'doppler_applied_count': 1}
    elif mode == 'supplied_frozen_cell_rate':
        require(packet.get('rate_units') == 's^-1 normal time', 'RATE_UNIT_MISMATCH')
        require(packet.get('doppler_applied_count') == 1, 'FROZEN_RATE_DOPPLER_NOT_ONCE')
        authority(packet, 'rate_authority')
        rates = [number(v, 'INVALID_CELL_RATE') for v in packet.get('cell_q_t_s1', [])]
        require(len(rates) == len(edges) - 1 and all(v >= 0 for v in rates), 'INVALID_CELL_RATES')
        values = {'cell_q_t_s1': [str(v) for v in rates], 'rate_units': 's^-1 normal time', 'rate_authority': packet['rate_authority'], 'density_conversion_count': 'NOT_APPLICABLE', 'doppler_applied_count': 1}
    else:
        raise SchemaError('MISSING_DECLARED_RECONSTRUCTION')
    return {**absent('BASS-OBS-SCHEMA01/v1'), **ids, **values, 'payload_status': 'SCHEMA_FIXTURE_ONLY', 'normal_time_edges': [str(v) for v in edges], 'epoch_ln_a_exact': [str(v) for v in epochs], 'reconstruction': mode, 'caller_observer_tail': str(tail), 'observer_tail_authority': packet['observer_tail_authority'], 'time_units': 'normal seconds', 'epoch_units': 'ln a exact rational', 'clock_conversion_count': 0}


def rec_initial(packet=None):
    """Validate initial-state metadata; do not infer radiation or matched history."""
    if packet is None:
        return absent('REC-INITIAL-SCHEMA01/v1')
    ids = identity(packet)
    require(packet.get('payload_scope') == 'schema_fixture', 'ACTUAL_HISTORY_ADMISSION_NOT_IMPLEMENTED')
    epoch = number(packet.get('epoch_ln_a_exact'), 'MISSING_EPOCH')
    require(packet.get('temperature_units') == 'K', 'TEMPERATURE_UNIT_MISMATCH')
    tgas = number(packet.get('Tgas'), 'MISSING_GAS_TEMPERATURE')
    trad = number(packet.get('Trad'), 'MISSING_RADIATION_TEMPERATURE')
    require(tgas > 0 and trad > 0, 'INVALID_TEMPERATURE')
    radiation = authority(packet, 'radiation_authority')
    authority(packet, 'gas_temperature_authority')
    require(packet.get('radiation_model') in ('blackbody', 'explicit_spectrum'), 'MISSING_RADIATION_MODEL')
    if packet['radiation_model'] == 'explicit_spectrum':
        authority(packet, 'radiation_spectrum_identity')
    nh, nhe, hii, heii, heiii, ne = fraction_state(packet)
    require(number(packet.get('n_e'), 'MISSING_ELECTRON_DENSITY') == ne, 'ELECTRON_DENSITY_MISMATCH')
    require(number(packet.get('x_e_per_H'), 'MISSING_ELECTRON_FRACTION') * nh == ne and nh > 0, 'ELECTRON_FRACTION_MISMATCH')
    return {**absent('REC-INITIAL-SCHEMA01/v1'), **ids, 'payload_status': 'SCHEMA_FIXTURE_ONLY', 'epoch_ln_a_exact': str(epoch), 'epoch_units': 'ln a exact rational', 'n_H': str(nh), 'n_He': str(nhe), 'n_e': str(ne), 'density_units': 'proper cm^-3', 'species_denominators': packet['species_denominators'], 'x_HII': str(hii), 'x_HeII': str(heii), 'x_HeIII': str(heiii), 'x_e_per_H': str(ne / nh), 'Tgas': str(tgas), 'Trad': str(trad), 'temperature_units': 'K', 'radiation_authority': radiation, 'radiation_model': packet['radiation_model'], 'radiation_spectrum_identity': packet.get('radiation_spectrum_identity'), 'gas_temperature_authority': packet['gas_temperature_authority'], 'density_conversion_count': 0, 'consumer_gate_I': 'DEFERRED_CONSUMER', 'matched_history_status': 'NOT_PROVIDED'}
