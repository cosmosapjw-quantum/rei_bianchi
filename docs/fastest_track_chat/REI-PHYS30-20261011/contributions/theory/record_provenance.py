"""Record theory-file identities and observed read scope; no scientific imports/evaluation."""
from pathlib import Path
from datetime import datetime, timezone
import difflib
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parents[2]
TASK = BASE / 'phys30'
START = datetime.now(timezone.utc).isoformat()


def identity(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


source_specs = [
    ('phys29/next/PHYS30_NEXT_HANDOFF_KO.md',
     '32281a9fed516e7d3edf2fab8287a40432bca5326a574977fe258abcb6558a70',
     'inputs/PHYS29/next/PHYS30_NEXT_HANDOFF_KO.md', 'Full file'),
    ('phys29/PHYSICS_CONTRACT.json',
     '603e2a30074800edd2226c86cf1f256efe5fd49ad45a2252788059d19a487d10',
     'inputs/PHYS29/PHYSICS_CONTRACT.json', 'Full file'),
    ('phys29/contributions/theory/DERIVATION_KO.md',
     '764cddda1c8af278995be4bf02476acefa82ecfbfff88699daebf30d524dd9f1',
     'inputs/PHYS29/contributions/theory/DERIVATION_KO.md', 'Full file in lines1-340 and341-end'),
    ('phys29/independent/DECISION_REVIEW.json',
     'c497fb6e6e21f7adb44b001f1d2d827847e0ee752fb4e28ed88afaaf9bfe6f2d',
     'inputs/PHYS29/independent/DECISION_REVIEW.json',
     'Selected semantic read: decision, reviewer, candidate, promoted_scope, not_promoted, mathematical_assessment, uncertainty, protected, next; related claims TC29-01,02,03,07,14 and P30-NEXT explicitly reread. Full-file byte read for identity is not full semantic review.'),
    ('phys30/PHYSICS_CONTRACT.json',
     '475ce8957b46ce1440f227cd1a4b8c5fb3979cf237e4c8e52a5e76028cd78a5d',
     'PHYSICS_CONTRACT.json', 'Full file'),
]
sources = []
for rel, expected, portable, scope in source_specs:
    p = BASE / rel
    row = identity(p)
    assert row['sha256'] == expected, rel
    copy = TASK / portable
    assert copy.read_bytes() == p.read_bytes(), portable
    row.update(semantic_read_scope=scope, portable_copy=portable,
               portable_copy_byte_equal=True, source_relation='supports definitions, inherited premises and scope; not independent new physics')
    sources.append(row)

archive = BASE / 'recovered_inputs_phys27/physmath-research-harness-gpt6-astra-v4.0.0-20260908.zip'
archive_id = identity(archive)
assert archive_id['sha256'] == 'dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7'
hpaths = ['START_HERE.md', 'README.md', 'PROJECT_INSTRUCTIONS.md',
          'state/RESEARCH_STATE.md', 'prompts/00_integrated_work_run.md',
          'docs/MODEL_ROUTING.md', 'prompts/phases/01_research_contract.md',
          'prompts/phases/06_physics_math_validation.md',
          'prompts/phases/09_survivor_formalization.md',
          'prompts/routing/PARALLELIZATION.md', 'policies/STOP_RULES.md']
hreads = []
with zipfile.ZipFile(archive) as z:
    archive_id['entry_count'] = len(z.namelist())
    for rel in hpaths:
        p = BASE / 'harness_phys27' / rel
        assert p.read_bytes() == z.read(rel), rel
        row = identity(p)
        row.update(semantic_read_scope='Full file', archive_member=rel, archive_byte_equal=True)
        hreads.append(row)

skillroot = Path('/root/.codex/skills/remote-skills/skill-6aa0657100b08191b7d67482d1f97c1d')
skills = []
for rel in ['SKILL.md', 'references/MODEL_ROUTER.json',
            'references/REI_EXECUTION_POLICY.md', 'references/REI_EXECUTION_POLICY.json']:
    row = identity(skillroot / rel)
    row['semantic_read_scope'] = 'Full body via skills.read' if rel == 'SKILL.md' else 'Full file via executor read'
    skills.append(row)

draft = ROOT / 'versions/DERIVATION_DRAFT1_KO.md'
doc = ROOT / 'DERIVATION_KO.md'
claims_path = ROOT / 'THEORY_CLAIMS.json'
claims = json.loads(claims_path.read_text())
assert len(claims['claims']) == 20
assert len({c['id'] for c in claims['claims']}) == 20
assert identity(draft)['sha256'] == '1ca0481b08d7bb1c8f40e5a4886fb144f4d3207a05bfe457475f167f1bcab886'
diff = ROOT / 'versions/DRAFT1_TO_FINAL.patch'
assert not diff.exists()
diff.write_text(''.join(difflib.unified_diff(draft.read_text().splitlines(keepends=True),
                                          doc.read_text().splitlines(keepends=True),
                                          fromfile='versions/DERIVATION_DRAFT1_KO.md',
                                          tofile='DERIVATION_KO.md')))
body = doc.read_text()
tags = re.findall(r'\\tag\{T30\.(\d+)\}', body)
assert tags == [str(i) for i in range(1, 55)], tags
assert body.count(r'\[') == body.count(r'\]')
assert body.count(r'\(') == body.count(r'\)')
assert re.search('[\u3040-\u30ff]', body) is None
target = ROOT / 'PROVENANCE.json'
assert not target.exists()
links = []
for link in re.findall(r'\[[^\]]+\]\(([^)\n]+)\)', body):
    linked = (ROOT / link).resolve()
    is_self = linked == target
    assert is_self or linked.is_file(), link
    links.append({'link': link, 'resolved_path': str(linked),
                  'scope': 'Self pointer to this receipt' if is_self else 'Existing local file observed'})

artifact_paths = [doc, claims_path, draft, diff, ROOT / 'PRE_FREEZE_EVENTS.json', Path(__file__)]
provenance = {
    'schema': 'rei-phys30-theory-provenance-v1',
    'task': 'REI-PHYS30-20261011',
    'recorded_utc': datetime.now(timezone.utc).isoformat(),
    'contributor': '/root/phys30_theory',
    'role': 'THEORY_CANDIDATE_GENERATOR_NONBLIND',
    'model': 'GPT-6 Astra Pro',
    'model_basis': 'Trusted developer designation; full-history fork with inherited actual model. No model switch or performance claim.',
    'authorization': 'Root focused task: pure derivation and source reading in contributions/theory only; new numeric scientific execution0.',
    'status': 'THEORY_CONTRIBUTION_READY_FOR_OWNER_AND_DISTINCT_FINAL_REVIEW',
    'actual_source_reads': sources,
    'harness': {'research_version': '4.0.0', 'archive': archive_id,
                'actual_full_reads': hreads, 'templates_are_execution_evidence': False,
                'coding_harness': 'Not applied by this pure-theory contributor; coding role is separate.'},
    'skill_reads': skills,
    'external_literature': {
        'directly_opened_by_this_contributor': [],
        'owner_reported_context_only': {
            'reported_by': '/root',
            'author': 'John K. Hunter', 'year_reported': 2011,
            'title_reported': 'Measure Theory, Chapter4',
            'location_reported': 'Theorem4.24, page49; chapter PDF page11',
            'urls_reported': ['https://www.math.ucdavis.edu/~hunter/measure_theory/measure_notes_ch4.pdf',
                              'https://www.math.ucdavis.edu/~hunter/measure_theory/measure_notes_intro.pdf'],
            'relation': 'contextual: dominated-convergence background for fixed finite measures',
            'full_source_not_read_here': True,
            'not_evidence_of': ['New profile theorem priority', 'Independent physics', 'A new derivative-sign certificate']
        }
    },
    'derivation_method': [
        'Product-measure pushforward and direct moment identities.',
        'Nonnegative (y-alpha)*(beta-y) identity plus explicit feasible center mixture.',
        'Support-preserving differentiation under a fixed finite measure using compact derivative bounds.',
        'Quadratic Hermite majorant/minorant with Rolle remainder and fixed moments.',
        'Physical half-rectangle, positive variance slope, sign persistence, right implicit derivatives and integral Taylor identity.',
        'Fixed-actual-W chain rule and retained nonzero A-level numerator identities.',
        'Analytic polynomial profile moments, quadratic degeneracy and dimensional audit.'
    ],
    'self_readback': {
        'classification': 'THEORY_CONTRIBUTOR_SELF_CHECK',
        'derivation': 'Complete body readback followed by actual readback of the final two wording changes.',
        'claims': 'Full JSON readback with claims09-12 explicitly reread after aggregate display truncation.',
        'equation_tag_sequence': 'T30.1 through T30.54 exactly once',
        'balanced_math_delimiters': True,
        'relative_links': links,
        'semantic_proof_is_not_certified_by_metadata_checks': True
    },
    'preserved_events': identity(ROOT / 'PRE_FREEZE_EVENTS.json'),
    'artifacts_bound_except_this_self_referential_receipt': [identity(p) for p in artifact_paths],
    'actual_scientific_execution_by_contributor': claims['execution'],
    'independence': {
        'NONBLIND': True, 'shared_parent_history': True,
        'theory_candidate_generation': True,
        'validation_design_communication': True,
        'independent_final_reviewer': False,
        'independent_physical_evidence_credit': 0,
        'role_limit': 'Candidate and self-check only. Parent owns integration, numeric execution, final reviewer gate and publication.'
    },
    'protected_state': claims['protected'],
    'next_question_status': 'PROPOSED_NOT_RUN; same-mu2 profiles and first higher-order threshold distinction.',
    'self_hash_policy': 'This receipt does not embed its own hash; owner/final manifest may bind it after creation.'
}
target.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')
assert all(Path(row['resolved_path']).is_file() for row in links)
receipt = {
    'task': provenance['task'], 'role': provenance['role'],
    'classification': 'METADATA_ONLY_NO_SCIENTIFIC_EXECUTION',
    'status': 'RECORDED_AND_LOCAL_FILE_CHECKS_PASS',
    'start_utc': START, 'end_utc': datetime.now(timezone.utc).isoformat(),
    'script': identity(Path(__file__)), 'provenance': identity(target),
    'derivation': identity(doc), 'claims': identity(claims_path),
    'source_portable_copy_count': len(sources), 'harness_member_count': len(hreads),
    'claim_count': len(claims['claims']), 'equation_tags': len(tags),
    'relative_link_count': len(links), 'all_relative_links_resolved': True,
    'scientific_main': 0, 'physical_kernel_derivative_root_evaluations': 0,
    'metadata_invocation_this_script': 1,
    'earlier_distinct_metadata_failure': 'PRE_FREEZE_EVENTS.json',
    'candidate_final_decision': 'NOT_PERFORMED_BY_THIS_CONTRIBUTOR'
}
execution = ROOT / 'METADATA_EXECUTION.json'
assert not execution.exists()
execution.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False, indent=2))
