//! Matched original, represented-exact-zero, and bounded-nonzero photon lane.
//! Source-native original physics; coupled differences are measured, NOT certified.
use rei_iso_couple_reference::{
    HHeModel,
    age_remainder::{BudgetedAgeHistory, TailControls},
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_spectral::SpectralMode,
    retarded_transport::RetardedControls,
    retarded_transport_threshold::PositiveThresholdBridge,
    source_age::SourceAgeBridge,
};
use std::hint::black_box;
use std::time::Instant;
fn initial() -> FullState {
    let mut n = [0.; 13];
    n[S::H1Neutral as usize] = 1000.;
    n[S::H1Ionized as usize] = 900.;
    n[S::He4Neutral as usize] = 300.;
    n[S::He4SinglyIonized as usize] = 100.;
    n[S::He4DoublyIonized as usize] = 60.;
    n[S::DNeutral as usize] = 25.;
    n[S::DIonized as usize] = 5.;
    let ni = IsotopeNumberState::new(n).unwrap();
    FullState {
        gas: MixtureState {
            nuclei: ni,
            thermal_j_m3: 1.5
                * KB_J_K
                * ni.thermal_particle_density_all_thermal_m3().unwrap()
                * 1e4,
        },
        photon_bins: vec![],
        elapsed_s: 0.,
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
    }
}
fn single(mode: &str, scenario: &str, nsteps: usize, repeat: usize) {
    let h = 1.2e-16;
    let shear = 0.06 * h;
    let src = AxbiSource::new(1900. / (21f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    let geo = ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1. / 21., 0., h, shear).unwrap(),
        [0., 1.5e14],
    )
    .unwrap();
    let bridge = PositiveThresholdBridge(
        SourceAgeBridge::new(src, geo).unwrap(),
        RetardedControls::new(2, 4, SpectralMode::OriginalCellMean).unwrap(),
    );
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let mut cfg = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    cfg.use_collisions = false;
    cfg.use_cx = false;
    cfg.use_cmb = false;
    let total = if scenario == "high_opacity" {
        (nsteps as f64) * 1e13
    } else {
        8e10
    };
    let dt = total / (nsteps as f64);
    let mut controls = if scenario == "high_opacity" {
        TailControls {
            max_weight_per_cohort_com3: 1e-11,
            max_cumulative_number_com3: 1e-14,
            max_cumulative_energy_j_com3: 1e-27,
            max_direct_species_events_com3: [f64::MAX; 4],
            horizon_s: 1.5e14,
        }
    } else {
        TailControls {
            max_weight_per_cohort_com3: 1e-13,
            max_cumulative_number_com3: 1e-10,
            max_cumulative_energy_j_com3: 1e-26,
            max_direct_species_events_com3: [f64::MAX; 4],
            horizon_s: 1.5e14,
        }
    };
    if mode == "species_guard" {
        controls.max_direct_species_events_com3 = if scenario == "high_opacity" {
            [1e-10, 1e-11, 1e-12, 1e-11]
        } else {
            [1e-10, 1e-11, 2e-14, 1e-11]
        };
    }
    let original = bridge.initial(initial(), &cfg, 0.).unwrap();
    let mut hstate = if mode == "budget_nonzero" || mode == "species_guard" {
        Some(
            bridge
                .with_tail_budget(original.clone(), &cfg, controls)
                .unwrap(),
        )
    } else {
        None::<BudgetedAgeHistory>
    };
    let mut native = original;
    let mut last_s = 0.;
    let mut last_abs = 0.;
    let mut last_temp = 0.;
    let mut peak = 0usize;
    let mut max_resid = 0f64;
    let mut last_step_s = 0.;
    let mut max_photon_energy_bound = 0.;
    let mut new_removed_nonzero = 0usize;
    let mut removed_mass = 0.;
    let mut retained_count = 0usize;
    let mut species = [0f64; 4];
    let start = Instant::now();
    for _ in 0..nsteps {
        let t_before = if let Some(h) = hstate.as_ref() {
            h.history().time_s
        } else {
            native.time_s
        };
        let vmid = bridge
            .0
            .geometry
            .snapshot(t_before + dt / 2.)
            .unwrap()
            .volume_factor()
            .unwrap();
        let start_one = Instant::now();
        let budgeted = if let Some(h) = hstate.as_ref() {
            let step = bridge.advance_budgeted(h, &cfg, dt).unwrap();
            for (i, x) in step
                .physics
                .chemistry_budget
                .photo_events_m3
                .iter()
                .enumerate()
            {
                species[i] += *x * vmid;
            }
            max_resid = max_resid.max(step.photon_inventory_relative_residual);
            new_removed_nonzero += step.new_removed_nonzero;
            removed_mass = step.state.remainder().cumulative_removed_number_com3;
            max_photon_energy_bound = step
                .state
                .remainder()
                .cumulative_future_photo_energy_bound_j_com3;
            let now = step.state.clone();
            hstate = Some(now);
            true
        } else {
            false
        };
        if !budgeted {
            let (step, _) = if mode == "exact_zero" {
                bridge
                    .advance_compact_exact_zeros(&native, &cfg, dt)
                    .unwrap()
            } else {
                bridge.advance_with_diagnostics(&native, &cfg, dt).unwrap()
            };
            for (i, x) in step.chemistry_budget.photo_events_m3.iter().enumerate() {
                species[i] += *x * vmid;
            }
            native = black_box(step.state);
        }
        last_step_s = start_one.elapsed().as_secs_f64();
        let s = if let Some(h) = hstate.as_ref() {
            h.history()
        } else {
            &native
        };
        retained_count = s.cohorts.len();
        peak = peak.max(retained_count);
        last_s = s.cohorts.iter().map(|co| co.n_comoving_m3).sum::<f64>();
        last_abs = s.photon_absorbed_count_com3;
        last_temp = s.full.gas.eos().unwrap().temperature_k;
    }
    let total_s = start.elapsed().as_secs_f64();
    println!(
        "{scenario},{nsteps},{repeat},{mode},{total_s:.12e},{last_step_s:.12e},{last_s:.12e},{last_abs:.12e},{last_temp:.12e},{retained_count},{peak},{removed_mass:.12e},{max_photon_energy_bound:.12e},{new_removed_nonzero},{max_resid:.12e},{:.12e},{:.12e},{:.12e},{:.12e}",
        species[0], species[1], species[2], species[3]
    );
}
fn main() {
    println!(
        "scenario,nsteps,repeat,mode,total_wall_s,last_step_s,photons_com3,absorbed_com3,temp_K,retained,peak,removed_com3,energy_error_envelope_J,removed_nonzero,number_inventory_residual,HI_com3,HeI_com3,HeII_com3,DI_com3"
    );
    for (scenario, nsteps) in [
        ("high_opacity", 12),
        ("low_opacity", 8),
        ("low_opacity", 16),
    ] {
        for rep in 0..3 {
            let modes = if rep % 2 == 0 {
                [
                    "retain_all",
                    "exact_zero",
                    "budget_nonzero",
                    "species_guard",
                ]
            } else {
                [
                    "species_guard",
                    "budget_nonzero",
                    "exact_zero",
                    "retain_all",
                ]
            };
            for m in modes {
                single(m, scenario, nsteps, rep)
            }
        }
    }
}
