//! Rust-only fixed-input microphysics kernels and synthetic static H/He microsteps.
//! f64 tests are implementation evidence, not a validated enclosure.
//! The original four-group N is comoving count per cMpc^3; atomic densities are proper cm^-3.
//! Synthetic three-group H/He photons are proper cm^-3.
#![forbid(unsafe_code)]

#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/adaptive_history.rs"]
mod adaptive_history;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/angular_photons.rs"]
mod angular_photons;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/atomic_provider.rs"]
mod atomic_provider;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axisym_contract.rs"]
pub mod axisym_contract;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axisym_coupling.rs"]
pub mod axisym_coupling;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axisym_radiation.rs"]
pub mod axisym_radiation;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axisym_sources.rs"]
pub mod axisym_sources;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/bianchi_i.rs"]
mod bianchi_i;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/coverage.rs"]
pub mod coverage;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/deuterium_charge_exchange.rs"]
pub mod deuterium_charge_exchange;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/deuterium_thermal_charge_exchange.rs"]
pub mod deuterium_thermal_charge_exchange;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/deuterium_thermal_coupling.rs"]
pub mod deuterium_thermal_coupling;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/ft03_controlled.rs"]
mod ft03_controlled;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/ft03_interval.rs"]
mod ft03_interval;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/ft03_rates.rs"]
mod ft03_rates;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/group_rates.rs"]
mod group_rates;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/hhe_events.rs"]
mod hhe_events;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/homogeneous_rates.rs"]
mod homogeneous_rates;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/hydrogen_step.rs"]
mod hydrogen_step;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/interval_ad.rs"]
mod interval_ad;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/interval_math.rs"]
mod interval_math;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/isotope_state.rs"]
pub mod isotope_state;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/lift.rs"]
mod lift;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/microstep.rs"]
mod microstep;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/thermal.rs"]
mod thermal;

pub use adaptive_history::{
    certified_ft03_trial, scaled as ft03_scaled, try_certified_ft03_step, CertifiedTrial, RootSite,
};
pub use angular_photons::{PhotonBins, PhotonGrid, PhotonPacket, RadiationState};
pub use atomic_provider::{
    Absorber, AtomicProvider, CoefficientUnits, ObservableKind, RawCoefficient, RawProcess,
    RawRecord, RecombinationCase, SourceFrame, TemperatureDomain,
};
pub use axisym_contract::{
    AxisymContractError, AxisymRunContract, AxisymmetryStatus, Clock, ClosureChoice, ExecutionMode,
    Frame, GeometryOnlyAdmission, ICProviderRecord, MuReflectionStatus, ProviderDomain,
    ProviderErrorStatus, ProviderRecord, RadiationUnits, SourceProviderRecord, SymmetryRecord,
};
pub use axisym_coupling::{isotropic_expansion_terms, IsotropicExpansionTerms};
pub use axisym_radiation::{AxisymPhotonLedgerContract, AxisymPhotonStep};
pub use axisym_sources::{
    validate_routing, ExcessPartition, PhotoEventLedger, PhotonRouting, PrimaryPhotoEvent,
};
pub use bianchi_i::{
    AxisymmetricPoint, CharacteristicRay, ConstantAxisymmetricBackground, ConstantHubbleBackground,
    GeometryBackground, GeometrySnapshot, RayDerivative,
};
pub use ft03_controlled::{
    ft03_adaptive_step, ft03_implicit_step, ft03_rhs, ft03_try_step, Ft03Events, Ft03Model,
    Ft03Rhs, Ft03Step, FT03_MODEL_ID,
};
pub use ft03_interval::ft03_interval_rhs;
pub use ft03_rates::{ft03_coefficients, Ft03Coefficients};
pub use group_rates::{
    gamma_species, opacity_cMpc_inv, pchip_eval, photon_rates, transform_z_to_y, PchipTable,
    C_LIGHT, MPC_CM,
};
pub use hhe_events::{hhe_rhs, HHeEvents, HHeModel, HHeRhs, HHeState};
pub use homogeneous_rates::{
    homogeneous_opacity, homogeneous_photo_rates, HomogeneousPhotoRates, OpacityOwners, PhotonNode,
};
pub use hydrogen_step::{hydrogen_step, HydrogenRates, HydrogenStep};
pub use interval_ad::Jet;
pub use interval_math::Interval;
pub use isotope_state::{
    IsotopeNumberMoments, IsotopeNumberState, IsotopeSpecies, LegacyHHeEosSnapshot,
    LegacyHHeProjection,
};
pub use lift::{positive_mass_projection, signed_transfer_lift};
pub use microstep::{adaptive_hhe_step, implicit_hhe_step, try_hhe_step, HHeStep, StepControl};

#[derive(Debug, Clone)]
pub struct State {
    pub n_comoving_per_cmpc3: [f64; 4],
    pub x_hii: f64,
    /// HeI, HeII, HeIII fractions.
    pub helium: [f64; 3],
    pub u_erg_per_cm3: f64,
    pub gamma_hi_per_s: f64,
}

#[derive(Debug, Clone)]
pub struct GroupParams {
    pub redshift: f64,
    pub n_h_proper_per_cm3: f64,
    pub n_he_proper_per_cm3: f64,
    pub hubble_per_s: f64,
    pub sigma_hi_cm2: [f64; 4],
    pub sigma_hei_cm2: [f64; 4],
    pub sigma_heii_cm2: [f64; 4],
    pub redshift_coeff: [f64; 4],
    pub source_fraction: [f64; 4],
    pub lowgroup_log_opacity: [PchipTable; 2],
}

#[derive(Debug, Clone)]
pub struct GammaSpecies {
    pub hi_per_s: f64,
    pub hei_per_s: f64,
    pub heii_per_s: f64,
    pub group_hi_per_s: [f64; 4],
}

#[derive(Debug, Clone)]
pub struct SignedLift {
    pub positive: Vec<f64>,
    pub negative: Vec<f64>,
    pub signed: Vec<f64>,
}

#[derive(Debug, Clone)]
pub enum ForwardError {
    InvalidInput(&'static str),
    OutsideTableDomain { x: f64, lower: f64, upper: f64 },
    InfeasibleZeroPriorSupport,
    MissingAuthority(&'static str),
}

impl ForwardError {
    pub fn code(&self) -> &'static str {
        match self {
            Self::InvalidInput(code) => code,
            Self::OutsideTableDomain { .. } => "OUTSIDE_TABLE_DOMAIN",
            Self::InfeasibleZeroPriorSupport => "INFEASIBLE_ZERO_PRIOR_SUPPORT",
            Self::MissingAuthority(_) => "MISSING_AUTHORITY",
        }
    }
}
impl std::fmt::Display for ForwardError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.code())
    }
}
impl std::error::Error for ForwardError {}

#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/flrw_three_equations.rs"]
pub mod flrw_three_equations;

#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/he_rct.rs"]
pub mod he_rct;

#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/coupled_primary.rs"]
pub mod coupled_primary;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/rux_adapter.rs"]
pub mod rux_adapter;

#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/igm_background.rs"]
pub mod igm_background;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/igm_state.rs"]
pub mod igm_state;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/igm_rates.rs"]
pub mod igm_rates;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/igm_thermal.rs"]
pub mod igm_thermal;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_rates.rs"]
pub mod axbi_rates;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_background.rs"]
pub mod axbi_background;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_bass_background.rs"]
pub mod axbi_bass_background;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_sources.rs"]
pub mod axbi_sources;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_driver.rs"]
pub mod axbi_driver;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_covariant_transport.rs"]
pub mod axbi_covariant_transport;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_parallel.rs"]
pub mod axbi_parallel;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_q_reference.rs"]
pub mod axbi_q_reference;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_q_advance.rs"]
pub mod axbi_q_advance;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_q_capacity.rs"]
pub mod axbi_q_capacity;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_q_grid.rs"]
pub mod axbi_q_grid;
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/axbi_q_closure.rs"]
pub mod axbi_q_closure;

#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/deuterium_atomic.rs"]
pub mod deuterium_atomic;

/// Opt-in immutable temperature coefficient evaluation and exact prepared reuse.
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/rate_table.rs"]
pub mod rate_table;
/// Explicit Li6/Li7 shared-electronic approximation and number-rate component.
#[path = "/workspace/scratch/56fd3625e428/rei_bianchi/rust/rei_microphysics/src/lithium_rates.rs"]
pub mod lithium_rates;
