#!/usr/bin/env python3
"""Pin the existing owner tables and their original 1001 query coordinates."""
import csv
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]


def main():
    contract = json.loads((UNIT / 'receipts/BASELINE_REUSE.json').read_text())
    tables = {}
    for mode, spec in contract['tables'].items():
        path = REPO / spec['repo_relative_path']
        data = path.read_bytes()
        assert len(data) == spec['bytes']
        assert hashlib.sha256(data).hexdigest() == spec['sha256']
        with gzip.open(path, 'rt') as stream:
            table = list(csv.DictReader(stream))
        assert len(table) == spec['rows'] == 1001
        assert list(table[0]) == spec['headers']
        tables[mode] = table
    u = np.linspace(np.log(1 / 21), np.log(.2), 1001)
    z = np.array([float(row['zbar']) for row in tables['fixed_a']])
    assert np.max(np.abs(np.exp(u) - 1 / (1 + z))) <= 2e-16
    result = {
        'schema': 'REI_AX11_T1_SAMPLING_GRID_V1',
        'baseline_contract_sha256': hashlib.sha256(
            (UNIT / 'receipts/BASELINE_REUSE.json').read_bytes()).hexdigest(),
        'baseline_tables': {k: {f: v[f] for f in
                            ['repo_relative_path', 'bytes', 'sha256', 'rows']}
                            for k, v in contract['tables'].items()},
        'fixed_a': [{'index': i, 'ln_a': float(v), 'a': float(np.exp(v)),
                     'zbar': float(z[i])} for i, v in enumerate(u)],
        'fixed_t': [{'index': i, 'elapsed_time_s': float(row['elapsed_time_s'])}
                    for i, row in enumerate(tables['fixed_t'])],
        'interpolation': 'Original numpy log/linspace and owner interp/field_at; no extrapolation.',
        'original_DAG': '10/17', 'expansion_DAG': '28/88',
    }
    out = UNIT / 'inputs/SAMPLING_GRID.json'
    assert not out.exists(), 'do not overwrite a pinned grid'
    out.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'path': str(out), 'bytes': out.stat().st_size,
                      'sha256': hashlib.sha256(out.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
