"""One approved new-consumer process, including startup in absolute CPU budget."""
import resource
import signal
import sys


def cpu():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


class BudgetStop(Exception):
    pass


def stop(signum, frame):
    raise BudgetStop('new scientific process CPU budget exhausted')


signal.signal(signal.SIGPROF, stop)
signal.setitimer(signal.ITIMER_PROF, max(0.000001, 0.28 - cpu()))

import hashlib
import json
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, localcontext
import unittest

ROOT = Path('/workspace/scratch/52cc495a5f0a/rei_bass_storage_unit')


def owned(value):
    path = Path(value)
    if not path.is_absolute() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('absolute new-unit path required')
    return path


def encode(value):
    if type(value) is Fraction:
        return {'num': str(value.numerator), 'den': str(value.denominator)}
    if type(value) is dict:
        return {key: encode(item) for key, item in value.items()}
    if type(value) in (list, tuple):
        return [encode(item) for item in value]
    return value


def guard_phase():
    if cpu() >= 0.27:
        raise BudgetStop('refusing next science phase near absolute CPU cap')


def main():
    result = {'status': 'FAIL', 'prior_planning': '15.612490885', 'absolute_cap': '16',
              'process_cap': '0.28', 'tail': '0.05', 'remote_CAS_separate_reserve': '0.02',
              'unmeasured_cost': 'UNKNOWN_NOT_ZERO', 'old_tests': 0, 'provider_solves': 0,
              'IVP': 0, 'actual_native25': None, 'full_state_update': False}
    result_path = None
    try:
        if len(sys.argv) != 4:
            raise ValueError('usage: run_once.py CODE_PINS_JSON RESULT_JSON TEST_STDERR')
        pins_path, result_path, test_stderr = map(owned, sys.argv[1:])
        if result_path.exists() or test_stderr.exists():
            raise ValueError('one-shot result/log already exists')
        pins = json.loads(pins_path.read_bytes())
        expected_names = {'atomic_storage.py', 'test_atomic_storage.py', 'run_once.py'}
        if set(pins['files']) != expected_names or type(pins.get('source_commit')) is not str or not pins['source_commit']:
            raise ValueError('exact three code pins and source commit required')
        verified = {}
        for filename, wanted in pins['files'].items():
            data = (ROOT / 'implementation' / filename).read_bytes()
            actual = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
            if actual != wanted:
                raise ValueError('code blob mismatch: ' + filename)
            verified[filename] = actual
        result.update({'code_source_commit': pins['source_commit'], 'code_blobs': verified,
                       'python': sys.version, 'argv': sys.argv})
        guard_phase()
        import atomic_storage as storage
        import test_atomic_storage
        suite = unittest.defaultTestLoader.loadTestsFromModule(test_atomic_storage)
        if suite.countTestCases() != 14:
            raise ValueError('expected exactly14 new focused tests')
        guard_phase()
        with test_stderr.open('x', encoding='utf-8') as stream:
            tests = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        result['tests'] = {'run': tests.testsRun, 'failures': len(tests.failures),
                           'errors': len(tests.errors), 'skips': len(tests.skipped)}
        if not tests.wasSuccessful() or tests.skipped:
            raise ValueError('new focused tests failed; actual consume not started')
        guard_phase()
        raw_path = ROOT / 'inputs/BASS_FINITE_CHANNEL_RESULT.json'
        raw = raw_path.read_bytes()
        sha256 = hashlib.sha256(raw).hexdigest()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()
        storage.source_guard(source_pin=storage.SOURCE_PIN, sha256=sha256,
                             git_blob=blob, byte_count=len(raw))
        result['input'] = {'source_pin': storage.SOURCE_PIN, 'sha256': sha256,
                           'git_blob': blob, 'bytes': len(raw)}
        guard_phase()
        document = json.loads(raw, parse_float=str)
        consumed = storage.consume(document, native_mapping=(('H1I', 1), ('H1II', 2)))
        controls = {}
        result['actual_controls'] = controls
        controls['exact_source_binding'] = True
        controls['mapped_energy_identity'] = consumed['representation_energy_residual'] == 0
        if consumed['representation_energy_residual'] != 0:
            raise ValueError('representation algebra failed')
        combined = tuple(a + b + c for a, b, c in zip(consumed['proper_event_part'],
                                                      consumed['volume_correction'],
                                                      consumed['source_endpoint_residual_proper']))
        controls['proper_endpoint_decomposition'] = combined == consumed['proper_endpoint_change']
        if not controls['proper_endpoint_decomposition']:
            raise ValueError('proper endpoint decomposition failed')
        controls['thermal_electron_ownership'] = consumed['coarse_event_common_V0'][1] == consumed['coarse_event_common_V0'][2]
        controls['fast_electron_zero'] = consumed['fast_zeta'] == 0
        controls['no_full_state_projection'] = consumed['actual_native25'] is None and consumed['full_state_update'] is False
        if not all(controls[name] for name in ('thermal_electron_ownership', 'fast_electron_zero', 'no_full_state_projection')):
            raise ValueError('thermal ownership or no-full-state guard failed')
        owners = document['finite_owners']
        controls['saved_residual_lexemes_preserved'] = (
            consumed['saved_event_energy_sum_residual_lexeme'] == owners['event_energy_sum_residual']
            and consumed['saved_total_energy_work_identity_residual_lexeme'] == owners['total_energy_work_identity_residual'])
        if not controls['saved_residual_lexemes_preserved']:
            raise ValueError('saved residual preservation failed')
        lya = owners['channel_groups']['Lyalpha']
        lya_delta = storage._source_rows(lya['atomic_change'], 4)
        lya_coarse = storage.coarse_mapping(lya_delta, fine_order=storage.FINE,
                                            native_mapping=(('H1I', 1), ('H1II', 2)))
        lya_vector = (lya_coarse.neutral, lya_coarse.ion, lya_coarse.thermal_electrons)
        controls['actual_lya_coarse_zero'] = lya_vector == (Fraction(0),) * 3
        controls['actual_lya_fast_zero'] = lya_coarse.fast_zeta == 0
        if not controls['actual_lya_coarse_zero'] or not controls['actual_lya_fast_zero']:
            raise ValueError('saved Lyalpha coarse/fast zero control failed')
        controls['mapped_apply_ports_no_double_count'] = sum(consumed['mapped_apply_ports'].values(), Fraction(0)) == consumed['source_energy_sum']
        if not controls['mapped_apply_ports_no_double_count']:
            raise ValueError('mapped apply ports double-count or omit source energy')
        result['actual_saved_lya'] = {'net_count': storage.rational(lya['net_count']),
                                     'coarse_event_common_V0': lya_vector,
                                     'fast_zeta': lya_coarse.fast_zeta}
        result['actual_thermal_fast_distinction'] = {'thermal_electron_delta': consumed['coarse_event_common_V0'][2],
                                                    'fast_zeta': consumed['fast_zeta']}
        result['consumer'] = consumed
        with localcontext() as context:
            context.prec = 12
            result['readable_decimal_preview'] = {
                name: str(Decimal(consumed[name].numerator) / Decimal(consumed[name].denominator))
                for name in ('chi_target_J', 'baryon_residual', 'hidden_atomic_storage_J_per_V0',
                             'source_energy_sum', 'right_volume_ratio')}
        guard_phase()
        result['status'] = 'PASS'
    except BaseException as error:
        result['status'] = 'BUDGET_STOP' if isinstance(error, BudgetStop) else 'FAIL'
        result['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        signal.setitimer(signal.ITIMER_PROF, max(0.000001, 0.33 - cpu()))
        result['cpu_before_final_serialization'] = cpu()
        result['final_accounting'] = 'Absolute process tail deadline0.33; outer Bash CPU includes final serialization/exit; no budget reset.'
        payload = encode(result)
        if result_path is not None:
            with result_path.open('x', encoding='utf-8') as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2)
                stream.write('\n')
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + '\n')
        sys.stdout.flush()
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
