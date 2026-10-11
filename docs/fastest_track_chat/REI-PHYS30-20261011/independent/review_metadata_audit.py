#!/usr/bin/env python3
"""Metadata-only final reviewer audit. Never imports or runs a candidate module."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from decimal import Decimal
import ast
import hashlib
import json
import stat
import zipfile

ROOT = Path('/workspace/scratch/603081e41728/phys30')
OUT = ROOT / 'independent/REVIEW_METADATA_AUDIT.json'
FREEZE = 'evidence/CANDIDATE_FROZEN.json'
FREEZE_SHA = '5dd90996f30de50a2e9901345102a79b934cfb2384e77d19e9345fa2a001e05d'
SCIENCE_ZERO = dict(candidate_main=0, candidate_import=0, physical_kernel=0,
                    physical_derivative=0, physical_root=0, toy=0, replay=0,
                    coefficient_formula_evaluation=0, higher_order_research=0)


def identity(path, name=None):
    path = Path(path)
    content = path.read_bytes()
    return dict(path=name or str(path), bytes=len(content),
                sha256=hashlib.sha256(content).hexdigest(),
                mode=format(stat.S_IMODE(path.stat().st_mode), '04o'),
                regular_file=path.is_file() and not path.is_symlink())


def read(name):
    return json.loads((ROOT / name).read_bytes())


def check_row(base, row):
    actual = identity(base / row['path'], row['path'])
    checks = {key: actual[key] == row[key] for key in ('bytes', 'sha256', 'mode')}
    checks['regular_file'] = actual['regular_file']
    return dict(actual=actual, expected=row, checks=checks, matches=all(checks.values()))


def put(name, value):
    with (ROOT / 'independent' / name).open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def main():
    if OUT.exists():
        raise FileExistsError('Preserve the first metadata audit; do not overwrite it')
    began = datetime.now(timezone.utc).isoformat()
    candidate = read(FREEZE)
    frozen_identity = identity(ROOT / FREEZE, FREEZE)
    candidate_rows = [check_row(ROOT, row) for row in candidate['files']]
    pre_name = 'contributions/numerics/PREEXECUTION_FROZEN.json'
    pre = read(pre_name)
    closure = pre['files'] + [{key: value for key, value in identity(ROOT / pre_name, pre_name).items()
                              if key != 'regular_file'}]
    pre_rows = [check_row(ROOT, row) for row in closure]
    raw_name = 'contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json'
    raw_bytes = (ROOT / raw_name).read_bytes()
    raw = json.loads(raw_bytes)
    protocol = read('contributions/numerics/PROTOCOL.json')
    first = read('contributions/numerics/EXECUTION.json')
    replay = read('portability/REPLAY_RECEIPT.json')
    replay_bytes = (ROOT / 'portability/raw/PROFILE_SECOND_ORDER_REPLAY.json').read_bytes()
    summary = read('report/PHYS30_RESULTS_SUMMARY.json')
    old = read('inputs/PHYS29/contributions/numerics/SECOND_ORDER_FIRST.json')
    owner = read('evidence/OWNER_FIRST_RESULT_INTAKE.json')
    checks = raw['checks']
    inventory = [dict(name=item['name'], passed=item['passed'],
                      component_count=len(item.get('components', [])),
                      all_component_flags_true=all(c['passed'] is True for c in item.get('components', [])),
                      identity_member_count=len(item.get('members', [])),
                      maximum_scaled_error=item.get('maximum_scaled_error'),
                      arithmetic=item.get('arithmetic', 'discrete')) for item in checks]
    # Decimal comparison orders already-stored errors only; no error or coefficient is reevaluated.
    maxima = [item for item in inventory if item['maximum_scaled_error'] is not None]
    maximum = max(maxima, key=lambda item: Decimal(item['maximum_scaled_error']))
    component_count = sum(item['component_count'] for item in inventory)
    member_count = sum(item['identity_member_count'] for item in inventory)
    flags = dict(group_count=len(checks), group_passed_count=sum(item['passed'] is True for item in checks),
                 all_group_flags=all(item['passed'] is True for item in checks),
                 component_count=component_count,
                 all_component_flags=all(item['all_component_flags_true'] for item in inventory),
                 identity_member_count=member_count,
                 all_member_flags=all(member['passed'] is True for item in checks for member in item.get('members', [])),
                 catalogue_equal=[item['name'] for item in checks] == protocol['acceptance_check_names'],
                 actual_counts_equal=raw['actual_counts'] == protocol['expected_counts_one_successful_main'],
                 inventory_equal_owner=inventory == owner['check_inventory'],
                 stored_maximum=maximum,
                 stored_maximum_equal_owner=maximum == owner['maximum_stored_scaled_error'])
    copies = dict(first_summary=summary['first_summary'] == raw['summary'],
                  profiles=summary['profiles'] == raw['exact_profile_moments'],
                  branch_profile_slopes=summary['branch_profile_slopes'] == raw['branch_profile_slopes'],
                  gap=summary['gap'] == raw['gap_results'])
    for profile in ('uniform', 'triangular'):
        for branch in ('upper_root', 'lower_root'):
            record = raw['profile_results'][profile]['branches'][branch]
            copies[f'{profile}.{branch}.affine'] = summary['profile_coefficients'][profile][branch] == record['affine']
            copies[f'{profile}.{branch}.retained_A'] = summary['retained_nonzero_A'][profile][branch] == record['retained_nonzero_A_diagnostics']
    cache = raw['retained_physical_data']
    copied_cache = dict(
        four_node_strings=cache['energy_nodes_eV'] == old['energy_nodes_eV'],
        twelve_component_strings=cache['components'] == {
            node: {key: values[key] for key in ('k_s-4', 'k_prime_s-4_eV-1', 'k_second_s-4_eV-2')}
            for node, values in old['joint_kernel_outputs']['jet'].items()},
        uniform_retained_branch_maps=cache['PHYS29_uniform_partials_weights_and_coefficients'] == old['second_order']['jet_chain'])
    proof = (ROOT / 'contributions/theory/DERIVATION_KO.md').read_text()
    proof = proof.replace('](../../', '](../').replace('](THEORY_CLAIMS.json)', '](../contributions/theory/THEORY_CLAIMS.json)').replace('](PROVENANCE.json)', '](../contributions/theory/PROVENANCE.json)')
    transformed = '\n'.join('#' + line if line.startswith('#') else line for line in proof.splitlines()) + '\n'
    report_text = (ROOT / 'report/PHYS30_REPORT_KO.md').read_text()
    appendix = dict(full_transformed_theory_is_report_suffix=report_text.endswith(transformed),
                    source_lines=len(proof.splitlines()), transformed_lines=len(transformed.splitlines()),
                    report_lines=len(report_text.splitlines()),
                    permitted_transform='heading depth plus three relative-link substitutions only')
    assembly = read('evidence/REPORT_ASSEMBLY.json')
    assembly_matches = []
    for row in assembly['inputs'] + assembly['outputs']:
        actual = identity(ROOT / row['path'], row['path'])
        assembly_matches.append(dict(path=row['path'], matches=all(actual[key] == row[key] for key in ('bytes', 'sha256'))))
    theory = read('contributions/theory/THEORY_CLAIMS.json')
    ledger = read('evidence/CLAIM_LEDGER.json')
    ledger_matches = ledger['theory_claims'] == theory['claims']
    figure = read('figures/FIGURE_PROVENANCE.json')
    display_rows = []
    for branch, profiles in figure['displayed_raw_strings'].items():
        for profile, row in profiles.items():
            values = []
            for pointer in row['source_pointers']:
                value = raw
                for key in pointer.split('.'):
                    value = value[key]
                values.append(value)
            display_rows.append(dict(branch=branch, profile=profile,
                all_six_raw_strings_equal=values == row['values'],
                c_string_equal=row['c_eV'] == raw['profile_results'][profile]['branches'][branch]['affine']['c_eV']))
    display_identities = []
    for key in ('input', 'source', 'output'):
        row = figure[key]
        actual = identity(ROOT / row['path'], row['path'])
        display_identities.append(dict(kind=key, actual=actual, matches=all(actual[k] == row[k] for k in ('bytes', 'sha256'))))
    runtime = Path(replay['runtime'])
    runtime_rows = [check_row(runtime, row) for row in closure]
    expected_set = {row['path'] for row in closure}
    actual_runtime_set = {path.relative_to(runtime).as_posix() for path in runtime.rglob('*') if path.is_file() or path.is_symlink()}
    archive_path = Path(replay['archive']['path'])
    zip_rows = []
    with zipfile.ZipFile(archive_path) as archive:
        members = archive.infolist()
        zip_names = [member.filename for member in members]
        for expected in closure:
            info = archive.getinfo(expected['path'])
            data = archive.read(info)
            actual = dict(path=info.filename, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                          mode=format(stat.S_IMODE(info.external_attr >> 16), '04o'))
            safe = (not info.is_dir() and not PurePosixPath(info.filename).is_absolute()
                    and '..' not in PurePosixPath(info.filename).parts
                    and stat.S_ISREG(info.external_attr >> 16))
            zip_rows.append(dict(actual=actual, safe_regular_file=safe,
                                 matches=safe and all(actual[key] == expected[key] for key in ('path', 'bytes', 'sha256', 'mode'))))
    retained_replay = []
    for row in replay['retained_raw_evidence']:
        original = identity(row['original_path'])
        retained = identity(ROOT / row['retained_path'], row['retained_path'])
        retained_replay.append(dict(original=original, retained=retained,
            matches=all(original[k] == retained[k] == row[k] for k in ('bytes', 'sha256', 'mode'))))
    source = read('SOURCE_MANIFEST.json')
    remote = read('evidence/REMOTE_INTAKE.json')
    remote_rows = {row['path']: row for row in remote['source_entries']}
    sources = []
    for row in source['files']:
        path = ROOT / 'inputs/PHYS29/inputs/pinned_source' / row['path']
        data = path.read_bytes()
        actual = identity(path)
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        rr = remote_rows[row['path']]
        matches = (actual['bytes'] == row['bytes'] == rr['size'] and actual['sha256'] == row['sha256']
                   and blob == row['git_blob'] == rr['sha'] and row['git_mode'] == rr['mode'] == '100644'
                   and actual['mode'] == '0644' and actual['regular_file'])
        sources.append(dict(path=row['path'], actual=actual, actual_git_blob=blob, matches=matches))
    source_text = (ROOT / 'contributions/numerics/profile_second_order.py').read_text()
    tree = ast.parse(source_text)  # Syntax tree only; never compile, import, exec or run.
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    source_inventory = dict(import_modules=sorted(set(imports)),
        functions=[node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))],
        float_literal_count=sum(isinstance(node, ast.Constant) and isinstance(node.value, float) for node in ast.walk(tree)),
        protocol_sha_literal_present=identity(ROOT / 'contributions/numerics/PROTOCOL.json')['sha256'] in source_text,
        interpretation='Static syntax inventory accompanies full reviewer source read; no candidate import and no scientific predicate rerun.')
    gates = dict(
        root_GO_freeze_identity=frozen_identity['sha256'] == FREEZE_SHA and frozen_identity['bytes'] == 25416 and frozen_identity['mode'] == '0644',
        candidate_123_preserved=len(candidate_rows) == 123 and all(row['matches'] for row in candidate_rows),
        preexecution_closure15_preserved=len(pre_rows) == 15 and all(row['matches'] for row in pre_rows),
        runtime_exact_set=actual_runtime_set == expected_set,
        runtime_15_identities=all(row['matches'] for row in runtime_rows),
        archive_exact_unique_set=set(zip_names) == expected_set and len(zip_names) == len(set(zip_names)) == 15,
        archive_15_identities=all(row['matches'] for row in zip_rows),
        archive_identity=identity(archive_path)['sha256'] == replay['archive']['sha256'] and identity(archive_path)['bytes'] == replay['archive']['bytes'],
        raw_byte_equal=raw_bytes == replay_bytes,
        raw_parsed_JSON_equal=raw == json.loads(replay_bytes),
        original_and_retained_replay_files=all(row['matches'] for row in retained_replay),
        first_replay_stdout_equal=(ROOT / 'contributions/numerics/FIRST_STDOUT.txt').read_bytes() == (ROOT / 'portability/raw/replay.stdout.txt').read_bytes(),
        first_replay_stderr_empty=(ROOT / 'contributions/numerics/FIRST_STDERR.txt').read_bytes() == (ROOT / 'portability/raw/replay.stderr.txt').read_bytes() == b'',
        stored_56_384_17_flags=flags['all_group_flags'] and flags['all_component_flags'] and flags['all_member_flags'] and (len(checks), component_count, member_count) == (56,384,17),
        stored_catalogue_and_counts=flags['catalogue_equal'] and flags['actual_counts_equal'],
        owner_intake_inventory=flags['inventory_equal_owner'] and flags['stored_maximum_equal_owner'],
        summary_copy_equality=all(copies.values()),
        PHYS29_cache_string_equality=all(copied_cache.values()),
        full_theory_appendix_equality=appendix['full_transformed_theory_is_report_suffix'],
        report_assembly_identities=all(row['matches'] for row in assembly_matches),
        theory_claim_ledger_equality=ledger_matches,
        figure_stored_display_equality=all(row['all_six_raw_strings_equal'] and row['c_string_equal'] for row in display_rows),
        figure_current_identities=all(row['matches'] for row in display_identities),
        source7_local_and_recorded_remote_identity=all(row['matches'] for row in sources),
        recorded_head_tree_agree=source['input_commit'] == remote['head'] and source['input_tree'] == remote['tree'] and source['scientific_src_tree'] == remote['scientific_src']['sha'],
        first_and_replay_receipt_actual_success=first['exit_code'] == 0 and first['actual_main_invocations'] == 1 and replay['actual_exit_code'] == 0 and replay['new_program_replay_invocations'] == 1 and not replay['timed_out'],
        source_only_allowed_imports=set(imports) <= {'__future__','argparse','decimal','fractions','hashlib','json','pathlib','sys','traceback'},
        source_no_float_literals=source_inventory['float_literal_count'] == 0,
        source_protocol_pin=source_inventory['protocol_sha_literal_present'])
    record = dict(task='REI-PHYS30-20261011', reviewer='/root/phys30_decision', role='distinct NONBLIND decision reviewer',
        began_utc=began, ended_utc=datetime.now(timezone.utc).isoformat(),
        status='METADATA_AUDIT_PASS' if all(gates.values()) else 'METADATA_AUDIT_FAILURE_PRESERVED',
        audit_science_counts=SCIENCE_ZERO,
        scope='Identity, exact string/object copying, stored-flag catalogue inspection, static AST inventory only. No new scientific check execution. Existing replay runtime/archive are only read, not restored again.',
        gates=gates, failed_gates=[key for key,value in gates.items() if not value],
        candidate_freeze=frozen_identity, candidate_rows=candidate_rows,
        preexecution_closure=pre_rows, existing_replay_runtime=runtime_rows,
        archive=identity(archive_path), archive_members=zip_rows, replay_retained_files=retained_replay,
        cached_flags=flags, cached_group_inventory=inventory, summary_copy_checks=copies,
        retained_PHYS29_copy_checks=copied_cache, report_appendix=appendix,
        report_assembly_checks=assembly_matches, figure_copy_checks=display_rows,
        figure_identity_checks=display_identities, pinned_source_identity_checks=sources,
        remote_scope='Recorded immutable intake identities compared to local bytes; reviewer does not claim a fresh remote API observation.',
        static_source_inventory=source_inventory)
    put('REVIEW_METADATA_AUDIT.json', record)
    print(json.dumps(dict(status=record['status'], gate_count=len(gates), failed_gates=record['failed_gates'],
        candidate_files=len(candidate_rows), closure_files=len(closure), grouped_flags=len(checks),
        component_flags=component_count, identity_member_flags=member_count,
        science_counts=SCIENCE_ZERO, output=identity(OUT)), ensure_ascii=False))
    return 0 if all(gates.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
