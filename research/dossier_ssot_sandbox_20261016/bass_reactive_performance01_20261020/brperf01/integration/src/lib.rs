//! Fixed-volume, source-off integration controls for BRPERF01 rate reuse.
//! All state updates and native adaptive CX half-flows belong to the parent.
#![forbid(unsafe_code)]

use parent::deuterium_atomic::DAtomicProvider;
use parent::deuterium_thermal_coupling::CxOwnership;
use parent::full_network::{EventBudget, FullState, NetworkConfig, NetworkError, NetworkResult};
use parent::igm_rates::{IgmRates, igm_rates};
use parent::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use parent::midpoint_gas::{self, GasRhs};
use parent::mixture_coupling::CoupleError;
use parent::mixture_eos::{KB_J_K, MixtureState};
use parent::rate_table::IgmRateTable;
use parent::{ForwardError, HHeModel};
use std::io::{self, Write};
use std::time::Instant;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Backend {
    Original,
    ReusedDirect,
    Legacy,
    #[cfg(feature = "compact")]
    Compact,
    #[cfg(feature = "compact")]
    CompactSimd,
}
impl Backend {
    pub fn name(self) -> &'static str {
        match self {
            Self::Original => "original_direct",
            Self::ReusedDirect => "reused_direct",
            Self::Legacy => "legacy_65537",
            #[cfg(feature = "compact")]
            Self::Compact => "compact_pchip",
            #[cfg(feature = "compact")]
            Self::CompactSimd => "compact_pchip_simd",
        }
    }
    pub fn all() -> Vec<Self> {
        let modes = vec![Self::Original, Self::ReusedDirect, Self::Legacy];
        #[cfg(feature = "compact")]
        let modes = {
            let mut modes = modes;
            modes.push(Self::Compact);
            modes.push(Self::CompactSimd);
            modes
        };
        modes
    }
}

pub struct Tables {
    pub legacy: IgmRateTable,
    #[cfg(feature = "compact")]
    pub compact: rates::CompactRateTable,
    pub legacy_setup_s: f64,
    #[cfg(feature = "compact")]
    pub compact_setup_s: f64,
}
impl Tables {
    pub fn build(_compact_nodes: usize) -> Result<Self, ForwardError> {
        let begin = Instant::now();
        let legacy = IgmRateTable::new(65537)?;
        let legacy_setup_s = begin.elapsed().as_secs_f64();
        #[cfg(feature = "compact")]
        let begin = Instant::now();
        #[cfg(feature = "compact")]
        let compact = rates::CompactRateTable::build(_compact_nodes)?;
        #[cfg(feature = "compact")]
        let compact_setup_s = begin.elapsed().as_secs_f64();
        Ok(Self {
            legacy,
            #[cfg(feature = "compact")]
            compact,
            legacy_setup_s,
            #[cfg(feature = "compact")]
            compact_setup_s,
        })
    }
    pub fn rates(&self, backend: Backend, t: f64) -> Result<IgmRates, ForwardError> {
        match backend {
            Backend::Original | Backend::ReusedDirect => igm_rates(t),
            Backend::Legacy => self.legacy.rates(t),
            #[cfg(feature = "compact")]
            Backend::Compact => self.compact.rates(t),
            #[cfg(feature = "compact")]
            Backend::CompactSimd => self.compact.rates_simd(t),
        }
    }
    pub fn rhs(
        &self,
        backend: Backend,
        s: &FullState,
        c: &NetworkConfig,
    ) -> Result<GasRhs, NetworkError> {
        if backend == Backend::Original {
            midpoint_gas::rhs(s, c)
        } else {
            native::rhs_with_evaluator(s, c, &mut |t| self.rates(backend, t))
        }
    }
    pub fn step(
        &self,
        backend: Backend,
        s: &FullState,
        c: &NetworkConfig,
        duration: f64,
    ) -> Result<NetworkResult, NetworkError> {
        if backend == Backend::Original {
            midpoint_gas::step_strang(s, c, duration)
        } else {
            native::step_strang_with_evaluator(s, c, duration, &mut |t| self.rates(backend, t))
        }
    }
    pub fn setup_csv(&self, out: &mut impl Write) -> io::Result<()> {
        writeln!(out, "backend,nodes,storage_bytes,blocked_cells,setup_s")?;
        writeln!(
            out,
            "legacy_65537,{},{},{},{:.17e}",
            self.legacy.grid().nodes(),
            self.legacy.storage_bytes(),
            self.legacy.grid().blocked_cells(),
            self.legacy_setup_s
        )?;
        #[cfg(feature = "compact")]
        writeln!(
            out,
            "compact_pchip,{},{},{},{:.17e}",
            self.compact.nodes(),
            self.compact.storage_bytes(),
            self.compact.blocked_cells(),
            self.compact_setup_s
        )?;
        Ok(())
    }
}

#[derive(Clone, Copy)]
pub struct Case {
    pub name: &'static str,
    pub temperature: f64,
    pub span_s: f64,
}
pub const CASES: [Case; 3] = [
    Case {
        name: "COOL_RR_3000",
        temperature: 3000.0,
        span_s: 8e12,
    },
    Case {
        name: "MID_CE_10000",
        temperature: 10000.0,
        span_s: 8e12,
    },
    Case {
        name: "HOT_CI_60000",
        temperature: 60000.0,
        span_s: 2e11,
    },
];

pub fn fixture(t: f64) -> Result<(FullState, NetworkConfig), NetworkError> {
    let mut n = [0.0; 13];
    for (sp, density) in [
        (S::H1Neutral, 1000.0),
        (S::H1Ionized, 900.0),
        (S::DNeutral, 25.0),
        (S::DIonized, 5.0),
        (S::He4Neutral, 300.0),
        (S::He4SinglyIonized, 100.0),
        (S::He4DoublyIonized, 60.0),
    ] {
        n[sp as usize] = density;
    }
    let nuclei = IsotopeNumberState::new(n).map_err(|_| NetworkError::InvalidInput)?;
    let s = FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: 1.5
                * KB_J_K
                * nuclei
                    .thermal_particle_density_all_thermal_m3()
                    .map_err(|_| NetworkError::InvalidInput)?
                * t,
        },
        photon_bins: Vec::new(),
        escaped_j_m3: 0.0,
        cmb_reservoir_j_m3: 0.0,
        elapsed_s: 0.0,
    };
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let d = DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI")
        .map_err(|_| NetworkError::SourceMismatch)?;
    let mut c = NetworkConfig::source_bound(d, "BRPERF01_FIXED_VOLUME_SOURCE_OFF_CONTROL");
    c.use_photo = false;
    c.owner = CxOwnership::ThermalSubstep;
    c.cx_controls.rtol = 1e-10;
    c.cx_controls.atol_normalized = 1e-13;
    s.validate(&c)?;
    Ok((s, c))
}

pub fn error_class(e: NetworkError) -> &'static str {
    match e {
        NetworkError::Cx(CoupleError::WorkLimit) => "CX_WORK_LIMIT",
        NetworkError::Cx(_) => "CX_NUMERICAL_OR_DOMAIN_REFUSAL",
        NetworkError::PhysicsLedger => "PHYSICS_LEDGER_REJECTION",
        NetworkError::NegativePopulation | NetworkError::NegativeEnergy => {
            "NEGATIVE_STATE_REJECTION"
        }
        NetworkError::TemperatureOutsideSource
        | NetworkError::InputOutsideDomain
        | NetworkError::SpeciesOutsideDomain => "SOURCE_DOMAIN_REJECTION",
        NetworkError::SourceMismatch | NetworkError::OwnershipConflict => "SOURCE_OWNER_REJECTION",
        NetworkError::NonFinite => "NONFINITE_ARITHMETIC",
        NetworkError::NoForwardProgress => "NO_FORWARD_PROGRESS",
        NetworkError::InvalidInput => "INVALID_INPUT",
    }
}

pub fn budget_values(b: EventBudget) -> Vec<f64> {
    b.photo_events_m3
        .into_iter()
        .chain(b.ci_events_m3)
        .chain(b.rr_events_m3)
        .chain([
            b.dr_hei_m3,
            b.cx_signed_m3,
            b.photo_energy_j_m3,
            b.thermal_change_j_m3,
            b.chemical_change_j_m3,
            b.escape_change_j_m3,
            b.cmb_change_j_m3,
            b.freefree_integrated_j_m3,
            b.d_electron_integrated_m3,
        ])
        .collect()
}
pub fn rhs_values(r: &GasRhs) -> Vec<f64> {
    r.nuclei_per_s
        .into_iter()
        .chain(budget_values(r.budget_per_s))
        .collect()
}
pub fn state_values(s: &FullState) -> Vec<f64> {
    S::ALL
        .into_iter()
        .map(|sp| s.gas.nuclei.density_m3(sp))
        .chain([
            s.gas.thermal_j_m3,
            s.escaped_j_m3,
            s.cmb_reservoir_j_m3,
            s.elapsed_s,
        ])
        .collect()
}

#[derive(Clone)]
pub struct Snapshot {
    pub state: FullState,
    pub accumulated: EventBudget,
}
pub struct History {
    pub snapshots: Vec<Snapshot>,
    pub failure: Option<NetworkError>,
    pub requested: usize,
}
impl History {
    pub fn accepted(&self) -> usize {
        self.snapshots.len() - 1
    }
    pub fn status(&self) -> &'static str {
        self.failure.map(error_class).unwrap_or("COMPLETE")
    }
}
pub fn history(
    tables: &Tables,
    backend: Backend,
    case: Case,
    steps: usize,
    force_work_limit: bool,
) -> Result<(History, NetworkConfig), NetworkError> {
    if steps == 0 {
        return Err(NetworkError::InvalidInput);
    }
    let (initial, mut config) = fixture(case.temperature)?;
    if force_work_limit {
        config.cx_controls.max_rate_calls = 1;
    }
    let mut snapshots = vec![Snapshot {
        state: initial,
        accumulated: EventBudget::default(),
    }];
    let mut failure = None;
    for _ in 0..steps {
        let previous = snapshots.last().unwrap();
        match tables.step(
            backend,
            &previous.state,
            &config,
            case.span_s / steps as f64,
        ) {
            Ok(result) => snapshots.push(Snapshot {
                state: result.state,
                accumulated: midpoint_gas::add_budget(previous.accumulated, result.budget),
            }),
            Err(error) => {
                failure = Some(error);
                break;
            }
        }
    }
    Ok((
        History {
            snapshots,
            failure,
            requested: steps,
        },
        config,
    ))
}

pub fn history_bits(h: &History) -> Vec<u64> {
    h.snapshots
        .iter()
        .flat_map(|row| {
            state_values(&row.state)
                .into_iter()
                .chain(budget_values(row.accumulated))
                .map(f64::to_bits)
        })
        .collect()
}

pub fn write_history(
    out: &mut impl Write,
    case: Case,
    backend: Backend,
    h: &History,
    c: &NetworkConfig,
) -> io::Result<()> {
    let initial = &h.snapshots[0].state;
    let initial_energy = initial.energy_j_m3(c);
    for (step, row) in h.snapshots.iter().enumerate() {
        let s = &row.state;
        let binding = s.binding_j_m3(c);
        let energy = s.energy_j_m3(c);
        let rel = (energy - initial_energy) / energy.abs().max(initial_energy.abs()).max(1e-50);
        let eos = s
            .gas
            .eos()
            .map_err(|e| io::Error::other(format!("{e:?}")))?;
        write!(
            out,
            "{},{},{},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            case.name,
            backend.name(),
            h.requested,
            step,
            h.status(),
            eos.temperature_k,
            binding,
            energy,
            rel,
            case.span_s
        )?;
        for value in state_values(s)
            .into_iter()
            .chain(budget_values(row.accumulated))
        {
            write!(out, ",{value:.17e}")?;
        }
        writeln!(out)?;
    }
    Ok(())
}

pub const BUDGET_HEADER: &str = "photo_HI,photo_HeI,photo_HeII,photo_DI,ci_HI,ci_HeI,ci_HeII,ci_DI,rr_HII,rr_HeII,rr_HeIII,rr_DII,dr_HeII,cx_signed,photo_energy,thermal_budget,chemical_budget,escape_budget,cmb_budget,freefree_budget,d_electron_budget";
pub const STATE_HEADER: &str = "N_neutron,N_HI,N_HII,N_DI,N_DII,N_TI,N_TII,N_He3I,N_He3II,N_He3III,N_He4I,N_He4II,N_He4III,thermal,escaped,cmb_reservoir,elapsed_s";
pub const RATE_LABELS: [&str; 15] = [
    "CI_HI",
    "CI_HeI",
    "CI_HeII",
    "RR_HII",
    "RR_HeII",
    "RR_HeIII",
    "DR_HeII",
    "CE_HI",
    "CE_HeI",
    "CE_HeII",
    "RRKIN_HII",
    "RRKIN_HeII",
    "RRKIN_HeIII",
    "DRKIN_RAW_HeII",
    "FREEFREE",
];

pub fn perturb_channel(r: &mut IgmRates, channel: usize, multiplier: f64) {
    match channel {
        0..=2 => r.ci_cm3_s[channel] *= multiplier,
        3..=5 => r.rr_cm3_s[channel - 3] *= multiplier,
        6 => r.dr_cm3_s *= multiplier,
        7..=9 => r.ce_erg[channel - 7] *= multiplier,
        10..=12 => r.rr_cooling_erg_cm3_s[channel - 10] *= multiplier,
        13 => {
            r.dr_raw_cooling_erg_cm3_s *= multiplier;
            r.dr_cooling_erg_cm3_s *= multiplier;
        }
        14 => r.freefree_erg_cm3_s *= multiplier,
        _ => panic!("invalid rate channel"),
    }
}
