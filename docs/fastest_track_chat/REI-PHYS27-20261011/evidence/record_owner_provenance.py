#!/usr/bin/env python3
"""Record already performed PHYS27 source/harness consumption; no science."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT.parent / 'harness_phys27'

def write(name, value):
    (ROOT / 'evidence' / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

reads = [
    'START_HERE.md', 'PROJECT_INSTRUCTIONS.md',
    'prompts/00_integrated_work_run.md', 'docs/MODEL_ROUTING.md',
    'state/RESEARCH_STATE.md', 'prompts/phases/06_physics_math_validation.md',
    'prompts/phases/08_external_decision_gate.md',
    'policies/EVIDENCE_AND_CITATION.md', 'policies/STOP_RULES.md',
]
write('HARNESS_LOAD.json', {
    'task': 'REI-PHYS27-20261011',
    'selected_model': 'GPT-6 Astra',
    'basis': 'Trusted host developer model metadata GPT-6 Astra Pro; skill MODEL_ROUTER.json read',
    'skill_package': 'skill://flora-user-skills/root/.codex/skills/remote-skills/skill-6aa0657100b08191b7d67482d1f97c1d',
    'harness_version': '4.0.0',
    'archive_sha256': 'dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7',
    'archive_bytes': 70628,
    'actual_owner_reads': [{'path': p, 'scope': 'full text',
        'sha256': hashlib.sha256((HARNESS / p).read_bytes()).hexdigest(),
        'bytes': (HARNESS / p).stat().st_size} for p in reads],
    'template_state_classification': 'NOT_RUN template; never counted as execution or prior research evidence',
    'historical_main_or_suite_invocations_for_load': 0,
})
write('LITERATURE_SCOPE.json', {
    'task': 'REI-PHYS27-20261011',
    'purpose': 'Primary-source context for the two preregistered quadrature methods only',
    'sources': [
        {'title': 'NIST Digital Library of Mathematical Functions, 3.5 Quadrature',
         'url': 'https://dlmf.nist.gov/3.5',
         'owner_direct_open': True,
         'actually_read_sections': ['Displayed lines 151-199: composite Simpson rule and error',
                                    'Displayed lines 380-490: Gaussian rule, polynomial exactness, remainder, Gauss-Legendre weight/domain'],
         'supports': ['Gauss polynomial exactness and positive weights', 'Composite Simpson method context'],
         'does_not_support': ['An interval error bound for this particular k', 'Physical or atomic/J uncertainty', 'Originality of PHYS27']},
        {'title': 'Nicholas Hu, Newton-Cotes quadrature',
         'url': 'https://math.ucla.edu/~njhu/notes/na/numint/newtoncotes/',
         'owner_direct_open': True,
         'actually_read_sections': ['Displayed lines 0-55: closed Newton-Cotes nodes, precision, sign/error structure and Simpson weights'],
         'supports': ['Independent scalar Simpson-rule context'],
         'does_not_support': ['Our numerical result', 'A bound on the Richardson extrapolation remainder']},
    ],
    'new_derivative_or_specialized_literature_campaign': False,
    'whole_page_read_claim': False,
    'primary_kernel_fit_source': 'Frozen repository source and actually consumed PHYS22/24/25/26 artifacts; not reconstructed from web prose',
})
write('OWNER_CONSUMPTION.json', {
    'task': 'REI-PHYS27-20261011',
    'role': 'NONBLIND owner, contract designer, candidate integrator; not independent final reviewer',
    'inheritance': {
        'PHYS26_archive': {'library_id': 'libfile_f4328f8b485c81918e6c64d06b0045f7',
            'bytes': 709198, 'sha256': '9a7919a4828d5285d1af9b408d46234fe36f1ddeaa8d6392d6682d151b2131e6',
            'actual_materialization_and_zip_restore': True, 'manifest_payloads_verified': 68,
            'scientific_rerun': False},
        'current_PHYS27_handoff': {'library_id': 'libfile_2b4dff85a6bc8191ba462bf35a376888',
            'read': 'All 84 lines; then actual archive copy and SHA consumed', 'bytes': 7231},
        'PHYS26_detached_receipt': {'library_id': 'libfile_a6faf46d7b68819194ae87eced1e2ad8',
            'read': 'Only lines 1-85 of 974; archive, gate and harness identities',
            'not_claimed': 'Full receipt read or complete local materialization'},
        'restored_owner_reads': [
            {'path': 'inputs/PHYS26/PHYSICS_CONTRACT.json', 'scope': 'full'},
            {'path': 'inputs/PHYS26/SOURCE_MANIFEST.json', 'scope': 'full'},
            {'path': 'inputs/PHYS26/contributions/theory/ENVELOPE_DERIVATION_KO.md', 'scope': 'full'},
            {'path': 'inputs/PHYS26/report/PHYS26_REPORT_KO.md', 'scope': 'full; display-truncated tail recovered by selected read'},
            {'path': 'inputs/PHYS26/independent/DECISION_REVIEW.json',
             'scope': 'selected decision, promoted_scope, findings, phase8_assessment, not_promoted, protected, stop_decision'},
            {'path': 'inputs/PHYS26/contributions/numerics/fixed_variance_envelope.py',
             'scope': 'owner first 110 lines only; numerical contributor records its separate full pure-code consumption'},
        ],
        'copied_selected_input_files': 41,
        'all_copied_inputs_claimed_fully_read_by_owner': False,
    },
    'current_source_binding': {
        'actual_commit': '75fd81e9e63c442d6da5f95bd3a80bdec16a4c37',
        'actual_root_tree': '9c6a7d39d3af2626c7b56c87f1f607fd693c39e6',
        'actual_source_tree': 'cb69b4736dd046e4675557577eb8e0ead037d1f3',
        'all_7_pinned_blobs_size_mode_match_current_tree': True,
        'governing_AGENTS': 'No local parent or relevant repository parent AGENTS; only a disjoint historical BASS_HE snapshot was present',
        'full_tree_is_metadata_not_full_source_read': True,
    },
    'new_owner_reads_before_integration': [
        'PHYSICS_CONTRACT.json full',
        'contributions/numerics/PROTOCOL.json full',
        'contributions/numerics/PREEXECUTION_FROZEN.json full',
        'contributions/numerics/finite_width_envelope.py all 576 lines in sequential windows',
        'contributions/theory/FINITE_WIDTH_DERIVATION_KO.md full before final provenance closeout; Japanese typo fixed by contributor',
        'FINITE_WIDTH_FIRST.json: all constants, endpoint signs, threshold comparison, summary, roots excluding histories, 9 case intervals, W19.74 bands and mixtures',
    ],
    'new_first_science_executor': '/root/phys27_numerics',
    'owner_old_science_main_invocations': 0,
    'owner_new_scientific_main_invocations': 0,
    'first_result_sha256': '3b2c71b7c2d650ac92e78e6eed041039ddd41f0d9e48cdfa95d9ebfec1448314',
    'review_independence_plan': 'Fresh distinct decision reviewer, not theory/numerical generator; full-history NONBLIND explicitly recorded',
})
print(json.dumps({'written': ['HARNESS_LOAD.json', 'LITERATURE_SCOPE.json', 'OWNER_CONSUMPTION.json'],
                  'science_invocations': 0}))
