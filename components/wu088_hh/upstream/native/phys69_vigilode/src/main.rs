use std::{fs, io::Write, path::Path, process::ExitCode, time::Instant};
use sha2::{Digest, Sha256};
use wu088_hh_phys69_vigilode::{
    B, D2_SCALE, FROZEN_SOURCE_SHA256, K, Q_SCALE, Request, T,
    TARGET_A, TARGET_B, UPSTREAM_COMMIT, get, parse_seed, solve,
};

fn digest(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }

fn run() -> Result<bool, Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args == ["--help"] {
        println!("wu088-hh-phys69-vigilode REQUEST_JSON SEED_TEXT FROZEN_NPZ\nComplete and partial results are JSON; partial/error exits nonzero. Fixed B=27,T=65,k=7/10,m=0,target=(21,20). Binary64 diagnostics; HH_R10=OFF.");
        return Ok(true);
    }
    if args.len() != 3 { return Err("usage: wu088-hh-phys69-vigilode REQUEST_JSON SEED_TEXT FROZEN_NPZ".into()); }
    let request_bytes = fs::read(&args[0])?;
    let request: Request = serde_json::from_slice(&request_bytes)?;
    request.validate()?;
    let source_bytes = fs::read(Path::new(&args[2]))?;
    let source_sha = digest(&source_bytes);
    if source_sha != FROZEN_SOURCE_SHA256 { return Err("original frozen source bytes mismatch".into()); }
    let seed_bytes = fs::read(&args[1])?;
    let seed = parse_seed(std::str::from_utf8(&seed_bytes)?, request.lmax)?;
    let started = Instant::now();
    let result = solve(&request, &seed)?;
    let elapsed = started.elapsed().as_secs_f64();
    let n = request.lmax + 1;
    let observed = &result.observed;
    let complete = observed.success && observed.t == [0.0, T-B]
        && observed.y.len() == 2
        && observed.y.iter().all(|y| y.len() == 2*(4*n+1) && y.iter().all(|x| x.is_finite()));
    let endpoint = if complete {
        let y = &observed.y[1];
        let d2 = get(y, 4*n) / D2_SCALE;
        let d1a = get(y, 2*n+TARGET_B) / Q_SCALE;
        let d1b = get(y, 3*n+TARGET_A) / Q_SCALE;
        let drift = (0..n).map(|j| (get(y,j)-1.0).norm()).fold(0.0_f64,f64::max);
        Some(serde_json::json!({
            "d2": {"real": d2.re, "imag": d2.im},
            "d1_q21_20": {"real": d1a.re, "imag": d1a.im},
            "d1_q20_21": {"real": d1b.re, "imag": d1b.im},
            "normalization_drift_max_abs_F_B_minus_1": drift,
        }))
    } else { None };
    let payload = serde_json::json!({
        "schema":"PHYS69_VIGILODE_RESULT_V1",
        "status":if complete {"COMPLETED_BINARY64_REFERENCE_NOT_CERTIFICATE"} else {"PARTIAL_INTEGRATION"},
        "complete":complete,"request":request,"request_sha256":digest(&request_bytes),
        "upstream_commit":UPSTREAM_COMMIT,"source_sha256":source_sha,"seed_sha256":digest(&seed_bytes),
        "B":B,"T":T,"k":K,"eta_C":"-10/7","m":0,"target":[21,20],
        "clock":"tau=65-r;0..38","q_scale":"2^80","d2_scale":"2^160",
        "endpoint":endpoint,"observed_times_tau":observed.t,"observed_states_scaled":observed.y,
        "message":observed.message,"attempts":result.attempts,"accepted_steps":result.accepted_steps,
        "rejected_steps":result.rejected_steps,"state_reuses":result.state_reuses,
        "driver":result.driver,"krylov_workspace":result.krylov_workspace,
        "internal_steps":observed.internal_steps,"output_clipped_steps":observed.output_clipped_steps,
        "counters":observed.counters,"integration_elapsed_seconds":elapsed,
        "dense_interpolation_used":false,"assembled_jacobian_supplied":false,
        "analytic_jvp":true,"analytic_time_partial":true,"HH_R10":"OFF",
        "scientific_scope":"finite-L original external second Born coefficient; independent binary64 diagnostic; not original source-driven xi",
    });
    let mut stdout = std::io::stdout().lock();
    serde_json::to_writer_pretty(&mut stdout,&payload)?;
    stdout.write_all(b"\n")?;
    Ok(complete)
}

fn main() -> ExitCode {
    match run() {
        Ok(true) => ExitCode::SUCCESS,
        Ok(false) => ExitCode::FAILURE,
        Err(error) => { eprintln!("{}",serde_json::json!({"status":"ERROR","error":error.to_string(),"HH_R10":"OFF"})); ExitCode::FAILURE }
    }
}
