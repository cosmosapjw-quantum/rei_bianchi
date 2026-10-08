"""Portable read-only admission of the preserved PR88 instantaneous observation.

This calls the unchanged PR88 adapter and PR87 algebra. Integrated owners,
opacity, and nonphoto RHS never supply missing instantaneous moments.
"""
from __future__ import annotations
import argparse
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent / 'igm_rate_export_receiver_20261008'
UPSTREAM = PACKAGE / 'repo/research/igm_rate_receiver01_20261008/adapter.py'
REQUIRED_PRODUCER_FIELDS = (
    'Gamma[HI,HeI,HeII] (absorber^-1 s^-1)',
    'incident_Ecal[HI,HeI,HeII] (eV absorber^-1 s^-1, incident energy)',
    'same sampled spectral energies, weights, photon density and sigma for both moments',
    'producer commit/source-tree/build identity and accepted transaction or observed snapshot ID',
    'gas h,y,z,w_erg_h; proper nH,nHe; H; kB; eV-to-erg; c*sigmaT',
    'exact gas/photon epoch ln(a), clock and background authority',
    'provider/version/cross-section source, binding chi_ev and distinct support cutoffs',
    'source/closure/quadrature identities and model domain',
    'family_id/kind and ordered shared generator IDs and six-component coefficients',
    'explicit observed-point or supplied uncertainty/common-spectrum premises',
    'separate extra observer/provider/RHS work counters',
)


def missing_result():
    return {
        'status': 'MISSING_INSTANTANEOUS_JOINT_MOMENTS',
        'required_producer_fields': list(REQUIRED_PRODUCER_FIELDS),
        'forbidden_substitutes': ['integrated A/B divided by dt', 'Segment.rates opacity',
                                 'nonphoto midpoint RHS photo zeros'],
        'physical': 'HOLD', 'extra_observer_calls': 0, 'extra_provider_calls': 0,
    }


def upstream():
    # This source is an unchanged PR88 dependency, pinned in SOURCE_IDENTITY.json.
    spec = importlib.util.spec_from_file_location('igm_pr88_point_adapter', UPSTREAM)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def readout(packet=None, *, expected_context=None):
    """Accept only the declared pinned singleton; return typed conditional algebra.

    Caller expectation is checked in the actual receiver. No native modules,
    provider queries, recomputed spectrum, or history solver are invoked.
    """
    if not isinstance(packet, dict) or any(packet.get(k) is None for k in ('Gamma', 'incident_Ecal')):
        return missing_result()
    a = upstream()
    if (packet.get('schema') != 'igm-instantaneous-singleton-observation/v1' or
            packet.get('family_id') != 'accepted-step2-observation:' +
            '9929edc36232b3620264f3a8b3cf55104ba31c4f63df238f02ed25079738b2b0'):
        raise ValueError('PINNED_PRODUCER_SCHEMA_FAMILY_ID_REQUIRED')
    original = copy.deepcopy(packet)
    state, chi, context, family = a.typed_input(packet)
    result = a.conditional_joint_enclosure(
        state, chi, family, context=context if expected_context is None else expected_context,
        premises=a.PREMISES)
    assert packet == original
    return {
        'status': 'PASS_CONDITIONAL_OBSERVED_POINT_ONLY',
        'typed_input': a.serialize_input(packet),
        'conditional_output': result.as_json(),
        'producer_context': copy.deepcopy(packet['context']),
        'producer_moment_identity': {k: copy.deepcopy(packet[k]) for k in
                                     ('schema', 'family_id', 'family_kind', 'generators',
                                      'generator_ids', 'uncertainty_widths', 'units',
                                      'context_id', 'observation_id')},
        'singleton_generator_semantics': 'zero generators for observed binary64 point only',
        'extra_observer_calls': 0, 'extra_provider_calls': 0, 'extra_rhs_calls': 0,
        'provider_error': 'UNKNOWN', 'continuum_error': 'UNKNOWN', 'physical': 'HOLD',
        'history_integrated': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, help='JSON packet; omission explicitly refuses missing moments')
    parser.add_argument('--output', type=Path, required=True, help='new output directory')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('fresh output directory required')
    packet = json.loads(args.packet.read_text()) if args.packet else None
    result = readout(packet)
    args.output.mkdir(parents=True)
    (args.output / 'READOUT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'])
    return 0 if result['status'].startswith('PASS_') else 2


if __name__ == '__main__':
    raise SystemExit(main())
