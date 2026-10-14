//! Batch protocol: `point_si Tm Tr nH_m3 H_s xp x2` or `point_cgs ... nH_cm3 ...`.
//! Each nonempty input line yields one JSON object; invalid rows never fall back.
use rei_peebles_reference::*;
use std::io::{self, BufRead};

fn source_json(s: SourceValues) -> String {
    format!("{{\"x1\":{:.17e},\"alpha_b_m3_s\":{:.17e},\"beta_p_s\":{:.17e},\"beta_shell_s\":{:.17e},\"r_alpha_s\":{:.17e},\"d_ground_s\":{:.17e},\"boltzmann_lya\":{:.17e},\"c_factor\":{:.17e}}}",
            s.x1,s.alpha_b_m3_s,s.beta_p_s,s.beta_shell_s,s.r_alpha_s,s.d_ground_s,s.boltzmann_lya,s.c_factor)
}
fn point(line: &str) -> Result<String, String> {
    let p: Vec<_> = line.split_whitespace().collect();
    if p.len()!=7 { return Err("expected_mode_and_six_numbers".into()); }
    let v: Vec<f64> = p[1..].iter().map(|s|s.parse::<f64>()).collect::<Result<_,_>>()
        .map_err(|_|"invalid_number")?;
    let input = match p[0] {
        "point_si" => ReferenceInput::from_si(v[0],v[1],v[2],v[3],v[4],v[5]),
        "point_cgs" => ReferenceInput::from_cgs(v[0],v[1],v[2],v[3],v[4],v[5]),
        _ => return Err("unknown_mode".into()),
    }.map_err(|e|format!("{e:?}"))?;
    let out = evaluate_reference(input).map_err(|e|format!("{e:?}"))?;
    let r=out.retained.rhs;
    let d=out.retained.same_rates_closure_defect;
    Ok(format!(concat!("{{\"ok\":true,\"mode\":\"{}\",\"source_profile\":\"{}\",",
        "\"rec_commit\":\"{}\",\"n_h_m3\":{:.17e},\"temperature_k\":{:.17e},",
        "\"hubble_s\":{:.17e},\"xp\":{:.17e},\"x2\":{:.17e},",
        "\"collapsed\":{{\"source\":{},\"dxp_dt\":{:.17e}}},",
        "\"retained\":{{\"source\":{},\"rhs\":{{\"dxp_dt\":{:.17e},\"dx2_dt\":{:.17e},\"dx1_dt\":{:.17e},\"continuum_flux\":{:.17e},\"ground_flux\":{:.17e}}},",
        "\"same_rates_peebles_dt\":{:.17e},\"closure_defect\":{{\"direct\":{:.17e},\"shell_lag\":{:.17e},\"ground_depletion\":{:.17e},\"reconstructed\":{:.17e}}},",
        "\"qss_at_actual_fixed_ground\":{:.17e}}},",
        "\"source_assembly_contribution\":{:.17e},\"retained_minus_standard_collapsed\":{:.17e},\"physical_admission\":false}}"),
        MODE_ID,SOURCE_PROFILE,REC_COMMIT,input.n_h_m3(),input.temperature_k(),input.hubble_s(),input.state().xp,input.state().x2,
        source_json(out.collapsed.source),out.collapsed.dxp_dt,
        source_json(out.retained.source),r.dxp_dt,r.dx2_dt,r.dx1_dt,r.continuum_flux,r.ground_flux,
        out.retained.same_rates_peebles_dt,d.direct,d.shell_lag,d.ground_depletion,d.reconstructed,
        out.retained.qss_at_actual_fixed_ground,out.source_assembly_contribution,out.retained_minus_standard_collapsed))
}
fn main() -> Result<(), io::Error> {
    for line in io::stdin().lock().lines() {
        let line=line?;
        if line.trim().is_empty()||line.trim_start().starts_with('#') {continue;}
        match point(&line) {
            Ok(value)=>println!("{value}"),
            Err(e)=>println!("{{\"ok\":false,\"error\":\"{e}\",\"physical_admission\":false}}"),
        }
    }
    Ok(())
}
