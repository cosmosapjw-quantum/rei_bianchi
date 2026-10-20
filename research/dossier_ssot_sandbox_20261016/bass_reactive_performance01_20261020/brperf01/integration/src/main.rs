use parent::deuterium_thermal_coupling::CxOwnership;
use parent::igm_rates::igm_rates;
use parent::rate_table::{igm_branch_knots, igm_flat};
use rei_brperf01_integration::*;
use std::{
    env, fs,
    hint::black_box,
    io::{self, Write},
    path::Path,
    time::Instant,
};

type AnyResult<T> = Result<T, Box<dyn std::error::Error>>;
fn err(e: impl std::fmt::Debug) -> io::Error {
    io::Error::other(format!("{e:?}"))
}

fn main() {
    if let Err(error) = execute() {
        eprintln!("integration failure: {error}");
        std::process::exit(2);
    }
}
fn execute() -> AnyResult<()> {
    let args: Vec<_> = env::args().collect();
    if args.len() < 3 {
        return Err(err(
            "usage: integration OUT science|bench|baseline [compact_nodes] [iterations] [pairs]",
        )
        .into());
    }
    let out = Path::new(&args[1]);
    fs::create_dir_all(out)?;
    let nodes = args.get(3).map(|x| x.parse()).transpose()?.unwrap_or(8193);
    let tables = Tables::build(nodes).map_err(err)?;
    tables.setup_csv(&mut fs::File::create(out.join("SETUP.csv"))?)?;
    match args[2].as_str() {
        "science" => {
            histories(out, &tables, false)?;
            points(out, &tables)?;
        }
        "baseline" => histories(out, &tables, true)?,
        "bench" => benchmark(
            out,
            &tables,
            args.get(4).map(|x| x.parse()).transpose()?.unwrap_or(32768),
            args.get(5).map(|x| x.parse()).transpose()?.unwrap_or(6),
        )?,
        _ => return Err(err("unknown integration stage").into()),
    }
    Ok(())
}

fn histories(out: &Path, tables: &Tables, baseline_only: bool) -> AnyResult<()> {
    let mut records = io::BufWriter::new(fs::File::create(out.join("HISTORIES.csv"))?);
    writeln!(
        records,
        "case,backend,nsteps,step,status,temperature,binding,total_energy,energy_relative_residual,requested_span_s,{STATE_HEADER},{BUDGET_HEADER}"
    )?;
    let mut plans = fs::File::create(out.join("HISTORY_STATUS.csv"))?;
    writeln!(
        plans,
        "case,backend,nsteps,accepted,status,error,direct_reuse_bit_parity"
    )?;
    for case in CASES {
        for steps in [48, 96, 192] {
            let (original, conf) =
                history(tables, Backend::Original, case, steps, false).map_err(err)?;
            let original_bits = history_bits(&original);
            write_history(&mut records, case, Backend::Original, &original, &conf)?;
            writeln!(
                plans,
                "{},{},{},{},{},{:?},NA",
                case.name,
                Backend::Original.name(),
                steps,
                original.accepted(),
                original.status(),
                original.failure
            )?;
            for backend in Backend::all()
                .into_iter()
                .filter(|b| *b != Backend::Original)
            {
                if baseline_only && backend != Backend::ReusedDirect {
                    continue;
                }
                let (trial, c) = history(tables, backend, case, steps, false).map_err(err)?;
                let parity = if backend == Backend::ReusedDirect {
                    let equal =
                        trial.failure == original.failure && history_bits(&trial) == original_bits;
                    if !equal {
                        return Err(err("original versus reused direct history parity").into());
                    }
                    "PASS"
                } else {
                    "NOT_REQUIRED_TABLE_APPROXIMATION"
                };
                write_history(&mut records, case, backend, &trial, &c)?;
                writeln!(
                    plans,
                    "{},{},{},{},{},{:?},{parity}",
                    case.name,
                    backend.name(),
                    steps,
                    trial.accepted(),
                    trial.status(),
                    trial.failure
                )?;
                println!(
                    "{} {} Nt={} accepted={} status={}",
                    case.name,
                    backend.name(),
                    steps,
                    trial.accepted(),
                    trial.status()
                );
            }
            println!(
                "{} original Nt={} accepted={} status={}",
                case.name,
                steps,
                original.accepted(),
                original.status()
            );
        }
    }
    // A separate deliberately exhausted-work control is not a convergence row.
    let mut work = fs::File::create(out.join("WORK_LIMIT_CONTROL.csv"))?;
    writeln!(work, "case,backend,nsteps,accepted,status,error")?;
    for backend in Backend::all() {
        let (h, _) = history(tables, backend, CASES[1], 48, true).map_err(err)?;
        if h.status() != "CX_WORK_LIMIT" || h.accepted() != 0 {
            return Err(err("work limit classification changed").into());
        }
        writeln!(
            work,
            "{},{},48,0,{},\"{:?}\"",
            CASES[1].name,
            backend.name(),
            h.status(),
            h.failure
        )?;
    }
    records.flush()?;
    Ok(())
}

fn points(out: &Path, tables: &Tables) -> AnyResult<()> {
    let lo = 2.7_f64.next_up();
    let hi = 200000.0_f64.next_down();
    let mut temperatures = vec![lo, hi];
    for i in 0..1024 {
        let coordinate = (i as f64 + 0.3141592653589793) / 1024.0;
        temperatures.push((lo.ln() + (hi.ln() - lo.ln()) * coordinate).exp());
    }
    for knot in igm_branch_knots() {
        temperatures.extend([knot.next_down(), knot, knot.next_up()]);
    }
    temperatures.sort_by(f64::total_cmp);
    temperatures.dedup_by(|a, b| a.to_bits() == b.to_bits());
    let mut coeff = io::BufWriter::new(fs::File::create(out.join("POINT_COEFFICIENTS.csv"))?);
    writeln!(
        coeff,
        "point,T_requested,T_eos,backend,channel,reference,value,relative_error"
    )?;
    let mut rhs = io::BufWriter::new(fs::File::create(out.join("POINT_RHS.csv"))?);
    writeln!(
        rhs,
        "point,T_eos,backend,field,reference,value,absolute_error"
    )?;
    for (i, t) in temperatures.into_iter().enumerate() {
        let (s, mut c) = fixture(t).map_err(err)?;
        c.use_cx = false;
        c.owner = CxOwnership::AtomicRhs;
        let te = s.gas.eos().map_err(err)?.temperature_k;
        let reference = igm_flat(igm_rates(te).map_err(err)?);
        let original = tables.rhs(Backend::Original, &s, &c).map_err(err)?;
        let original_values = rhs_values(&original);
        for backend in Backend::all()
            .into_iter()
            .filter(|b| *b != Backend::Original)
        {
            let values = igm_flat(tables.rates(backend, te).map_err(err)?);
            for channel in 0..15 {
                let re = if reference[channel] == 0.0 {
                    if values[channel] == 0.0 {
                        0.0
                    } else {
                        f64::INFINITY
                    }
                } else {
                    (values[channel] - reference[channel]) / reference[channel]
                };
                if !re.is_finite() {
                    return Err(err("structural zero changed").into());
                }
                writeln!(
                    coeff,
                    "{i},{t:.17e},{te:.17e},{},{},{:.17e},{:.17e},{re:.17e}",
                    backend.name(),
                    RATE_LABELS[channel],
                    reference[channel],
                    values[channel]
                )?;
            }
            let r = tables.rhs(backend, &s, &c).map_err(err)?;
            let row = rhs_values(&r);
            if backend == Backend::ReusedDirect
                && row
                    .iter()
                    .map(|v| v.to_bits())
                    .ne(original_values.iter().map(|v| v.to_bits()))
            {
                return Err(err("point direct parity").into());
            }
            for (field, (reference, value)) in original_values.iter().zip(row).enumerate() {
                writeln!(
                    rhs,
                    "{i},{te:.17e},{},{field},{reference:.17e},{value:.17e},{:.17e}",
                    backend.name(),
                    value - reference
                )?;
            }
        }
    }
    coeff.flush()?;
    rhs.flush()?;
    let (s, mut c) = fixture(60000.0).map_err(err)?;
    c.use_cx = false;
    c.owner = CxOwnership::AtomicRhs;
    let t = s.gas.eos().map_err(err)?.temperature_k;
    let rate = igm_rates(t).map_err(err)?;
    let original = rhs_values(&native::rhs_with_rates(&s, &c, t, &rate).map_err(err)?);
    let mut influence = fs::File::create(out.join("CHANNEL_INFLUENCE.csv"))?;
    writeln!(influence, "channel,T_eos,multiplier,changed_rhs_fields")?;
    for (channel, label) in RATE_LABELS.iter().enumerate() {
        let mut altered = rate;
        perturb_channel(&mut altered, channel, 1.01);
        let result = rhs_values(&native::rhs_with_rates(&s, &c, t, &altered).map_err(err)?);
        let changed = original
            .iter()
            .zip(result)
            .filter(|(a, b)| a.to_bits() != b.to_bits())
            .count();
        if changed == 0 {
            return Err(err(format!("unused coefficient {label}")).into());
        }
        writeln!(influence, "{label},{t:.17e},1.01,{changed}")?;
    }
    Ok(())
}

fn benchmark(out: &Path, tables: &Tables, iterations: usize, pairs: usize) -> AnyResult<()> {
    if iterations < 128 || !(2..=32).contains(&pairs) {
        return Err(err("benchmark bounds").into());
    }
    let mut states = Vec::new();
    for i in 0..64 {
        let t = (100.0_f64.ln() + (180000.0_f64.ln() - 100.0_f64.ln()) * (i as f64 + 0.37) / 64.0)
            .exp();
        let (s, mut c) = fixture(t).map_err(err)?;
        c.use_cx = false;
        c.owner = CxOwnership::AtomicRhs;
        states.push((s, c));
    }
    let mut file = fs::File::create(out.join("RHS_TIMINGS.csv"))?;
    writeln!(
        file,
        "session,pair,comparison,position,backend,iterations,seconds,checksum"
    )?;
    let mut measured =
        |pair: usize, comparison: &str, position: usize, backend: Backend| -> AnyResult<()> {
            let mut checksum = 0u64;
            let start = Instant::now();
            for i in 0..iterations {
                let (s, c) = &states[i % states.len()];
                let r = black_box(
                    tables
                        .rhs(black_box(backend), black_box(s), black_box(c))
                        .map_err(err)?,
                );
                checksum = checksum.rotate_left(3).wrapping_add(0x9e37_79b9_7f4a_7c15)
                    ^ r.budget_per_s.thermal_change_j_m3.to_bits()
                    ^ r.nuclei_per_s[1].to_bits();
            }
            let duration = start.elapsed().as_secs_f64();
            writeln!(
                file,
                "{},{pair},{comparison},{position},{},{iterations},{duration:.17e},{checksum:016x}",
                std::process::id(),
                backend.name()
            )?;
            file.flush()?;
            Ok(())
        };
    for backend in Backend::all() {
        measured(0, "WARMUP", 0, backend)?;
        measured(1, "WARMUP", 1, backend)?;
    }
    for trial in Backend::all()
        .into_iter()
        .filter(|b| *b != Backend::Original)
    {
        for pair in 0..pairs {
            let sequence = if pair % 2 == 0 {
                [Backend::Original, trial, trial, Backend::Original]
            } else {
                [trial, Backend::Original, Backend::Original, trial]
            };
            for (position, backend) in sequence.into_iter().enumerate() {
                measured(pair, trial.name(), position, backend)?;
            }
        }
    }
    for pair in 0..3 {
        measured(pair, "AA_CONTROL", 0, Backend::Original)?;
        measured(pair, "AA_CONTROL", 1, Backend::Original)?;
    }
    Ok(())
}
