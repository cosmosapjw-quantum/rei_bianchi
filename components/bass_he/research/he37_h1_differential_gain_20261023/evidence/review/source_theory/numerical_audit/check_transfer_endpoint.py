"""New targeted check for a suspected overflow at an admitted finite endpoint.

This does not invoke any pre-existing suite or model/IVP/benchmark. Author files
are imported read-only, with bytecode writing disabled by the execution command.
"""
from pathlib import Path
import hashlib
import json
import sys
import warnings

import numpy as np

SOURCE = Path('/tmp/he37_source_implementation/lc_ionization.py')
sys.path.insert(0, str(SOURCE.parent))
from lc_ionization import transfer_u

out = Path(__file__).with_name('TRANSFER_ENDPOINT_OBSERVATIONS.json')
if out.exists():
    raise SystemExit('Targeted observations already exist; do not replay.')
maximum = np.finfo(np.float64).max
energies = [1e307, 1e308, float(np.nextafter(maximum, 0.0)), float(maximum)]
rows = []
for energy in energies:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        transfer = float(transfer_u(energy, 1.0))
    rows.append({
        'energy_eV': energy,
        'quantile': 1.0,
        'transfer_eV': transfer if np.isfinite(transfer) else str(transfer),
        'finite': bool(np.isfinite(transfer)),
        'in_closed_support': bool(13.6 <= transfer <= energy),
        'exact_upper_endpoint': bool(transfer == energy),
        'warnings': [str(w.message) for w in caught],
    })
result = {
    'purpose': 'Resolve finite-binary64 upper-endpoint overflow suspicion only',
    'new_transfer_quantile_calls': len(rows),
    'old_suite_replays': 0,
    'IVPs': 0,
    'benchmarks': 0,
    'renders': 0,
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'check_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'numpy': np.__version__,
    'observations': rows,
}
out.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
print(json.dumps(result, indent=2, allow_nan=False))
