//! One bounded NCP sweep on an immutable populated V4 diagnostic fixture.
//! This is not a production resume or a scientific full-history run.
use rei_microphysics::axbi_covariant_transport::{
    AbsorptionResult, PhotonState, PreparedAbsorption,
};
use rei_microphysics::axbi_driver::{compiled_identity, Driver, DriverConfig, DriverState};
use std::error::Error;
use std::fs;
use std::io::{self, Write};
use std::path::Path;
use std::time::{Duration, Instant};

const WIDTHS: [usize; 4] = [1, 8, 32, 64];
const WARMUP: usize = 4;
const TIMED: usize = 32;
const WALL_CAP_S: f64 = 300.0;
const ACCEPTED_CAP: usize = 2000;
const RHS_CAP: usize = 100_000;
const OUTPUT_CAP: u64 = 2 * 1024 * 1024 * 1024;

type Result<T> = std::result::Result<T, Box<dyn Error>>;

struct Budget {
    started: Instant,
    accepted: usize,
    rhs: usize,
    output_bytes: u64,
}
impl Budget {
    fn check(&self) -> Result<()> {
        if self.started.elapsed().as_secs_f64() > WALL_CAP_S
            || self.accepted > ACCEPTED_CAP
            || self.rhs > RHS_CAP
        {
            return Err("HPC_BENCHMARK_AGGREGATE_CAP".into());
        }
        Ok(())
    }
    fn write(&mut self, path: &Path, bytes: &[u8]) -> Result<()> {
        self.check()?;
        let next = self
            .output_bytes
            .checked_add(bytes.len() as u64)
            .ok_or("HPC_BENCHMARK_OUTPUT_OVERFLOW")?;
        if next > OUTPUT_CAP || path.exists() {
            return Err("HPC_BENCHMARK_OUTPUT_CAP_OR_EXISTING_FILE".into());
        }
        fs::write(path, bytes)?;
        self.output_bytes = next;
        Ok(())
    }
}

fn photons(s: &DriverState) -> PhotonState {
    PhotonState {
        number: s.photons.clone(),
        energy_ref: s.photon_energy_ref.clone(),
        support_lo: s.photon_support_lo.clone(),
        support_hi: s.photon_support_hi.clone(),
    }
}

fn push_floats(words: &mut Vec<u64>, xs: &[f64]) {
    words.extend(xs.iter().map(|x| x.to_bits()));
}

/// Complete DriverState physics/control data, excluding only wall_elapsed_s.
/// Include cosmological proper time/geometry (derived by the exact background).
fn state_words(d: &Driver, s: &DriverState) -> Result<Vec<u64>> {
    let p = d.background.point_at_scale(s.a)?;
    let mut out = Vec::new();
    push_floats(&mut out, &[s.a, p.time_s, p.b]);
    push_floats(&mut out, &s.gas.fractions);
    push_floats(
        &mut out,
        &[
            s.gas.w_erg_per_h,
            s.next_dln_a,
            s.max_newton_residual,
            s.last_error,
        ],
    );
    out.extend(
        [
            s.accepted,
            s.attempts,
            s.comparisons,
            s.rejects,
            s.consecutive_rejects,
            s.rhs_evaluations,
        ]
        .map(|v| v as u64),
    );
    let l = &s.ledgers;
    push_floats(
        &mut out,
        &[
            l.source_n,
            l.source_u,
            l.absorbed_n,
            l.escaped_u,
            l.boundary_n,
            l.boundary_u,
            l.thermal_work,
            l.photon_work,
            l.cmb_input,
        ],
    );
    for xs in [&l.rr_events, &l.ci_events, &l.photo_events] {
        push_floats(&mut out, xs);
    }
    push_floats(&mut out, &[l.dr_events]);
    push_floats(&mut out, &l.ci_floor_events);
    push_floats(&mut out, &[l.ce_cap_ev, l.excluded_dr_ev]);
    for xs in [
        &s.photons,
        &s.photon_energy_ref,
        &s.photon_support_lo,
        &s.photon_support_hi,
        &s.photon_inactive_number,
        &s.photon_inactive_energy_ref,
    ] {
        out.push(xs.len() as u64);
        push_floats(&mut out, xs);
    }
    Ok(out)
}

fn absorption_words(p: &PreparedAbsorption, r: &AbsorptionResult) -> Vec<u64> {
    let mut out = vec![p.node_count() as u64];
    let q = p.diagnostics;
    push_floats(
        &mut out,
        &[
            q.max_count_relative_defect,
            q.max_energy_relative_defect,
            q.omitted_tail_number_bound_per_h,
            q.omitted_tail_energy_bound_ev_per_h,
            q.omitted_tail_endpoint_moment_bound_ev_per_h,
            q.max_asymptotic_mean_defect_ev,
        ],
    );
    push_floats(&mut out, &r.photo.gamma_s);
    push_floats(&mut out, &r.photo.heat_erg_per_absorber_s);
    push_floats(&mut out, &r.absorbed_per_h);
    push_floats(&mut out, &[r.binding_ev_per_h, r.heat_ev_per_h]);
    for xs in [
        &r.state.number,
        &r.state.energy_ref,
        &r.state.support_lo,
        &r.state.support_hi,
    ] {
        out.push(xs.len() as u64);
        push_floats(&mut out, xs);
    }
    out
}

fn require_equal(label: &str, a: &[u64], b: &[u64]) -> Result<()> {
    if a != b {
        let first = a
            .iter()
            .zip(b)
            .position(|(x, y)| x != y)
            .unwrap_or(a.len().min(b.len()));
        return Err(format!(
            "HPC_BITWISE_MISMATCH {label} first_word={first} lengths={}/{}",
            a.len(),
            b.len()
        )
        .into());
    }
    Ok(())
}

fn words_json(xs: &[u64]) -> String {
    format!(
        "[{}]",
        xs.iter()
            .map(|x| format!("\"{x:016x}\""))
            .collect::<Vec<_>>()
            .join(",")
    )
}

fn checksum(xs: &[u64]) -> String {
    // A compact non-cryptographic aid; complete words are also preserved.
    let mut value = 0xcbf29ce484222325_u64;
    for x in xs {
        for byte in x.to_le_bytes() {
            value ^= u64::from(byte);
            value = value.wrapping_mul(0x100000001b3);
        }
    }
    format!("{value:016x}")
}

fn quoted(s: &str) -> String {
    let mut out = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c.is_control() => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

/// Linux process-group CPU ticks, including worker threads. Conversion to
/// seconds/core-hours requires the external runner's actual CLK_TCK value.
fn cpu_ticks() -> Option<u64> {
    let text = fs::read_to_string("/proc/self/stat").ok()?;
    let rest = text
        .rsplit_once(')')?
        .1
        .split_whitespace()
        .collect::<Vec<_>>();
    let user = rest.get(11)?.parse::<u64>().ok()?;
    let system = rest.get(12)?.parse::<u64>().ok()?;
    user.checked_add(system)
}
fn tick_delta(before: Option<u64>, after: Option<u64>) -> Option<u64> {
    after?.checked_sub(before?)
}
fn option_u64(v: Option<u64>) -> String {
    v.map(|x| x.to_string()).unwrap_or_else(|| "null".into())
}

struct KernelCheck {
    bits: Vec<u64>,
    nodes: usize,
    capacity: usize,
    legacy_prepare_wall: f64,
    pool_prepare_wall: f64,
}
fn kernel_check(d: &Driver, s: &DriverState) -> Result<KernelCheck> {
    let geometry = d.background.point_at_scale(s.a)?.geometry()?;
    let input = photons(s);
    let start = Instant::now();
    let legacy = d.transport.prepare_legacy_serial(&input, &geometry)?;
    let legacy_prepare_wall = start.elapsed().as_secs_f64();
    let start = Instant::now();
    let prepared = d.transport.prepare(&input, &geometry)?;
    let pool_prepare_wall = start.elapsed().as_secs_f64();
    let nh = d.n_h0_cm3 / s.a.powi(3);
    let nhe = d.n_he0_cm3 / s.a.powi(3);
    let [x, y, z] = s.gas.fractions;
    let absorbers = [nh * (1.0 - x), nhe * (1.0 - y - z), nhe * y];
    let endpoint = (s.a * s.next_dln_a.exp()).min(1.0 / (1.0 + d.config.end_zbar));
    if endpoint <= s.a {
        return Err("HPC_FIXTURE_AT_ENDPOINT".into());
    }
    let dt = d
        .background
        .interval_increment(s.a, endpoint)?
        .proper_time_s;
    let mut bits = Vec::new();
    // Zero-duration Gamma/heat and finite BE event/survivor results both count.
    for duration in [0.0, dt] {
        let old = legacy.evaluate(absorbers, nh, duration)?;
        let new = prepared.evaluate(absorbers, nh, duration)?;
        let old_words = absorption_words(&legacy, &old);
        let new_words = absorption_words(&prepared, &new);
        require_equal("legacy_serial_vs_selected_prepare", &old_words, &new_words)?;
        bits.extend(old_words);
    }
    Ok(KernelCheck {
        bits,
        nodes: prepared.node_count(),
        capacity: prepared.buffer_capacity_bytes(),
        legacy_prepare_wall,
        pool_prepare_wall,
    })
}

struct Evolution {
    state: DriverState,
    trace: Vec<u64>,
    kernel_wall: Duration,
    region_wall: f64,
    cpu_ticks: Option<u64>,
}
fn evolve(
    d: &mut Driver,
    fixture: &DriverState,
    target: usize,
    budget: &mut Budget,
) -> Result<Evolution> {
    let mut s = fixture.clone();
    let mut trace = Vec::new();
    let mut kernel_wall = Duration::ZERO;
    let region_started = Instant::now();
    let cpu_before = cpu_ticks();
    let mut accepted = 0;
    while accepted < target {
        budget.check()?;
        if budget.accepted >= ACCEPTED_CAP || budget.rhs >= RHS_CAP {
            return Err("HPC_BENCHMARK_COUNTER_CAP".into());
        }
        d.config.max_rhs = s
            .rhs_evaluations
            .checked_add(RHS_CAP - budget.rhs)
            .ok_or("HPC_RHS_COUNTER_OVERFLOW")?;
        d.config.max_steps = s
            .accepted
            .checked_add(ACCEPTED_CAP - budget.accepted)
            .ok_or("HPC_ACCEPTED_COUNTER_OVERFLOW")?;
        d.config.max_attempts = s
            .attempts
            .checked_add(RHS_CAP - budget.rhs)
            .ok_or("HPC_ATTEMPTS_COUNTER_OVERFLOW")?;
        let before_rhs = s.rhs_evaluations;
        let before_accepted = s.accepted;
        let before_a = s.a;
        let started = Instant::now();
        let decision = d.adaptive_step(&mut s);
        kernel_wall += started.elapsed();
        // Count every actually launched RHS, including an erroneous trial.
        budget.rhs += s
            .rhs_evaluations
            .checked_sub(before_rhs)
            .ok_or("HPC_RHS_COUNTER_BACKTRACK")?;
        budget.accepted += s
            .accepted
            .checked_sub(before_accepted)
            .ok_or("HPC_ACCEPTED_COUNTER_BACKTRACK")?;
        budget.check()?;
        let decision = decision?;
        trace.push(u64::from(decision));
        let words = state_words(d, &s)?;
        trace.push(words.len() as u64);
        trace.extend(words);
        if decision {
            if s.accepted != before_accepted + 1 || s.a <= before_a {
                return Err("HPC_BENCHMARK_NOT_A_NEW_ACCEPTED_STEP".into());
            }
            accepted += 1;
        }
    }
    let after = cpu_ticks();
    Ok(Evolution {
        state: s,
        trace,
        kernel_wall,
        region_wall: region_started.elapsed().as_secs_f64(),
        cpu_ticks: tick_delta(cpu_before, after),
    })
}

fn state_buffer_capacity(s: &DriverState) -> usize {
    [
        &s.photons,
        &s.photon_energy_ref,
        &s.photon_support_lo,
        &s.photon_support_hi,
        &s.photon_inactive_number,
        &s.photon_inactive_energy_ref,
    ]
    .iter()
    .map(|v| v.capacity() * std::mem::size_of::<f64>())
    .sum()
}

fn event(kind: &str, width: usize, elapsed: f64) -> Result<()> {
    println!(
        "{{\"kind\":{},\"width\":{width},\"elapsed_global_s\":{elapsed}}}",
        quoted(kind)
    );
    io::stdout().flush()?;
    Ok(())
}

fn run(config: &Path, checkpoint: &Path, output: &Path) -> Result<()> {
    let mut budget = Budget {
        started: Instant::now(),
        accepted: 0,
        rhs: 0,
        output_bytes: 0,
    };
    if std::thread::available_parallelism()?.get() < 64 {
        return Err("HPC_SWEEP_REQUIRES_OBSERVED_64_CPU_AFFINITY".into());
    }
    fs::create_dir(output)?;
    let config_bytes = fs::read(config)?;
    let checkpoint_bytes = fs::read(checkpoint)?;
    if !checkpoint_bytes.starts_with(b"AXBI_CHECKPOINT_V4\n") {
        return Err("HPC_SWEEP_REQUIRES_ORIGINAL_V4_FIXTURE".into());
    }
    let text = std::str::from_utf8(&config_bytes)?;
    let original_config = DriverConfig::read(text)?;
    if !original_config.inactive_hi_split || original_config.q_ref != 0.0 {
        return Err("HPC_SWEEP_REQUIRES_EXPLICIT_FLRW_INACTIVE_FIXTURE_CONFIG".into());
    }
    budget.write(&output.join("input_config.cfg"), &config_bytes)?;
    budget.write(&output.join("input_checkpoint.txt"), &checkpoint_bytes)?;
    budget.write(
        &output.join("source_identity.txt"),
        compiled_identity().as_bytes(),
    )?;
    budget.write(
        &output.join("benchmark_source.rs"),
        include_bytes!("axbi_hpc_scaling.rs"),
    )?;
    let mut reference_initial: Option<Vec<u64>> = None;
    let mut reference_kernel: Option<Vec<u64>> = None;
    let mut reference_warmup: Option<Vec<u64>> = None;
    let mut reference_trace: Option<Vec<u64>> = None;
    let mut reference_final: Option<Vec<u64>> = None;
    let mut serial_wall = 0.0;
    let mut records = Vec::new();
    for width in WIDTHS {
        budget.check()?;
        event("width_start", width, budget.started.elapsed().as_secs_f64())?;
        let setup_started = Instant::now();
        let mut cfg = original_config.clone();
        cfg.transport_threads = width;
        let (mut d, _) = Driver::new(cfg)?;
        if d.transport.transport_threads() != width {
            return Err("HPC_POOL_WIDTH_NOT_APPLIED".into());
        }
        // Explicit diagnostic initial state, never the production run/resume API.
        let fixture = d.read_checkpoint(&output.join("input_checkpoint.txt"))?;
        if !fixture.photons.iter().any(|&n| n > 0.0) {
            return Err("HPC_FIXTURE_MUST_HAVE_POPULATED_ACTIVE_CELLS".into());
        }
        let initial = state_words(&d, &fixture)?;
        if let Some(reference) = &reference_initial {
            require_equal("initial_fixture", reference, &initial)?;
        } else {
            reference_initial = Some(initial);
        }
        let setup_wall = setup_started.elapsed().as_secs_f64();
        let initial_kernel = kernel_check(&d, &fixture)?;
        if let Some(reference) = &reference_kernel {
            require_equal(
                "legacy_fixture_across_widths",
                reference,
                &initial_kernel.bits,
            )?;
        } else {
            reference_kernel = Some(initial_kernel.bits.clone());
        }
        let warmup = evolve(&mut d, &fixture, WARMUP, &mut budget)?;
        if let Some(reference) = &reference_warmup {
            require_equal(
                "warmup_decisions_complete_physics",
                reference,
                &warmup.trace,
            )?;
        } else {
            reference_warmup = Some(warmup.trace.clone());
        }
        // Restart the timed region from the identical original fixture, not
        // the warmup endpoint. Every width performs the same evolution.
        event("timed_start", width, budget.started.elapsed().as_secs_f64())?;
        let timed = evolve(&mut d, &fixture, TIMED, &mut budget)?;
        event("timed_end", width, budget.started.elapsed().as_secs_f64())?;
        let final_kernel = kernel_check(&d, &timed.state)?;
        let mut final_words = state_words(&d, &timed.state)?;
        final_words.extend_from_slice(&final_kernel.bits);
        let parity = (|| {
            if let Some(reference) = &reference_trace {
                require_equal(
                    "all_timed_decisions_complete_physics",
                    reference,
                    &timed.trace,
                )?;
            }
            if let Some(reference) = &reference_final {
                require_equal(
                    "complete_final_physics_Gamma_heat_events",
                    reference,
                    &final_words,
                )?;
            }
            Ok::<(), Box<dyn Error>>(())
        })();
        // Save complete evidence even if a first cross-width mismatch occurs.
        let trace_json = format!("{{\"kind\":\"complete_physics_words_after_every_adaptive_call\",\"encoding\":\"u64hex_f64bits_and_integer_counters\",\"wall_and_source_metadata_excluded\":true,\"warmup_trace\":{},\"timed_trace\":{}}}\n",words_json(&warmup.trace),words_json(&timed.trace));
        budget.write(
            &output.join(format!("width{width}_trace.json")),
            trace_json.as_bytes(),
        )?;
        let final_json = format!("{{\"width\":{width},\"encoding\":\"u64hex_f64bits_and_integer_counters\",\"noncryptographic_fnv1a64\":{},\"complete_final_physics_and_prepared_results\":{}}}\n",quoted(&checksum(&final_words)),words_json(&final_words));
        budget.write(
            &output.join(format!("width{width}_final_physics.json")),
            final_json.as_bytes(),
        )?;
        let checkpoint_path = output.join(format!("width{width}_final_checkpoint.txt"));
        d.save_checkpoint(&checkpoint_path, &timed.state)?;
        budget.output_bytes += fs::metadata(&checkpoint_path)?.len();
        if budget.output_bytes > OUTPUT_CAP {
            return Err("HPC_BENCHMARK_OUTPUT_CAP".into());
        }
        let parity_status = if parity.is_ok() {
            "PASS"
        } else {
            "FAIL_FIRST_MISMATCH"
        };
        let wall = timed.kernel_wall.as_secs_f64();
        if width == 1 {
            serial_wall = wall;
        }
        let speedup = serial_wall / wall;
        let eos = timed.state.gas.eos(
            d.n_h0_cm3 / timed.state.a.powi(3),
            d.n_he0_cm3 / timed.state.a.powi(3),
        )?;
        let (nr, ur) = d.residuals(&timed.state)?;
        let record = format!(concat!("{{\"width\":{},\"parity\":{},\"warmup_accepted\":{},\"timed_accepted\":{},",
            "\"setup_wall_s\":{},\"timed_adaptive_calls_wall_s\":{},\"timed_region_including_trace_wall_s\":{},",
            "\"timed_region_process_cpu_ticks\":{},\"speedup_vs_width1\":{},\"parallel_efficiency\":{},\"accepted_per_kernel_wall_s\":{},",
            "\"timed_attempts\":{},\"timed_comparisons\":{},\"timed_rejects\":{},\"timed_rhs\":{},",
            "\"fixture_cells\":{},\"fixture_occupied_active_cells\":{},\"fixture_prepared_nodes\":{},\"final_prepared_nodes\":{},",
            "\"fixture_prepared_capacity_bytes\":{},\"final_prepared_capacity_bytes\":{},\"state_buffer_capacity_bytes\":{},",
            "\"fixture_legacy_prepare_wall_s\":{},\"fixture_selected_prepare_wall_s\":{},",
            "\"final_a\":{},\"final_temperature_K\":{},\"number_residual_per_H\":{},\"energy_residual_eV_per_H\":{},\"final_noncryptographic_fnv1a64\":{}}}"),
            width,quoted(parity_status),WARMUP,TIMED,setup_wall,wall,timed.region_wall,option_u64(timed.cpu_ticks),speedup,speedup/(width as f64),(TIMED as f64)/wall,
            timed.state.attempts-fixture.attempts,timed.state.comparisons-fixture.comparisons,timed.state.rejects-fixture.rejects,timed.state.rhs_evaluations-fixture.rhs_evaluations,
            d.transport.cell_count(),fixture.photons.iter().filter(|&&x|x>0.0).count(),initial_kernel.nodes,final_kernel.nodes,
            initial_kernel.capacity,final_kernel.capacity,state_buffer_capacity(&timed.state),initial_kernel.legacy_prepare_wall,initial_kernel.pool_prepare_wall,
            timed.state.a,eos.temperature_k,nr,ur,quoted(&checksum(&final_words)));
        budget.write(
            &output.join(format!("width{width}_result.json")),
            record.as_bytes(),
        )?;
        records.push(record);
        if let Err(error) = parity {
            budget.write(
                &output.join("first_mismatch.json"),
                format!(
                    "{{\"width\":{width},\"error\":{}}}\n",
                    quoted(&error.to_string())
                )
                .as_bytes(),
            )?;
            return Err(error);
        }
        if reference_trace.is_none() {
            reference_trace = Some(timed.trace.clone());
        }
        if reference_final.is_none() {
            reference_final = Some(final_words);
        }
        event("width_end", width, budget.started.elapsed().as_secs_f64())?;
        // Driver/persistent pool drops here before the next width is created.
    }
    budget.check()?;
    let summary = format!(concat!("{{\"status\":\"COMPLETED_SWEEP_BITWISE_PARITY_PASS\",",
        "\"fixture_use\":\"IMMUTABLE_V4_DIAGNOSTIC_INITIAL_STATE_NOT_PRODUCTION_RESUME\",",
        "\"warmup_on_separate_fixture_clone\":true,\"timed_region_restarts_original_fixture\":true,",
        "\"legacy_direct_prepare_differential\":\"PASS_fixture_and_final_at_zero_and_finite_dt_each_width\",",
        "\"width1_trajectory_kernel\":\"retained_original_prepare_legacy_serial\",",
        "\"aggregate_accepted\":{},\"aggregate_actual_rhs\":{},\"elapsed_wall_s\":{},\"output_bytes_before_summary\":{},",
        "\"wall_cap_s\":300,\"accepted_cap\":2000,\"rhs_cap\":100000,\"output_cap_bytes\":2147483648,",
        "\"cpu_time_owner\":\"external_runner_records_CPU_seconds_RSS_and_CLK_TCK;raw_process_ticks_also_reported\",",
        "\"requested_executor\":\"lower_tier_benchmark_preparation\",\"observed_runtime_model\":\"not_independently_observed\",",
        "\"historical_tests_rerun\":false,\"scientific_history_admission\":\"NOT_ISSUED_BY_BENCHMARK\",\"results\":[{}]}}\n"),
        budget.accepted,budget.rhs,budget.started.elapsed().as_secs_f64(),budget.output_bytes,records.join(","));
    budget.write(&output.join("summary.json"), summary.as_bytes())?;
    println!("{summary}");
    Ok(())
}

fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 3 {
        return Err("usage: axbi_hpc_scaling CONFIG IMMUTABLE_V4_CHECKPOINT FRESH_OUTPUT".into());
    }
    run(
        Path::new(&args[0]),
        Path::new(&args[1]),
        Path::new(&args[2]),
    )
}
