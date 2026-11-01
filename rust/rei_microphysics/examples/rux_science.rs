//! Explicit-input primary entrypoint. This remains a conditional warm path.
//! Example invocation requires every value; it supplies no physical defaults.
use rei_microphysics::coupled_primary::{primary_stage_step, PrimaryPacket};
use rei_microphysics::rux_adapter::*;
use rei_microphysics::StepControl;

fn number(args: &[String], index: usize) -> Result<f64, String> {
    args.get(index)
        .ok_or_else(|| format!("missing argument {index}"))?
        .parse::<f64>()
        .map_err(|_| format!("invalid number at argument {index}"))
}

fn run() -> Result<(), String> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 16 {
        return Err("usage: rux_science ORIGIN T_S N_H_PROPER_CM3 F_HE H_PER_S X_HII X_HEII X_HEIII W_EV_PER_H ESCAPE_EV_PER_H ENERGY_EV PACKETS_PER_H DT_S MAX_ITER RESIDUAL_TOL; conditional warm initial-stock Case-A path only".into());
    }
    let origin = args[1].clone();
    let input = ScenarioInput {
        clock: ProperClock { origin: origin.clone(), seconds_since_origin: number(&args, 2)? },
        hydrogen_density: HydrogenDensity::ProperCm3(number(&args, 3)?),
        helium_to_hydrogen: number(&args, 4)?,
        mean_hubble_per_s: number(&args, 5)?,
        fractions: [number(&args, 6)?, number(&args, 7)?, number(&args, 8)?],
        thermal_ev_per_h: number(&args, 9)?,
        escape_ev_per_h: number(&args, 10)?,
        packets: vec![PrimaryPacket { energy_ev: number(&args, 11)?, per_h: number(&args, 12)? }],
        source_role: PhotonSourceRole::InitialStock,
        closure: PrimaryClosure::HomogeneousCaseAEscape,
        event_owner: EventOwner::PrimaryStage,
    };
    let dt = number(&args, 13)?;
    let max_iterations = args[14].parse::<usize>().map_err(|_| "invalid max iterations")?;
    let residual_tolerance = number(&args, 15)?;
    let (stage, state) = bind_primary(input).map_err(|e| e.to_string())?;
    let result = primary_stage_step(&stage, &state, dt, StepControl { max_iterations, residual_tolerance })
        .map_err(|e| e.to_string())?;
    println!("scope=CONDITIONAL_WARM_PRIMARY_ONLY origin={origin} t_end_s={} x_hii={} x_heii={} x_heiii={} w_ev_per_h={} escape_ev_per_h={} packet_per_h={} residual={}",
        number(&args, 2)? + dt, result.state.fractions[0], result.state.fractions[1], result.state.fractions[2],
        result.state.w_ev_per_h, result.state.escape_ev_per_h, result.state.packets[0].per_h, result.residual);
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(2);
    }
}
