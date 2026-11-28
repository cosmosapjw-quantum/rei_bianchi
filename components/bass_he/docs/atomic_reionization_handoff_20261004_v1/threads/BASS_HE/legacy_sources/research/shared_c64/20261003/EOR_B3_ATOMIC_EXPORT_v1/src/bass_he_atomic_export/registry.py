"""Explicit source registry. Availability never grants scientific admission."""
from __future__ import annotations
from . import _rate

CORE_SHA256 = '529ae325622718b48292c3b748a7850ccb315733b28bff930388f00915f2d217'
IO_SHA256 = '3dd8d8080216d6e4448d66590e411afdab4b6a801abf37a1c1fad47754c3bd88'
ORIGIN_COMMIT = '9e3d54bf13045b01b3d7a493db78fa3289d3da9d'


def sources() -> dict:
    """Return a fresh registry object, not mutable process-global state."""
    return {
        'schema': 'bass-he.atomic-sources.v1',
        'default_source_id': None,
        'automatic_source_ranking': False,
        'sources': [
            {
                'source_id': _rate.SOURCE_ID,
                'availability': 'LITERATURE_FIT_OPT_IN',
                'thermal_rate_available': True,
                'event_count_coefficients_available': True,
                'origin_commit': ORIGIN_COMMIT,
                'upstream_path': 'research/shared_c64/20261003/EOR_B1_RCX_RATE_v1/src/bass_he_rcx/core.py',
                'core_git_blob': 'c3f5cb56b7f5babcbead21694de31b57ca4ff992',
                'core_sha256': CORE_SHA256,
                'numerical_model_changed': False,
                'code_migration': 'identical core bytes; new private module path',
                'rate_source': 'arXiv:2511.21966v1, Appendix B.3',
                'rate_source_url': 'https://arxiv.org/html/2511.21966v1',
                'mechanism_source_doi': '10.1103/PhysRevA.26.3164',
                'reaction_id': _rate.REACTION_ID,
                'domain_K': ['200', '10000'],
                'native_coefficient': _rate.K_CGS,
                'native_unit': 'cm3 s-1',
                'conflict': 'GM25 reports >10-fold disagreement with KF96; not resolved here',
                'uncertainty': None,
                'fit_error_bound': None,
                'spectral_energy_moment': None,
                'independent_reintegration': False,
                'physical_accuracy_certified': False,
                'required_acknowledgment_is_not_approval': True,
            },
            {
                'source_id': 'WEST82_OPTICAL_REFERENCE_V2',
                'availability': 'DECLARED_OPERATOR_REFERENCE_NOT_ATOMIC_RATE_SOURCE',
                'thermal_rate_available': False,
                'event_count_coefficients_available': False,
                'distribution_name': 'bass-he-west82-reference',
                'distribution_version': '0.2.0',
                'import_namespace': 'bass_he_west82',
                'supported_ell': [0, 64],
                'supported_operator': 'piecewise-constant finite range, exact-free exterior',
                'V_and_Gamma_physical_arrays': None,
                'physical_accuracy_certified': False,
                'origin_commit': '70396fdc38fa64ede799d8a4929a203a422256d6',
            },
        ],
    }
