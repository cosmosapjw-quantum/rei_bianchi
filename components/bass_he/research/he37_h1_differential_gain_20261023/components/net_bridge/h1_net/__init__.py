"""HE37 source-defined H1 CI net event bridge; importing executes no case."""
from .net_source import (
    h1_ci_source, H1CISource, H0_INDEX, HP_INDEX, MASS_NUMBER, IONIC_CHARGE,
    ALL_RETAINED_THERMAL, NEUTRAL_21_STATE_CENSUS,
    FROZEN_NE_JACOBIAN_SCOPE, PHYSICAL_JACOBIAN_SCOPE,
)
from .he36.reactive_moments import MomentDomainError, MomentRepresentabilityError
from .he36.vendor.rei_resolved_local import Unresolved
