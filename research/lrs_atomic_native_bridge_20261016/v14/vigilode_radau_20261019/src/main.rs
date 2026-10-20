use rei_microphysics::axbi_driver::PhysicalBirthRule;
use rei_vigilode_radau_research::{
    Budget, NativeEval, Events, R, birth_step, chemical_step, initial, state_json,
};
use serde_json::json;
use std::{fs::File, io::Write, time::Instant};
fn main() -> R<()> {
    let args = std::env::args().collect::<Vec<_>>();
    if args.len() < 5 {
        return Err("usage: output.json fixed|birth|disabled radau|ssprk N".into());
    }
    let n = args[4].parse::<usize>().map_err(|e| e.to_string())?;
    if n == 0 {
        return Err("N must be positive".into());
    }
    let mode = args[2].as_str();
    let method = args[3].as_str();
    if !["fixed", "birth", "disabled"].contains(&mode) || !["radau", "ssprk"].contains(&method) {
        return Err("mode/method".into());
    }
    let mut native_eval = NativeEval::Legacy;
    let mut profile = false;
    let mut option = 5;
    while option < args.len() {
        match args[option].as_str() {
            "--profile" => {profile=true;option+=1;},
            "--native-eval" if option+1<args.len() => {native_eval=match args[option+1].as_str(){"legacy"=>NativeEval::Legacy,"cell-cache"=>NativeEval::CellCache,"cell-borrowed"=>NativeEval::CellBorrowed,_=>return Err("invalid native-eval".into())};option+=2;},
            _=>return Err("unknown option".into()),
        }
    }
    let clock = Instant::now();
    let (d, mut s, kref) = initial(mode != "birth")?;
    let start_a = s.a;
    let before = state_json(&d, &s)?;
    let budget = Budget::with_options(200000, 30., native_eval, profile);
    let mut records = vec![];
    let mut ssprk_counter = 0;
    let mut failed = None;
    for step in 1..=n {
        eprintln!(
            "START mode={mode} method={method} N={n} step={step} rhs={} wall={:.6}",
            budget.calls(),
            clock.elapsed().as_secs_f64()
        );
        let result: R<serde_json::Value> = if method == "radau" {
            if mode == "fixed" {
                chemical_step(&d, &mut s, 1. / (kref * n as f64), 1e-13, budget.clone())
                    .and_then(|r| serde_json::to_value(r).map_err(|e| e.to_string()))
            } else {
                let to = start_a * (step as f64 * 1e-6 / n as f64).exp();
                birth_step(
                    &d,
                    &mut s,
                    to,
                    if mode == "birth" {
                        PhysicalBirthRule::Gauss2
                    } else {
                        PhysicalBirthRule::DisabledGauss2
                    },
                    1e-13,
                    budget.clone(),
                )
                .and_then(|r| serde_json::to_value(r).map_err(|e| e.to_string()))
            }
        } else if mode == "fixed" {
            s.attempts += 1;
            d.chemical_stage_ssprk2(&mut s,1./(kref*n as f64),&mut ssprk_counter).map(|r| {
                s.accepted+=1;
                s.rhs_evaluations=ssprk_counter;
                { let mut integrated=Events::default(); integrated.add_scaled(&Events::from_rhs(&r.rhs,d.n_h0_cm3/s.a.powi(3)),r.dt_s); json!({"dt_s":r.dt_s,"integrated":integrated,"tau1":r.transport.max_tau_stage1,"tau2":r.transport.max_tau_stage2,"nodes1":r.transport.nodes_stage1,"nodes2":r.transport.nodes_stage2}) }
            }
            ).map_err(|e|format!("{e:?}"))
        } else {
            let to = start_a * (step as f64 * 1e-6 / n as f64).exp();
            let dx = ((to - s.a) / s.a).ln_1p();
            d.fixed_step_physical_birth_ssprk2(&mut s,dx,if mode=="birth" {
                PhysicalBirthRule::Gauss2
            }
            else {
                PhysicalBirthRule::DisabledGauss2
            }
            ).map(|r| { let births=r.birth.births.iter().map(|b|json!({"a":b.a,"weight_dln_a":b.weight_dln_a,"proper_time_weight_s":b.proper_time_weight_s,"added_n":b.added_photons_per_h,"added_u":b.added_energy_ev_per_h})).collect::<Vec<_>>(); let segments=r.birth.segments.iter().map(|t|json!({"begin":t.a_begin,"midpoint":t.a_mid,"end":t.a_end,"dt_s":t.dt_s,"n_h_cm3":t.n_h_cm3,"p":t.photo_events_per_h,"c":t.ci_events_per_h,"r":t.rr_events_per_h,"d":t.dr_events_per_h,"photo_binding":t.photo_binding_ev_per_h,"photo_heat":t.photo_heat_ev_per_h,"ce":t.ce_cooling_ev_per_h,"rrdr":t.rrdr_cooling_ev_per_h,"ff":t.ff_cooling_ev_per_h,"cmb":t.cmb_input_ev_per_h,"escape":t.escaped_ev_per_h})).collect::<Vec<_>>(); json!({"births":births,"segments":segments,"tau1":r.stages.max_tau_stage1,"tau2":r.stages.max_tau_stage2,"nodes1":r.stages.nodes_stage1,"nodes2":r.stages.nodes_stage2}) }).map_err(|e|format!("{e:?}"))
        };
        match result {
            Ok(report) => {
                records.push(json!( {
                    "step":step,"state":state_json(&d,&s)?,"report":report
                }
                ));
            }
            Err(e) => {
                failed = Some(format!("step={step}: {e}"));
                break;
            }
        }
    }
    let mut payload = json!( {
        "schema":"v16-native-radau-raw-v1","config": {
            "q":0.,"cells":8,"n_mu":8,"threads":1,"background_panels":128,"source_energy_subdivisions":d.config.energy_subdivisions,
            "inactive_hi_split":false,"initial_fractions":[0.075,0.12,0.03],"initial_temperature_k":15000.,"seed_dt_s":if mode=="birth" {
                0.
            }
            else {
                1e16
            }
            ,"newton_atol_scaled":1e-13,"newton_rtol":0.,"native_rhs_cap":200000,"case_wall_cap_s":30.,"Xend":if mode=="fixed" {
                0.
            }
            else {
                1e-6
            }
        }
        ,"mode":mode,"method":method,"N":n,"k_ref20":kref,"initial":before,"records":records,"completed":failed.is_none(),
        "failure":failed,"native_rhs_attempts_including_fd_replay":if method=="radau" {
            budget.calls()
        }
        else {
            s.rhs_evaluations
        }
        ,"wall_s":clock.elapsed().as_secs_f64()
    }
    );
    payload["native_evaluation"] = json!({"mode":format!("{native_eval:?}"),"profile":budget.profile_json()});
    let mut f = File::create(&args[1]).map_err(|e| e.to_string())?;
    serde_json::to_writer_pretty(&mut f, &payload).map_err(|e| e.to_string())?;
    writeln!(f).map_err(|e| e.to_string())?;
    if let Some(e) = failed {
        eprintln!("FAILED {e}");
        return Err(e);
    }
    eprintln!(
        "COMPLETE native_rhs={} wall={:.6}",
        s.rhs_evaluations,
        clock.elapsed().as_secs_f64()
    );
    Ok(())
}
