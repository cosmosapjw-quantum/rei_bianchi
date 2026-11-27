"""HE38 source-qualified finite-mass H1 CI component; no execution on import."""
from .model import (
    FiniteMassModel, FiniteMassEvaluation, SpeciesSources, EventKinematics,
    finite_mass_source, event_kinematics, sigma_m2, transfer_u, transfer_mean_eV,
    ME_KG, MP_KG, MH_KG, TOTAL_MASS_KG, MU_KG, MU_INNER_KG,
    ETA, ZETA, ION_FRACTION_INNER, ELECTRON_FRACTION_INNER,
    I_EV, I_J, EV_J, KB_J_K, A0_M, MODEL_IDENTITY, MODEL_SCOPE, ENERGY_MAPPING,
    MomentDomainError, MomentRepresentabilityError,
)
from .bridge import (
    H1FiniteMassSource, h1_ci_source, H0_INDEX, HP_INDEX,
    ALL_RETAINED_THERMAL, NEUTRAL_21_STATE_CENSUS,
    PHYSICAL_JACOBIAN_SCOPE, FROZEN_NE_JACOBIAN_SCOPE,
)
