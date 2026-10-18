use rei_microphysics::{
    axbi_driver::{Driver, DriverConfig, NativeClockMode},
    igm_state::{w_erg_per_h_to_ev, IgmGasState},
    HHeModel,
};
use std::{
    fs::File,
    io::{BufWriter, Write},
    path::PathBuf,
    time::Instant,
};

const A0: f64 = 1.0 / 21.0;
const FRACTIONS: [f64; 3] = [0.075, 0.12, 0.03];
const TEMPERATURE_K: f64 = 15_000.0;
const N_STEPS: [usize; 6] = [8, 16, 32, 64, 128, 256];
const CASES: [(&str, f64, f64); 3] = [
    ("D1_X1E5", 1.0e-5, 1.0),
    ("D1_X1E4", 1.0e-4, 1.0),
    ("D5_X1E5", 1.0e-5, 5.0),
];
const MODES: [NativeClockMode; 8] = [
    NativeClockMode::OwnerBe,
    NativeClockMode::CiMid,
    NativeClockMode::CeMid,
    NativeClockMode::FfMid,
    NativeClockMode::CmbMid,
    NativeClockMode::ThermalMid,
    NativeClockMode::ChemicalMid,
    NativeClockMode::AllMid,
];

fn initial_driver(
    density_factor: f64,
    mode: NativeClockMode,
) -> Result<(Driver, rei_microphysics::axbi_driver::DriverState), String> {
    let mut config = DriverConfig::baseline();
    config.q_ref = 0.0;
    config.same_h = false;
    config.initial_x_hii = FRACTIONS[0];
    config.initial_temperature_k = TEMPERATURE_K;
    config.transport_cells = 8;
    config.transport_threads = 1;
    config.parallel_jacobian_columns = false;
    let (mut driver, mut state) = Driver::new(config).map_err(|e| format!("{e:?}"))?;
    driver.n_h0_cm3 *= density_factor;
    driver.n_he0_cm3 *= density_factor;
    let nh = driver.n_h0_cm3 / state.a.powi(3);
    let nhe = driver.n_he0_cm3 / state.a.powi(3);
    state.gas = IgmGasState::from_temperature(FRACTIONS, nh, nhe, TEMPERATURE_K)
        .map_err(|e| format!("{e:?}"))?;
    driver
        .set_source_free_clock(&state, mode)
        .map_err(|e| format!("{e:?}"))?;
    Ok((driver, state))
}

fn main() -> Result<(), String> {
    let output = std::env::args_os()
        .nth(1)
        .map(PathBuf::from)
        .ok_or("usage: v12_thermal_clock_sweep OUTPUT.csv")?;
    let mut w = BufWriter::new(File::create(&output).map_err(|e| e.to_string())?);
    writeln!(w, "case,mode,n,step,x,a,dt_s,H_per_s,nH_proper_cm3,nHe_proper_cm3,ne_proper_cm3,electrons_per_H,T_K,HI_per_H,HII_per_H,HeI_per_H,HeII_per_H,HeIII_per_H,CI_HI_events_per_H,CI_HeI_events_per_H,CI_HeII_events_per_H,CI_HI_binding_eV_per_H,CI_HeI_binding_eV_per_H,CI_HeII_binding_eV_per_H,RR_HII_events_per_H,RR_HeII_events_per_H,RR_HeIII_events_per_H,DR_HeII_events_per_H,RR_HII_cooling_eV_per_H,RR_HeII_cooling_eV_per_H,RR_HeIII_cooling_eV_per_H,DR_HeII_cooling_eV_per_H,RRDR_binding_escape_eV_per_H,CE_HI_cooling_eV_per_H,CE_HeI_cooling_eV_per_H,CE_HeII_cooling_eV_per_H,freefree_cooling_eV_per_H,CMB_signed_gas_input_eV_per_H,gas_adiabatic_work_eV_per_H_step,source_photons_per_H,source_energy_eV_per_H,photon_count_residual_per_H,total_energy_residual_eV_per_H,newton_residual,rhs_evaluations,elapsed_wall_s")
        .map_err(|e| e.to_string())?;
    let constants = HHeModel::controlled_fixture();
    for (case, x_end, density_factor) in CASES {
        for mode in MODES {
            for n in N_STEPS {
                let (driver, mut state) = initial_driver(density_factor, mode)?;
                let run_started = Instant::now();
                let dx = x_end / n as f64;
                for step in 1..=n {
                    let old = state.clone();
                    let to = old.a * dx.exp();
                    let amid = (old.a * to).sqrt();
                    let h_mid = driver
                        .geometry_point(amid)
                        .map_err(|e| format!("{e:?}"))?
                        .h_flrw_per_s;
                    let dt = dx / h_mid;
                    driver.fixed_step(&mut state, dx).map_err(|e| {
                        format!(
                            "case={case} mode={} N={n} step={step}: {e:?}",
                            mode.as_str()
                        )
                    })?;
                    driver
                        .validate(&state, 1e-8)
                        .map_err(|e| format!("{e:?}"))?;
                    let rhs = driver
                        .last_clock_rhs()
                        .map_err(|e| format!("{e:?}"))?
                        .ok_or("missing source-free RHS diagnostic")?;
                    let nh = driver.n_h0_cm3 / amid.powi(3);
                    let nhe = driver.n_he0_cm3 / amid.powi(3);
                    let eos = state
                        .gas
                        .eos(
                            driver.n_h0_cm3 / state.a.powi(3),
                            driver.n_he0_cm3 / state.a.powi(3),
                        )
                        .map_err(|e| format!("{e:?}"))?;
                    let ev_nh = nh * constants.ev_erg;
                    let ci_events = rhs.ci_events_cm3_s.map(|v| v * dt / nh);
                    let ci_binding = rhs.ci_thermal_sink_erg_cm3_s.map(|v| v * dt / ev_nh);
                    let rr_events = rhs.rr_events_cm3_s.map(|v| v * dt / nh);
                    let rr_cooling = rhs.rr_thermal_sink_erg_cm3_s.map(|v| v * dt / ev_nh);
                    let ce_cooling = rhs.ce_thermal_sink_erg_cm3_s.map(|v| v * dt / ev_nh);
                    let dr_events = rhs.dr_events_cm3_s * dt / nh;
                    let dr_cooling = rhs.dr_thermal_sink_erg_cm3_s * dt / ev_nh;
                    let threshold = constants.threshold_ev;
                    let rrdr_binding_escape = threshold[0] * rr_events[0]
                        + threshold[1] * rr_events[1]
                        + threshold[2] * rr_events[2]
                        + threshold[1] * dr_events;
                    let rrdr_binding_escape =
                        rrdr_binding_escape + rr_cooling.iter().sum::<f64>() + dr_cooling;
                    let ff_cooling = rhs.freefree_thermal_sink_erg_cm3_s * dt / ev_nh;
                    let cmb = rhs.cmb_to_gas_erg_cm3_s * dt / ev_nh;
                    let (photon_residual, energy_residual) =
                        driver.residuals(&state).map_err(|e| format!("{e:?}"))?;
                    let work = state.ledgers.thermal_work - old.ledgers.thermal_work;
                    let y = driver.n_he0_cm3 / driver.n_h0_cm3;
                    let electrons_per_h = state.gas.fractions[0]
                        + y * (state.gas.fractions[1] + 2.0 * state.gas.fractions[2]);
                    let _thermal_w_ev =
                        w_erg_per_h_to_ev(state.gas.w_erg_per_h).map_err(|e| format!("{e:?}"))?;
                    write!(w, "{case},{},{n},{step}", mode.as_str()).map_err(|e| e.to_string())?;
                    for value in [
                        (state.a / A0).ln(),
                        state.a,
                        dt,
                        h_mid,
                        nh,
                        nhe,
                        eos.electron_density_cm3,
                        electrons_per_h,
                        eos.temperature_k,
                        1.0 - state.gas.fractions[0],
                        state.gas.fractions[0],
                        y * (1.0 - state.gas.fractions[1] - state.gas.fractions[2]),
                        y * state.gas.fractions[1],
                        y * state.gas.fractions[2],
                        ci_events[0],
                        ci_events[1],
                        ci_events[2],
                        ci_binding[0],
                        ci_binding[1],
                        ci_binding[2],
                        rr_events[0],
                        rr_events[1],
                        rr_events[2],
                        dr_events,
                        rr_cooling[0],
                        rr_cooling[1],
                        rr_cooling[2],
                        dr_cooling,
                        rrdr_binding_escape,
                        ce_cooling[0],
                        ce_cooling[1],
                        ce_cooling[2],
                        ff_cooling,
                        cmb,
                        work,
                        state.ledgers.source_n,
                        state.ledgers.source_u,
                        photon_residual,
                        energy_residual,
                        state.max_newton_residual,
                        state.rhs_evaluations as f64,
                        run_started.elapsed().as_secs_f64(),
                    ] {
                        write!(w, ",{value:.17e}").map_err(|e| e.to_string())?;
                    }
                    writeln!(w).map_err(|e| e.to_string())?;
                }
                w.flush().map_err(|e| e.to_string())?;
            }
        }
    }
    Ok(())
}
