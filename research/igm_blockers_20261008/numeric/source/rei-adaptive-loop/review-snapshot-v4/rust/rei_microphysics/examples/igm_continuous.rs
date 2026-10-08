//! Additive continuous-emissivity research runner; no checkpoint/restart claim.
use rei_microphysics::{
    igm_checkpoint::sha256_bytes,
    igm_config::parse_config,
    igm_continuous::{ContinuousHistory, ContinuousState, SpectralGrid},
};
use std::{fs, io::Write, path::PathBuf};
const CSV_HEADER: &str = "ln_a,z,x_hii,x_heii,x_heiii,w,T,Tcmb,ne_per_h,Gamma_hi,Gamma_hei,Gamma_heii,Nactive,Eactive,emitted_N,emitted_E,abs_HI,abs_HeI,abs_HeII,out_N,out_E,redshift_E,escape_E,work_E,cmb_reservoir_E,number_residual,energy_residual,ci_HI,ci_HeI,ci_HeII,rr_HII,rr_HeII,rr_HeIII,dr_HeII,ci_floor_HI,ci_floor_HeI,ci_floor_HeII,ce_cap_HI_E,ce_cap_HeI_E,ce_cap_HeII_E,excluded_dr_E,underflow_N_bound,underflow_E_bound,cmb_absolute_exchange_E,accepted_steps,rejected_steps,max_residual,packet_count,endpoint_stage_steps\n";
fn csv_row(h: &ContinuousHistory, s: &ContinuousState) -> Result<String, String> {
    let point = h
        .config
        .background
        .at_ln_a(s.ln_a)
        .map_err(|e| e.to_string())?;
    let eos = s
        .gas
        .eos(point.n_h_cm3, point.n_he_cm3)
        .map_err(|e| e.to_string())?;
    let photo = h.endpoint_photo(s).map_err(|e| e.to_string())?;
    let r = h.radiation(s);
    let b = h.balances(s).map_err(|e| e.to_string())?;
    let l = &s.ledger;
    let values = [
        s.ln_a,
        (-s.ln_a).exp() - 1.0,
        s.gas.fractions[0],
        s.gas.fractions[1],
        s.gas.fractions[2],
        s.gas.w_erg_per_h,
        eos.temperature_k,
        point.tcmb_k,
        eos.electron_density_cm3 / point.n_h_cm3,
        photo.input.gamma_s[0],
        photo.input.gamma_s[1],
        photo.input.gamma_s[2],
        r[0],
        r[1],
        l.emitted_n,
        l.emitted_e,
        l.absorption[0],
        l.absorption[1],
        l.absorption[2],
        l.out_n,
        l.out_e,
        l.redshift_e,
        l.escape_e,
        l.work_e,
        l.cmb_e,
        b[0],
        b[1],
        l.ci[0],
        l.ci[1],
        l.ci[2],
        l.rr[0],
        l.rr[1],
        l.rr[2],
        l.dr,
        l.floor[0],
        l.floor[1],
        l.floor[2],
        l.cap_e[0],
        l.cap_e[1],
        l.cap_e[2],
        l.excluded_dr_e,
        l.underflow_n_bound,
        l.underflow_e_bound,
        l.cmb_abs_e,
    ];
    if !values.iter().all(|v| v.is_finite()) {
        return Err("IGM_CSV_NONFINITE".into());
    }
    let mut row = values
        .iter()
        .map(f64::to_string)
        .collect::<Vec<_>>()
        .join(",");
    row.push_str(&format!(
        ",{},{},{},{},{}\n",
        s.accepted_steps,
        s.rejected_steps,
        s.max_residual,
        s.counts.len(),
        s.endpoint_stage_steps
    ));
    Ok(row)
}

fn run() -> Result<(), String> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args == ["--help"] {
        println!("igm_continuous --config FILE --output NEW_DIRECTORY --spectral-panels N [--spectral-grid uniform|threshold-bands] [--max-dln-a H] [--output-panels N]");
        return Ok(());
    }
    let mut config = None;
    let mut output = None;
    let mut panels = None;
    let mut grid = SpectralGrid::Uniform;
    let mut dx = None;
    let mut outputs = None;
    let mut seen = std::collections::BTreeSet::new();
    if args.len() % 2 != 0 {
        return Err("arguments require values".into());
    }
    for pair in args.chunks_exact(2) {
        if !seen.insert(pair[0].clone()) {
            return Err("duplicate option".into());
        }
        match pair[0].as_str() {
            "--config" => config = Some(PathBuf::from(&pair[1])),
            "--output" => output = Some(PathBuf::from(&pair[1])),
            "--spectral-panels" => {
                panels = Some(
                    pair[1]
                        .parse::<usize>()
                        .map_err(|_| "bad spectral panels")?,
                )
            }
            "--spectral-grid" => {
                grid = match pair[1].as_str() {
                    "uniform" => SpectralGrid::Uniform,
                    "threshold-bands" => SpectralGrid::ThresholdBands,
                    _ => return Err("unknown spectral grid".into()),
                }
            }
            "--max-dln-a" => dx = Some(pair[1].parse::<f64>().map_err(|_| "bad max step")?),
            "--output-panels" => {
                outputs = Some(pair[1].parse::<usize>().map_err(|_| "bad outputs")?)
            }
            _ => return Err(format!("unknown option {}", pair[0])),
        }
    }
    let bytes = fs::read(config.ok_or("missing --config")?).map_err(|e| e.to_string())?;
    let mut c = parse_config(std::str::from_utf8(&bytes).map_err(|e| e.to_string())?)
        .map_err(|e| e.to_string())?;
    if let Some(h) = dx {
        c.max_dln_a = h;
    }
    if let Some(n) = outputs {
        if n == 0 {
            return Err("zero output panels".into());
        }
        c.output_panels = n;
    }
    let (h, mut state) =
        ContinuousHistory::new_with_grid(c, panels.ok_or("missing --spectral-panels")?, grid)
            .map_err(|e| e.to_string())?;
    let output = output.ok_or("missing --output")?;
    fs::create_dir(&output).map_err(|e| format!("new output directory required: {e}"))?;
    let status = |s: &ContinuousState, complete: bool, error: Option<&str>| -> Result<(), String> {
        let error = error.map(|e| format!("{e:?}")).unwrap_or("null".into());
        fs::write(output.join("status.json"),format!("{{\"schema\":\"igm_continuous_status_v1\",\"complete\":{complete},\"ln_a\":{},\"accepted_steps\":{},\"rejected_steps\":{},\"endpoint_stage_steps\":{},\"error\":{error}}}\n",s.ln_a,s.accepted_steps,s.rejected_steps,s.endpoint_stage_steps)).map_err(|e|e.to_string())
    };
    let result = (|| -> Result<(), String> {
        status(&state, false, None)?;
        fs::write(output.join("config.cfg"), &bytes).map_err(|e| e.to_string())?;
        let mut nodes = String::from("eta,weight\n");
        for n in &h.nodes {
            nodes.push_str(&format!("{},{}\n", n.eta, n.weight));
        }
        fs::write(output.join("nodes.csv"), &nodes).map_err(|e| e.to_string())?;
        let src = &h.config.source;
        let identity = format!(
            "continuous_proper_powerlaw_minus2_eta_gauss2_v1\n{:016x},{:016x},{:016x}\n{}",
            src.photons_per_h_per_s.to_bits(),
            src.energy_min_ev.to_bits(),
            src.energy_max_ev.to_bits(),
            nodes
        );
        let manifest=format!("{{\"schema\":\"igm_continuous_manifest_v1\",\"solver_id\":\"continuous_eta_midpoint_redshift_source_be_v1\",\"source_mode\":\"continuous_proper_emissivity\",\"spectral_grid\":{:?},\"node_count\":{},\"spectral_panels\":{},\"max_dln_a\":{},\"output_panels\":{},\"config_sha256\":{:?},\"source_sha256\":{:?},\"source_identity_definition\":\"analytic source parameters plus exact eta nodes and weights\",\"clock\":\"dt=delta_ln_a/H_stage; midpoint unless adjacent IEEE events require a right endpoint stage with explicit interval support masks\",\"endpoint_Gamma\":\"physical endpoint spectrum, distinct from BE interval ownership\",\"claim\":\"research prototype; fixed spectral quadrature; no checkpoint/restart; accuracy requires independent temporal and spectral refinement\"}}\n",h.spectral_grid.as_str(),h.nodes.len(),h.spectral_panels,h.config.max_dln_a,h.config.output_panels,sha256_bytes(&bytes)?,sha256_bytes(identity.as_bytes())?);
        fs::write(output.join("manifest.json"), manifest).map_err(|e| e.to_string())?;
        let mut csv = std::io::BufWriter::new(
            fs::File::create(output.join("history.csv")).map_err(|e| e.to_string())?,
        );
        csv.write_all(CSV_HEADER.as_bytes())
            .and_then(|_| {
                csv.write_all(
                    csv_row(&h, &state)
                        .map_err(std::io::Error::other)?
                        .as_bytes(),
                )
            })
            .and_then(|_| csv.flush())
            .map_err(|e| e.to_string())?;
        for index in 1..=h.config.output_panels {
            let end = if index == h.config.output_panels {
                h.config.end
            } else {
                h.config.start
                    + (h.config.end - h.config.start) * index as f64 / h.config.output_panels as f64
            };
            while state.ln_a < end {
                state = h.advance_one(&state, end).map_err(|e| e.to_string())?;
            }
            csv.write_all(csv_row(&h, &state)?.as_bytes())
                .and_then(|_| csv.flush())
                .map_err(|e| e.to_string())?;
            status(&state, false, None)?;
        }
        let mut final_nodes =
            String::from("eta,weight,current_energy,source_active,readout_count,log_count\n");
        for (i, n) in h.nodes.iter().enumerate() {
            final_nodes.push_str(&format!(
                "{},{},{},{},{},{}\n",
                n.eta,
                n.weight,
                h.energy(i, state.ln_a),
                h.source_rate(i, state.ln_a) > 0.0,
                state.counts[i],
                state.log_counts[i]
            ));
        }
        fs::write(output.join("nodes_final.csv"), final_nodes).map_err(|e| e.to_string())?;
        status(&state, true, None)?;
        Ok(())
    })();
    if let Err(ref error) = result {
        status(&state, false, Some(error))?;
    }
    result
}
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(1);
    }
}
