#!/usr/bin/env python3
"""Metadata-only record of the distinct PHYS30 reviewer's completed actual reads."""
from pathlib import Path
import datetime
import hashlib
import json
import zipfile

ROOT = Path('/workspace/scratch/603081e41728')
OUT = ROOT / 'phys30/independent'
SKILL = Path('/root/.codex/skills/remote-skills/skill-6aa0657100b08191b7d67482d1f97c1d')

def identity(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def main():
    records = []
    for rel in ['SKILL.md', 'references/MODEL_ROUTER.json', 'references/REI_EXECUTION_POLICY.md', 'references/REI_EXECUTION_POLICY.json']:
        row = identity(SKILL / rel)
        row.update(actual_read_scope='full contents through skills.read in this reviewer turn', read_kind='skill_or_policy')
        records.append(row)
    groups = [
        ('research', 'harness_phys27', 'recovered_inputs_phys27/physmath-research-harness-gpt6-astra-v4.0.0-20260908.zip', 'dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7', ['START_HERE.md', 'PROJECT_INSTRUCTIONS.md', 'prompts/00_integrated_work_run.md', 'state/RESEARCH_STATE.md', 'docs/MODEL_ROUTING.md', 'policies/EVIDENCE_AND_CITATION.md', 'policies/STOP_RULES.md', 'prompts/phases/06_physics_math_validation.md', 'prompts/phases/07_verification_design.md', 'prompts/phases/08_external_decision_gate.md']),
        ('coding', 'coding_harness_phys28', 'recovered_inputs_phys28/physmath-coding-harness-gpt6-astra-v4.0.0-20260908.zip', 'dc99e7ab2f9629dcce3ec0758d97e19acc5b645f86e208d1b338bb6430ff8d7a', ['START_HERE.md', 'AGENTS.md', 'SCIENTIFIC_CONTRACT.md', 'VALIDATION_MATRIX.md', 'docs/MODEL_ROUTING.md', 'prompts/00_ultralight.md', 'README.md']),
    ]
    archives = []
    for kind, base, archive_rel, expected_sha, rels in groups:
        archive = ROOT / archive_rel
        ar = identity(archive)
        assert ar['sha256'] == expected_sha
        archives.append(ar)
        with zipfile.ZipFile(archive) as z:
            for rel in rels:
                p = ROOT / base / rel
                row = identity(p)
                assert p.read_bytes() == z.read(rel)
                row.update(actual_read_scope='full contents displayed and read in this reviewer turn', read_kind=kind, archive_entry=rel, staging_matches_archive=True)
                records.append(row)
    for rel in ['phys30/evidence/HARNESS_APPLICATION.json', 'phys30/PHYSICS_CONTRACT.json']:
        row = identity(ROOT / rel)
        row.update(actual_read_scope='full contents displayed and read in this reviewer turn', read_kind='current_contract_or_root_harness_record')
        records.append(row)
    contract = next(r for r in records if r['path'].endswith('/phys30/PHYSICS_CONTRACT.json'))
    assert contract['bytes'] == 8241
    assert contract['sha256'] == '475ce8957b46ce1440f227cd1a4b8c5fb3979cf237e4c8e52a5e76028cd78a5d'
    result = {
        'task': 'REI-PHYS30-20261011',
        'reviewer': '/root/phys30_decision',
        'phase': 'PREPARED_AWAITING_ROOT_GO',
        'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'model': 'GPT-6 Astra',
        'model_basis': 'Trusted developer designation GPT-6 Astra Pro inherited by this actual reviewer; no model switch or performance comparison',
        'harness_version': {'research': '4.0.0', 'coding': '4.0.0'},
        'independence': {
            'role': 'distinct final decision reviewer',
            'mode': 'NONBLIND',
            'candidate_generation_participation': False,
            'validation_design_participation': False,
            'same_host': True,
            'same_model_family': True,
            'parent_history_inherited': True,
            'shared_evidence_available': True,
            'independent_physical_evidence_credit': 0,
            'limitation': 'Separate reviewer responsibility and actual own reads; no blind context or independent physical inputs.'
        },
        'review_gate': 'Do not begin claim-by-claim decision until root supplies fixed CANDIDATE_FROZEN identity and explicit GO with first-result, replay, report, and next handoff complete.',
        'decision_status': 'NOT_RUN',
        'candidate_scientific_read_or_evaluation_this_preparation': False,
        'archives': archives,
        'read_file_count': len(records),
        'read_files': records,
        'scientific_execution_counts': {'candidate_main': 0, 'candidate_import': 0, 'physical_kernel': 0, 'physical_derivative': 0, 'physical_root': 0, 'toy': 0, 'replay': 0},
        'metadata_action': 'Only identity/read-provenance recording in independent/; no candidate modification; no harness validator rerun.',
        'protected_state': json.loads((ROOT / 'phys30/PHYSICS_CONTRACT.json').read_text())['protected_state'],
    }
    path = OUT / 'PREPARATION_READ_MANIFEST.json'
    with path.open('x') as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['phase'], 'path': str(path), 'read_file_count': len(records), **identity(path), 'scientific_execution_counts': result['scientific_execution_counts']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
