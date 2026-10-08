"""Opt-in PR87 typed consumption of one preserved binary64 observation.

No uncertainty family is asserted: zero generators identify only this point.
"""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXPORT_SOURCE = HERE.parent / 'igm_rate_export01_20261008'
PRODUCER = '8477bae16accaf3de168669aafd2f31eac2ca811'
PRODUCER_TREE = '118cb0e67de8f649244dd6798a6c6f37af2dc1f2'
RECEIVER_HEAD = '17f43b84ee49bada32d6efe84c3377e7d645f230'
RECEIVER_CORE = '93bed7e210296db7cd250421f48cdc25aff3029f'
BUILD_PIN = 'e34740bf7972cc4bd9223373024450fdb85dab25331e8354e1273701134c2cd0'
CONTEXT_ID = '721809c83a225cf680aee5f92da2f9847d9dd556aec7b2d7201c0bcfcee6abd0'
OBSERVATION_ID = '1623af1f8e661047f0b339c614ea90ae61b8b50f8f0a961158ea1591b0a9db25'
PACKET_SHA = 'ff24f004e3ef53b4f43d0484a678c0aa7224f1cfd7aa0e007a43cb13f59ac99d'
ALGEBRA_SHA = 'ed571813f97b3f041a72739db865411538584016614d1b6b1b8a8961ea6a4952'
PRESERVED_ZIP_SHA = '13c2294985af682c58c15d45eab5cca0aa025ed78432712fd5d44ffbc9c4d68b'
SOURCE_PINS = {
    'packet.py': '05a15912bbe2fa49e1fe1afd3c09c9f2809a0a2846ced7e467ef045e455c8828',
    'upstream_bridge/joint_moment.py': '6f4cf88c2bc9f240d4bb29b429df5d257d55381a5699d75af78da2897a4443cf',
    'upstream_bridge/vendor/source_transfer.py': '1ce2e7e18425191be95722c4f4eee72a5b0cd43e6c3832e0497bba728ee28459',
}
PREMISES = (
    'observed fixed binary64 finite-rule point only; provider/continuum errors UNKNOWN',
    'center is Fraction.from_float of the preserved six ordered outputs; '
    'zero generators do not enclose an exact spectral integral or provider error',
    'fixed full gas/EOS, photon/gas epoch, provider, quadrature, source/build and '
    'producer tree identities apply only to accepted committed-2; no history claim',
)


def pinned_bytes(path, expected):
    if path.is_symlink() or not path.is_file():
        raise ValueError('REGULAR_PINNED_FILE_REQUIRED')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('PINNED_SOURCE_OR_PACKET_MISMATCH:' + path.name)
    return data


# Verify the original receiver and checker before importing them, unchanged.
for relative, expected in SOURCE_PINS.items():
    pinned_bytes(EXPORT_SOURCE / relative, expected)
sys.path.insert(0, str(EXPORT_SOURCE))
from packet import check
from upstream_bridge.joint_moment import (
    FixedContext, JointMomentFamily, conditional_joint_enclosure, SPECIES,
)
from upstream_bridge.vendor.source_transfer import State, Moments


def exact_float(x):
    if type(x) is not float:
        raise ValueError('OBSERVED_BINARY64_FLOAT_REQUIRED')
    return Fraction.from_float(x)


def load_packet():
    return json.loads(pinned_bytes(ROOT / 'observed/EXPORT01.json', PACKET_SHA))


def typed_input(packet, *, producer_tree=PRODUCER_TREE, species=SPECIES):
    """Keep the original singleton unchanged; make a separate typed point view."""
    check(packet, CONTEXT_ID)
    c = packet['context']
    if (c['producer_commit'] != PRODUCER or producer_tree != PRODUCER_TREE or
            c['accepted_source_build_pin'] != BUILD_PIN or
            c['receiver_contract_head'] != RECEIVER_HEAD or
            c['receiver_contract_core'] != RECEIVER_CORE or
            packet['observation_id'] != OBSERVATION_ID):
        raise ValueError('PINNED_PRODUCER_OBSERVATION_RECEIVER_IDENTITY_REQUIRED')
    if tuple(species) != ('HI', 'HeI', 'HeII'):
        raise ValueError('HI_HEI_HEII_ORDER_REQUIRED')
    # The preserved context digest binds ALL background positions. Select only
    # proper nH, nHe and H; do not use integrated owner A/B or opacity arrays.
    h, y, z, w = map(exact_float, c['gas_state'])
    background = c['background']
    k = c['constants']
    state = State(h, y, z, w, exact_float(background[3]),
                  exact_float(background[4]), exact_float(background[2]),
                  exact_float(k['kb_erg_k']), exact_float(k['ev_erg']),
                  exact_float(k['c_thomson_cm3_s']))
    epoch = exact_float(c['epoch_ln_a'])
    if (exact_float(c['gas_epoch_ln_a']) != epoch or
            exact_float(c['photon_epoch_ln_a']) != epoch):
        raise ValueError('SAME_GAS_PHOTON_EPOCH_REQUIRED')
    chi = tuple(map(exact_float, c['chi_ev']))
    context = FixedContext(
        source_id='producer:' + PRODUCER + ';tree:' + producer_tree +
                  ';build:' + BUILD_PIN + ';export-context:' + CONTEXT_ID,
        clock_id='accepted-committed-2;gas-and-photon-ln-a:' + str(epoch),
        state_id='typed-sha256:' + c['accepted_payload_sha256'] +
                 ';observation:' + OBSERVATION_ID,
        provider_id=c['photo_provider'] + ';source-sha256:' +
                    c['provider_source_sha256'] + ';context:' + CONTEXT_ID,
        bound_state=state, epoch_ln_a=epoch, chi_ev=chi,
    )
    center = Moments(tuple(map(exact_float, packet['Gamma'])),
                     tuple(map(exact_float, packet['incident_Ecal'])))
    family = JointMomentFamily(
        center=center, generators=(), context=context,
        family_id='observed-fixed-binary64-point:' + OBSERVATION_ID,
        family_kind='finite_rule_envelope', generator_ids=(),
        gamma_unit=packet['units']['Gamma'],
        energy_unit=packet['units']['incident_Ecal'],
    )
    return state, chi, context, family


def consume(packet):
    state, chi, context, family = typed_input(packet)
    # This is the actual typed PR87 receiver, not direct project alone.
    return conditional_joint_enclosure(
        state, chi, family, context=context, premises=PREMISES)


def rational(x):
    return str(x.numerator) + '/' + str(x.denominator)


def serialize_input(packet):
    state, chi, context, family = typed_input(packet)
    return {
        'schema': 'igm-observed-point-typed-adapter/v1',
        'original_packet_sha256': PACKET_SHA,
        'original_packet_context_id': CONTEXT_ID,
        'original_observation_id': OBSERVATION_ID,
        'producer_commit': PRODUCER, 'producer_tree': PRODUCER_TREE,
        'producer_tree_evidence': 'existing delivery-20261008/HANDOFF.md and DELIVERY_STATUS.json; not a new remote lookup',
        'receiver_head': RECEIVER_HEAD, 'receiver_core': RECEIVER_CORE,
        'receiver_source_pins': SOURCE_PINS,
        'species_order': list(SPECIES), 'units': packet['units'],
        'family_id': family.family_id, 'family_kind': family.family_kind,
        'generators': [], 'generator_ids': [],
        'center': {'Gamma': list(map(rational, family.center.gamma)),
                   'incident_Ecal': list(map(rational, family.center.energy_ev_s))},
        'bound_state': {k: rational(v) for k, v in state.__dict__.items()},
        'context_labels': {k: getattr(context, k) for k in
                           ('source_id', 'clock_id', 'state_id', 'provider_id')},
        'epoch_ln_a': rational(context.epoch_ln_a),
        'chi_ev': list(map(rational, chi)), 'premises': list(PREMISES),
        'provider_error': 'UNKNOWN', 'continuum_error': 'UNKNOWN',
        'residual_repair': False, 'independent_marginal_uncertainty': False,
        'point_bounds_meaning': 'exact image of observed binary64 center only; not an uncertainty enclosure of underlying science',
        'physical': 'HOLD', 'full_Wide': 'HOLD', 'history_integrated': False,
    }
