//! Bounded source-on controls, retaining the original source, spectrum and EOS.
//! CLI: output.csv Xend max_N cells [nonlinear_tolerance]
use rei_microphysics::{
    axbi_covariant_transport::PhotonAttenuation,
    axbi_driver::{Driver, DriverConfig, NativeClockMode, SourceClockConfig, SourcePlacement},
    igm_state::IgmGasState,
    HHeModel,
};
use std::{
    fs::File,
    io::{BufWriter, Write},
    time::Instant,
};

fn controls(name: &str, tolerance: f64) -> SourceClockConfig {
    let mut c = SourceClockConfig {
        microphysics: NativeClockMode::OwnerBe,
        opacity_midpoint: false,
        attenuation: PhotonAttenuation::BackwardEuler,
        source: SourcePlacement::Before,
        nonlinear_tolerance: tolerance,
    };
    match name {
        "be_control" => (),
        "gas_mid" => c.microphysics = NativeClockMode::AllMid,
        "gas_opacity_mid" => {
            c.microphysics = NativeClockMode::AllMid;
            c.opacity_midpoint = true;
        }
        "gas_opacity_exp" => {
            c.microphysics = NativeClockMode::AllMid;
            c.opacity_midpoint = true;
            c.attenuation = PhotonAttenuation::Exponential;
        }
        "symmetric_be" => {
            c.microphysics = NativeClockMode::AllMid;
            c.opacity_midpoint = true;
            c.source = SourcePlacement::SymmetricHalves;
        }
        "combined" => {
            c.microphysics = NativeClockMode::AllMid;
            c.opacity_midpoint = true;
            c.attenuation = PhotonAttenuation::Exponential;
            c.source = SourcePlacement::SymmetricHalves;
        }
        "source_off" => {
            c.microphysics = NativeClockMode::AllMid;
            c.opacity_midpoint = true;
            c.attenuation = PhotonAttenuation::Exponential;
            c.source = SourcePlacement::Disabled;
        }
        _ => panic!("unknown fixed internal mode"),
    }
    c
}
fn main() -> Result<(), String> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 5 || args.len() > 6 {
        return Err("usage: output.csv Xend max_N cells [nonlinear_tolerance]".into());
    }
    let xend: f64 = args[2].parse().map_err(|_| "invalid Xend")?;
    let max_n: usize = args[3].parse().map_err(|_| "invalid max_N")?;
    let cells: usize = args[4].parse().map_err(|_| "invalid cells")?;
    let tolerance: f64 = if args.len() == 6 {
        args[5].parse().map_err(|_| "invalid tolerance")?
    } else {
        1e-13
    };
    if !(xend > 0. && xend <= 0.002 && max_n >= 8 && max_n <= 2048 && max_n.is_power_of_two()) {
        return Err("bounded run domain".into());
    }
    let shard_case = std::env::var("LRS_SHARD_CASE").map_err(|_| "mandatory LRS_SHARD_CASE")?;
    let shard_mode = std::env::var("LRS_SHARD_MODE").map_err(|_| "mandatory LRS_SHARD_MODE")?;
    let shard_n: usize = std::env::var("LRS_SHARD_N").map_err(|_| "mandatory LRS_SHARD_N")?.parse().map_err(|_| "invalid LRS_SHARD_N")?;
    if !["1e-5","1e-4"].contains(&shard_case.as_str()) || shard_case.parse::<f64>().map_err(|_| "invalid shard Xend")? != xend || !["be_control","gas_mid","gas_opacity_mid","gas_opacity_exp","symmetric_be","combined","source_off"].contains(&shard_mode.as_str()) || ![8usize,16,32,64,128,256].contains(&shard_n) || shard_n > max_n { return Err("invalid mandatory shard selector".into()); }
    let mut w = BufWriter::new(File::create(&args[1]).map_err(|e| e.to_string())?);
    writeln!(w,"mode,cells,N,step,X,Xend,T_K,HII,HeII,HeIII,electrons_per_H,photons_per_H,source_N,source_U,photo_HI,photo_HeI,photo_HeII,photo_binding_eV_H,photo_heat_eV_H,CE_eV_H,RRDR_eV_H,FF_eV_H,CMB_eV_H,thermal_work_eV_H,photon_work_eV_H,boundary_U_eV_H,energy_residual_eV_H,photon_residual_H,max_newton_residual,rhs_calls,wall_s") .map_err(|e|e.to_string())?;
    let constants = HHeModel::controlled_fixture();
    for name in [
        "be_control",
        "gas_mid",
        "gas_opacity_mid",
        "gas_opacity_exp",
        "symmetric_be",
        "combined",
        "source_off",
    ] {
        let mut n = 8;
        while n <= max_n {
            if name != shard_mode || n != shard_n { n *= 2; continue; }
            let mut config = DriverConfig::baseline();
            config.transport_cells = cells;
            config.transport_threads = 1;
            config.background_panels = 128;
            config.parallel_jacobian_columns = false;
            let (mut driver, mut state) = Driver::new(config).map_err(|e| format!("init {e:?}"))?;
            let nh = driver.n_h0_cm3 / state.a.powi(3);
            let nhe = driver.n_he0_cm3 / state.a.powi(3);
            state.gas = IgmGasState::from_temperature([0.075, 0.12, 0.03], nh, nhe, 15000.)
                .map_err(|e| format!("gas {e:?}"))?;
            driver
                .set_source_clocks(&state, controls(name, tolerance))
                .map_err(|e| format!("clock {e:?}"))?;
            let initial_a = state.a;
            let start = Instant::now();
            let dx = xend / n as f64;
            let (mut photo_binding, mut photo_heat, mut ce, mut rrc, mut ff) = (0., 0., 0., 0., 0.);
            for step in 1..=n {
                let aold = state.a;
                let amid = aold * (0.5 * dx).exp();
                let nhmid = driver.n_h0_cm3 / amid.powi(3);
                let dt = dx
                    / driver
                        .geometry_point(amid)
                        .map_err(|e| format!("geometry {e:?}"))?
                        .h_flrw_per_s;
                driver
                    .fixed_step(&mut state, dx)
                    .map_err(|e| format!("mode={name} N={n} step={step}: {e:?}"))?;
                let rhs = driver
                    .last_clock_rhs()
                    .map_err(|e| format!("rhs {e:?}"))?
                    .ok_or("missing diagnostic")?;
                let scale = dt / (nhmid * constants.ev_erg);
                let events = rhs.photo_events_cm3_s.map(|x| x * dt / nhmid);
                let bind = (0..3)
                    .map(|i| constants.threshold_ev[i] * events[i])
                    .sum::<f64>();
                photo_binding += bind;
                photo_heat += rhs.photo_input_erg_cm3_s * scale - bind;
                ce += rhs.ce_thermal_sink_erg_cm3_s.iter().sum::<f64>() * scale;
                rrc += (rhs.rr_thermal_sink_erg_cm3_s.iter().sum::<f64>()
                    + rhs.dr_thermal_sink_erg_cm3_s)
                    * scale;
                ff += rhs.freefree_thermal_sink_erg_cm3_s * scale;
                let nh = driver.n_h0_cm3 / state.a.powi(3);
                let nhe = driver.n_he0_cm3 / state.a.powi(3);
                let eos = state.gas.eos(nh, nhe).map_err(|e| format!("eos {e:?}"))?;
                let (nr, er) = driver
                    .residuals(&state)
                    .map_err(|e| format!("ledger {e:?}"))?;
                let values = [
                    (state.a / initial_a).ln(),
                    xend,
                    eos.temperature_k,
                    state.gas.fractions[0],
                    state.gas.fractions[1],
                    state.gas.fractions[2],
                    eos.electron_density_cm3 / nh,
                    state
                        .photons
                        .iter()
                        .chain(state.photon_inactive_number.iter())
                        .sum(),
                    state.ledgers.source_n,
                    state.ledgers.source_u,
                    state.ledgers.photo_events[0],
                    state.ledgers.photo_events[1],
                    state.ledgers.photo_events[2],
                    photo_binding,
                    photo_heat,
                    ce,
                    rrc,
                    ff,
                    state.ledgers.cmb_input,
                    state.ledgers.thermal_work,
                    state.ledgers.photon_work,
                    state.ledgers.boundary_u,
                    er,
                    nr,
                    state.max_newton_residual,
                    state.rhs_evaluations as f64,
                    start.elapsed().as_secs_f64(),
                ];
                if !values.iter().all(|v| v.is_finite()) {
                    return Err("nonfinite diagnostic".into());
                }
                write!(w, "{name},{cells},{n},{step}").map_err(|e| e.to_string())?;
                for v in values {
                    write!(w, ",{v:.17e}").map_err(|e| e.to_string())?;
                }
                writeln!(w).map_err(|e| e.to_string())?;
            }
            w.flush().map_err(|e| e.to_string())?;
            eprintln!(
                "COMPLETE mode={name} N={n} cells={cells} Xend={xend} wall={:.4}",
                start.elapsed().as_secs_f64()
            );
            n *= 2;
        }
    }
    Ok(())
}
