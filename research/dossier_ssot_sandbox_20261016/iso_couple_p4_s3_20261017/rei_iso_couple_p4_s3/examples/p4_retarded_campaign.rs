//! Bounded P4/S3 source-native H/He/D with original PR150 source+Verner+D
//! providers, prescribed FLRW/Bianchi-I and isolated optical clock/spectrum.
//! Mode and N are command-line; no remote production/Full EoR.
use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
    positive_birth_clock::PositiveBirthClockBridge,
    positive_spectral::SpectralMode,
    retarded_transport::{PositiveRetardedBridge, RetardedControls},
    source_age::SourceAgeBridge,
};
fn initial() -> FullState {
    let mut n = [0.; 13];
    n[S::H1Neutral as usize] = 1000.;
    n[S::H1Ionized as usize] = 900.;
    n[S::He4Neutral as usize] = 300.;
    n[S::He4SinglyIonized as usize] = 100.;
    n[S::He4DoublyIonized as usize] = 60.;
    n[S::DNeutral as usize] = 25.;
    n[S::DIonized as usize] = 5.;
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let thermal = 1.5 * KB_J_K * nuclei.thermal_particle_density_all_thermal_m3().unwrap() * 1e4;
    FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: thermal,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    }
}
fn run(case: &str, steps: usize, mode: &str) {
    let h = 1.2e-16;
    let shear = match case {
        "flrw" => 0.,
        "bi_plus" => 0.06 * h,
        "bi_minus" => -0.06 * h,
        _ => panic!("Unknown case"),
    };
    let source = AxbiSource::new(1900.0 / (21_f64.powi(3) * 1e6), 0.2, 16, 8).unwrap();
    let geometry = ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1. / 21., 0., h, shear).unwrap(),
        [0., 1.5e14],
    )
    .unwrap();
    let owner = SourceAgeBridge::new(source, geometry).unwrap();
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let conf = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    let mut state = owner.initial(initial(), &conf, 0.).unwrap();
    let duration = 8e10;
    let dt = duration / steps as f64;
    let (method, gl, ms, smode) = match mode {
        "p4s2_phi" => (0, 0, 0, SpectralMode::OriginalCellMean),
        "age_gl2_m2" => (1, 2, 2, SpectralMode::OriginalCellMean),
        "age_gl4_m4" => (1, 4, 4, SpectralMode::OriginalCellMean),
        "age_gl4_m8" => (1, 4, 8, SpectralMode::OriginalCellMean),
        "split_gl4_m4" => (1, 4, 4, SpectralMode::SplitPositiveGauss3),
        "split_gl2_m4" => (1, 2, 4, SpectralMode::SplitPositiveGauss3),
        "split_gl4_m8" => (1, 4, 8, SpectralMode::SplitPositiveGauss3),
        _ => panic!("Unknown mode"),
    };
    let mut cumulative = [0.; 4];
    let mut maxe = 0_f64;
    let mut maxphwork_abs = 0_f64;
    let mut maxphwork_rel = 0_f64;
    let mut n_born_last = 0;
    for _ in 0..steps {
        let vm = owner
            .geometry
            .snapshot(state.time_s + dt / 2.)
            .unwrap()
            .volume_factor()
            .unwrap();
        let (step, work, work_ind, newborn) = if method == 0 {
            let result = PositiveBirthClockBridge(owner.clone())
                .advance(&state, &conf, dt)
                .unwrap();
            (result, 0., 0., 384)
        } else {
            let c = RetardedControls::new(gl, ms, smode).unwrap();
            let (result, diag) = PositiveRetardedBridge(owner.clone(), c)
                .advance_with_diagnostics(&state, &conf, dt)
                .unwrap();
            (
                result,
                diag.photon_work_ledger_j_com3,
                diag.photon_work_independent_j_com3,
                diag.newborn_gl_count,
            )
        };
        let geom_delta = (work - work_ind).abs();
        maxphwork_abs = maxphwork_abs.max(geom_delta);
        maxphwork_rel = maxphwork_rel
            .max(geom_delta / step.state.source_injected_energy_j_com3.abs().max(1e-70));
        for (j, x) in step.chemistry_budget.photo_events_m3.iter().enumerate() {
            cumulative[j] += vm * x;
        }
        maxe = maxe.max(step.global_energy_relative_error);
        n_born_last = newborn;
        state = step.state;
    }
    let c = state.cohorts.iter().map(|x| x.n_comoving_m3).sum::<f64>();
    let emission = state.source_injected_count_com3;
    let absorbed = state.photon_absorbed_count_com3;
    let photon_number_residual = (emission - absorbed - c).abs() / emission.max(1e-70);
    let values = [
        state.full.gas.eos().unwrap().temperature_k,
        c,
        emission,
        absorbed,
        photon_number_residual,
        maxe,
        cumulative[0],
        cumulative[1],
        cumulative[2],
        cumulative[3],
        state.full.gas.nuclei.density_m3(S::DNeutral),
        state.full.gas.nuclei.density_m3(S::DIonized),
        maxphwork_abs,
        maxphwork_rel,
        state.cohorts.len() as f64,
        n_born_last as f64,
        dt,
    ];
    print!("{case},{steps},{mode}");
    for v in values {
        print!(",{v:.16e}");
    }
    println!();
}
fn main() {
    let args: Vec<String> = std::env::args().collect();
    println!(
        "case,nsteps,mode,T_final_K,survivors_com_m3,emitted_com_m3,absorbed_com_m3,number_residual,energy_residual,HI_events_com3,HeI_events_com3,HeII_events_com3,DI_events_com3,DNeutral_m3,DIonized_m3,work_discrepancy_abs_J_com3,work_discrepancy_relative,cohorts,newborn_per_step,dt_s"
    );
    if args.len() == 4 {
        run(&args[1], args[2].parse().unwrap(), &args[3]);
    } else {
        for case in ["flrw", "bi_plus"] {
            for n in [4, 8, 16] {
                for mode in [
                    "p4s2_phi",
                    "age_gl2_m2",
                    "age_gl4_m4",
                    "split_gl2_m4",
                    "split_gl4_m8",
                ] {
                    run(case, n, mode);
                }
            }
        }
    }
}
