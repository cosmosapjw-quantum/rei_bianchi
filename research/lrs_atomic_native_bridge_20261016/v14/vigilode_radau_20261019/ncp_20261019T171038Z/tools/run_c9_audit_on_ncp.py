#!/usr/bin/env python3
"""Run the committed C9 independent raw audit unchanged on NCP evidence.

Only layout differences are bridged: a shim directory symlinks each case's raw,
outcome, stdout, stderr and source archive, and a copied inputs.json gains the
`executables_sha256` mapping the C9 audit expects (NCP runner writes the singular
`executable_sha256`). Original evidence bytes are not modified.
"""
import importlib, json, sys
from decimal import localcontext
from pathlib import Path

c9_dir, evidence, shim, out = map(Path, sys.argv[1:5])
sys.path.insert(0, str(c9_dir))
am = importlib.import_module('audit_matrix')

matrix = json.loads((evidence / 'MATRIX_RECEIPT.json').read_text())
shim.mkdir(parents=True, exist_ok=False)
cases, total_rhs = [], 0
for c in matrix['cases']:
    name = f"{c['mode']}_{c['method']}_n{c['N']}"
    src, dst = evidence / name, shim / name
    dst.mkdir()
    for f in ('raw.json', 'outcome.json', 'stdout.txt', 'stderr.txt', 'sources.tar.gz'):
        (dst / f).symlink_to(src / f)
    inputs = json.loads((src / 'inputs.json').read_text())
    inputs['executables_sha256'] = {'rei-vigilode-radau-research': inputs['executable_sha256']}
    # Portable runner archives store members as source_NNNN/<name> with an explicit
    # member->original-path map; re-key the hash manifest by member so the C9
    # byte check reads the same bytes it would under the sandbox layout.
    by_path = inputs['source_sha256']
    inputs['source_sha256'] = {m: by_path[p] for m, p in inputs['source_archive_member_paths'].items()}
    assert len(inputs['source_sha256']) == len(by_path)
    (dst / 'inputs.json').write_text(json.dumps(inputs, indent=2) + '\n')
    total_rhs += json.loads((src / 'raw.json').read_text())['native_rhs_attempts_including_fd_replay']
    cases.append({'mode': c['mode'], 'method': c['method'], 'N': int(c['N']), 'receipt': str(dst)})
(shim / 'MATRIX_RECEIPT.json').write_text(json.dumps({
    'binary_sha256': matrix['executable_sha256'], 'unique_total_native_rhs_attempts': total_rhs,
    'cases': cases, 'shim_of': str(evidence / 'MATRIX_RECEIPT.json')}, indent=2) + '\n')

am.ROOT = Path('/')  # receipts are absolute; ROOT/abs == abs
am.REC = shim
with localcontext() as ctx:
    ctx.prec = 60
    result = am.review()
result['reviewer'] = 'C9 audit_matrix.py re-applied unchanged by the NCP execution session (not an independent reviewer)'
result['evidence_root'] = str(evidence)
out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ['unique_cases', 'accepted_macro_records', 'Radau_chemical_segments',
                                          'Radau_accepted_stages', 'native_rhs_attempts', 'native_wall_s',
                                          'max_abs_independent_audits', 'max_abs_cumulative_balances_over_all_prefixes']}, indent=1))
