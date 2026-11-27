#!/usr/bin/env python3
"""Read an existing HH checkpoint; perform no native evolution or root solve.

Layout: candidate/src/hh_paired_extension.rs::hh_checkpoint_encode/decode.
Provider arithmetic: source transcription of AtomicProvider::cross_section;
Python binary64 math is diagnostic, not a new Rust callback receipt.
"""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import math
import struct

BASE = Path(__file__).resolve().parent
DATA = (BASE / 'inputs/COMMON_SEED_MEMBER1.bin').read_bytes()
EXPECTED = '678f967f0d50ad1fff47a73e2e63193429b708246cd84ca8ffc72191c31b522b'
assert hashlib.sha256(DATA).hexdigest() == EXPECTED
assert len(DATA) == 108416


def fnv(data):
    value = 0xcbf29ce484222325
    for byte in data:
        value = ((value ^ byte) * 0x100000001b3) & ((1 << 64) - 1)
    return value


assert fnv(DATA[:-8]) == struct.unpack('<Q', DATA[-8:])[0]
at = 0


def words(n=1):
    global at
    value = struct.unpack_from('<' + 'Q' * n, DATA, at)
    at += 8 * n
    return list(value)


def floats(n=1):
    global at
    value = struct.unpack_from('<' + 'd' * n, DATA, at)
    at += 8 * n
    assert all(math.isfinite(x) for x in value)
    return list(value)


def boxes(n):
    result = [floats(2) for _ in range(n)]
    assert all(lo <= hi for lo, hi in result)
    return result


magic, source_tag, schema, identity_len = words(4)
assert magic.to_bytes(8, 'little') == b'HH06Bv01'
identity_words = words(identity_len)
assert schema == 1 and identity_len == 27
m, nmu, nphi, mode = identity_words[:4]
assert (m, nmu, nphi, mode) == (8, 8, 16, 1)
float_id = [struct.unpack('<d', struct.pack('<Q', x))[0]
            for x in identity_words[4:-1]]
hubble = float_id[:3]
names = ['source_per_H_per_s', 'birth_energy_eV', 'fHe', 'chi_HI_eV',
         'chi_HeI_eV', 'chi_HeII_eV', 'c_cm_per_s', 'k_B_erg_per_K',
         'eV_erg', 'HH_A', 'HH_power', 'HH_activation_K', 'n_H0_cm3',
         'residual_tolerance', 'legacy_gate_2e4', 'legacy_gate_2e3',
         'ledger_tolerance', 'HH_temperature_min_K', 'HH_temperature_max_K']
constants = dict(zip(names, float_id[3:], strict=True))
edges = [10.0, constants['chi_HI_eV'], 13.6, constants['birth_energy_eV'], 20.0]
energies = [edges[k] + (edges[k + 1] - edges[k]) * j / m
            for k in range(4) for j in range(m)] + [20.0]
assert len(energies) == 33
indices = {struct.pack('<d', e): i for i, e in enumerate(energies)}
time_s = floats()[0]
fractions = floats(3)
w, escaped = floats(2)
packet_count = words()[0]
packets = [floats(2) for _ in range(packet_count)]
gas_box = boxes(4)
nd = nmu * nphi
photons = floats(nd * len(energies))
photon_boxes = boxes(nd * len(energies))
guard_n = floats(nd)
guard_u = floats(nd)
guard_n_box = boxes(nd)
guard_u_box = boxes(nd)
ledger = floats(5)
ledger_compensation = floats(5)
energy_compensation, hh_events, hh_heat, hh_comp_n, hh_comp_e = floats(5)
assert at == len(DATA) - 8
assert all(x >= 0 for x in photons + guard_n + guard_u)
assert all(lo <= x <= hi for x, (lo, hi) in zip(fractions + [w], gas_box))
assert all(lo <= x <= hi for x, (lo, hi) in zip(photons, photon_boxes))
point_packets = [0.0] * 33
for energy, count in packets:
    assert struct.pack('<d', energy) in indices
    point_packets[indices[struct.pack('<d', energy)]] = count


def sigma_source_transcription(energy, species):
    table = [(13.60, 0.4298, 5.475e4, 32.88, 2.963, 0.0, 0.0, 0.0),
             (24.59, 13.61, 949.2, 1.469, 3.188, 2.039, 0.4434, 2.136),
             (54.42, 1.720, 1.369e4, 32.88, 2.963, 0.0, 0.0, 0.0)]
    eth, e0, sigma0, ya, p, yw, y0, y1 = table[species]
    if energy < eth:
        return 0.0
    x = energy / e0 - y0
    y = math.sqrt(x * x + y1 * y1)
    value = (sigma0 * ((x - 1.0) * (x - 1.0) + yw * yw)
             * math.pow(y, p / 2.0 - 5.5)
             * math.pow(1.0 + math.sqrt(y / ya), -p) * 1e-18)
    assert math.isfinite(value) and value >= 0
    return value


groups = []
for i, energy in enumerate(energies):
    counts = photons[i::33]
    exact = sum(map(Fraction.from_float, counts), Fraction(0))
    groups.append({'index': i, 'energy_eV': energy, 'energy_binary64_hex': energy.hex(),
                   'stored_primary_packet_count_per_H': point_packets[i],
                   'direction_sum_nearest_binary64_per_H': float(exact),
                   'direction_sum_exact': {'numerator': str(exact.numerator),
                                           'denominator': str(exact.denominator)},
                   'sigma_cm2_python_source_diagnostic':
                   [sigma_source_transcription(energy, a) for a in range(3)]})
particles = 1 + constants['fHe'] + fractions[0] + constants['fHe'] * (fractions[1] + 2 * fractions[2])
temperature = 2 * constants['eV_erg'] * w / (3 * constants['k_B_erg_per_K'] * particles)
proposed_macro = 1.25e9
summary = {
    'schema': 'WU088_HH_PHYS06_ARCHIVED_SEED_READ_ONLY_V1',
    'status': 'ARCHIVE_FIELD_EXTRACTION_AND_SCALAR_SOURCE_DIAGNOSTIC',
    'seed': {'path': 'inputs/COMMON_SEED_MEMBER1.bin', 'sha256': EXPECTED,
             'bytes': len(DATA), 'schema': schema, 'source_tag_hex': hex(source_tag),
             'source_tag_recomputed': False, 'FNV_checksum_verified': True,
             'native_original_decode_executed_here': False,
             'existing_decode_roundtrip_evidence': 'evidence/v2_targeted.stdout'},
    'scope': {'root_evaluations': 0, 'endpoint_evaluations': 0, 'IVP_evaluations': 0,
              'historical_suites_replayed': 0, 'native_Rust_provider_evaluations': 0,
              'python_source_cross_section_calls': 99,
              'claim_ceiling': 'Input snapshot and point scalar arithmetic only; no trajectory, root, tube, finite sign or error certification'},
    'source_commit': '4b9231a0eff113701e7178ad98624233f387dd15',
    'source_bindings': {
        'layout': 'candidate/src/hh_paired_extension.rs::hh_checkpoint_encode/decode',
        'nodes': 'candidate/src/paired_runtime.rs::energy_nodes',
        'provider': 'candidate/src/atomic_provider.rs::cross_section',
        'density': 'candidate/src/hh_paired_extension.rs::hh_source_endpoint_returned',
        'provider_note': 'Python binary64 transcription, not a bitwise attestation of NCP Rust libm output; binding thresholds remain distinct from fit cutoffs'},
    'grid': {'spectral_subdivisions': m, 'n_mu': nmu, 'n_phi': nphi, 'directions': nd, 'energies': 33},
    'original_mode': 'Lcs91', 'time_s': time_s, 'hubble_per_s': hubble,
    'constants_from_identity_words': constants,
    'gas_point': {'coordinate_order': ['x_HII', 'x_HeII', 'x_HeIII', 'w_eV_per_H'],
                  'values': fractions + [w], 'binary64_hex': [x.hex() for x in fractions + [w]],
                  'box': gas_box, 'escaped_energy_eV_per_H': escaped},
    'point_derived_temperature_K': temperature,
    'point_derived_n_H_cm3': constants['n_H0_cm3'] * math.exp(-sum(hubble) * time_s),
    'proposed_dt_s_from_NCP_return_not_executed': {'macro': proposed_macro, 'half': proposed_macro / 2},
    'point_derived_endpoint_densities_not_evolved': [
        {'time_s': time_s + dt, 'dt_s': dt,
         'n_H_cm3': constants['n_H0_cm3'] * math.exp(-sum(hubble) * (time_s + dt))}
        for dt in [proposed_macro / 2, proposed_macro]],
    'groups': groups, 'stored_primary_packets': packets,
    'packet_point_vs_direction_sum': {'definition': 'Stored post-BE primary packet entries and exact directional sums are retained separately; never equate their floating point bytes',
        'max_abs_difference_per_H': max(abs(x['stored_primary_packet_count_per_H'] - x['direction_sum_nearest_binary64_per_H']) for x in groups)},
    'historical_hh': [hh_events, hh_heat, hh_comp_n, hh_comp_e],
    'photon_sum_per_H': math.fsum(photons), 'guard_n_sum_per_H': math.fsum(guard_n),
    'guard_energy_sum_eV_per_H': math.fsum(guard_u),
    'ledgers': {'redshift_work_eV_per_H': ledger[0], 'thermal_work_eV_per_H': ledger[1],
                'source_photons_per_H': ledger[2], 'source_energy_eV_per_H': ledger[3],
                'absorbed_photons_per_H': ledger[4], 'compensation': ledger_compensation,
                'energy_compensation': energy_compensation}}
out = BASE / 'ARCHIVED_COMMON_SEED_POINT_INPUT.json'
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'output': str(out), 'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
                  'gas': fractions + [w], 'T_K': temperature, 'n_H_cm3': summary['point_derived_n_H_cm3'],
                  'photon_groups': 33, 'native_roots': 0}, ensure_ascii=False))
