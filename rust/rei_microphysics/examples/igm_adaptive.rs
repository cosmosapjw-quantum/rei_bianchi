//! Additive adaptive research runner with detached output observation branches.
//! Neither requested output times nor discarded sampling work change the primary path.
use rei_microphysics::{
    igm_adaptive::{
        AdaptiveControl, AdaptiveDiagnostics, AdaptiveIntegrator, AdaptiveState, MicrostepPolicy,
        MicrostepRecord,
    },
    igm_checkpoint::sha256_bytes,
    igm_config::{parse_config, HistoryConfig},
    igm_continuous::{ContinuousHistory, ContinuousState, SpectralGrid},
};
use std::{
    fmt::Write as _,
    fs,
    io::Write,
    path::{Path, PathBuf},
};

const CSV_HEADER: &str = "ln_a,z,x_hii,x_heii,x_heiii,w,T,Tcmb,ne_per_h,Gamma_hi,Gamma_hei,Gamma_heii,Nactive,Eactive,emitted_N,emitted_E,abs_HI,abs_HeI,abs_HeII,out_N,out_E,redshift_E,escape_E,work_E,cmb_reservoir_E,number_residual,energy_residual,ci_HI,ci_HeI,ci_HeII,rr_HII,rr_HeII,rr_HeIII,dr_HeII,ci_floor_HI,ci_floor_HeI,ci_floor_HeII,ce_cap_HI_E,ce_cap_HeI_E,ce_cap_HeII_E,excluded_dr_E,underflow_N_bound,underflow_E_bound,cmb_absolute_exchange_E,accepted_steps,rejected_steps,max_residual,packet_count,endpoint_stage_steps,primary_ln_a,primary_accepted_macros,primary_rejected_lte,primary_rejected_physical,primary_trial_evaluations,primary_guarded_microsteps,primary_last_error,primary_max_error,primary_last_guard,primary_max_guard,primary_last_was_guarded,primary_last_error_measured,primary_last_error_factor\n";
fn csv_row(
    h: &ContinuousHistory,
    s: &ContinuousState,
    primary: &AdaptiveState,
) -> Result<String, String> {
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
        ",{},{},{},{},{}",
        primary.state.accepted_steps,
        primary.state.rejected_steps,
        primary.state.max_residual,
        s.counts.len(),
        primary.state.endpoint_stage_steps
    ));
    let d = &primary.diagnostics;
    row.push_str(&format!(
        ",{},{},{},{},{},{},{},{},{},{},{},{},{}\n",
        primary.state.ln_a,
        d.accepted_macros,
        d.rejected_lte,
        d.rejected_physical,
        d.trial_evaluations,
        d.guarded_microsteps,
        d.last_error,
        d.max_error,
        d.last_guard,
        d.max_guard,
        usize::from(d.last_was_guarded),
        usize::from(d.accepted_macros > d.guarded_microsteps && !d.last_was_guarded),
        d.last_error_factor,
    ));
    Ok(row)
}

fn json_string(value: &str) -> String {
    let mut out = String::from("\"");
    for c in value.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c <= '\u{1f}' => {
                write!(out, "\\u{:04x}", c as u32).unwrap();
            }
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

// A failed estimator may contain a nonfinite diagnostic. JSON null preserves
// that failure honestly without creating an invalid NaN/Infinity JSON token.
fn json_number(value: f64) -> String {
    if value.is_finite() {
        value.to_string()
    } else {
        "null".into()
    }
}

fn microstep_json(m: &MicrostepRecord) -> String {
    let fields = m
        .field_motion
        .iter()
        .map(|(name, bound, ratio)| {
            format!(
                "{{\"name\":{},\"bound\":{},\"ratio\":{}}}",
                json_string(name),
                json_number(*bound),
                json_number(*ratio),
            )
        })
        .collect::<Vec<_>>()
        .join(",");
    let events = m
        .events
        .iter()
        .map(|event| {
            format!(
                "{{\"node\":{},\"kind\":{},\"at\":{},\"at_bits\":\"{:016x}\",\"energy_ev\":{}}}",
                event.node,
                json_string(event.kind),
                json_number(event.at),
                event.at.to_bits(),
                json_number(event.energy_ev),
            )
        })
        .collect::<Vec<_>>()
        .join(",");
    format!(
        "{{\"start\":{},\"end\":{},\"start_bits\":\"{:016x}\",\"end_bits\":\"{:016x}\",\"proper_dt\":{},\"max_motion_ratio\":{},\"worst_component\":{},\"boundary_kind\":{},\"events\":[{}],\"field_motion\":[{}],\"fraction_equation_defect\":[{},{},{}],\"energy_equation_defect\":{},\"post_event_rate_guard\":{}}}",
        json_number(m.start), json_number(m.end), m.start.to_bits(), m.end.to_bits(),
        json_number(m.proper_dt), json_number(m.max_motion_ratio), json_string(m.worst_component),
        json_string(m.boundary_kind), events, fields,
        json_number(m.fraction_equation_defect[0]), json_number(m.fraction_equation_defect[1]), json_number(m.fraction_equation_defect[2]),
        json_number(m.energy_equation_defect), m.post_event_rate_guard,
    )
}

fn diagnostics_fields(d: &AdaptiveDiagnostics) -> String {
    let measured = d.accepted_macros > d.guarded_microsteps && !d.last_was_guarded;
    let microsteps = d
        .microsteps
        .iter()
        .map(microstep_json)
        .collect::<Vec<_>>()
        .join(",");
    format!(
        "\"accepted_macros\":{},\"rejected_lte\":{},\"rejected_physical\":{},\"trial_evaluations\":{},\"guarded_microsteps\":{},\"last_error\":{},\"max_error\":{},\"last_guard\":{},\"max_guard\":{},\"last_was_guarded\":{},\"last_error_measured\":{},\"last_error_factor\":{},\"worst_component\":{},\"last_attempt_error\":{},\"last_attempt_component\":{},\"last_attempt_width\":{},\"last_failure_code\":{},\"last_trial_phase\":{},\"microsteps\":[{}]",
        d.accepted_macros, d.rejected_lte, d.rejected_physical, d.trial_evaluations,
        d.guarded_microsteps, if measured { json_number(d.last_error) } else { "null".into() }, json_number(d.max_error),
        json_number(d.last_guard), json_number(d.max_guard), d.last_was_guarded, measured,
        if measured { json_number(d.last_error_factor) } else { "null".into() },
        json_string(d.worst_component), d.last_attempt_error.map(json_number).unwrap_or_else(|| "null".into()),
        json_string(d.last_attempt_component), json_number(d.last_attempt_width), json_string(d.last_failure_code), json_string(d.last_trial_phase), microsteps,
    )
}

#[derive(Default)]
struct ObservationWork {
    samples: usize,
    endpoint_reuses: usize,
    accepted_macros: usize,
    rejected_lte: usize,
    rejected_physical: usize,
    trial_evaluations: usize,
    guarded_microsteps: usize,
    microsteps: Vec<(f64, MicrostepRecord)>,
}
impl ObservationWork {
    fn add(&mut self, target: f64, before: &AdaptiveDiagnostics, after: &AdaptiveDiagnostics) {
        self.accepted_macros += after.accepted_macros.saturating_sub(before.accepted_macros);
        self.rejected_lte += after.rejected_lte.saturating_sub(before.rejected_lte);
        self.rejected_physical += after
            .rejected_physical
            .saturating_sub(before.rejected_physical);
        self.trial_evaluations += after
            .trial_evaluations
            .saturating_sub(before.trial_evaluations);
        self.guarded_microsteps += after
            .guarded_microsteps
            .saturating_sub(before.guarded_microsteps);
        self.microsteps.extend(
            after
                .microsteps
                .iter()
                .skip(before.microsteps.len())
                .cloned()
                .map(|m| (target, m)),
        );
    }
    fn json(&self) -> String {
        let records = self
            .microsteps
            .iter()
            .map(|(t, m)| {
                format!(
                    "{{\"sample_ln_a\":{},\"sample_bits\":\"{:016x}\",\"microstep\":{}}}",
                    t,
                    t.to_bits(),
                    microstep_json(m)
                )
            })
            .collect::<Vec<_>>()
            .join(",");
        format!(
            "{{\"samples\":{},\"endpoint_reuses\":{},\"accepted_macros\":{},\"rejected_lte\":{},\"rejected_physical\":{},\"trial_evaluations\":{},\"guarded_microsteps\":{},\"microsteps\":[{}]}}",
            self.samples, self.endpoint_reuses, self.accepted_macros, self.rejected_lte,
            self.rejected_physical, self.trial_evaluations, self.guarded_microsteps, records,
        )
    }
}

fn write_status(
    output: &Path,
    primary: &AdaptiveState,
    work: &ObservationWork,
    complete: bool,
    error: Option<&str>,
    failure_scope: Option<&str>,
    failed_attempt: Option<&AdaptiveDiagnostics>,
) -> Result<(), String> {
    let s = &primary.state;
    let content = format!(
        "{{\"schema\":\"igm_adaptive_status_v1\",\"complete\":{complete},\"primary\":{{\"ln_a\":{},\"next_dln_a\":{},\"accepted_steps\":{},\"rejected_steps\":{},\"endpoint_stage_steps\":{},\"max_residual\":{},{} }},\"observation\":{},\"failure_scope\":{},\"failed_attempt\":{},\"error\":{}}}\n",
        s.ln_a, s.next_dln_a, s.accepted_steps, s.rejected_steps,
        s.endpoint_stage_steps, json_number(s.max_residual), diagnostics_fields(&primary.diagnostics), work.json(),
        failure_scope.map(json_string).unwrap_or_else(|| "null".into()),
        failed_attempt.map(|d| format!("{{{}}}", diagnostics_fields(d))).unwrap_or_else(|| "null".into()),
        error.map(json_string).unwrap_or_else(|| "null".into()),
    );
    fs::write(output.join("status.json"), content).map_err(|e| e.to_string())
}

fn write_primary(
    output: &Path,
    h: &ContinuousHistory,
    primary: &AdaptiveState,
) -> Result<(), String> {
    fs::write(
        output.join("primary_state.csv"),
        format!("{}{}", CSV_HEADER, csv_row(h, &primary.state, primary)?),
    )
    .map_err(|e| e.to_string())?;
    let s = &primary.state;
    let mut final_nodes =
        String::from("eta,weight,current_energy,source_active,readout_count,log_count\n");
    for (i, n) in h.nodes.iter().enumerate() {
        writeln!(
            final_nodes,
            "{},{},{},{},{},{}",
            n.eta,
            n.weight,
            h.energy(i, s.ln_a),
            h.source_rate(i, s.ln_a) > 0.0,
            s.counts[i],
            s.log_counts[i]
        )
        .unwrap();
    }
    fs::write(output.join("nodes_final.csv"), final_nodes).map_err(|e| e.to_string())
}

struct OutputSchedule {
    times: Vec<f64>,
    bytes: Vec<u8>,
    kind: &'static str,
}
impl OutputSchedule {
    fn new(config: &HistoryConfig, file: Option<PathBuf>) -> Result<Self, String> {
        if let Some(file) = file {
            let bytes = fs::read(file).map_err(|e| format!("output times: {e}"))?;
            let text = std::str::from_utf8(&bytes).map_err(|e| format!("output times: {e}"))?;
            let mut lines = text
                .lines()
                .map(str::trim)
                .filter(|line| !line.is_empty())
                .peekable();
            // Frozen independent schedules use a one-column CSV with this
            // literal header. Keep all original bytes for identity/replay.
            if lines.peek() == Some(&"ln_a") {
                lines.next();
            }
            let times = lines
                .map(|line| {
                    line.parse::<f64>()
                        .map_err(|_| "invalid output epoch".to_string())
                })
                .collect::<Result<Vec<_>, _>>()?;
            if times.len() < 2
                || times.first() != Some(&config.start)
                || times.last() != Some(&config.end)
                || times
                    .iter()
                    .any(|t| !t.is_finite() || *t < config.start || *t > config.end)
                || times.windows(2).any(|pair| pair[0] >= pair[1])
            {
                return Err("output times must be finite and strictly increasing, with exact config start and end".into());
            }
            Ok(Self {
                times,
                bytes,
                kind: "explicit",
            })
        } else {
            let count = config
                .output_panels
                .checked_add(1)
                .ok_or("output panel count overflow")?;
            let mut times = Vec::new();
            times
                .try_reserve_exact(count)
                .map_err(|e| format!("output schedule allocation: {e}"))?;
            for index in 0..count {
                times.push(if index == config.output_panels {
                    config.end
                } else {
                    config.start
                        + (config.end - config.start) * index as f64 / config.output_panels as f64
                });
            }
            let mut text = String::new();
            for t in &times {
                writeln!(text, "{t}").unwrap();
            }
            Ok(Self {
                times,
                bytes: text.into_bytes(),
                kind: "regular",
            })
        }
    }
}

fn write_manifest(
    output: &Path,
    integrator: &AdaptiveIntegrator,
    bytes: &[u8],
    policy: &str,
    schedule: &OutputSchedule,
) -> Result<(), String> {
    let h = &integrator.history;
    let c = &integrator.control;
    fs::write(output.join("config.cfg"), bytes).map_err(|e| e.to_string())?;
    let mut nodes = String::from("eta,weight\n");
    for n in &h.nodes {
        writeln!(nodes, "{},{}", n.eta, n.weight).unwrap();
    }
    fs::write(output.join("nodes.csv"), &nodes).map_err(|e| e.to_string())?;
    let src = &h.config.source;
    let identity = format!(
        "continuous_proper_powerlaw_minus2_eta_gauss2_v1\n{:016x},{:016x},{:016x}\n{}",
        src.photons_per_h_per_s.to_bits(),
        src.energy_min_ev.to_bits(),
        src.energy_max_ev.to_bits(),
        nodes,
    );
    // The original config, effective overrides, and exact output schedule are
    // all preserved. Output identity never enters the primary physical stepping.
    let raw_hash = sha256_bytes(bytes)?;
    let output_hash = sha256_bytes(&schedule.bytes)?;
    fs::write(output.join("output_times.txt"), &schedule.bytes).map_err(|e| e.to_string())?;
    let effective_identity = format!(
        "igm_adaptive_effective_config_v1\n{raw_hash}\nmax_dln_a_bits={:016x}\noutput_panels={}\noutput_schedule={}\noutput_times_sha256={output_hash}\n",
        h.config.max_dln_a.to_bits(), h.config.output_panels, schedule.kind,
    );
    fs::write(
        output.join("effective_config_identity.txt"),
        &effective_identity,
    )
    .map_err(|e| e.to_string())?;
    let manifest = format!(concat!(
        "{{\"schema\":\"igm_adaptive_manifest_v1\",",
        "\"solver_id\":\"continuous_eta_be_step_doubling_p1_adaptive_v1\",",
        "\"source_mode\":\"continuous_proper_emissivity\",",
        "\"model_id\":{},\"provider_id\":{},\"closure_id\":{},",
        "\"spectral_grid\":{},\"node_count\":{},\"spectral_panels\":{},",
        "\"max_dln_a\":{},\"min_dln_a\":{},\"max_steps\":{},\"output_panels\":{},",
        "\"config_sha256\":{},\"effective_config_sha256\":{},\"source_sha256\":{},",
        "\"output_schedule\":{},\"output_time_count\":{},\"output_times_sha256\":{},",
        "\"source_identity_definition\":\"analytic source parameters by f64 bits plus exact eta nodes and weights\",",
        "\"effective_config_identity_definition\":\"SHA256 of effective_config_identity.txt: raw config SHA256, effective max_dln_a bits, effective output panels, schedule kind and exact output_times.txt SHA256\",",
        "\"tolerances\":{{\"relative\":{},\"fraction_atol\":{},\"temperature_atol\":{},\"energy_atol\":{},\"count_atol\":{},\"gamma_atol\":{},\"heat_atol\":{}}},",
        "\"controller\":{{\"safety\":{},\"min_factor\":{},\"max_factor\":{},\"max_attempts\":{},\"max_trial_evaluations\":{},\"microstep_motion_limit\":{}}},",
        "\"microstep_policy\":{},",
        "\"microstep_exception\":\"Strict fails when step doubling has no representable midpoint. Guarded-research admits only independently guarded adjacent-f64 transactions at a hard physical-event, final, or requested endpoint. Records distinguish these boundary kinds. Retry-created interior microsteps are rejected. Admitted exceptions are unestimated, counted separately, and are not LTE-certified.\",",
        "\"sampling\":\"Each interior output independently restarts at the same primary accepted left endpoint; exact primary endpoints are reused. Primary integration ignores output times.\",",
        "\"csv_diagnostics\":\"Legacy and primary diagnostic columns describe the accepted primary right endpoint covering the sample; aggregate observation-only work is in status.json. CSV last-error and error-factor values are retained diagnostics, not current estimates, whenever primary_last_error_measured=0.\",",
        "\"claim\":\"research prototype; fixed spectral quadrature; no checkpoint/restart; local estimates do not establish a global continuum bound; independent temporal and spectral validation required\"}}\n"
    ),
        json_string(&h.config.model_id), json_string(&h.config.provider_id), json_string(&h.config.closure_id),
        json_string(h.spectral_grid.as_str()), h.nodes.len(), h.spectral_panels,
        h.config.max_dln_a, h.config.min_dln_a, h.config.max_steps, h.config.output_panels,
        json_string(&raw_hash), json_string(&sha256_bytes(effective_identity.as_bytes())?), json_string(&sha256_bytes(identity.as_bytes())?),
        json_string(schedule.kind), schedule.times.len(), json_string(&output_hash),
        c.relative, c.fraction_atol, c.temperature_atol, c.energy_atol, c.count_atol, c.gamma_atol, c.heat_atol,
        c.safety, c.min_factor, c.max_factor, c.max_attempts, c.max_trial_evaluations, c.microstep_motion_limit, json_string(policy),
    );
    fs::write(output.join("manifest.json"), manifest).map_err(|e| e.to_string())
}

fn positive_number(value: &str, name: &str) -> Result<f64, String> {
    let x = value
        .parse::<f64>()
        .map_err(|_| format!("invalid {name}"))?;
    if !x.is_finite() || x <= 0.0 {
        return Err(format!("{name} must be finite and positive"));
    }
    Ok(x)
}

fn run() -> Result<(), String> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args == ["--help"] {
        println!("igm_adaptive --config FILE --output NEW_DIRECTORY --spectral-panels N [--spectral-grid uniform|threshold-bands] [--max-dln-a H] [--output-panels N | --output-times FILE] [--rtol R] [--atol-scale S] [--microstep-policy strict|guarded-research]");
        return Ok(());
    }
    if !args.len().is_multiple_of(2) {
        return Err("arguments require values".into());
    }
    let (mut config, mut output, mut panels) = (None, None, None);
    let (mut dx, mut outputs) = (None, None);
    let mut output_times = None;
    let mut grid = SpectralGrid::Uniform;
    let mut control = AdaptiveControl::default();
    let mut policy = "strict";
    // Explicit strict mode remains the CLI default even if a library user's
    // preferred default changes in a future version.
    control.microstep_policy = MicrostepPolicy::Strict;
    let mut scale = 1.0;
    let mut seen = std::collections::BTreeSet::new();
    for pair in args.chunks_exact(2) {
        if !seen.insert(pair[0].clone()) {
            return Err(format!("duplicate option {}", pair[0]));
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
            "--max-dln-a" => dx = Some(positive_number(&pair[1], "max step")?),
            "--output-panels" => {
                outputs = Some(pair[1].parse::<usize>().map_err(|_| "bad output panels")?)
            }
            "--output-times" => output_times = Some(PathBuf::from(&pair[1])),
            "--rtol" => control.relative = positive_number(&pair[1], "relative tolerance")?,
            "--atol-scale" => scale = positive_number(&pair[1], "absolute tolerance scale")?,
            "--microstep-policy" => {
                (policy, control.microstep_policy) = match pair[1].as_str() {
                    "strict" => ("strict", MicrostepPolicy::Strict),
                    "guarded-research" => ("guarded-research", MicrostepPolicy::GuardedResearch),
                    _ => return Err("unknown microstep policy".into()),
                };
            }
            _ => return Err(format!("unknown option {}", pair[0])),
        }
    }
    if outputs.is_some() && output_times.is_some() {
        return Err("--output-panels and --output-times are mutually exclusive".into());
    }
    for absolute in [
        &mut control.fraction_atol,
        &mut control.temperature_atol,
        &mut control.energy_atol,
        &mut control.count_atol,
        &mut control.gamma_atol,
        &mut control.heat_atol,
    ] {
        *absolute *= scale;
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
    let schedule = OutputSchedule::new(&c, output_times)?;
    c.output_panels = schedule.times.len() - 1;
    let output = output.ok_or("missing --output")?;
    let (history, initial) =
        ContinuousHistory::new_with_grid(c, panels.ok_or("missing --spectral-panels")?, grid)
            .map_err(|e| e.to_string())?;
    let integrator = AdaptiveIntegrator::new(history, control).map_err(|e| e.to_string())?;
    let mut primary = AdaptiveState::new(initial);
    fs::create_dir(&output).map_err(|e| format!("new output directory required: {e}"))?;
    let mut work = ObservationWork::default();
    let mut failure_scope = "output";
    let mut failed_attempt = None;
    let result = (|| -> Result<(), String> {
        write_status(&output, &primary, &work, false, None, None, None)?;
        write_manifest(&output, &integrator, &bytes, policy, &schedule)?;
        let h = &integrator.history;
        let mut csv = std::io::BufWriter::new(
            fs::File::create(output.join("history.csv")).map_err(|e| e.to_string())?,
        );
        csv.write_all(CSV_HEADER.as_bytes())
            .map_err(|e| e.to_string())?;
        csv.write_all(csv_row(h, &primary.state, &primary)?.as_bytes())
            .and_then(|_| csv.flush())
            .map_err(|e| e.to_string())?;
        let mut next_output = 1;
        while primary.state.ln_a < h.config.end {
            // The primary target is always the physical final endpoint, never an
            // output target. The core alone caps each step at physical events.
            let left = primary.clone();
            primary = match integrator.advance_one(&left, h.config.end) {
                Ok(next) => next,
                Err(error) => {
                    failure_scope = "primary";
                    let message = error.to_string();
                    failed_attempt = Some(*error.diagnostics);
                    return Err(message);
                }
            };
            while next_output < schedule.times.len() {
                let target = schedule.times[next_output];
                if target > primary.state.ln_a {
                    break;
                }
                if target <= left.state.ln_a {
                    failure_scope = "observation";
                    return Err("IGM_ADAPTIVE_OUTPUT_NO_REPRESENTABLE_PROGRESS".into());
                }
                if target == primary.state.ln_a {
                    work.endpoint_reuses += 1;
                    csv.write_all(csv_row(h, &primary.state, &primary)?.as_bytes())
                        .map_err(|e| e.to_string())?;
                } else {
                    work.samples += 1;
                    // Deliberately do not chain probes. Every target in this main
                    // interval starts from the SAME immutable left state.
                    let sample = match integrator.advance_to(&left, target) {
                        Ok(sample) => sample,
                        Err(error) => {
                            failure_scope = "observation";
                            work.add(target, &left.diagnostics, &error.diagnostics);
                            let message = error.to_string();
                            failed_attempt = Some(*error.diagnostics);
                            return Err(message);
                        }
                    };
                    work.add(target, &left.diagnostics, &sample.diagnostics);
                    csv.write_all(csv_row(h, &sample.state, &primary)?.as_bytes())
                        .map_err(|e| e.to_string())?;
                }
                csv.flush().map_err(|e| e.to_string())?;
                next_output += 1;
            }
            write_status(&output, &primary, &work, false, None, None, None)?;
        }
        if next_output != schedule.times.len() {
            return Err("IGM_ADAPTIVE_MISSING_OUTPUT".into());
        }
        Ok(())
    })();
    // These files always describe the last accepted primary state, including
    // when a later primary attempt or an independent observation branch fails.
    let saved = write_primary(&output, &integrator.history, &primary);
    let final_result = result.and(saved);
    write_status(
        &output,
        &primary,
        &work,
        final_result.is_ok(),
        final_result.as_ref().err().map(String::as_str),
        final_result.as_ref().err().map(|_| failure_scope),
        failed_attempt.as_ref(),
    )?;
    final_result
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
