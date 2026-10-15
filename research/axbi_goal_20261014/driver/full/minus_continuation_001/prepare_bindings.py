#!/usr/bin/env python3
"""One-shot private binding assembly for the two frozen minus continuations.

Consumes the already exported checkpoint Debug lines; never invokes a solver.
"""
import hashlib
import json
import os
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
FULL = HERE.parent
CASES = {
    'SHEAR_MINUS': ('minus_continuation_001', '0f4d12dc725e3ae3657357a3f005b7885c2d7292a5747a7d96b528dfe21a93e7'),
    'SHEAR_HALF_MINUS': ('half_minus_continuation_001', '8cbd03102b79017cbe14247c0cc2da506d7336c5df2672ad275e6efc9573b690'),
}
REFERENCE = FULL / 'half_plus_continuation_001/EXECUTION.binding'
MECHANISM_REVIEW = ROOT / 'research/axbi_goal_20261014/reviews/SIGNED_CONTINUATION_MECHANISM_REREVIEW.json'
MECHANISM_REVIEW_SHA = '88d70aa746b4baed1b281c2027f26a6ff7d722100c2e17f1e05480619b8461d0'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def parse(path):
    pairs = [line.split('=', 1) for line in path.read_text().splitlines()]
    if any(len(p) != 2 for p in pairs) or len(pairs) != len({p[0] for p in pairs}):
        raise RuntimeError('REFERENCE_BINDING_FORMAT')
    return [p[0] for p in pairs], dict(pairs)


def ensure(path, expected, name):
    if sha(path) != expected:
        raise RuntimeError('FROZEN_IDENTITY_CHANGED:' + name)


def write_private(path, content):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(content)
    os.chmod(path, 0o600)


def prepare(case, folder, authority_sha, keys, reference):
    owned = FULL / folder
    a_path = owned / 'AUTHORITY.json'
    ensure(a_path, authority_sha, case + ':authority')
    a = json.loads(a_path.read_text())
    p, c, alloc = a['predecessor'], a['continuation'], a['allocation']['binding_fields']
    if p['case'] != case or c['q_ref'] != {'SHEAR_MINUS': -.01, 'SHEAR_HALF_MINUS': -.005}[case]:
        raise RuntimeError('CASE_AUTHORITY_MISMATCH')
    predecessor = ROOT / p['path']
    checks = {
        f'research/axbi_goal_20261014/driver/full/{case}.cfg': p['config_sha256'],
        p['path'] + '/config.cfg': p['config_sha256'],
        p['path'] + '/checkpoint.txt': p['checkpoint_sha256'],
        p['path'] + '/RETURN.txt': p['return_sha256'],
        p['path'] + '/source_identity.txt': p['source_sha256'],
        str(predecessor.parent.relative_to(ROOT) / (case + '_raw') / 'execution_receipt.json'): p['execution_receipt_sha256'],
        c['binary']: c['binary_sha256'],
        a['preparation']['helper_binary']: a['preparation']['helper_binary_sha256'],
        reference['current_source']: c['compiled_source_sha256'],
        reference['decision']: reference['decision_sha256'],
        reference['review']: reference['review_sha256'],
        reference['example']: reference['example_sha256'],
    }
    for name, expected in checks.items():
        ensure(ROOT / name, expected, case + ':' + name)
    if (ROOT / c['output']).exists() or (ROOT / c['raw']).exists():
        raise RuntimeError('CONTINUATION_OUTPUT_OR_RAW_EXISTS:' + case)
    if (predecessor / 'case_id.txt').read_text() != case:
        raise RuntimeError('PREDECESSOR_CASE_ID_CHANGED:' + case)
    state_path = owned / 'starting_state_debug.txt'
    if (owned / 'state_export.exit').read_text() != '0\n' or (owned / 'state_export.stderr').stat().st_size:
        raise RuntimeError('CHECKPOINT_EXPORT_FAILED:' + case)
    state = state_path.read_text().removesuffix('\n')
    photons = re.search(r'photons: \[(.*?)\], ledgers:', state)
    if not state.startswith('DriverState {') or len(state.splitlines()) != 1 or photons is None or len(photons.group(1).split(', ')) != 392:
        raise RuntimeError('CHECKPOINT_DEBUG_FORMAT:' + case)
    for field, expected in [('a', p['a']), ('accepted', p['accepted']),
                            ('attempts', p['attempted']), ('rhs_evaluations', p['rhs']),
                            ('wall_elapsed_s', p['solver_wall_s'])]:
        match = re.search(r'\b' + field + r': ([^,} ]+)', state)
        if match is None or float(match.group(1)) != float(expected):
            raise RuntimeError('CHECKPOINT_DEBUG_SCALAR:' + case + ':' + field)
    binding = dict(reference)
    binding.update(case=case, segment=case + '_RESOURCE_CONTINUATION_001',
                   config=f'research/axbi_goal_20261014/driver/full/{case}.cfg',
                   config_sha256=p['config_sha256'], q_ref=str(c['q_ref']),
                   predecessor=p['path'], output=c['output'], raw_output=c['raw'],
                   checkpoint_sha256=p['checkpoint_sha256'], terminal_sha256=p['return_sha256'],
                   old_source_sha256=p['source_sha256'], current_source_sha256=c['compiled_source_sha256'],
                   binary_sha256=c['binary_sha256'], starting_state_debug=state,
                   **{key: str(value) for key, value in alloc.items()})
    if set(binding) != set(keys) or len(keys) != 34:
        raise RuntimeError('BINDING_KEY_SET')
    if 10800.0 + float(binding['additional_wall_s']) != float(binding['effective_max_wall_s']):
        raise RuntimeError('BINDING_WALL_ARITHMETIC:' + case)
    if int(binding['effective_max_steps']) != 200000 + int(binding['additional_steps']) or \
       int(binding['effective_max_attempts']) != 650000 + int(binding['additional_attempts']) or \
       int(binding['effective_output_budget_mib']) != 2048 + int(binding['additional_output_mib']):
        raise RuntimeError('BINDING_RESOURCE_ARITHMETIC:' + case)
    authority_path = owned / 'EXECUTION_AUTHORITY.binding'
    execution_path = owned / 'EXECUTION.binding'
    if authority_path.exists() or execution_path.exists() or (owned / 'PREPARATION_RECEIPT.json').exists():
        raise RuntimeError('PRIVATE_BINDING_ALREADY_PREPARED:' + case)
    mirrored = ''.join(key + '=' + binding[key] + '\n' for key in keys if key not in ('authority', 'authority_sha256'))
    write_private(authority_path, mirrored)
    binding['authority'] = str(authority_path.relative_to(ROOT))
    binding['authority_sha256'] = sha(authority_path)
    execution = ''.join(key + '=' + binding[key] + '\n' for key in keys)
    write_private(execution_path, execution)
    receipt = {
        'schema': 'rei.axbi.signed_case_continuation_preparation.v1',
        'status': 'PREPARED_PENDING_INDEPENDENT_BINDING_REVIEW',
        'case': case,
        'authority_json_sha256': authority_sha,
        'mechanism_review_sha256': MECHANISM_REVIEW_SHA,
        'binary_path': c['binary'], 'binary_sha256': c['binary_sha256'],
        'helper_binary_path': a['preparation']['helper_binary'],
        'helper_binary_sha256': a['preparation']['helper_binary_sha256'],
        'checkpoint_exports': 1, 'helper_builds': 0, 'solver_starts': 0,
        'synthetic_launcher_fixtures': 0,
        'starting_state_debug_path': str(state_path.relative_to(ROOT)),
        'starting_state_debug_sha256': sha(state_path),
        'checkpoint_debug_photon_stocks': 392,
        'execution_binding_path': str(execution_path.relative_to(ROOT)),
        'execution_binding_sha256': sha(execution_path),
        'execution_binding_keys': 34,
        'private_authority_binding_path': str(authority_path.relative_to(ROOT)),
        'private_authority_binding_sha256': sha(authority_path),
        'authority_mirror': 'PASS_32_KEYS',
        'input_sha256': checks,
        'predecessor_output': p['path'],
        'continuation_output': c['output'],
        'continuation_raw': c['raw'],
        'continuation_output_raw_absent': True,
        'driver_argv_after_independent_binding_PASS_only': [c['binary'], '--binding', str(execution_path.relative_to(ROOT)), '--binding-sha256', sha(execution_path)],
        'requested_executor': 'gpt-6.1-sol/medium',
        'observed_executor_runtime': 'NOT_INDEPENDENTLY_OBSERVED',
        'scientific_admission': 'NOT_ISSUED',
        'launch_preconditions_pending': 'Independent exact binding PASS; ordered prior PLUS/HALF_PLUS/MINUS terminal classification; scheduler/slot/disk/duplicate/absence checks at launch.',
    }
    write_private(owned / 'PREPARATION_RECEIPT.json', json.dumps(receipt, indent=2) + '\n')
    return {'case': case, 'binding_sha256': receipt['execution_binding_sha256'],
            'authority_binding_sha256': receipt['private_authority_binding_sha256'],
            'receipt_sha256': sha(owned / 'PREPARATION_RECEIPT.json')}


def main():
    ensure(MECHANISM_REVIEW, MECHANISM_REVIEW_SHA, 'mechanism_review')
    keys, reference = parse(REFERENCE)
    if len(keys) != 34 or reference['case'] != 'SHEAR_HALF_PLUS':
        raise RuntimeError('REFERENCE_BINDING_SCOPE')
    results = [prepare(case, folder, authority_sha, keys, reference)
               for case, (folder, authority_sha) in CASES.items()]
    print(json.dumps(results))


if __name__ == '__main__':
    main()
