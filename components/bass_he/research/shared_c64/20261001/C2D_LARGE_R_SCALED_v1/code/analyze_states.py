"""Scalar-only C2d collection; bound artifacts, endpoint and bridge gates."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'code'))
from mpi_batch import atomic_create, json_bytes, read_manifest, SAFE_TASK_ID


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('DUPLICATE_JSON_KEY: '+key)
        result[key] = value
    return result


def _read(path):
    return json.loads(Path(path).read_bytes(), object_pairs_hook=_unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('NONFINITE_JSON: '+x)))


def _path(folder, name):
    if not isinstance(name, str) or Path(name).name != name or name in ('.', '..'):
        raise RuntimeError('UNSAFE_ARTIFACT_NAME')
    path = folder/name
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('ARTIFACT_NOT_REGULAR_FILE: '+str(path))
    return path


def _check(path, meta, label):
    if path.stat().st_size != meta['bytes'] or digest(path) != meta['sha256']:
        raise RuntimeError(label+'_IDENTITY_MISMATCH')


def documents():
    """Only completed batch entries; reject identity drift and duplicate work."""
    docs, task_ids, semantic_ids = [], set(), set()
    for folder in sorted((ROOT/'evidence').glob('*MPI')):
        if folder.is_symlink():
            raise RuntimeError('SYMLINK_BATCH_DIRECTORY')
        if (folder/'BATCH_SUMMARY.json').exists():
            if (folder/'PARTIAL_BATCH_INDEX.json').exists():
                raise RuntimeError('AMBIGUOUS_FULL_AND_PARTIAL_BATCH')
            batch = _read(_path(folder, 'BATCH_SUMMARY.json'))
        elif (folder/'PARTIAL_BATCH_INDEX.json').exists():
            from recovery_support import load_partial_batch
            batch = load_partial_batch(ROOT, folder)
        else:
            continue
        run = _read(_path(folder, 'RUN_IDENTITY.json'))
        manifest, manifest_sha, _ = read_manifest(_path(folder, 'MANIFEST_INPUT.json'))
        code_sha = hashlib.sha256(json_bytes(run['code']['files'])).hexdigest()
        if (code_sha != run['code']['sha256'] or code_sha != batch['code_sha256']
                or manifest_sha != run['manifest_sha256'] or manifest_sha != batch['manifest_sha256']):
            raise RuntimeError('BATCH_IDENTITY_MISMATCH')
        expected = {t['task_id']: t for t in manifest['tasks']}
        if [e['task_id'] for e in batch['tasks']] != list(expected):
            raise RuntimeError('SUMMARY_MANIFEST_TASK_ORDER_OR_DUPLICATE_MISMATCH')
        for execution in batch['tasks']:
            task_id = execution['task_id']
            if not SAFE_TASK_ID.fullmatch(task_id) or task_id in task_ids:
                raise RuntimeError('DUPLICATE_OR_INVALID_TASK_ID: '+task_id)
            task_ids.add(task_id)
            if execution['status'] != 'WORKER_RESULT_PASS':
                continue
            taskdir = folder/task_id
            if taskdir.is_symlink() or not taskdir.is_dir():
                raise RuntimeError('INVALID_TASK_DIRECTORY')
            artifacts = execution['artifacts']
            for name in ('RESULT.json', 'TASK_INPUT.json', 'DATA.json'):
                _check(_path(taskdir, name), artifacts[name], name)
            task = _read(taskdir/'TASK_INPUT.json')
            r = _read(taskdir/'RESULT.json')
            data = _read(taskdir/'DATA.json')
            input_sha = digest(taskdir/'TASK_INPUT.json')
            if (task != expected[task_id] or execution['task_sha256'] != input_sha
                    or r['input_sha256'] != input_sha or r['task_id'] != task_id
                    or data['task_id'] != task_id or r['status'] != 'PASS'
                    or r['parameters'] != task['parameters'] or data['parameters'] != task['parameters']):
                raise RuntimeError('TASK_DATA_RESULT_BINDING_MISMATCH')
            if (r['code_identity_sha256'] != code_sha or execution['code_sha256'] != code_sha
                    or r['selected_backend'] != run['selected_backend']
                    or execution['selected_backend'] != run['selected_backend']
                    or r['backend'] != run['backend']):
                raise RuntimeError('TASK_SOURCE_BACKEND_MISMATCH')
            if (r['evidence_file'] != 'DATA.json' or r['evidence_bytes'] != artifacts['DATA.json']['bytes']
                    or r['evidence_sha256'] != artifacts['DATA.json']['sha256']
                    or r['new_eigenstates'] != data['new_eigenstates']
                    or execution['worker_result_sha256'] != artifacts['RESULT.json']['sha256']):
                raise RuntimeError('RESULT_ARTIFACT_BINDING_MISMATCH')
            if 'state_file' in r:
                if r['state_file'] != 'STATE.npz':
                    raise RuntimeError('INVALID_STATE_NAME')
                state_meta = {'bytes': r['state_bytes'], 'sha256': r['state_sha256']}
                if artifacts['STATE.npz'] != state_meta:
                    raise RuntimeError('STATE_EXECUTION_BINDING_MISMATCH')
                _check(_path(taskdir, 'STATE.npz'), state_meta, 'STATE')
            semantic = json_bytes(task['parameters'])
            if semantic in semantic_ids:
                raise RuntimeError('DUPLICATE_SCIENTIFIC_TASK_PARAMETERS')
            semantic_ids.add(semantic)
            data.update(path=str((taskdir/'DATA.json').relative_to(ROOT)),
                        folder=str(taskdir.relative_to(ROOT)), result=r,
                        result_sha256=artifacts['RESULT.json']['sha256'])
            docs.append(data)
    return docs


def state_ref(doc):
    relative = Path(doc['folder'])
    if relative.is_absolute() or '..' in relative.parts:
        raise RuntimeError('STATE_FOLDER_OUTSIDE_PACKAGE')
    folder = ROOT/relative
    if folder.is_symlink() or not folder.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError('STATE_FOLDER_OUTSIDE_PACKAGE')
    path = _path(folder, 'RESULT.json')
    r = _read(path)
    if r != doc['result'] or r['status'] != 'PASS' or r['state_file'] != 'STATE.npz':
        raise RuntimeError('STATE_REFERENCE_RESULT_MISMATCH')
    if doc.get('result_sha256', digest(path)) != digest(path):
        raise RuntimeError('STATE_REFERENCE_RESULT_IDENTITY_MISMATCH')
    _check(_path(folder, 'STATE.npz'), {'bytes': r['state_bytes'], 'sha256': r['state_sha256']}, 'STATE')
    return {'folder':str(relative), 'state_sha256':r['state_sha256'], 'result_sha256':digest(path)}


def frozen_state_ref(R):
    folder = ROOT/'frozen'/('R'+format(R, 'g')+'_base')
    provenance = _read(ROOT/'provenance/PARENT_INPUTS.json')
    for name in ('RESULT.json', 'STATE.npz', 'TASK_INPUT.json'):
        path = _path(folder, name)
        _check(path, provenance[str(path.relative_to(ROOT))], 'FROZEN_'+name)
    r, task = _read(folder/'RESULT.json'), _read(folder/'TASK_INPUT.json')
    if (r['parameters'] != task['parameters'] or r['parameters']['R'] != R
            or r['input_sha256'] != digest(folder/'TASK_INPUT.json')):
        raise RuntimeError('FROZEN_INPUT_BINDING_MISMATCH')
    return state_ref({'folder':str(folder.relative_to(ROOT)), 'result':r})


def _bridge_audit(doc, R, contract):
    gates = {'execution':doc['result']['status'] == 'PASS'}
    try:
        p, value = doc['parameters'], doc['value']
        config = contract['bridge_configurations'][format(R, 'g')]
        states = value['states']
        gates['registered_configuration'] = p['configuration'] == config
        gates['state_binding'] = (value['R'] == R and len(states) == 2
            and [s['m'] for s in states] == [0, 1]
            and [s['energy'] for s in states] == value['energies']
            and all(s['R'] == R and s['config'] == config for s in states))
        residuals = [s['residuals'][key] for s in states
                     for key in ('radial_discrete_relative','angular_discrete_relative')]
        gates['residual'] = all(math.isfinite(x) and 0 <= x <= contract['raw_criteria']['algebraic_residual_relative'] for x in residuals)
        gates['finite_energies'] = all(math.isfinite(e) for e in value['energies'])
        gates['phase'] = all(s['phase']['algorithm'] == contract['phase']['algorithm']
            and all(math.isfinite(s['phase'][axis]['dominant_value']) and s['phase'][axis]['dominant_value'] > 0
                    and math.isfinite(s['phase'][axis]['negative_l2_fraction'])
                    and 0 <= s['phase'][axis]['negative_l2_fraction'] <= contract['phase']['max_weighted_negative_L2_fraction']
                    for axis in ('radial','angular')) for s in states)
        ref = state_ref(doc)
        return {'R':R, 'pass':all(gates.values()), 'gates':gates, 'state':ref,
                'scope':'EXECUTION_RESIDUAL_PHASE_ONLY; overlap norms pending; no bridge spatial closure'}
    except (KeyError, TypeError, ValueError) as exc:
        return {'R':R, 'pass':False, 'gates':gates, 'error':str(exc), 'reason':'MALFORMED_BRIDGE_SCALARS'}


def audit_states(docs, contract):
    from scaled_audit import quartet_audit
    rows, selected, needs = [], {}, []
    refs = {json_bytes(state_ref(d)):d for d in docs if d['parameters']['kind'] == 'prolate'}
    extras = {}
    for d in docs:
        if d['parameters']['kind'] == 'operator_refinement':
            key = json_bytes(d['parameters']['state'])
            if key not in refs:
                raise RuntimeError('UNBOUND_OPERATOR_REFINEMENT_STATE')
            extras.setdefault(key, []).append(d)
    for R in contract['new_R']:
        tiers = []
        for tier in (0, 1):
            found = [d for d in docs if d['parameters']['kind'] == 'prolate'
                     and d['parameters']['R'] == R and d['parameters']['tier'] == tier]
            if not found:
                continue
            names = [d['parameters']['profile'] for d in found]
            if len(names) != len(set(names)):
                raise RuntimeError('DUPLICATE_QUARTET_PROFILE')
            if set(names) != {'base','h','p','tail'}:
                tiers.append({'tier':tier, 'pass':False, 'reason':'INCOMPLETE_QUARTET', 'available':names})
                continue
            vals, states = {}, {}
            for d in found:
                name, value, ref = d['parameters']['profile'], copy.deepcopy(d['value']), state_ref(d)
                for extra in extras.get(json_bytes(ref), []):
                    if extra['value']['R'] != R:
                        raise RuntimeError('REFINEMENT_R_MISMATCH')
                    for lane in ('direct','force'):
                        if set(value[lane]) & set(extra['value'][lane]):
                            raise RuntimeError('DUPLICATE_OPERATOR_ORDER')
                        value[lane].update(extra['value'][lane])
                vals[name], states[name] = value, ref
            audit = quartet_audit(vals, contract)
            tiers.append({'tier':tier, 'audit':audit, 'pass':audit['pass'], 'states':states})
        passing = [x for x in tiers if x['pass']]
        chosen = passing[-1] if passing else None
        if chosen:
            selected[format(R, 'g')] = chosen['states']['base']
        else:
            needs.append(R)
        rows.append({'R':R, 'tiers':tiers, 'pass':chosen is not None,
                     'selected_tier':None if chosen is None else chosen['tier']})
    endpoint_states = dict(selected)
    bridges = []
    for key in sorted(contract['bridge_configurations'], key=float):
        R = float(key)
        found = [d for d in docs if d['parameters']['kind'] == 'bridge' and d['parameters']['R'] == R]
        if len(found) > 1:
            raise RuntimeError('DUPLICATE_BRIDGE_STATE')
        row = (_bridge_audit(found[0], R, contract) if found else
               {'R':R, 'pass':False, 'reason':'BRIDGE_EXECUTION_MISSING', 'gates':{'execution':False}})
        bridges.append(row)
        if row['pass']:
            selected[key] = row['state']
    start = min(contract['continuation']['grid'])
    selected[format(start, 'g')] = frozen_state_ref(start)
    missing = [R for R in contract['continuation']['grid'] if format(R, 'g') not in selected]
    return {'rows':rows, 'all_new_R_numerical_gates_pass':all(x['pass'] for x in rows),
            'selected_states':selected, 'selected_endpoint_states':endpoint_states, 'unresolved_R':needs,
            'bridge_rows':bridges, 'all_bridge_execution_phase_gates_pass':all(x['pass'] for x in bridges),
            'all_bridge_gates_pass':all(x['pass'] for x in bridges),
            'unresolved_bridge_R':[x['R'] for x in bridges if not x['pass']],
            'continuation_state_grid_complete':not missing, 'missing_continuation_R':missing,
            'bridge_overlap_norms_status':'SEPARATE_FOLLOWUP_REQUIRED',
            'frozen_endpoint_policy':'INHERITED_IDENTITY_CHECKED; no new scaled or three-order closure'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    contract = _read(ROOT/'CONTRACT.json')
    docs = documents()
    out = audit_states(docs, contract)
    out.update({'contract_sha256':digest(ROOT/'CONTRACT.json'),
                'input_data_sha256':{d['path']:digest(ROOT/d['path']) for d in docs},
                'new_eigensolves_performed_by_analysis':0, 'full_C2_closed':False})
    atomic_create(args.output, json_bytes(out))
    print(json.dumps({k:out[k] for k in ('all_new_R_numerical_gates_pass','unresolved_R',
          'all_bridge_execution_phase_gates_pass','unresolved_bridge_R','continuation_state_grid_complete')}, indent=2))


if __name__ == '__main__':
    main()
