"""Ground-target Badnell DR scalar candidate; no thermal moment or spectrum.

N counts incident-target electrons. Electronic isotope reuse is explicitly
ElementalElectronicEquality, without isotope spectroscopy or injection closure.
"""
import json
import math
from pathlib import Path

_DATA = json.loads(Path(__file__).with_name('dr_rows.json').read_text())
_ROWS = {tuple(r['key']): r for r in _DATA['rows']}
CHANNELS = tuple(_ROWS)
STATUS = 'CANDIDATE_SCALAR_FIT_NUMERICALLY_CHECKED'
T_LIMITS_K = (100.0, 10000.0)


def dr_rate(key, T_K):
    """Return SI scalar rate and finite logs, including float underflow status.

    Unsupported H/fully-stripped channels raise; no missing-rate zero fill.
    Signed fit coefficients are retained. Status is a numerical candidate claim,
    not fitted-rate physical accuracy, thermal closure, or cascade admission.
    """
    try:
        key = tuple(key)
        row = _ROWS[key]
    except (TypeError, KeyError) as exc:
        raise ValueError(f'unknown DR key: {key!r}') from exc
    try:
        temperature = float(T_K)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError('T_K must be finite in [100, 10000] K') from exc
    if not math.isfinite(temperature) or not T_LIMITS_K[0] <= temperature <= T_LIMITS_K[1]:
        raise ValueError('T_K must be finite in [100, 10000] K')
    e_star = min(row['E_K'])
    shifted_sum = math.fsum(c * math.exp(-(e-e_star)/temperature)
                            for c, e in zip(row['c'], row['E_K']))
    if not math.isfinite(shifted_sum) or shifted_sum <= 0:
        raise ValueError('nonpositive or nonfinite signed DR shifted sum')
    log_cm = -1.5*math.log(temperature)-e_star/temperature+math.log(shifted_sum)
    log_si = log_cm+math.log(1e-6)
    if not all(math.isfinite(v) for v in (log_cm, log_si)):
        raise ValueError('nonfinite DR log rate')
    alpha = math.exp(log_si)
    if not math.isfinite(alpha):
        raise ValueError('nonfinite DR rate')
    z, n, _ = key
    return {'key': key, 'T_K': temperature, 'input_charge': z-n,
            'output_charge': z-n-1, 'alpha_m3_s': alpha,
            'log_alpha_cm3_s': log_cm, 'log_alpha_m3_s': log_si,
            'shifted_signed_sum': shifted_sum,
            'representability_status': 'FLOAT_UNDERFLOW' if alpha == 0 else 'REPRESENTABLE',
            'status': STATUS, 'T_limits_K': T_LIMITS_K,
            'isotope_model': 'ElementalElectronicEquality',
            'isotopes': tuple(row['isotopes']),
            'source_identity': {k: _DATA[k] for k in ('source_url','source_sha256','version')}}
