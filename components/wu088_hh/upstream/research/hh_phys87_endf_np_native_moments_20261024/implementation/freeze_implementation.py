"""Metadata and AST/syntax only; never import or execute the candidate sources."""
from pathlib import Path
import ast
import hashlib
import json
import datetime

UNIT = Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p): return {'bytes': p.stat().st_size, 'sha256': sha(p)}
def save(path, value): path.write_text(json.dumps(value, indent=2)+'\n')

python = '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python'
u = str(UNIT)
commands = {'schema': 'PHYS87_FROZEN_DISPATCH_ARGUMENTS_V1', 'status': 'PREPARED_NOT_DISPATCHED',
 'primary': [python, '-B', u+'/source/leased_call.py', '--kind', 'primary', '--label', 'primary001',
             '--receipt', u+'/results/primary001_lease.json', '--admission-receipt', u+'/results/primary001_admission.json', '--',
             python, '-B', u+'/source/run_primary.py', '--output', u+'/results/primary001'],
 'resume_read_only': [python, '-B', u+'/source/run_primary.py', '--output', u+'/results/primary001', '--resume'],
 'reference': [python, '-B', u+'/source/leased_call.py', '--kind', 'reference', '--label', 'reference001',
             '--receipt', u+'/results/reference001_lease.json', '--admission-receipt', u+'/results/reference001_admission.json', '--',
             python, '-B', u+'/verification/independent_reference.py', '--unit', u, '--primary', u+'/results/primary001/RESULT.json',
             '--expected-primary-sha256', 'ACTUAL_PRIMARY_RESULT_SHA256', '--output', u+'/results/INDEPENDENT_REFERENCE.json',
             '--controller-admission-receipt', u+'/results/reference001_admission.json'],
 'figures': [python, '-B', u+'/source/leased_call.py', '--kind', 'figures', '--label', 'figures001',
             '--receipt', u+'/results/figures001_lease.json', '--admission-receipt', u+'/results/figures001_admission.json', '--',
             python, '-B', u+'/source/plot_saved_results.py', '--result', u+'/results/primary001/RESULT.json', '--output', u+'/results/figures001'],
 'reference_SHA_placeholder_policy': 'Controller must replace from actual completed primary immutable bytes; no guessed digest',
 'execution_precondition': 'S1 published, stage ACKs and explicit root dispatch; fresh pinned gate each child; no scientific execution during freeze'}
save(UNIT/'implementation/EXECUTION_COMMANDS.json', commands)
syntax = []
for p in sorted((UNIT/'source').rglob('*.py')) + [Path(__file__)]:
 text = p.read_text()
 ast.parse(text, filename=str(p))
 compile(text, str(p), 'exec', dont_inherit=True)  # code object only, never executed
 syntax.append({'path': str(p.relative_to(UNIT)), **record(p), 'AST': 'PASS', 'syntax_compile_no_exec': 'PASS'})
assert sha(UNIT/'CONTRACT.json') == '464df6f83a7ac8bd64813dc9da3ca34f19398a2f970f3d69c706e3d089f6fd38'
assert sha(UNIT/'source/vendor/phys78_run_pilot.py') == '76ff57ba687fd9830b84c3fcff69eb8ed0e9f6ceab4551e61c67c84d3ea65124'
static = {'schema': 'PHYS87_STATIC_SYNTAX_ONLY_V1', 'status': 'PASS_STATIC_SYNTAX_ONLY',
          'files': syntax, 'candidate_imports': 0, 'candidate_code_execution': 0, 'tests': 0,
          'scientific_callbacks': 0, 'lease_acquisitions': 0, 'figures': 0}
save(UNIT/'implementation/STATIC_SYNTAX_RECEIPT.json', static)
paths = sorted((UNIT/'source').rglob('*.py')) + sorted((UNIT/'implementation').glob('*'))
paths = [p for p in paths if p.is_file() and p.name != 'FROZEN_IMPLEMENTATION_MANIFEST.json']
manifest = {'schema': 'PHYS87_IMPLEMENTATION_FREEZE_V1', 'status': 'PREPARED_NOT_EXECUTED',
            'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'contract_revision': 2, 'contract': record(UNIT/'CONTRACT.json'),
            'theory': record(UNIT/'theory/NATIVE_FINITE_T_MOMENTS_KO.md'),
            'raw_ENDF': record(UNIT/'source_data/n-001_H_001.endf'),
            'literal_table': record(UNIT/'source_data/SOURCE_TABLE.json'),
            'source_files': {str(p.relative_to(UNIT)): record(p) for p in paths},
            'S0_preparation_commit': 'b4e606c433bc0d7969227635b62f33e67a56c705',
            'base_PHYS86_HEAD': 'f4a6d5505c845a046e3b81d33a2992a239ab4c8b',
            'expected_primary_counts': {'thermal_integrations': 12, 'full_moment_integrations': 8,
               'FD_scalar_integrations': 4, 'source_knots': 153, 'native_cells_per_integral': 152,
               'angular_cases': 18, 'adopted_owner_rows': 16},
            'independent_reference': 'Reviewer-owned verification/independent_reference.py; separate code identity/review, no production imports',
            'requested_implementation_backend': 'gpt-6.1-sol/high', 'observed_backend': 'UNOBSERVED',
            'scientific_execution_during_preparation': 0, 'tests_during_preparation': 0,
            'lease_acquisitions_during_preparation': 0, 'reference_calls_during_preparation': 0,
            'new_ODE': 0, 'network_rate_activation': 0, 'old_PHYS85_86_calls': 0,
            'scientific_admission': 'PENDING_FRESH_C9_AND_ACTUAL_DISPATCH_RESULTS'}
save(UNIT/'implementation/FROZEN_IMPLEMENTATION_MANIFEST.json', manifest)
print(json.dumps({'status': static['status'], 'AST_files': len(syntax),
                  'source_and_implementation_files': len(paths),
                  'wrapper_sha256': sha(UNIT/'source/leased_call.py'),
                  'freeze_manifest_sha256': sha(UNIT/'implementation/FROZEN_IMPLEMENTATION_MANIFEST.json'),
                  'scientific_execution': 0}))
