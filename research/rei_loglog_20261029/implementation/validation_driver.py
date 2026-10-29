"""Source-compiled, explicitly fixed-field structural Jacobian validation."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
import numpy as np
from chemistry_jacobian import jacobian, physical_jacobian
from test_chemistry_jacobian import check_saved_state


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'intake/github'
IDENTITIES = {'coupled.py': '4773d4278e1fa2f1a8a24a9df79f9ba5d46d5771',
              'model.py': '1f8d7965fe286a4ed78ea6bbfcc38178aafe8adc',
              'config.json': '64c551f5ec23580e19ad1177375ae65e8c1c542f'}


def validate(data_path, old_metadata_path, output):
    for filename, expected in IDENTITIES.items():
        raw = (SOURCE / filename).read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        if actual != expected:
            raise ValueError('immutable source mismatch: ' + filename)
    spec = importlib.util.spec_from_file_location('frozen_event_operator', SOURCE/'model.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    parsed = ast.parse((SOURCE/'coupled.py').read_text())
    compile_node = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == 'compile_new')
    class_node = next(n for n in parsed.body if isinstance(n, ast.ClassDef) and n.name == 'Coupled')
    methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef) and n.name in ('rhs', 'rhs_physical')]
    extracted = ast.Module(body=[compile_node, ast.ClassDef(name='FrozenRHS', bases=[], keywords=[], body=methods, decorator_list=[])], type_ignores=[])
    namespace = {'np': np, 'old': old}
    exec(compile(ast.fix_missing_locations(extracted), str(SOURCE/'coupled.py'), 'exec'), namespace)
    model = namespace['FrozenRHS']()
    model.c = old.config()
    model.new = {mode: namespace['compile_new'](model.c, mode) for mode in ('OFF', 'ON')}
    data = json.loads(Path(data_path).read_text())
    saved = data['cases']['ON_refined']
    model.scale = np.array(saved['scales'])
    # Deliberate coefficient fixture: these are NOT reconstructed saved hazards.
    G = np.zeros((17, 17))
    edges = [(1,2),(3,4),(5,6),(7,8),(8,9),(10,11),(11,12),(13,14),(14,15),(15,16)]
    for l, u in edges:
        photo, rec = 2e-16, 3e-16
        G[l,l] -= photo; G[u,l] += photo
        G[u,u] -= rec; G[l,u] += rec
    nref = 1e-5
    model.fields = lambda t: (G, nref, np.zeros(4), np.zeros(4))
    directions = [np.ones(23), np.where(np.arange(23) % 2, -1., 1.), np.linspace(-1., 1., 23)]
    indices = [0, len(data['t_s'])//2, len(data['t_s'])-1]
    records = []
    for mode in ('OFF', 'ON'):
        for index in indices:
            state = np.array(saved['physical'])[:, index]
            t = data['t_s'][index]
            report = check_saved_state(model, t, state, mode, directions, (1e-4, 1e-5))
            scaled = state / model.scale
            J = jacobian(model, t, scaled, mode == 'ON')
            for row in report['checks']:
                v = directions[row['direction']]; h = row['step']
                plus = model.rhs(t, scaled+h*v, mode)
                minus = model.rhs(t, scaled-h*v, mode)
                # Componentwise signal bound avoids relative division by zero;
                # 64 eps safely covers short affine/quadratic event sums and FD.
                signal = np.abs(J) @ np.abs(v)
                roundoff = 64*np.finfo(float).eps*(np.abs(plus)+np.abs(minus))/(2*h)
                allowed = 1e-6*signal + roundoff
                error = np.array(row['absolute_error'])
                row['signal_bound'] = signal.tolist()
                row['roundoff_allowance'] = roundoff.tolist()
                row['pass'] = bool(np.all(error <= allowed))
            report['saved_state_index'] = index
            report['pass'] = (report['finite_jacobian'] and
                all(r['pass'] for r in report['checks']) and
                all(v['maximum_relative_residual'] <= 1e-12 for v in report['ledger_invariants'].values()) and
                report['ledger_feedback_columns_max'] == 0)
            records.append(report)
    # Exact zero signed-extension derivative: no clamp, no finite division by stock.
    zero = np.zeros(23)
    zero_checks = []
    capture_checks = []
    for mode in ('OFF', 'ON'):
        J = physical_jacobian(model, 0., zero, mode)
        _, M, _, P, loss = model.new[mode]
        expected = np.zeros((23,23)); expected[:19,:19] = M[:19]
        expected[:17,:17] += G; expected[21:,:19] = M[19:]
        expected[22,:17] += old.Q[:17]@G
        expected[19:21,:17] = P; expected[19,19], expected[20,20] = -loss
        zero_checks.append({'mode':mode, 'pass':bool(np.array_equal(J,expected))})
        for varied_column in (0,1,2):
            point = zero.copy(); point[varied_column] = 1.
            expected_capture = np.zeros((23,23))
            for h,d in ((1,3),(2,4)):
                gradient = np.zeros(23)
                gradient[0] = nref*model.c['capture_C_cm3_s']*point[h]
                gradient[h] = nref*model.c['capture_C_cm3_s']*point[0]
                expected_capture[0] -= gradient
                expected_capture[h] -= gradient
                expected_capture[d] += gradient
            actual_capture = physical_jacobian(model,0.,point,mode)-J
            # Adding a tiny capture term to a larger affine coefficient can
            # round once; compare against the corresponding addition bound.
            bound = 8*np.finfo(float).eps*(np.abs(J)+np.abs(expected_capture))
            capture_checks.append({'mode':mode,'nonzero_stock_column':varied_column,
                'pass':bool(np.all(np.abs(actual_capture-expected_capture)<=bound))})
    import start_audit
    audit = start_audit.audit(data, json.loads(Path(old_metadata_path).read_text()))
    (output/'START_AUDIT.json').write_text(json.dumps(audit, indent=2)+'\n')
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern='test_contract.py')
    tests = unittest.TextTestRunner(verbosity=2).run(suite)
    result = {'scope':'SOURCE_COMPILED_FIXED_FIELD_STRUCTURAL_VALIDATION_NOT_SAVED_BATH',
              'source_blobs':IDENTITIES, 'fixture':{'photo_s':2e-16,'rec_s':3e-16,'nref_cm3':nref,
              'edges':edges,'hidden_dot':[0.,0.,0.,0.], 'scale_source':'ON_refined.scales in supplied plot_data.json'},
              'ivp_calls':0, 'saved_bath_linkage':'MISSING', 'records':records,
              'zero_signed_polynomial_checks':zero_checks, 'plot_contract_tests_pass':tests.wasSuccessful(),
              'capture_zero_stock_gradient_checks':capture_checks,
              'plot_contract_tests_run':tests.testsRun,
              'pass':all(r['pass'] for r in records) and all(r['pass'] for r in zero_checks)
                     and all(r['pass'] for r in capture_checks) and tests.wasSuccessful()}
    (output/'JACOBIAN_VALIDATION.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    if not result['pass']:
        raise AssertionError('bounded structural validation failed; no automatic retry')
    return result
