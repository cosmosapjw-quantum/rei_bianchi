#!/usr/bin/env python3
"""Join a frozen signed prefix and its completed resource-only segment.
No solver, interpolation, clock rebasing, or full-history feedback integration.
"""
import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
FILES = ('history.csv', 'abundances.csv', 'ledgers.csv', 'feedback.csv', 'spectra.csv')

class NotReady(ValueError):
    pass

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def terminal(path):
    return dict(line.split('=', 1) for line in Path(path).read_text().splitlines() if '=' in line)

def equivalent(left, right):
    if left.keys() != right.keys():
        return False
    for key in left:
        if left[key] == right[key]:
            continue
        try:
            a, b = float(left[key]), float(right[key])
            if not math.isfinite(a) or not math.isfinite(b) or a != b:
                return False
        except ValueError:
            return False
    return True

def groups(path, case='SHEAR_MINUS'):
    with Path(path).open(newline='') as f:
        reader = csv.DictReader(f)
        previous = None
        for t, rows in itertools.groupby(reader, lambda r: float(r['time_s'])):
            block = list(rows)
            if not math.isfinite(t) or (previous is not None and t <= previous):
                raise NotReady('HOLD_TIME_ORDER:' + str(path))
            for row in block:
                if None in row or any(v is None for v in row.values()):
                    raise NotReady('HOLD_INCOMPLETE_CSV_ROW:' + str(path))
                for k, v in row.items():
                    try:
                        x = float(v)
                    except ValueError:
                        continue
                    if not math.isfinite(x):
                        raise NotReady('HOLD_NONFINITE:' + k)
                if row.get('case_id', case) != case or row.get('run_id', case) != case:
                    raise NotReady('HOLD_CSV_CASE_IDENTITY')
                if 'ledger_name' in row and row['status'] == 'VALUE':
                    if row['tolerance'] != '':
                        raise NotReady('HOLD_VALUE_LEDGER_SCHEMA')
                elif 'ledger_name' in row:
                    tol = float(row['tolerance'])
                    if tol <= 0 or abs(float(row['residual'])) > tol or row['status'] != 'PASS':
                        raise NotReady('HOLD_SAVED_LEDGER:' + row['ledger_name'])
            yield t, block
            previous = t

def join_csv(original, segment, target, boundary, case):
    """Stream groups, retain exact original bytes as values, discard boundary once."""
    with Path(original).open(newline='') as f:
        header = next(csv.reader(f))
    with Path(segment).open(newline='') as f:
        if next(csv.reader(f)) != header:
            raise NotReady('HOLD_HEADER_MISMATCH:' + str(segment))
    counts = {'original_rows': 0, 'segment_rows_after_boundary': 0, 'boundary_rows_removed': 0}
    last = None
    with Path(target).open('x', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for t, block in groups(original, case):
            writer.writerows(block)
            counts['original_rows'] += len(block)
            last = (t, block)
        stream = iter(groups(segment, case))
        first = next(stream, None)
        if last is None or first is None or last[0] != boundary or first[0] != boundary:
            raise NotReady('HOLD_SHARED_BOUNDARY_TIME')
        if len(last[1]) != len(first[1]) or not all(equivalent(a, b) for a, b in zip(last[1], first[1])):
            raise NotReady('HOLD_SHARED_BOUNDARY_VALUES:' + str(segment))
        counts['boundary_rows_removed'] = len(first[1])
        for t, block in stream:
            writer.writerows(block)
            counts['segment_rows_after_boundary'] += len(block)
    counts['composed_rows'] = counts['original_rows'] + counts['segment_rows_after_boundary']
    return counts

def check_counters(prior, final, history_counts):
    for name in ('accepted', 'attempts', 'rejections', 'rhs_evaluations', 'wall_s'):
        if float(final[name]) < float(prior[name]):
            raise NotReady('HOLD_COUNTER_REBASE:' + name)
    if history_counts['original_rows'] != int(prior['accepted']) + 1:
        raise NotReady('HOLD_PREFIX_ACCEPTED_ROWS')
    if history_counts['segment_rows_after_boundary'] != int(final['accepted']) - int(prior['accepted']):
        raise NotReady('HOLD_SEGMENT_ACCEPTED_ROWS')
    if history_counts['composed_rows'] != int(final['accepted']) + 1:
        raise NotReady('HOLD_GLOBAL_ACCEPTED_ROWS')

CASES = ('SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS')
OLD = 'd7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185'
NEW = '4de69c1e68ebd395fe2d0b5580d901b9a82bde86cadbd11bdd07e5ad2042b4a1'
DECISION = '80dd0bf70778f82a8bd10e1bb603fa31d270cc0dcfdfd00b9c8ddf07c7855e9a'
REVIEW = '03a291a56b9f3b7b22c63f7a7e75ef69ef58e990e6fe4d2e0541c5b2275f3399'
BINDING_KEYS = ('execution_authorized', 'start_authorized', 'case', 'segment', 'config', 'config_sha256', 'q_ref', 'predecessor', 'output', 'raw_output', 'checkpoint_sha256', 'terminal_sha256', 'old_source_sha256', 'current_source', 'current_source_sha256', 'decision', 'decision_sha256', 'review', 'review_sha256', 'example', 'example_sha256', 'binary_sha256', 'authority', 'authority_sha256', 'starting_state_debug', 'additional_steps', 'additional_attempts', 'additional_wall_s', 'additional_output_mib', 'effective_max_steps', 'effective_max_attempts', 'effective_max_rhs', 'effective_max_wall_s', 'effective_output_budget_mib')
def parse_binding(path):
    result={}
    for line in Path(path).read_text().splitlines():
        if not line or line.startswith('#'): continue
        key, value=line.split('=',1)
        if key not in BINDING_KEYS or key in result or not value: raise NotReady('HOLD_BINDING_DUPLICATE_OR_EMPTY')
        result[key]=value
    return result

def verify_epochs(old, new, c):
    if old != OLD or new != NEW or c.get('old_source_sha256') != OLD or c.get('current_source_sha256') != NEW or c.get('decision_sha256') != DECISION or c.get('review_sha256') != REVIEW or c.get('relation') != 'REVIEWED_RESOURCE_ONLY':
        raise NotReady('HOLD_SOURCE_EPOCH_COMPATIBILITY')

def compose(binding_path, segment_terminal_sha256, output):
    binding_path, output = Path(binding_path), Path(output)
    if output.exists():
        raise NotReady('HOLD_OUTPUT_EXISTS')
    binding = parse_binding(binding_path)
    case = binding['case']
    if case not in CASES or binding['execution_authorized'] != 'true' or binding['start_authorized'] != 'true':
        raise NotReady('HOLD_BINDING_AUTHORITY')
    prefix, segment = Path(binding['predecessor']), Path(binding['output'])
    prior = terminal(prefix / 'RETURN.txt'); end = terminal(segment / 'RETURN.txt')
    if end.get('status') != 'COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT' or end.get('result') != 'Ok(())':
        raise NotReady('NOT_READY_CONTINUATION_INCOMPLETE')
    if sha(segment / 'RETURN.txt') != segment_terminal_sha256:
        raise NotReady('HOLD_TERMINAL_IDENTITY')
    for path,key in [(Path(binding['config']),'config_sha256'),(prefix/'config.cfg','config_sha256'),(prefix/'checkpoint.txt','checkpoint_sha256'),(prefix/'RETURN.txt','terminal_sha256'),(Path(binding['decision']),'decision_sha256'),(Path(binding['review']),'review_sha256'),(Path(binding['authority']),'authority_sha256')]:
        if sha(path) != binding[key]: raise NotReady('HOLD_FROZEN_INPUT_IDENTITY:'+key)
    authority = parse_binding(binding['authority'])
    for key,value in binding.items():
        if key not in ('authority','authority_sha256') and authority.get(key) != value:
            raise NotReady('HOLD_AUTHORITY_BINDING:'+key)
    compatibility = json.loads((segment/'source_compatibility.json').read_text())
    verify_epochs(sha(prefix/'source_identity.txt'), sha(segment/'source_identity.txt'), compatibility)
    if (segment/'predecessor_source_identity.txt').read_bytes() != (prefix/'source_identity.txt').read_bytes(): raise NotReady('HOLD_PREDECESSOR_SOURCE')
    for name in ('config.cfg','case_id.txt'):
        if (prefix/name).read_bytes() != (segment/name).read_bytes(): raise NotReady('HOLD_SEGMENT_COMPATIBILITY:'+name)
    if (prefix/'case_id.txt').read_text() != case or (segment/'segment_id.txt').read_text() != binding['segment']:
        raise NotReady('HOLD_CASE_OR_SEGMENT_IDENTITY')
    for key in ('decision_sha256','review_sha256','authority_sha256','checkpoint_sha256','terminal_sha256'):
        if compatibility[key] != binding[key]: raise NotReady('HOLD_COMPATIBILITY_BINDING:'+key)
    if compatibility['binding_sha256'] != sha(binding_path) or compatibility['new_binary_sha256'] != binding['binary_sha256'] or binding['old_source_sha256'] != OLD or binding['current_source_sha256'] != NEW:
        raise NotReady('HOLD_EXECUTION_BINDING')
    cp = (prefix/'checkpoint.txt').read_text().splitlines()
    segment_cp = (segment/'checkpoint.txt').read_text().splitlines()
    config = terminal(prefix/'config.cfg'); endpoint=1/(1+float(config['end_zbar']))
    if cp[0] != 'AXBI_CHECKPOINT_V2' or segment_cp[0] != 'AXBI_CHECKPOINT_V2' or float(segment_cp[1].split()[0]) != endpoint or float(end['a']) != endpoint:
        raise NotReady('HOLD_CHECKPOINT_SCHEMA_OR_ENDPOINT')
    for data, record, is_legacy_prefix in ((cp, prior, True), (segment_cp, end, False)):
        counters = data[2].split()
        for key, index in [('accepted', 0), ('attempts', 1), ('rejections', 2), ('rhs_evaluations', 4), ('comparisons', 5)]:
            value = int(counters[index])
            if key == 'comparisons' and key not in record:
                # The original AX08 full-run RETURN schema omits this field.
                # Its V2 checkpoint retains it; never infer a segment count.
                if not is_legacy_prefix or not (int(record['accepted']) <= value <= int(record['attempts'])):
                    raise NotReady('HOLD_MISSING_COMPARISONS:' + key)
                continue
            if value != int(record[key]):
                raise NotReady('HOLD_CHECKPOINT_COUNTER:' + key)
        if float(data[1].split()[10]) != float(record['wall_s']):
            raise NotReady('HOLD_CHECKPOINT_WALL')
    state=list(map(float,cp[1].split()))
    if state[0]!=float(prior['a']): raise NotReady('HOLD_CHECKPOINT_TERMINAL_ALIGNMENT')
    overrides=json.loads((segment/'effective_resource_overrides.json').read_text())
    for name,key in [('max_steps','effective_max_steps'),('max_attempts','effective_max_attempts'),('max_rhs','effective_max_rhs'),('max_wall_s','effective_max_wall_s'),('output_budget_mib','effective_output_budget_mib')]:
        if float(overrides[name]) != float(binding[key]): raise NotReady('HOLD_RESOURCE_OVERRIDE:'+name)
    wrapper=compatibility
    roles = list(FILES) + ['RETURN.txt', 'checkpoint.txt', 'source_identity.txt', 'config.cfg', 'case_id.txt']
    inputs = {str(p / name): sha(p / name) for p in (prefix, segment) for name in roles}
    inputs[str(binding_path)] = sha(binding_path)
    for name in ('source_compatibility.json', 'predecessor_source_identity.txt', 'effective_resource_overrides.json', 'segment_id.txt'):
        inputs[str(segment / name)] = sha(segment / name)
    output.mkdir(parents=True)
    receipt = {'status': 'HOLD_VALIDATION_PENDING', 'input_sha256': inputs, 'composer_sha256': sha(__file__), 'original_binary_sha256': compatibility['original_binary_sha256'], 'execution_wrapper_identity': wrapper, 'global_clock': 'elapsed proper seconds since zbar20', 'boundary_counted_once': True, 'full_history_feedback': 'PENDING', 'full_history_tau': 'PENDING', 'scientific_admission': 'NOT_ISSUED', 'solver_runs': 0, 'source_epochs': {'predecessor': OLD, 'current': NEW}, 'source_compatibility': compatibility}
    try:
        counts = {name: join_csv(prefix / name, segment / name, output / name, state[1], case) for name in FILES}
        check_counters(prior, end, counts['history.csv'])
        # Last original history must be the checkpoint state, not merely its time.
        last = None
        for _, block in groups(prefix / 'history.csv', case):
            last = block[-1]
        for name, index in [('a', 0), ('time_s', 1), ('b', 2), ('x_HII', 3), ('x_HeII', 4), ('x_HeIII', 5)]:
            if float(last[name]) != state[index]:
                raise NotReady('HOLD_CHECKPOINT_HISTORY_ALIGNMENT:' + name)
        for name in ('config.cfg', 'case_id.txt'):
            shutil.copyfile(prefix / name, output / name)
        shutil.copyfile(segment / 'checkpoint.txt', output / 'checkpoint.txt')
        shutil.copyfile(prefix/'source_identity.txt',output/'predecessor_source_identity.txt')
        shutil.copyfile(segment/'source_identity.txt',output/'source_identity.txt')
        shutil.copyfile(segment/'source_compatibility.json',output/'source_compatibility.json')
        shutil.copyfile(prefix / 'RETURN.txt', output / 'ORIGINAL_RETURN.txt')
        shutil.copyfile(segment / 'RETURN.txt', output / 'SEGMENT_RETURN.txt')
        pending = output / 'RETURN.pending.txt'
        pending.write_text('\n'.join(k + '=' + v for k, v in dict(end, status='COMPLETE_REPRESENTED_INTERVAL', full_history_feedback='PENDING', full_history_tau='PENDING').items()) + '\n')
        module_path = ROOT / 'research/axbi_goal_20261014/convergence/compare_histories.py'
        spec = importlib.util.spec_from_file_location('axbi_completed_reader', module_path)
        reader = importlib.util.module_from_spec(spec)
        # The analysis module imports two sibling scientific checks by bare name.
        import sys
        sys.path.insert(0, str(module_path.parent))
        try:
            spec.loader.exec_module(reader)
        finally:
            sys.path.remove(str(module_path.parent))
        case = {'id': binding['case'], 'clock_origin': reader.CLOCK, 'source_epochs': {'predecessor': OLD, 'current': NEW, 'compatibility': compatibility}}
        for role, name in [('history', 'history.csv'), ('abundances', 'abundances.csv'), ('config', 'config.cfg'), ('source_identity', 'source_identity.txt'), ('terminal', 'RETURN.pending.txt')]:
            case[role] = {'path': str(output / name), 'sha256': sha(output / name)}
        reader.load_case(case)  # Existing 1e-12 census/normalization/domain checks.
        for path, digest in inputs.items():
            if sha(path) != digest:
                raise NotReady('HOLD_INPUT_CHANGED_DURING_COMPOSITION:' + path)
        pending.rename(output / 'RETURN.txt')
        case['terminal']['path'] = str(output / 'RETURN.txt')
        receipt.update(status='COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION', row_counts=counts, cumulative_terminal=end, whole_history_feedback_not_computed=True)
        (output / 'COMPLETED_CASE_INPUT.json').write_text(json.dumps(case, indent=2) + '\n')
    except Exception as error:
        receipt.update(status='HOLD_COMPOSITION_VALIDATION', error=str(error))
        (output / 'COMPOSITION_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
        raise
    receipt['output_sha256'] = {p.name: sha(p) for p in output.iterdir() if p.is_file()}
    (output / 'COMPOSITION_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binding', required=True)
    parser.add_argument('--segment-terminal-sha256', required=True, help='Frozen completed segment RETURN digest')
    parser.add_argument('--output', required=True, help='Fresh directory; failed validation has no canonical RETURN')
    args = parser.parse_args()
    try:
        print(compose(args.binding, args.segment_terminal_sha256, args.output)['status'])
    except (NotReady, FileNotFoundError, KeyError, ValueError) as error:
        print(json.dumps({'status': 'NOT_READY_OR_HOLD', 'reason': str(error), 'scientific_admission': 'NOT_ISSUED'}))
        raise SystemExit(2)
