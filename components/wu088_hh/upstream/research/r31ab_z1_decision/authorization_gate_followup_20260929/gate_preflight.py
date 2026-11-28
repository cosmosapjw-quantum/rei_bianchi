"""Read-only identity check for the unapproved R31AB z=1 gate."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    repo = a.repo.resolve()
    base = repo/'research/r31ab_z1_decision'
    old = json.loads((base/'ncp_followup_20260929/PREFLIGHT_LOCK.json').read_text())
    old_return = json.loads((base/'ncp_followup_20260929/RETURN.json').read_text())
    decision = json.loads((base/'DECISION.json').read_text())
    recommendation = json.loads((base/'AUTHORIZATION_DECISION_V2.json').read_text())
    checks = {}
    for name, entry in old['entries'].items():
        source = Path(entry['path']) if entry['path'].startswith('/') else repo/entry['path']
        checks[name] = source.stat().st_size == entry['bytes'] and sha(source) == entry['sha256']
    checks['prior_rule_hash'] = old_return['prereg_model_metric_rule_sha256'] == old['comparison_contract_sha256']
    checks['comparison_tolerance'] = old['comparison_contract']['comparison_tolerance'] == 1e-10
    checks['decision_not_authorized'] = decision['execution_authorized'] is False
    checks['recommendation_not_authorized'] = recommendation['execution_authorized'] is False
    checks['prior_science_count_zero'] = old_return['science_node_count'] == 0
    checks['prior_science_commands_empty'] = old_return['science_producer_commands'] == []
    if not all(checks.values()):
        raise ValueError('authorization preflight identity failed: '+json.dumps(checks))
    result = {'schema': 'WU088_R31AB_AUTHORIZATION_GATE_PREFLIGHT_V1',
              'checks': checks,
              'prereg_model_metric_rule_sha256': old['comparison_contract_sha256'],
              'preregistration_sha256': old['entries']['prereg']['sha256'],
              'R31Z_model_source_sha256': old['entries']['r31z_model']['sha256'],
              'R31AA_model_source_sha256': old['entries']['r31aa_model']['sha256'],
              'comparison_tolerance': 1e-10,
              'Z1_EXECUTION_STATUS': 'AWAITING_EXPLICIT_AUTHORIZATION',
              'science_producer_commands': [], 'science_node_count': 0,
              'z1_direct_output_accessed': False}
    payload = json.dumps(result, indent=2, allow_nan=False)+'\n'
    a.out.write_text(payload)
    print(payload, end='')


if __name__ == '__main__':
    main()
