"""Read-only R31AC scope binding check; no science producer is invoked."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    repo = a.repo.resolve()
    base = repo/'research/r31ac_z1_authorization'
    scope_path = base/'AUTHORIZATION_SCOPE.json'
    scope = json.loads(scope_path.read_text())
    template = json.loads((base/'AUTHORIZATION_ENVELOPE_TEMPLATE.json').read_text())
    prior = json.loads((repo/'research/r31ab_z1_decision/ncp_followup_20260929/PREFLIGHT_LOCK.json').read_text())
    prior_return = json.loads((repo/'research/r31ab_z1_decision/ncp_followup_20260929/RETURN.json').read_text())
    files = {
        'preregistration': repo/'research/r31aa_validation/Z1_PREREGISTRATION.json',
        'R31Z_model': repo/'research/r31z_source_bound/source_bound.py',
        'R31AA_model': repo/'research/r31aa_validation/local_candidate.py',
        'producer_archive': a.archive,
    }
    hashes = {key: sha(path) for key, path in files.items()}
    checks = {
        'preregistration': hashes['preregistration'] == scope['preregistration_sha256'] == prior['entries']['prereg']['sha256'],
        'R31Z_model': hashes['R31Z_model'] == scope['R31Z_model_sha256'] == prior['entries']['r31z_model']['sha256'],
        'R31AA_model': hashes['R31AA_model'] == scope['R31AA_model_sha256'] == prior['entries']['r31aa_model']['sha256'],
        'producer_archive': hashes['producer_archive'] == scope['producer_archive_sha256'],
        'metric_rule': scope['metric_rule_sha256'] == prior['comparison_contract_sha256'],
        'tolerance': prior['comparison_contract']['comparison_tolerance'] == 1e-10,
        'scope_declared_id': scope['canonical_sha256'] == template['scope_sha256'] == '730cf09525d3b09e3b45fab7b8cec78cce631182b2c87e7008f766a10839787c',
        'one_shot': scope['one_shot'] is True and template['one_shot'] is True,
        'prior_science_count_zero': prior_return['science_node_count'] == 0,
        'prior_science_commands_empty': prior_return['science_producer_commands'] == [],
    }
    if not all(checks.values()):
        raise ValueError('scope binding mismatch: '+json.dumps(checks))
    scope_content = {k: v for k, v in scope.items() if k != 'canonical_sha256'}
    standard_canonical = json.dumps(scope_content, sort_keys=True, separators=(',', ':')).encode()
    result = {
        'schema': 'WU088_R31AC_AUTHORIZATION_GATE_PREFLIGHT_V1',
        'checks': checks, 'actual_sha256': hashes,
        'scope_file_sha256': sha(scope_path),
        'declared_scope_sha256': scope['canonical_sha256'],
        'sorted_minified_scope_without_digest_sha256': hashlib.sha256(standard_canonical).hexdigest(),
        'canonical_scope_serialization_specified': False,
        'Z1_EXECUTION_STATUS': 'AWAITING_STRUCTURED_AUTHORIZATION',
        'science_producer_commands': [], 'science_node_count': 0,
        'z1_direct_output_accessed': False,
    }
    payload = json.dumps(result, indent=2, allow_nan=False)+'\n'
    a.out.write_text(payload)
    print(payload, end='')


if __name__ == '__main__':
    main()
