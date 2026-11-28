"""Read-only R31AE scope preflight; never invokes a science producer."""
import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_SCOPE = 'f9872cb045fef146987829620c669fb99f2417a787d74cde26dfee107153a567'
PINS = {
    'R31AD_model_sha256': 'research/r31ad_five_node/unit_cell_model.py',
    'R31Z_model_sha256': 'research/r31z_source_bound/source_bound.py',
    'five_node_manifest_sha256': 'research/r31ad_five_node/ncp_followup_20260929/FIVE_NODE_INPUT_MANIFEST.json',
    'selection_sha256': 'research/r31ad_five_node/ncp_followup_20260929/MIDPOINT_SELECTION.json',
    'selection_rule_sha256': 'research/r31ad_five_node/ncp_followup_20260929/FROZEN_SELECTION_RULE.json',
    'preregistration_sha256': 'research/r31ad_five_node/ncp_followup_20260929/NEXT_VALIDATION_PREREGISTRATION.json',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    root = a.repo.resolve()
    scope_path = root/'research/r31ae_z05_gate/AUTHORIZATION_SCOPE.json'
    scope_bytes = scope_path.read_bytes()
    scope = json.loads(scope_bytes, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    canonical = json.dumps(scope, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                           allow_nan=False).encode('utf-8')
    canonical_hash = sha(canonical)
    checks = {key: {'path': rel, 'actual_sha256': sha((root/rel).read_bytes()),
                    'expected_sha256': scope[key]} for key, rel in PINS.items()}
    binding_ok = all(x['actual_sha256'] == x['expected_sha256'] for x in checks.values())
    prereg = json.loads((root/PINS['preregistration_sha256']).read_text())
    selection = json.loads((root/PINS['selection_sha256']).read_text())
    semantic_ok = (scope['selected_z_a0'] == selection['selected_z_a0'] == prereg['selected_z_a0'] == 0.5
                   and scope['selected_time_ta'] == selection['selected_time_ta'] == prereg['selected_time_ta']
                   and scope['radial_order'] == prereg['radial_order'] == 192
                   and scope['comparison_tolerance'] == prereg['comparison_tolerance'] == 1e-10
                   and prereg['execution_authorized'] is False)
    status = ('AUTHORIZATION_SCOPE_DRIFT' if canonical_hash != EXPECTED_SCOPE or not binding_ok or not semantic_ok
              else 'AWAITING_STRUCTURED_AUTHORIZATION')
    result = {
        'schema': 'WU088_R31AE_Z05_NCP_GATE_PREFLIGHT_V1',
        'scope_file': str(scope_path), 'scope_file_sha256': sha(scope_bytes),
        'canonicalization': 'UTF-8; recursive sorted keys; separators comma and colon; no whitespace; finite numbers',
        'canonical_scope_sha256': canonical_hash, 'expected_scope_sha256': EXPECTED_SCOPE,
        'scope_digest_match': canonical_hash == EXPECTED_SCOPE,
        'individual_bindings': checks, 'individual_bindings_match': binding_ok,
        'selection_prereg_geometry_and_tolerance_match': semantic_ok,
        'current_user_instruction': 'conditional/example envelope; no affirmative structured authorization directive',
        'affirmative_authorization_present': False,
        'Z05_EXECUTION_STATUS': status,
        'science_producer_commands': 0, 'science_node_count': 0,
        'direct_z05_output_accessed': False,
    }
    a.out.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'Z05_EXECUTION_STATUS': status, 'scope_digest_match': result['scope_digest_match'],
                      'individual_bindings_match': binding_ok, 'science_node_count': 0}))


if __name__ == '__main__':
    main()
