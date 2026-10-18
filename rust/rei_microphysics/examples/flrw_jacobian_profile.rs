//! One fixed-fixture whole chemical-stage serial/parallel comparison. Not a history.
use rei_microphysics::axbi_driver::{compiled_identity, Driver, DriverConfig, DriverState};
use std::{error::Error, fs, path::Path, time::Instant};
type Result<T> = std::result::Result<T, Box<dyn Error>>;
fn cpu_ticks() -> Result<u64> {
    let text = fs::read_to_string("/proc/self/stat")?;
    let words: Vec<_> = text
        .rsplit_once(')')
        .ok_or("proc stat")?
        .1
        .split_whitespace()
        .collect();
    Ok(words[11].parse::<u64>()? + words[12].parse::<u64>()?)
}
fn state_words(s: &DriverState) -> Vec<u64> {
    let mut out = Vec::new();
    let l = &s.ledgers;
    for v in [
        s.a,
        s.gas.w_erg_per_h,
        s.next_dln_a,
        s.max_newton_residual,
        s.last_error,
        s.wall_elapsed_s,
        l.source_n,
        l.source_u,
        l.absorbed_n,
        l.escaped_u,
        l.boundary_n,
        l.boundary_u,
        l.thermal_work,
        l.photon_work,
        l.cmb_input,
        l.dr_events,
        l.ce_cap_ev,
        l.excluded_dr_ev,
    ] {
        out.push(v.to_bits());
    }
    for values in [
        &s.gas.fractions[..],
        &l.rr_events[..],
        &l.ci_events[..],
        &l.photo_events[..],
        &l.ci_floor_events[..],
        &s.photons[..],
        &s.photon_energy_ref[..],
        &s.photon_support_lo[..],
        &s.photon_support_hi[..],
        &s.photon_inactive_number[..],
        &s.photon_inactive_energy_ref[..],
    ] {
        out.push(values.len() as u64);
        out.extend(values.iter().map(|v| v.to_bits()));
    }
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
    out
}
fn guard(start: Instant) -> Result<()> {
    if start.elapsed().as_secs_f64() > 55.0 {
        Err("diagnostic wall cap".into())
    } else {
        Ok(())
    }
}
fn main() -> Result<()> {
    let started = Instant::now();
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 3 {
        return Err("CONFIG CHECKPOINT FRESH_OUTPUT".into());
    }
    let out = Path::new(&args[2]);
    fs::create_dir(out)?;
    let input = fs::read_to_string(&args[0])?;
    let mut config = DriverConfig::read(&input)?;
    config.transport_threads = 8;
    config.max_rhs = 10000;
    config.parallel_jacobian_columns = false;
    let (mut driver, _) = Driver::new(config)?;
    let fixture = driver.read_checkpoint(Path::new(&args[1]))?;
    let earlier = fixture.a * (-fixture.next_dln_a).exp();
    let dt = driver
        .background
        .interval_increment(earlier, fixture.a)?
        .proper_time_s;
    fs::copy(&args[0], out.join("input_config.cfg"))?;
    fs::copy(&args[1], out.join("input_checkpoint.txt"))?;
    fs::write(out.join("source_identity.txt"), compiled_identity())?;
    fs::write(
        out.join("profile_source.rs"),
        include_str!("flrw_jacobian_profile.rs"),
    )?;
    let effective_base = input
        .lines()
        .filter(|line| {
            !line.starts_with("transport_threads=")
                && !line.starts_with("parallel_jacobian_columns=")
                && !line.starts_with("max_rhs=")
        })
        .collect::<Vec<_>>()
        .join("\n");
    let mut counter = 0;
    let mut records = Vec::new();
    let mut reference = None;
    let mut stage_debits = Vec::new();
    let mut wall_sums = Vec::new();
    for (label, parallel) in [("serial", false), ("parallel", true)] {
        guard(started)?;
        driver.config.parallel_jacobian_columns = parallel;
        fs::write(out.join(format!("effective_{label}.cfg")), format!("{effective_base}\ntransport_threads=8\nmax_rhs=10000\nparallel_jacobian_columns={parallel}\n"))?;
        let before = counter;
        let mut warm_states = Vec::new();
        for _ in 0..4 {
            guard(started)?;
            let mut state = fixture.clone();
            let debit = counter;
            driver.chemical_stage(&mut state, dt, &mut counter)?;
            stage_debits.push(counter - debit);
            warm_states.push(state);
        }
        let warm_rhs = counter - before;
        let before_timed = counter;
        let before_ticks = cpu_ticks()?;
        let timed = Instant::now();
        let mut states = Vec::with_capacity(32);
        let mut kernel_wall = 0.0;
        for _ in 0..32 {
            guard(started)?;
            let mut state = fixture.clone();
            let debit = counter;
            let kernel = Instant::now();
            driver.chemical_stage(&mut state, dt, &mut counter)?;
            kernel_wall += kernel.elapsed().as_secs_f64();
            stage_debits.push(counter - debit);
            states.push(state);
        }
        let phase_wall = timed.elapsed().as_secs_f64();
        let phase_ticks = cpu_ticks()? - before_ticks;
        let mut mode_words = None;
        for state in warm_states.iter().chain(states.iter()) {
            let words = state_words(state);
            if let Some(expected) = &reference {
                if &words != expected {
                    return Err("whole chemical-stage state/ledger/control bit mismatch".into());
                }
            } else {
                reference = Some(words.clone());
            }
            mode_words = Some(words);
        }
        fs::write(
            out.join(format!("{label}_state_words.json")),
            format!("{:?}\n", mode_words.unwrap()),
        )?;
        wall_sums.push(kernel_wall);
        records.push(format!(r#"{{"mode":"{label}","parallel_jacobian_columns":{parallel},"shared_workers":8,"warmup_stages":4,"timed_stages":32,"warmup_rhs":{warm_rhs},"timed_rhs":{},"chemical_stage_wall_s_sum":{kernel_wall},"timed_region_wall_s":{phase_wall},"timed_region_process_cpu_ticks":{phase_ticks}}}"#,counter-before_timed));
    }
    let summary = format!(
        r#"{{"kind":"source006_fixed_fixture_whole_chemical_stage_not_history","proper_dt_s":{dt},"checkpoint_accepted":{},"combined_actual_rhs":{counter},"combined_rhs_cap":10000,"all72_stage_states_ledgers_controls_f64_bits_equal":true,"rhs_per_stage":{stage_debits:?},"serial_over_parallel_stage_wall_ratio":{},"timing_scope":"chemical_stage wall sum excludes fixture cloning and result parity; process CPU ticks cover32stage region including clones/result retention; warmups excluded","records":[{}],"diagnostic_wall_s":{}}}"#,
        fixture.accepted,
        wall_sums[0] / wall_sums[1],
        records.join(","),
        started.elapsed().as_secs_f64()
    );
    fs::write(out.join("profile.json"), &summary)?;
    println!("{summary}");
    Ok(())
}
