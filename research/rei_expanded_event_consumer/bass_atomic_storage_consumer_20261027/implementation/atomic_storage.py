"""Exact common-V0 atomic inventory/energy representation, not state projection."""
from dataclasses import dataclass
from fractions import Fraction as Q

FINE = ('ground', '2s', '2p', 'continuum')
ENERGY = ('rest_dust', 'atomic_internal', 'gas_thermal', 'ambient_radiation', 'outgoing_Lyalpha')
SOURCE_PIN = '634c3046ffccc5d00f1ab7588b5834a6eb8053ad'
SOURCE_SHA256 = 'a0fa9b5237481e66f178f19eb1589607412d9d1188d7fb571e5df03b67fd93ac'
SOURCE_BLOB = 'a9ea559f123da6c8f1fe070139bc80145d4582fc'
CHI = Q('13.6') * Q('1.602176634e-19')


def rational(value):
    """Accept exact Fraction or original decimal/rational string only."""
    if type(value) is Q:
        return value
    if type(value) is str and value and value.strip() == value:
        return Q(value)
    raise TypeError('exact Fraction or source numeric string required')


def vector(values, length):
    if type(values) is not tuple or len(values) != length:
        raise ValueError('immutable tuple of required dimension expected')
    if any(type(value) is not Q for value in values):
        raise TypeError('exact Fraction coordinates required')
    return values


def h1_guard(mapping):
    if type(mapping) is not tuple or mapping != (('H1I', 1), ('H1II', 2)):
        raise ValueError('explicit matched H1I=1/H1II=2 mapping required')
    if any(type(index) is not int for name, index in mapping):
        raise TypeError('native indices must be integers')


@dataclass(frozen=True)
class Coarse:
    neutral: Q
    ion: Q
    thermal_electrons: Q
    fast_zeta: Q
    neutral_complement_diagnostic: Q
    baryon_residual: Q


def coarse_mapping(delta, *, fine_order, native_mapping):
    vector(delta, 4)
    if type(fine_order) is not tuple or fine_order != FINE:
        raise ValueError('explicit ground/2s/2p/continuum order required')
    h1_guard(native_mapping)
    neutral = sum(delta[:3], Q(0))
    return Coarse(neutral, delta[3], delta[3], Q(0), -delta[3], neutral + delta[3])


@dataclass(frozen=True)
class EnergyLift:
    direct_source: tuple
    target_ion_storage: Q
    hidden_atomic_storage: Q
    mapped_sum: Q
    source_sum: Q
    representation_residual: Q


def energy_lift(source_energies, continuum_delta, *, chi, energy_order):
    vector(source_energies, 5)
    if type(continuum_delta) is not Q or type(chi) is not Q:
        raise TypeError('exact continuum and threshold required')
    if chi <= 0 or type(energy_order) is not tuple or energy_order != ENERGY:
        raise ValueError('positive declared threshold and exact energy order required')
    target = chi * continuum_delta
    hidden = source_energies[1] - target
    total = sum(source_energies, Q(0))
    mapped = target + hidden + sum(source_energies[:1] + source_energies[2:], Q(0))
    return EnergyLift(source_energies, target, hidden, mapped, total, mapped - total)


def right_proper(values, ratio):
    if type(values) is not tuple or any(type(value) is not Q for value in values):
        raise TypeError('exact immutable tuple required')
    if type(ratio) is not Q:
        raise TypeError('exact volume ratio required')
    if ratio <= 0:
        raise ValueError('positive right volume ratio required')
    return tuple(value / ratio for value in values)


def linearization(delta_direction, source_atomic_direction, *, chi, dchi, continuum):
    vector(delta_direction, 4)
    if any(type(value) is not Q for value in (source_atomic_direction, chi, dchi, continuum)):
        raise TypeError('exact directional quantities required')
    if chi <= 0:
        raise ValueError('positive threshold required')
    coarse = (sum(delta_direction[:3], Q(0)), delta_direction[3], delta_direction[3])
    hidden = source_atomic_direction - chi * delta_direction[3] - dchi * continuum
    return coarse, hidden


def source_guard(*, source_pin, sha256, git_blob, byte_count):
    if (source_pin != SOURCE_PIN or sha256 != SOURCE_SHA256
            or git_blob != SOURCE_BLOB or type(byte_count) is not int or byte_count != 3554206):
        raise ValueError('frozen BASS source identity mismatch')


def _project(values):
    vector(values, 4)
    return (sum(values[:3], Q(0)), values[3], values[3])


def endpoint_split(initial, final, events, ratio):
    """Proper endpoint delta = event/R + volume correction + residual/R."""
    a, b, d = _project(initial), _project(final), _project(events)
    right_proper((), ratio)
    actual = tuple(y / ratio - x for x, y in zip(a, b))
    event = tuple(x / ratio for x in d)
    volume = tuple(x * (1 / ratio - 1) for x in a)
    residual = tuple((y - x - z) / ratio for x, y, z in zip(a, b, d))
    return actual, event, volume, residual


def conditional_abundance(initial, final, *, ratio, b_a, b_b):
    right_proper((), ratio)
    for value in (b_a, b_b):
        if type(value) is not Q:
            raise TypeError('exact supplied recipient density required')
        if value <= 0:
            raise ValueError('positive recipient densities required')
    return tuple(y / (ratio * b_b) - x / b_a
                 for x, y in zip(_project(initial), _project(final)))


def conditional_abundance_jvp(initial, final, d_initial, d_final, *, ratio, b_a, b_b, d_ratio, d_b_a, d_b_b):
    conditional_abundance(initial, final, ratio=ratio, b_a=b_a, b_b=b_b)
    for value in (d_ratio, d_b_a, d_b_b):
        if type(value) is not Q:
            raise TypeError('exact scale directions required')
    return tuple(dy / (ratio * b_b) - dx / b_a
                 - y * d_ratio / (ratio * ratio * b_b)
                 - y * d_b_b / (ratio * b_b * b_b)
                 + x * d_b_a / (b_a * b_a)
                 for x, y, dx, dy in zip(_project(initial), _project(final),
                                          _project(d_initial), _project(d_final)))


def _source_rows(values, count):
    if type(values) is not list or len(values) != count:
        raise ValueError('saved source row dimension mismatch')
    result = []
    for row in values:
        if type(row) is not list or len(row) != 1 or type(row[0]) is not str:
            raise ValueError('saved source requires singleton decimal-string rows')
        result.append(rational(row[0]))
    return tuple(result)


def _source_vector(values, count):
    if type(values) is not list or len(values) != count or any(type(x) is not str for x in values):
        raise ValueError('saved source requires decimal-string vector')
    return tuple(rational(x) for x in values)


def consume(document, *, native_mapping):
    """Consume already byte-verified source once; retain inherited diagnostics."""
    h1_guard(native_mapping)
    if type(document) is not dict or document.get('schema') != 'BASS_QSS_FINITE_SOURCE_CHANNEL_TRANSACTION_V1':
        raise ValueError('saved BASS schema mismatch')
    owners = document['finite_owners']
    if tuple(owners['inventory_order']) != FINE or tuple(owners['sector_order']) != ENERGY:
        raise ValueError('saved inventory/energy ownership order mismatch')
    initial = _source_rows(owners['initial_stocks'], 4)
    final = _source_rows(owners['final_stocks'], 4)
    events = _source_rows(owners['stock_change_from_events'], 4)
    ratio = rational(owners['right_volume_ratio'])
    coarse = coarse_mapping(events, fine_order=FINE, native_mapping=native_mapping)
    energies = _source_vector(owners['event_sector_energy_J_m3'], 5)
    lifted = energy_lift(energies, events[3], chi=CHI, energy_order=ENERGY)
    proper, event_proper, volume, endpoint_residual = endpoint_split(initial, final, events, ratio)
    initial_energy = _source_vector(owners['initial_sector_energy_J_m3'], 5)
    final_energy = _source_vector(owners['final_sector_energy_common_V0_J_m3'], 5)
    final_energy_proper = _source_vector(owners['final_sector_energy_J_m3'], 5)
    work = _source_vector(owners['geometry_work_J_m3'], 5)
    initial_e = rational(owners['electrons_initial'])
    final_e = rational(owners['electrons_final'])
    return {
        'scope': 'SELECTED_FINITE_BASS_ATOMIC_STORAGE_REPRESENTATION',
        'canonical_transaction_id': 'BASS:' + SOURCE_PIN + '/result:' + SOURCE_BLOB + '/full-finite-owner-transaction',
        'source_original_energy_encoding': document['energy_unit_encoding'],
        'threshold_encoding': 'DECLARED_TARGET_DECIMAL_13.6_eV_TIMES_EXACT_SI; not native binary runtime equivalence',
        'chi_target_J': CHI, 'source_energy_encoding': 'Saved source decimal strings retained; source binary64-eV convention distinct',
        'fine_order': FINE, 'energy_order': ENERGY,
        'initial_stock_common_V0': initial, 'final_stock_common_V0': final,
        'event_delta_common_V0': events,
        'stock_endpoint_minus_event_residual': tuple(y - x - d for x, y, d in zip(initial, final, events)),
        'coarse_event_common_V0': (coarse.neutral, coarse.ion, coarse.thermal_electrons),
        'neutral_complement_diagnostic': coarse.neutral_complement_diagnostic,
        'baryon_residual': coarse.baryon_residual, 'fast_zeta': coarse.fast_zeta,
        'right_volume_ratio': ratio,
        'initial_coarse_proper': _project(initial), 'final_coarse_proper': right_proper(_project(final), ratio),
        'proper_endpoint_change': proper, 'proper_event_part': event_proper,
        'volume_correction': volume, 'source_endpoint_residual_proper': endpoint_residual,
        'electron_endpoint_minus_event_residual': final_e - initial_e - events[3],
        'direct_source_energies_J_per_V0': lifted.direct_source,
        'source_reference': {'event_sector_energy_J_per_V0': lifted.direct_source,
                             'role': 'Reference only; do not add original atomic port again to mapped apply ports'},
        'mapped_apply_ports': {'rest_dust': energies[0],
                               'target_ion_binding': lifted.target_ion_storage,
                               'hidden_atomic_storage': lifted.hidden_atomic_storage,
                               'gas_thermal': energies[2],
                               'ambient_radiation': energies[3],
                               'outgoing_Lyalpha': energies[4]},
        'initial_sector_energy_J_per_V0': initial_energy,
        'final_sector_energy_J_per_V0': final_energy,
        'saved_final_sector_energy_proper_J_m3': final_energy_proper,
        'energy_volume_encoding_residual': tuple(y / ratio - z for y, z in zip(final_energy, final_energy_proper)),
        'target_ion_storage_J_per_V0': lifted.target_ion_storage,
        'hidden_atomic_storage_J_per_V0': lifted.hidden_atomic_storage,
        'mapped_energy_sum': lifted.mapped_sum, 'source_energy_sum': lifted.source_sum,
        'representation_energy_residual': lifted.representation_residual,
        'geometry_work_ports_J_per_V0': work,
        'energy_endpoint_minus_event_work_diagnostic': tuple(y - x - d - w for x, y, d, w in zip(initial_energy, final_energy, energies, work)),
        'saved_interface_storage_residual_lexemes': owners['interface_storage_residual'],
        'saved_event_energy_sum_residual_lexeme': owners['event_energy_sum_residual'],
        'saved_total_energy_work_identity_residual_lexeme': owners['total_energy_work_identity_residual'],
        'physical_radii': owners['physical_radii'],
        'actual_recipient_nb': None, 'actual_native25': None, 'full_state_update': False,
        'temperature_update': None, 'virtual_311_photons_included': False,
        'hidden_is_heat': False, 'hidden_is_external_work': False,
    }
