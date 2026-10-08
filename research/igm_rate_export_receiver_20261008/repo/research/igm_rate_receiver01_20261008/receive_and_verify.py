#!/usr/bin/env python3
"""Consume preserved EXPORT01 via the typed receiver and test only this adapter."""
from pathlib import Path
from fractions import Fraction
from dataclasses import replace
import copy
import hashlib
import json
import sys

# Actual Python call counters and executable-spawn audit for this invocation.
# No native scientific module is imported or native executable is launched.
counts = {'conditional_joint_enclosure': 0, 'project': 0,
          'spectral_moments': 0, 'cross_section': 0,
          'igm_point_rhs': 0, 'advance': 0, 'native_or_child_spawns': 0}


def profile(frame, event, arg):
    if event == 'call':
        name = frame.f_code.co_name
        if name in counts:
            counts[name] += 1
            if name in ('cross_section', 'igm_point_rhs', 'advance', 'spectral_moments'):
                raise RuntimeError('FORBIDDEN_NEW_SCIENCE_CALL:' + name)


def audit(event, args):
    if event in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn', 'ctypes.dlopen'):
        counts['native_or_child_spawns'] += 1
        raise RuntimeError('NO_NATIVE_OR_CHILD_EXECUTION_AUTHORIZED')


sys.addaudithook(audit)
sys.setprofile(profile)
import adapter as a
from upstream_bridge.vendor.source_transfer import ContractError


def main():
    if len(sys.argv) != 2:
        raise ValueError('fresh_output_directory required')
    out = Path(sys.argv[1])
    if out.exists():
        raise ValueError('FRESH_OUTPUT_REQUIRED')
    packet = a.load_packet()
    original_bytes = (a.ROOT / 'observed/EXPORT01.json').read_bytes()
    original_copy = copy.deepcopy(packet)
    state, chi, context, family = a.typed_input(packet)
    result = a.consume(packet)
    primary_counts = counts.copy()
    assert primary_counts['conditional_joint_enclosure'] == 1
    assert primary_counts['project'] == 1
    controls = []
    assert tuple(family.center.gamma) == tuple(Fraction.from_float(x) for x in packet['Gamma'])
    assert tuple(family.center.energy_ev_s) == tuple(Fraction.from_float(x) for x in packet['incident_Ecal'])
    assert a.SPECIES == ('HI', 'HeI', 'HeII')
    controls.append('six exact Fraction.from_float centers in HI/HeI/HeII order')
    assert family.generators == family.generator_ids == ()
    assert result.generators_native == result.generator_ids == ()
    assert result.joint_image_retained and not result.history_integrated
    assert all(lo == hi == result.center_native[k] for k, (lo, hi) in result.bounds_native.items())
    controls.append('zero generators; shared point image; no residual repair or independent marginal uncertainty')
    previous = json.loads(a.pinned_bytes(a.ROOT / 'observed/PHOTO_ALGEBRA.json', a.ALGEBRA_SHA))
    assert {k: a.rational(v) for k, v in result.center_native.items()} == previous['native_per_second']
    controls.append('actual typed receiver singleton algebra equals preserved direct point algebra exactly')
    for key, (lo, hi) in result.bounds_dln_a.items():
        native_key = key if key == 'photo_q_ell_source' else next(
            k for k, v in a.conditional_joint_enclosure.__globals__['DLN_A_NAMES'].items() if v == key)
        expected = result.center_native[native_key]
        if key != 'photo_q_ell_source':
            expected /= state.hubble_s
        assert lo == hi == expected
    controls.append('dt-to-dln-a divides same H once; q_ell receives no extra H division')
    assert a.PRODUCER_TREE in context.source_id and a.BUILD_PIN in context.source_id
    assert a.CONTEXT_ID in context.source_id and state == context.bound_state
    assert context.epoch_ln_a == Fraction.from_float(packet['context']['epoch_ln_a'])
    controls.append('producer/tree/build/full-context identities and exact fixed state/epoch bound')

    def refused(label, fn, code):
        try:
            fn()
        except ValueError as e:
            assert code in str(e), (label, str(e))
            controls.append(label + ': ' + str(e))
            return
        raise AssertionError(label + ' was accepted')

    # Genuine pinned receiver refusal, not only the local packet checker.
    wrong = replace(context, source_id=context.source_id + ';wrong-source')
    refused('actual typed receiver changed-source context refusal', lambda:
            a.conditional_joint_enclosure(state, chi, family, context=wrong,
                                           premises=a.PREMISES), 'CONTEXT_MISMATCH')
    wrong_epoch = replace(context, epoch_ln_a=context.epoch_ln_a + Fraction(1, 2**60))
    refused('actual typed receiver changed-epoch context refusal', lambda:
            a.conditional_joint_enclosure(state, chi, family, context=wrong_epoch,
                                           premises=a.PREMISES), 'CONTEXT_MISMATCH')
    refused('actual typed receiver empty-premise refusal', lambda:
            a.conditional_joint_enclosure(state, chi, family, context=context,
                                           premises=()), 'PREMISES_REQUIRED')
    refused('producer-tree substitution refused', lambda:
            a.typed_input(packet, producer_tree='wrong'), 'IDENTITY_REQUIRED')
    refused('species permutation refused', lambda:
            a.typed_input(packet, species=('HeI', 'HI', 'HeII')), 'ORDER_REQUIRED')
    for field, value in [('Gamma', 'cm^-3 s^-1'), ('incident_Ecal', 'erg absorber^-1 s^-1')]:
        changed = copy.deepcopy(packet)
        changed['units'][field] = value
        refused('changed ' + field + ' units refused', lambda p=changed:
                a.typed_input(p), 'UNITS_REQUIRED')
    for field in ('provider_source_sha256', 'producer_commit'):
        changed = copy.deepcopy(packet)
        changed['context'][field] += 'wrong'
        refused('changed ' + field + ' refused', lambda p=changed:
                a.typed_input(p), 'CONTEXT_MISMATCH')
    changed = copy.deepcopy(packet)
    changed['Gamma'][0], changed['Gamma'][1] = changed['Gamma'][1], changed['Gamma'][0]
    refused('permuted actual Gamma values refused', lambda:
            a.typed_input(changed), 'IDENTITY_MISMATCH')
    assert packet == original_copy
    assert original_bytes == (a.ROOT / 'observed/EXPORT01.json').read_bytes()
    a.pinned_bytes(a.ROOT / 'IGM_RATE_EXPORT01_LOCAL_SINGLETON_20261008.zip', a.PRESERVED_ZIP_SHA)
    controls.append('original packet values/bytes and original archive SHA remain unchanged')
    assert all(counts[k] == 0 for k in ('spectral_moments', 'cross_section', 'igm_point_rhs', 'advance', 'native_or_child_spawns'))
    total_counts = counts.copy()
    sys.setprofile(None)
    out.mkdir()
    typed = a.serialize_input(packet)
    receipt = {
        'status': 'PASS_ACTUAL_PINNED_TYPED_RECEIVER_CONSUMPTION',
        'entrypoint': 'upstream_bridge.joint_moment.conditional_joint_enclosure',
        'receiver_head': a.RECEIVER_HEAD, 'receiver_core': a.RECEIVER_CORE,
        'source_pins': a.SOURCE_PINS,
        'adapter_sources': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(a.HERE.glob('*.py'))},
        'packet_sha256': a.PACKET_SHA, 'context_id': a.CONTEXT_ID,
        'producer_commit': a.PRODUCER, 'producer_tree': a.PRODUCER_TREE,
        'primary_call_counts': primary_counts, 'all_adapter_and_test_call_counts': total_counts,
        'count_scope': 'Python profile observed function calls; executable/ctypes audit observed zero launches. Native in-process scientific counters are not available; no native scientific code loaded.',
        'control_count': len(controls), 'controls': controls,
        'premises': list(a.PREMISES), 'parameter_family_uncertainty_admission': False,
        'provider_error': 'UNKNOWN', 'continuum_error': 'UNKNOWN',
        'physical': 'HOLD', 'full_Wide': 'HOLD', 'history_integrated': False,
        'remote_receiver_adoption': False,
        'scope': 'actual local invocation of exact pinned PR87 typed receiver; no upstream production/default adoption or coupled experiment',
    }
    for name, value in [('TYPED_INPUT.json', typed), ('RECEIVER_OUTPUT.json', result.as_json()),
                        ('RECEIVER_RECEIPT.json', receipt)]:
        (out / name).write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
