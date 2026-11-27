"""Read-only source/result bridge after interval input guard hardening.

No finite packet evaluation, ODE solve or actual certificate replay.
"""
from __future__ import annotations

import ast
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path('/workspace/scratch/61913f66989c')
PHYS77 = ROOT / 'WU088_HH_PHYS77/research/hh_phys77_whole_cell_20261021'
OUT = ROOT / 'phys77_theory/verification'
SOURCE = PHYS77 / 'source'
sys.path.insert(0, str(SOURCE))
from owner_interval import Interval, _valid_box
from export_owner import canonical


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RemoveOnlyGuards(ast.NodeTransformer):
    def __init__(self, module):
        self.module = module
        self.removed_import_names = 0
        self.removed_functions = 0
        self.removed_loops = []
        self.functions = []

    def visit_ImportFrom(self, node):
        if self.module == 'cell_enclosure' and node.module == 'owner_interval':
            self.removed_import_names += sum(item.name == '_valid_box' for item in node.names)
            node.names = [item for item in node.names if item.name != '_valid_box']
        return node

    def visit_FunctionDef(self, node):
        if self.module == 'owner_interval' and node.name == '_valid_box':
            self.removed_functions += 1
            return None
        self.functions.append(node.name)
        node = self.generic_visit(node)
        self.functions.pop()
        return node

    def visit_For(self, node):
        if self.module == 'cell_enclosure' and self.functions == ['certify_cell']:
            for collection in ('initial_box', 'rhs'):
                expected = ast.parse(f'for value in {collection}:\n    _valid_box(value)').body[0]
                if ast.dump(node, include_attributes=False) == ast.dump(expected, include_attributes=False):
                    self.removed_loops.append(collection)
                    return None
        return self.generic_visit(node)


def normalized(path, module):
    transform = RemoveOnlyGuards(module)
    tree = transform.visit(ast.parse(path.read_text()))
    dump = ast.dump(tree, include_attributes=False)
    return dump, {'removed_import_names': transform.removed_import_names,
                  'removed_functions': transform.removed_functions,
                  'removed_loops': transform.removed_loops}


def run():
    comparisons = []
    for module in ('owner_interval', 'cell_enclosure'):
        before = ROOT / 'phys77_audit' / f'{module}_before_input_guard.py'
        after = SOURCE / f'{module}.py'
        old_ast, old_removed = normalized(before, module)
        new_ast, new_removed = normalized(after, module)
        assert old_ast == new_ast
        if module == 'cell_enclosure':
            assert old_removed == {'removed_import_names':0,'removed_functions':0,'removed_loops':[]}
            assert new_removed == {'removed_import_names':1,'removed_functions':0,'removed_loops':['initial_box','rhs']}
        else:
            assert old_removed == new_removed == {'removed_import_names':0,'removed_functions':1,'removed_loops':[]}
        comparisons.append({'module':module,'before_path':str(before),'before_sha256':sha(before),
                            'after_path':str(after),'after_sha256':sha(after),
                            'normalized_ast_sha256':hashlib.sha256(old_ast.encode()).hexdigest(),
                            'equal_after_only_guard_removal':True,
                            'before_removed':old_removed,'after_removed':new_removed})

    result_path = PHYS77 / 'results/FIRST_CELL_AFTER_RADIUS_FIX.json'
    run_receipt_path = PHYS77 / 'verification/FIRST_CELL_AFTER_RADIUS_FIX_RECEIPT.json'
    request_path = PHYS77 / 'inputs/REQUEST_FIRST_CELL.json'
    result = json.loads(result_path.read_text())
    run_receipt = json.loads(run_receipt_path.read_text())
    request = json.loads(request_path.read_text())
    assert result['status'] == 'PASS_REQUESTED_PREFIX'
    assert result['enclosed_cells'] == result['requested_cells'] == 1
    assert run_receipt['input_sha256'] == sha(request_path)
    assert result['request_sha256'] == hashlib.sha256(canonical(request)).hexdigest()
    assert sha(SOURCE/'export_owner.py') == run_receipt['sources']['export_owner.py']
    for comparison in comparisons:
        assert comparison['before_sha256'] == run_receipt['sources'][comparison['module']+'.py']

    checked = []
    def check_pair(value, label):
        assert isinstance(value, list) and len(value) == 2
        item = Interval(Decimal(value[0]), Decimal(value[1]))
        _valid_box(item)
        checked.append(label)
        return item

    def check_vector(values, label):
        assert len(values) == 8
        return [check_pair(v, f'{label}/{i}') for i,v in enumerate(values)]

    for name, value in result['initial_observables'].items():
        if name == 'rhs':
            check_vector(value, 'initial_observables/rhs')
        else:
            check_pair(value, 'initial_observables/'+name)
    for cell in result['cells']:
        assert cell['status'] == 'FINITE_OWNER_CELL_ENCLOSED'
        assert Fraction(Decimal(cell['x'][1]))-Fraction(Decimal(cell['x'][0])) == Fraction(Decimal(cell['h']))
        assert Decimal(cell['h']) > 0
        for key in ('initial_state_box','initial_error_box','predictor_actual_endpoint',
                    'whole_cell_state_box','defect_box','endpoint_state_box','endpoint_error_box'):
            check_vector(cell[key], 'cell/'+key)
        for name,value in cell['observables'].items():
            if name == 'rhs':
                check_vector(value, 'cell/observables/rhs')
            else:
                check_pair(value, 'cell/observables/'+name)
        for index, attempt in enumerate(cell['attempts']):
            assert len(attempt['radii']) == 8
            assert all(Decimal(v).is_finite() and Decimal(v)>0 for v in attempt['radii'])
            check_vector(attempt['image'], f'cell/attempt/{index}/image')
        assert all(cell['attempts'][-1]['strict_inclusion'])
    for field in ('full_history_certificate','angular_continuum_certificate',
                  'momentum_continuum_certificate','past_machine_trajectory_certificate'):
        assert result[field] is False
    assert result['new_ODE_solves'] == result['benchmark_runs'] == result['NCP_jobs'] == 0

    receipt = {
      'schema':'PHYS77_INPUT_GUARD_BRIDGE_V1',
      'status':'PASS_SCOPED_VALID_INPUT_COMPUTATIONAL_BODY_UNCHANGED',
      'source_comparisons':comparisons,
      'actual_result':{'path':str(result_path),'sha256':sha(result_path),'status':result['status'],
                       'case_id':result['case_id'],'covered_x':result['covered_x']},
      'original_run_receipt_sha256':sha(run_receipt_path),
      'original_request_sha256':sha(request_path),
      'saved_intervals_checked':len(checked),
      'saved_interval_labels':checked,
      'bridge_reason':'Only finite ordered interval precondition guards changed. Source AST outside those guards is identical; serialized first-success initial and RHS boxes satisfy the added guards. Intermediate successful owner evaluations produce finite ordered intervals by the reviewed arithmetic invariant; their full RHS values were not saved and were not recomputed.',
      'limits':'This does not rerun or relabel the original actual source hash. It connects that preserved valid-input computation to guard-only hardening. No new full-history, historic-machine or continuum certificate.',
      'actual_finite_packet_evaluations':0,'new_ODE_solves':0,'benchmark_runs':0,'NCP_jobs':0,
      'HH_R10':'OFF','production_admission':'NOT_ISSUED'
    }
    with (OUT/'INPUT_GUARD_VALIDATION_BRIDGE.json').open('x') as stream:
        json.dump(receipt,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(json.dumps({key:receipt[key] for key in ('status','saved_intervals_checked','actual_result')},indent=2))


if __name__ == '__main__':
    run()
