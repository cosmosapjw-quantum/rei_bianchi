//! E13A additive accepted-stage input witness on the exact E12 shadow source.
//! This is source-aligned re-evaluation, NOT independent stage RHS certification.
//! The 41-column owner readout is unchanged; the RCT sidecar is separate.
use rei_microphysics::{
    he_rct::{EscapingMeanPhotonEnergy, RctProvider, RctScenario, RctSelection, RctSource},
    igm_config::{parse_config, HistoryConfig},
};
use short_hhe_control::{coupled, material, output, radiation};
use std::{
    fs::{self, File, OpenOptions},
    io::Write,
    path::Path,
};
fn clock(c: &HistoryConfig, k: usize) -> Result<f64, String> {
    if k > 384 {
        return Err("N384_INDEX_OUT_OF_RANGE".into());
    }
    let s = c.start + c.max_dln_a * (k as f64 / 16.0) / 24.0;
    if !s.is_finite() {
        return Err("NONFINITE_CLOCK".into());
    }
    Ok(s)
}
fn selection(mode: &str) -> Result<RctSelection, String> {
    if mode == "OFF" {
        return Ok(RctSelection::Disabled);
    }
    let src = match mode {
        "KF" => RctSource::Kf96Nominal,
        "GM" => RctSource::Gm25Constant,
        _ => return Err("UNDECLARED_RCT_MODE".into()),
    };
    Ok(RctSelection::Escaping {
        provider: RctProvider::new(
            src,
            RctScenario::W82GroundStateCommonTemperatureZeroDrift,
            true,
        )
        .map_err(|e| format!("{e:?}"))?,
        closure: EscapingMeanPhotonEnergy::research_input_ev(35.).map_err(|e| format!("{e:?}"))?,
    })
}
fn checked_file(dir: &Path, name: &str) -> Result<File, String> {
    OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(dir.join(name))
        .map_err(|e| e.to_string())
}
fn sync(f: &mut File) -> Result<(), String> {
    f.flush().map_err(|e| e.to_string())?;
    f.sync_all().map_err(|e| e.to_string())
}

// Exact-stage INPUT WITNESS for the accepted step, not a second physics evaluator.
// This intentionally re-evaluates the same source and *cannot* count as
// algorithmically independent stage RHS or photon-characteristic certification.
const E13_HEADER:&str="step,mode,s0,s1,sm,dt,nH,nHe,H,Tcmb,fHe,mid_T,mid_ne,old_x,old_y,old_z,old_w,new_x,new_y,new_z,new_w,mid_x,mid_y,mid_z,mid_w,A_HI,A_HeI,A_HeII,B_HI,B_HeI,B_HeII,rhs_fx,rhs_fy,rhs_fz,rhs_w_dt,photo_delta_x,photo_delta_y,photo_delta_z,photo_delta_w,reeval_res_x,reeval_res_y,reeval_res_z,reeval_res_w,rct_events,rct_heat,rct_chemical,rct_escape,native_norm,reeval_norm";
fn stage_witness(
    sink: &mut File,
    cfg: &HistoryConfig,
    grid: &radiation::Grid,
    old: &coupled::State,
    accepted: &coupled::State,
    k: usize,
    mode: &str,
) -> Result<(), String> {
    if !["OFF", "KF", "GM"].contains(&mode) {
        return Err("STAGE_MODE_NOT_DECLARED".into());
    }
    if !(k == 1 || k == 2) {
        return Err("E13_PILOT_STEP_ONLY".into());
    }
    let before_old = old.clone();
    let before_accept = accepted.clone();
    let sm = (old.s + accepted.s) * 0.5;
    let pm = cfg.background.at_ln_a(sm).map_err(|e| format!("{e:?}"))?;
    let p1 = cfg
        .background
        .at_ln_a(accepted.s)
        .map_err(|e| format!("{e:?}"))?;
    let ym: [f64; 4] = std::array::from_fn(|j| (old.y[j] + accepted.y[j]) * 0.5);
    let response = material::rhs_selected(ym, pm, accepted.rct_selection())?;
    let eos = material::gas(ym)?
        .eos(pm.n_h_cm3, pm.n_he_cm3)
        .map_err(|e| format!("{e:?}"))?;
    let eval = coupled::evaluate(cfg, grid, old, accepted.s, p1, accepted.y)?;
    if before_old != *old || before_accept != *accepted {
        return Err("STAGE_PROBE_MUTATED_GAS_OR_OWNER".into());
    }
    // E13A scientific rows are source inputs, never certified outputs.
    let dt = (accepted.s - old.s) / pm.hubble_per_s;
    let f_he = p1.n_he_cm3 / p1.n_h_cm3;
    let pdelta = material::photo_delta(eval.radiation.owners.an, eval.radiation.owners.be, f_he);
    let mut numbers: Vec<f64> = vec![
        old.s,
        accepted.s,
        sm,
        dt,
        pm.n_h_cm3,
        pm.n_he_cm3,
        pm.hubble_per_s,
        pm.tcmb_k,
        f_he,
        eos.temperature_k,
        eos.electron_density_cm3,
    ];
    numbers.extend(old.y);
    numbers.extend(accepted.y);
    numbers.extend(ym);
    numbers.extend(eval.radiation.owners.an);
    numbers.extend(eval.radiation.owners.be);
    numbers.extend(response.combined.fraction_dt);
    numbers.push(response.combined.w_dt_erg_per_h_s);
    numbers.extend(pdelta);
    numbers.extend(eval.r);
    numbers.extend([
        eval.rct.events,
        eval.rct.heat,
        eval.rct.chemical,
        eval.rct.escape,
    ]);
    numbers.push(accepted.norm);
    numbers.push(coupled::norm(eval.r));
    if numbers.len() != E13_HEADER.split(',').count() - 2 {
        return Err("STAGE_INPUT_HEADER_COUNT".into());
    }
    if numbers.iter().any(|x| !x.is_finite()) {
        return Err("STAGE_INPUT_NONFINITE".into());
    }
    let mut line = format!("{k},{mode}");
    for number in numbers {
        line.push_str(&format!(",{number:.17e}"));
    }
    writeln!(sink, "{line}").map_err(|e| e.to_string())?;
    sync(sink)?;
    Ok(())
}
fn run() -> Result<(), String> {
    let args = std::env::args().collect::<Vec<_>>();
    if args.len() != 5 {
        return Err("USAGE: e13_stage_inputs CONFIG OFF|KF|GM NEW_DIR 2".into());
    }
    let mode = args[2].as_str();
    let sel = selection(mode)?;
    let count: usize = args[4]
        .parse()
        .map_err(|_| "UNSUPPORTED_STEP_LIMIT".to_string())?;
    if count != 2 {
        return Err("E13_TWO_STEP_PILOT_ONLY".into());
    }
    let cfg = parse_config(&fs::read_to_string(&args[1]).map_err(|e| e.to_string())?)
        .map_err(|e| format!("{e:?}"))?;
    let output_dir = Path::new(&args[3]);
    fs::create_dir(output_dir).map_err(|e| format!("NEW_OUTPUT_DIRECTORY_REQUIRED: {e}"))?;
    let grid = radiation::Grid::new(&cfg, 512, 4)?;
    if grid.nodes.len() > 4096 {
        return Err("ACTIVE_GRID_LIMIT".into());
    }
    let mut state = if mode == "OFF" {
        coupled::State::new(&cfg, &grid)?
    } else {
        coupled::State::with_rct(&cfg, &grid, sel)?
    };
    let p0 = cfg
        .background
        .at_ln_a(cfg.start)
        .map_err(|e| format!("{e:?}"))?;
    let initial = state.y[3] + material::binding(state.y, p0.n_he_cm3 / p0.n_h_cm3);
    let mut original = checked_file(output_dir, "OWNER_NATIVE_41.csv")?;
    let mut side = checked_file(output_dir, "OWNER_SELECTED_RCT.csv")?;
    let mut trace = checked_file(output_dir, "STEPS.csv")?;
    let mut internal = checked_file(output_dir, "OWNER_INTERNAL_5.csv")?;
    let mut stages = checked_file(output_dir, "OWNER_ACCEPTED_STAGES.csv")?;
    let mut stage_input = checked_file(output_dir, "OWNER_STAGE_INPUTS.csv")?;
    writeln!(original, "{}", output::HEADER).map_err(|e| e.to_string())?;
    writeln!(side, "step,s,x,y,z,w,RCT,RCT_heat,RCT_chem,RCT_escape").map_err(|e| e.to_string())?;
    writeln!(trace, "step,iterations,norm,Nratio,Eratio").map_err(|e| e.to_string())?;
    writeln!(internal, "step,s,BH,BY,BZ,bindMicro,thermalMicro").map_err(|e| e.to_string())?;
    writeln!(
        stages,
        "step,stage,count,min,max,any,all,continuity_checks,continuity_max_relative"
    )
    .map_err(|e| e.to_string())?;
    writeln!(stage_input, "{E13_HEADER}").map_err(|e| e.to_string())?;
    for k in 0..=count {
        let prior = if k > 0 { Some(state.clone()) } else { None };
        if k > 0 {
            state = coupled::advance(&cfg, &grid, &state, clock(&cfg, k)?, initial)?;
            if !(state.norm <= 1. && state.n_ratio <= 1. && state.e_ratio <= 1.) {
                return Err(format!("NATIVE_ACCEPTANCE_GATE_STEP_{k}"));
            }
        }
        if let Some(ref old) = prior {
            stage_witness(&mut stage_input, &cfg, &grid, old, &state, k, mode)?;
        }
        let before = state.clone();
        let row = output::row(&cfg, &grid, &state, initial)?;
        if state != before {
            return Err("OWNER_READOUT_MUTATED_STATE".into());
        }
        if row.len() != 41 {
            return Err("OWNER_41_SCHEMA_CHANGE".into());
        }
        output::write_row(&mut original, &row)?;
        writeln!(
            side,
            "{k},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            state.s,
            state.y[0],
            state.y[1],
            state.y[2],
            state.y[3],
            state.rct.events,
            state.rct.heat,
            state.rct.chemical,
            state.rct.escape
        )
        .map_err(|e| e.to_string())?;
        writeln!(
            trace,
            "{k},{},{:.17e},{:.17e},{:.17e}",
            state.iterations, state.norm, state.n_ratio, state.e_ratio
        )
        .map_err(|e| e.to_string())?;
        writeln!(
            internal,
            "{k},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            state.s,
            state.radiation.be[0],
            state.radiation.be[1],
            state.radiation.be[2],
            state.material.nonphoto_binding,
            state.material.nonphoto_thermal
        )
        .map_err(|e| e.to_string())?;
        for (j, t) in state.accepted_trace.stages.iter().enumerate() {
            writeln!(
                stages,
                "{k},{j},{},{:.17e},{:.17e},{},{},{},{:.17e}",
                t.count,
                t.min,
                t.max,
                t.any,
                t.all,
                state.accepted_trace.continuity_checks,
                state.accepted_trace.continuity_max_relative
            )
            .map_err(|e| e.to_string())?;
        }
        for f in [
            &mut original,
            &mut side,
            &mut trace,
            &mut internal,
            &mut stages,
        ] {
            sync(f)?
        }
        eprintln!(
            "E10_ACCEPTED mode={mode} N=384 k={k} nodes={} norm={:.9e} nr={:.9e} er={:.9e}",
            grid.nodes.len(),
            state.norm,
            state.n_ratio,
            state.e_ratio
        );
    }
    let mut ready = checked_file(output_dir, "READY.json")?;
    writeln!(ready,"{{\"task\":\"E13_STAGE_INPUT_PILOT\",\"mode\":\"{mode}\",\"N\":384,\"steps\":{count},\"rows\":{},\"owner_remote_adopted\":false,\"checkpoint_resumable\":false,\"RCT_mean_energy_eV\":{},\"photo_heating_true_moment\":null,\"physical_admission\":false,\"telemetry\":\"OWNER_INTERNAL_5.csv\",\"accepted_stage_diagnostic\":\"OWNER_ACCEPTED_STAGES.csv\",\"stage_inputs\":\"OWNER_STAGE_INPUTS.csv\",\"independent_stage_certificate\":false}}",count+1,if mode=="OFF"{"null"}else{"35.0"}).map_err(|e|e.to_string())?;
    sync(&mut ready)?;
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("E10_NATIVE_SHADOW_FAIL: {e}");
        std::process::exit(2)
    }
}
