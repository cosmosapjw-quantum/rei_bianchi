#!/usr/bin/env python3
"""Mechanical static syntax, byte manifest and primary identity; no code imports.

Runs only standard-library parsing/hash/serialization. Does not load or evaluate
the candidate, scientific dependencies, source parser, gate or numerical rules.
Create-only outputs make an already frozen implementation immutable by default.
"""
from pathlib import Path
import ast
import hashlib
import json
import shlex
import sys

UNIT = Path(__file__).resolve().parents[1]


def file_record(p):
    data = p.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def write(name, data):
    with (UNIT/name).open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')


def main():
    driver_tree = ast.parse((UNIT/'source/run_primary.py').read_bytes())
    literals = {}
    for statement in driver_tree.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in ('CONTRACT_SHA', 'DEPENDENCIES'):
                    literals[target.id] = ast.literal_eval(statement.value)
    if file_record(UNIT/'CONTRACT.json')['sha256'] != literals['CONTRACT_SHA']:
        raise ValueError('Frozen revision3 contract identity mismatch')
    source_files = sorted((UNIT/'source').rglob('*.py'))
    dependency_files = [UNIT/p for p in literals['DEPENDENCIES']]+source_files
    descriptor = {'schema': 'PHYS88_PRIMARY_FROZEN_DEPENDENCIES_V1',
        'files': {str(p.relative_to(UNIT)): file_record(p) for p in dependency_files},
        'integration_plan': '2maps x4T xGL16/32full +2maps x2FDscalar=20; nooldcallbacks',
        'conditional_source_native_finite_window': True}
    binding = {'descriptor': descriptor, 'sha256': hashlib.sha256(json.dumps(descriptor,
        sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()}
    write('implementation/PRIMARY_IDENTITY.json', binding)
    wrapper = [sys.executable, '-B', str(UNIT/'source/leased_call.py')]
    output = UNIT/'results/primary001'
    def child(kind, label, command):
        return wrapper+['--kind', kind, '--label', label, '--receipt', str(UNIT/('results/'+label+'_lease.json')),
            '--admission-receipt', str(UNIT/('results/'+label+'_admission.json')), '--', *command]
    primary = [sys.executable, '-B', str(UNIT/'source/run_primary.py'), '--output', str(output)]
    reference = [sys.executable, '-B', str(UNIT/'verification/independent_reference.py'), '--unit', str(UNIT),
        '--primary', str(output/'RESULT.json'), '--expected-primary-sha256', '__ACTUAL_PRIMARY_RESULT_SHA256__',
        '--output', str(UNIT/'results/INDEPENDENT_REFERENCE.json'),
        '--controller-admission-receipt', str(UNIT/'results/reference001_admission.json')]
    figures = [sys.executable, '-B', str(UNIT/'source/plot_saved_results.py'), '--result', str(output/'RESULT.json'),
               '--output', str(UNIT/'results/figures001')]
    commands = {'schema': 'PHYS88_FROZEN_EXECUTION_COMMANDS_V1', 'primary': child('primary', 'primary001', primary),
        'resume': primary+['--resume'], 'reference': child('reference', 'reference001', reference),
        'figures': child('figures', 'figures001', figures),
        'permitted_runtime_substitution': 'Only __ACTUAL_PRIMARY_RESULT_SHA256__ in reference fromactualsuccessfulprimaryRESULTbytes',
        'dispatch': 'Sequential root explicitGO only after scientific review and required S1 publication/ACK; noautomaticretry',
        'primary_output': 'Fixedsingle results/primary001; existingdirectoryrefusesreplay',
        'admission': 'Distinct actualpostacquire/prelaunchreceipt; final outerreceipt createdafterchild',
        'figures_cache': 'Exclude results/figures001/.mpl_config fromGit/publication; no cachecredit or cleanup',
        'shell_commands': {k: shlex.join(v) for k, v in [('primary', child('primary', 'primary001', primary)),
             ('resume', primary+['--resume']), ('reference', child('reference', 'reference001', reference)),
             ('figures', child('figures', 'figures001', figures))]}}
    write('implementation/EXECUTION_COMMANDS.json', commands)
    static_rows = []
    python_files = source_files+[UNIT/'verification/independent_reference.py', Path(__file__).resolve()]
    for p in python_files:
        tree = ast.parse(p.read_bytes(), filename=str(p)); compile(tree, str(p), 'exec')
        static_rows.append({'path': str(p.relative_to(UNIT)), **file_record(p),
                            'AST_parse': True, 'code_object_compile': True, 'import_or_execution': False})
    # Prior syntax receipt is historical; this is the final static preparation receipt.
    write('implementation/FINAL_STATIC_SYNTAX_RECEIPT.json', {
        'schema': 'PHYS88_FINAL_STATIC_SYNTAX_ONLY_V1', 'files': static_rows,
        'scientific_execution': 0, 'tests': 0, 'candidate_imports': 0})
    files = set(dependency_files+python_files)
    files.update(p for p in (UNIT/'implementation').iterdir() if p.is_file() and
                 p.name != 'FROZEN_IMPLEMENTATION_MANIFEST.json')
    files.add(UNIT/'verification/REFERENCE_PLAN.json')
    write('implementation/FROZEN_IMPLEMENTATION_MANIFEST.json', {
        'schema': 'PHYS88_FROZEN_IMPLEMENTATION_MANIFEST_V1',
        'status': 'STATIC_READY_FOR_ASTRA_CODE_REVIEW_NO_EXECUTION',
        'contract_revision': 3, 'contract_sha256': literals['CONTRACT_SHA'],
        'primary_identity': binding['sha256'],
        'files': {str(p.relative_to(UNIT)): file_record(p) for p in sorted(files)},
        'self_exclusion': 'Manifest excludes ownbytes; nofutureoutput/receiptbinding',
        'runtime_reuse': ['vendor.NativeSource', 'vendor.ScaledBesselSix'],
        'old_campaign_callbacks': 0, 'scientific_executions': 0, 'tests': 0,
        'requested_executor': 'gpt-6.1-sol/high', 'actual_backend': 'UNOBSERVED'})
    print(json.dumps({'status': 'STATIC_IMPLEMENTATION_FROZEN', 'primary_identity': binding['sha256'],
        'files': len(files), 'AST_compiled_python_files': len(static_rows), 'scientific_execution': 0}))


if __name__ == '__main__':
    main()
