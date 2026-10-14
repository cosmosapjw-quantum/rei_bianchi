#!/usr/bin/env python3
"""Join the frozen ZERO prefix and its completed resource-only segment.
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

ROOT = Path(__file__).resolve().parents[5]
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

def groups(path):
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
                if row.get('case_id', 'ZERO') != 'ZERO' or row.get('run_id', 'ZERO') != 'ZERO':
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

def join_csv(original, segment, target, boundary):
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
        for t, block in groups(original):
            writer.writerows(block)
            counts['original_rows'] += len(block)
            last = (t, block)
        stream = iter(groups(segment))
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

def compose(binding_path, segment_terminal_sha256, output):
    binding_path, output = Path(binding_path), Path(output)
    if output.exists():
        raise NotReady('HOLD_OUTPUT_EXISTS')
    binding = json.loads(binding_path.read_text())
    prefix, segment = Path(binding['original_prefix_path']), Path(binding['output_segment_path'])
    if not (segment / 'RETURN.txt').is_file():
        raise NotReady('NOT_READY_CONTINUATION_TERMINAL_ABSENT')
    end = terminal(segment / 'RETURN.txt')
    if end.get('status') != 'COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT' or end.get('result') != 'Ok(())' or float(end.get('a', 'nan')) != 0.2:
        raise NotReady('NOT_READY_CONTINUATION_INCOMPLETE')
    if sha(segment / 'RETURN.txt') != segment_terminal_sha256:
        raise NotReady('HOLD_TERMINAL_IDENTITY')
    for key in ('original_config_path_and_sha256', 'predecessor_checkpoint_path_and_sha256', 'predecessor_RETURN_path_and_sha256'):
        bound = binding[key]
        if sha(bound['path']) != bound['sha256']:
            raise NotReady('HOLD_FROZEN_INPUT_IDENTITY:' + key)
    if sha(prefix / 'source_identity.txt') != binding['original_source_identity_sha256']:
        raise NotReady('HOLD_ORIGINAL_SOURCE_IDENTITY')
    for name in ('config.cfg', 'source_identity.txt', 'case_id.txt'):
        if (prefix / name).read_bytes() != (segment / name).read_bytes():
            raise NotReady('HOLD_SEGMENT_COMPATIBILITY:' + name)
    if (segment / 'case_id.txt').read_text().strip() != 'ZERO' or (segment / 'segment_id.txt').read_text().strip() != binding['segment_id']:
        raise NotReady('HOLD_CASE_OR_SEGMENT_IDENTITY')
    wrapper = json.loads((segment / 'execution_wrapper_identity.json').read_text())
    for key in ('new_binary_sha256', 'new_example_source_sha256', 'original_binary_sha256'):
        if wrapper[key] != binding[key]:
            raise NotReady('HOLD_WRAPPER_IDENTITY:' + key)
    if json.loads((segment / 'effective_resource_overrides.json').read_text()) != binding['effective_resource_overrides']:
        raise NotReady('HOLD_RESOURCE_OVERRIDE_IDENTITY')
    prior = terminal(prefix / 'RETURN.txt')
    if int(prior['accepted']) != 200000:
        raise NotReady('HOLD_FROZEN_PREFIX_COUNT')
    cp = (prefix / 'checkpoint.txt').read_text().splitlines()
    if cp[0] != 'AXBI_CHECKPOINT_V2' or int(cp[2].split()[0]) != int(prior['accepted']):
        raise NotReady('HOLD_CHECKPOINT_SCHEMA')
    segment_cp = (segment / 'checkpoint.txt').read_text().splitlines()
    if segment_cp[0] != 'AXBI_CHECKPOINT_V2' or float(segment_cp[1].split()[0]) != 0.2:
        raise NotReady('HOLD_SEGMENT_CHECKPOINT_ENDPOINT')
    for key, index in [('accepted', 0), ('attempts', 1), ('rejections', 2), ('rhs_evaluations', 4)]:
        if int(segment_cp[2].split()[index]) != int(end[key]):
            raise NotReady('HOLD_SEGMENT_CHECKPOINT_COUNTER:' + key)
    state = list(map(float, cp[1].split()))
    if state[0] != float(prior['a']):
        raise NotReady('HOLD_CHECKPOINT_TERMINAL_ALIGNMENT')
    roles = list(FILES) + ['RETURN.txt', 'checkpoint.txt', 'source_identity.txt', 'config.cfg', 'case_id.txt']
    inputs = {str(p / name): sha(p / name) for p in (prefix, segment) for name in roles}
    inputs[str(binding_path)] = sha(binding_path)
    for name in ('execution_wrapper_identity.json', 'effective_resource_overrides.json', 'segment_id.txt'):
        inputs[str(segment / name)] = sha(segment / name)
    output.mkdir(parents=True)
    receipt = {'status': 'HOLD_VALIDATION_PENDING', 'input_sha256': inputs, 'composer_sha256': sha(__file__), 'original_binary_sha256': binding['original_binary_sha256'], 'execution_wrapper_identity': wrapper, 'global_clock': 'elapsed proper seconds since zbar20', 'boundary_counted_once': True, 'full_history_feedback': 'PENDING', 'full_history_tau': 'PENDING', 'scientific_admission': 'NOT_ISSUED', 'solver_runs': 0}
    try:
        counts = {name: join_csv(prefix / name, segment / name, output / name, state[1]) for name in FILES}
        check_counters(prior, end, counts['history.csv'])
        # Last original history must be the checkpoint state, not merely its time.
        last = None
        for _, block in groups(prefix / 'history.csv'):
            last = block[-1]
        for name, index in [('a', 0), ('time_s', 1), ('b', 2), ('x_HII', 3), ('x_HeII', 4), ('x_HeIII', 5)]:
            if float(last[name]) != state[index]:
                raise NotReady('HOLD_CHECKPOINT_HISTORY_ALIGNMENT:' + name)
        for name in ('config.cfg', 'source_identity.txt', 'case_id.txt'):
            shutil.copyfile(prefix / name, output / name)
        shutil.copyfile(segment / 'checkpoint.txt', output / 'checkpoint.txt')
        shutil.copyfile(prefix / 'RETURN.txt', output / 'ORIGINAL_RETURN.txt')
        shutil.copyfile(segment / 'RETURN.txt', output / 'SEGMENT_RETURN.txt')
        pending = output / 'RETURN.pending.txt'
        pending.write_text('\n'.join(k + '=' + v for k, v in dict(end, status='COMPLETE_REPRESENTED_INTERVAL', full_history_feedback='PENDING', full_history_tau='PENDING').items()) + '\n')
        module_path = ROOT / 'research/axbi_goal_20261014/convergence/compare_histories.py'
        spec = importlib.util.spec_from_file_location('axbi_completed_reader', module_path)
        reader = importlib.util.module_from_spec(spec); spec.loader.exec_module(reader)
        case = {'id': 'ZERO', 'clock_origin': reader.CLOCK}
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
