"""Pure AST JSON test; never import or execute the science validator."""
import ast
import hashlib
import json
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent.parent
started = time.monotonic()
start = {'unit': 'Q1B_SELECTIVE_C12_02_SERIALIZATION_R1', 'started_unix_s': time.time(),
         'execution': {'test_process': 1, 'native': 0, 'SIGMA': 0, 'RHS': 0,
                       'JAC': 0, 'ODE': 0, 'build': 0, 'quadrature': 0}}
(OUT / 'START.json').write_text(json.dumps(start, indent=2) + '\n')
result = dict(start)
try:
    import numpy as np

    def expression(path):
        tree = ast.parse(path.read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'endpoint_fixtures')
        calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == 'append'
                 and isinstance(n.func.value, ast.Name) and n.func.value.id == 'rows']
        assert len(calls) == 1 and len(calls[0].args) == 1
        node = calls[0].args[0]
        assert isinstance(node, ast.Dict)
        assert [ast.literal_eval(k) for k in node.keys] == [
            'atom', 'threshold', 'threshold_hex', 'included']
        return compile(ast.Expression(node), str(path), 'eval')

    before = OUT / 'validate_selective.before.py'
    after = BASE / 'validate_selective.py'
    before_text, after_text = before.read_text(), after.read_text()
    needle = "'included':active"
    assert before_text.count(needle) == 1
    assert after_text == before_text.replace(needle, "'included':bool(active)", 1)
    expressions = {'before': expression(before), 'after': expression(after)}
    cases = [('python_true', True), ('python_false', False),
             ('numpy_true', np.bool_(True)), ('numpy_false', np.bool_(False))]
    rows = []
    for label, active in cases:
        env = {'atom': 10.0, 'threshold': 2.5, 'active': active,
               'float': float, 'bool': bool, '__builtins__': {}}
        original = eval(expressions['before'], env)
        if isinstance(active, np.bool_):
            try:
                json.dumps(original, allow_nan=False)
            except TypeError:
                original_status = 'EXPECTED_TYPEERROR'
            else:
                raise AssertionError('original NumPy bool unexpectedly serializes')
        else:
            assert json.loads(json.dumps(original, allow_nan=False))['included'] is active
            original_status = 'STRICT_JSON_PASS'
        repaired = eval(expressions['after'], env)
        decoded = json.loads(json.dumps(repaired, allow_nan=False))
        assert type(repaired['included']) is bool
        assert decoded['included'] is bool(active)
        assert decoded == {'atom': 10.0, 'threshold': 2.5,
                           'threshold_hex': float(2.5).hex(), 'included': bool(active)}
        rows.append({'case': label, 'original': original_status,
                     'repaired': 'STRICT_JSON_PASS', 'included': decoded['included']})
    result.update(outcome='SOURCE_REPAIR_SERIALIZATION_TEST_PASS_SCOPED', cases=rows,
                  sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (before, after, Path(__file__).resolve())},
                  science_status='HOLD_CUMULATIVE_NATIVE_CAP_EXHAUSTED')
except BaseException as exc:
    result.update(outcome='HOLD_SERIALIZATION_TEST_FIRST_FAILURE',
                  error_type=type(exc).__name__, error=str(exc))
    raise
finally:
    end = {'ended_unix_s': time.time(), 'wall_s': time.monotonic() - started,
           'outcome': result.get('outcome')}
    (OUT / 'RESULT.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    (OUT / 'END.json').write_text(json.dumps(end, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'outcome': result.get('outcome'), **end}, allow_nan=False))
