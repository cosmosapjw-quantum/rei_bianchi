//! Static FT03 first canonical interval: atomic accepted trials and exact resume.
use rei_microphysics::{
    certified_ft03_trial, Ft03Events, Ft03Model, HHeState, Interval, RootSite, StepControl,
    FT03_MODEL_ID,
};
use std::{
    env,
    fmt::Write as FmtWrite,
    fs::{self, File, OpenOptions},
    io::{self, Write as IoWrite},
    path::{Path, PathBuf},
};

const INPUT: &str = include_str!(
    "../../../docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json"
);
// Exact compile-time source bytes are written once and compared before resume.
// This records accidental source changes without adding a hashing dependency.
fn source_identity() -> String {
    let mut out = String::from("REI_F05_SOURCE_V1\n");
    let parts = [
        (
            "rust/rei_microphysics/src/adaptive_history.rs",
            include_str!("../src/adaptive_history.rs"),
        ),
        (
            "rust/rei_microphysics/src/angular_photons.rs",
            include_str!("../src/angular_photons.rs"),
        ),
        (
            "rust/rei_microphysics/src/atomic_provider.rs",
            include_str!("../src/atomic_provider.rs"),
        ),
        (
            "rust/rei_microphysics/src/bianchi_i.rs",
            include_str!("../src/bianchi_i.rs"),
        ),
        (
            "rust/rei_microphysics/src/coverage.rs",
            include_str!("../src/coverage.rs"),
        ),
        (
            "rust/rei_microphysics/src/flrw_three_equations.rs",
            include_str!("../src/flrw_three_equations.rs"),
        ),
        (
            "rust/rei_microphysics/src/ft03_controlled.rs",
            include_str!("../src/ft03_controlled.rs"),
        ),
        (
            "rust/rei_microphysics/src/ft03_interval.rs",
            include_str!("../src/ft03_interval.rs"),
        ),
        (
            "rust/rei_microphysics/src/ft03_rates.rs",
            include_str!("../src/ft03_rates.rs"),
        ),
        (
            "rust/rei_microphysics/src/group_rates.rs",
            include_str!("../src/group_rates.rs"),
        ),
        (
            "rust/rei_microphysics/src/he_rct.rs",
            include_str!("../src/he_rct.rs"),
        ),
        (
            "rust/rei_microphysics/src/hhe_events.rs",
            include_str!("../src/hhe_events.rs"),
        ),
        (
            "rust/rei_microphysics/src/homogeneous_rates.rs",
            include_str!("../src/homogeneous_rates.rs"),
        ),
        (
            "rust/rei_microphysics/src/hydrogen_step.rs",
            include_str!("../src/hydrogen_step.rs"),
        ),
        (
            "rust/rei_microphysics/src/interval_ad.rs",
            include_str!("../src/interval_ad.rs"),
        ),
        (
            "rust/rei_microphysics/src/interval_math.rs",
            include_str!("../src/interval_math.rs"),
        ),
        (
            "rust/rei_microphysics/src/joint_affine.rs",
            include_str!("../src/joint_affine.rs"),
        ),
        (
            "rust/rei_microphysics/src/lib.rs",
            include_str!("../src/lib.rs"),
        ),
        (
            "rust/rei_microphysics/src/lift.rs",
            include_str!("../src/lift.rs"),
        ),
        (
            "rust/rei_microphysics/src/microstep.rs",
            include_str!("../src/microstep.rs"),
        ),
        (
            "rust/rei_microphysics/src/thermal.rs",
            include_str!("../src/thermal.rs"),
        ),
        (
            "rust/rei_microphysics/examples/first_interval.rs",
            include_str!("first_interval.rs"),
        ),
    ];
    for (name, text) in parts {
        writeln!(out, "{} {}", name, text.len()).unwrap();
        out.push_str(text);
        out.push('\n');
    }
    out
}
const RADII: [f64; 7] = [1e-7, 1e-7, 1e-7, 1e-5, 1e-8, 1e-8, 1e-8];
const IDS: [&str; 7] = [
    "H_nuclei",
    "He_nuclei",
    "electron_charge_neutrality",
    "photon_group0_absorption",
    "photon_group1_absorption",
    "photon_group2_absorption",
    "thermal_binding_photon_escape_total_energy",
];
fn error(s: &str) -> io::Error {
    io::Error::other(s.to_owned())
}
fn num(out: &mut String, x: f64) {
    write!(out, "{x:.17e}").unwrap();
}
fn scalars(out: &mut String, x: &[f64]) {
    out.push('[');
    for (i, v) in x.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        num(out, *v);
    }
    out.push(']');
}
fn pair(out: &mut String, x: Interval) {
    out.push('[');
    num(out, x.lo);
    out.push(',');
    num(out, x.hi);
    out.push(']');
}
fn boxes(out: &mut String, x: &[Interval; 7]) {
    out.push('[');
    for (i, v) in x.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        pair(out, *v);
    }
    out.push(']');
}
fn state_array(s: &HHeState) -> [f64; 8] {
    [
        s.fractions[0],
        s.fractions[1],
        s.fractions[2],
        s.u_erg_cm3,
        s.photon_cm3[0],
        s.photon_cm3[1],
        s.photon_cm3[2],
        s.escaped_erg_cm3,
    ]
}
fn state_json(out: &mut String, s: &HHeState) {
    scalars(out, &state_array(s));
}
fn site(out: &mut String, s: &RootSite) {
    write!(out, "{{\"id\":\"{}\",\"step_s\":", s.id).unwrap();
    num(out, s.step_s);
    out.push_str(",\"center\":");
    scalars(out, &s.center);
    out.push_str(",\"box\":");
    boxes(out, &s.r#box);
    out.push_str(",\"preconditioner\":[");
    for (i, row) in s.preconditioner.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        scalars(out, row);
    }
    out.push_str("]}");
}
fn events_json(out: &mut String, e: &Ft03Events) {
    out.push_str("{\"photo\":[");
    for (i, row) in e.photo_per_cm3.iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        scalars(out, row);
    }
    out.push_str("],\"collision\":");
    scalars(out, &e.collision_per_cm3);
    out.push_str(",\"recombination\":");
    scalars(out, &e.recombination_per_cm3);
    out.push_str(",\"dr\":");
    scalars(out, &e.dr_per_cm3);
    out.push('}');
}
fn ledgers_json(out: &mut String, x: &[f64; 7]) {
    out.push('{');
    for i in 0..7 {
        if i > 0 {
            out.push(',');
        }
        write!(out, "\"{}\":", IDS[i]).unwrap();
        num(out, x[i]);
    }
    out.push('}');
}
fn step_residual(
    model: &Ft03Model,
    old: &HHeState,
    new: &HHeState,
    e: &Ft03Events,
) -> Result<[f64; 7], String> {
    let nh = model.gas.n_h_cm3;
    let nhe = model.gas.n_he_cm3;
    let mut j = [0.0; 3];
    for a in 0..3 {
        j[a] = e.photo_per_cm3[a].iter().sum::<f64>() + e.collision_per_cm3[a]
            - e.recombination_per_cm3[a];
    }
    j[1] -= e.dr_per_cm3.iter().sum::<f64>();
    let mut r = [0.0; 7];
    r[0] = 0.0;
    r[1] = 0.0;
    // The state stores independent ion fractions. Nuclear totals and charge
    // are structural identities, hence these three residuals are zero.
    r[2] = 0.0;
    let species = [
        (nh * (new.fractions[0] - old.fractions[0]) - j[0]) / nh,
        (nhe * (new.fractions[1] - old.fractions[1]) - j[1] + j[2]) / nhe,
        (nhe * (new.fractions[2] - old.fractions[2]) - j[2]) / nhe,
    ];
    for k in 0..3 {
        let absorbed = (0..3).map(|a| e.photo_per_cm3[a][k]).sum::<f64>();
        r[3 + k] = (old.photon_cm3[k] - new.photon_cm3[k] - absorbed) / old.photon_cm3[k];
    }
    let energy0 = model.gas.total_energy(old).map_err(|e| e.to_string())?;
    let energy1 = model.gas.total_energy(new).map_err(|e| e.to_string())?;
    r[6] = (energy1 - energy0) / energy0;
    if species
        .iter()
        .chain(r.iter())
        .any(|x| !x.is_finite() || x.abs() > 1e-12)
    {
        return Err("FT03_LEDGER_RESIDUAL".into());
    }
    Ok(r)
}
#[derive(Clone)]
struct Progress {
    time: f64,
    dt: f64,
    accepted: u64,
    rejected: u64,
    state: HHeState,
    parent: [Interval; 7],
    sum: [f64; 7],
    comp: [f64; 7],
    offset: u64,
}
fn compensated(p: &mut Progress, events: &Ft03Events) {
    let mut r = [0.0; 7];
    for k in 0..3 {
        r[3 + k] = (0..3).map(|a| events.photo_per_cm3[a][k]).sum();
    }
    for i in 0..7 {
        let y = r[i] - p.comp[i];
        let t = p.sum[i] + y;
        p.comp[i] = (t - p.sum[i]) - y;
        p.sum[i] = t;
    }
}
fn hex(bytes: &[u8]) -> String {
    let mut s = String::new();
    for b in bytes {
        write!(s, "{b:02x}").unwrap();
    }
    s
}
fn bits(v: f64) -> String {
    format!("{:016x}", v.to_bits())
}
fn read_bits(s: &str) -> io::Result<f64> {
    Ok(f64::from_bits(
        u64::from_str_radix(s, 16).map_err(|_| error("bad checkpoint bits"))?,
    ))
}
fn checkpoint_text(level: usize, mode: &str, p: &Progress) -> String {
    let mut v = vec![
        "REI_F05_CHECKPOINT_V2".to_string(),
        hex(INPUT.as_bytes()),
        level.to_string(),
        mode.to_string(),
        bits(p.time),
        bits(p.dt),
        p.accepted.to_string(),
        p.rejected.to_string(),
        p.offset.to_string(),
    ];
    for x in state_array(&p.state) {
        v.push(bits(x));
    }
    for x in p.parent {
        v.push(bits(x.lo));
        v.push(bits(x.hi));
    }
    for x in p.sum {
        v.push(bits(x));
    }
    for x in p.comp {
        v.push(bits(x));
    }
    v.join("\n") + "\n"
}
fn read_checkpoint(path: &Path, level: usize, mode: &str) -> io::Result<Progress> {
    let s = fs::read_to_string(path)?;
    let v: Vec<_> = s.split_whitespace().collect();
    if v.len() != 45
        || v[0] != "REI_F05_CHECKPOINT_V2"
        || v[1] != hex(INPUT.as_bytes())
        || v[2] != level.to_string()
        || v[3] != mode
    {
        return Err(error("checkpoint identity mismatch"));
    }
    let time = read_bits(v[4])?;
    let dt = read_bits(v[5])?;
    let accepted = v[6].parse().map_err(|_| error("checkpoint accepted"))?;
    let rejected = v[7].parse().map_err(|_| error("checkpoint rejected"))?;
    let offset = v[8].parse().map_err(|_| error("checkpoint offset"))?;
    let mut values = [0.0; 8];
    for i in 0..8 {
        values[i] = read_bits(v[9 + i])?;
    }
    let state = HHeState {
        fractions: [values[0], values[1], values[2]],
        u_erg_cm3: values[3],
        photon_cm3: [values[4], values[5], values[6]],
        escaped_erg_cm3: values[7],
    };
    let mut parent = [Interval { lo: 0.0, hi: 0.0 }; 7];
    for i in 0..7 {
        parent[i] = Interval::new(read_bits(v[17 + 2 * i])?, read_bits(v[18 + 2 * i])?)
            .map_err(|_| error("checkpoint box"))?;
    }
    let mut sum = [0.0; 7];
    let mut comp = [0.0; 7];
    for i in 0..7 {
        sum[i] = read_bits(v[31 + i])?;
        comp[i] = read_bits(v[38 + i])?;
    }
    Ok(Progress {
        time,
        dt,
        accepted,
        rejected,
        state,
        parent,
        sum,
        comp,
        offset,
    })
}
fn sync_replace(path: &Path, data: &str) -> io::Result<()> {
    let tmp = path.with_extension("tmp");
    {
        let mut f = File::create(&tmp)?;
        f.write_all(data.as_bytes())?;
        f.sync_all()?;
    }
    fs::rename(tmp, path)?;
    if let Some(parent) = path.parent() {
        File::open(parent)?.sync_all()?;
    }
    Ok(())
}
fn summary(
    level: usize,
    factor: f64,
    mode: &str,
    initial: &HHeState,
    initial_parent: &[Interval; 7],
    p: &Progress,
    finished: bool,
) -> String {
    let mut s = String::new();
    write!(
        s,
        "{{\"refinement_factor\":{factor},\"mode\":\"{mode}\",\"initial_parent_box\":"
    )
    .unwrap();
    boxes(&mut s, initial_parent);
    s.push_str(",\"initial_state\":");
    state_json(&mut s, initial);
    write!(
        s,
        ",\"accepted_steps\":{},\"rejected_steps\":{},\"final_state\":",
        p.accepted, p.rejected
    )
    .unwrap();
    state_json(&mut s, &p.state);
    s.push_str(",\"t_end_s\":");
    num(&mut s, p.time);
    write!(s, ",\"finished\":{},\"all_seven_ledgers\":", finished).unwrap();
    let mut budget = [0.0; 7];
    for k in 0..3 {
        budget[3 + k] =
            (initial.photon_cm3[k] - p.state.photon_cm3[k] - p.sum[3 + k]) / initial.photon_cm3[k];
    }
    // Structural nucleus/charge identities are derived, not integrated slots.
    let model = Ft03Model::controlled().expect("frozen FT03 model");
    let energy0 = model.gas.total_energy(initial).expect("initial energy");
    budget[6] = (model.gas.total_energy(&p.state).expect("final energy") - energy0) / energy0;
    ledgers_json(&mut s, &budget);
    write!(s,",\"level\":{level},\"scientific_admission\":\"HOLD\",\"claim\":\"CANDIDATE_PENDING_EXTERNAL_CHECK\"}}\n").unwrap();
    s
}
fn record(
    accepted: bool,
    t: f64,
    dt: f64,
    old: &HHeState,
    parent: &[Interval; 7],
    center: &[f64; 7],
    state: &HHeState,
    next: &[Interval; 7],
    trial: Option<&rei_microphysics::CertifiedTrial>,
    failure: Option<&str>,
    ledgers: &[f64; 7],
) -> String {
    let mut s = String::new();
    write!(
        s,
        "{{\"accepted\":{accepted},\"model_id\":\"{FT03_MODEL_ID}\",\"t0_s\":"
    )
    .unwrap();
    num(&mut s, t);
    s.push_str(",\"dt_s\":");
    num(&mut s, dt);
    s.push_str(",\"old_state\":");
    state_json(&mut s, old);
    s.push_str(",\"parent_box\":");
    boxes(&mut s, parent);
    s.push_str(",\"parent_center\":");
    scalars(&mut s, center);
    s.push_str(",\"state\":");
    state_json(&mut s, state);
    s.push_str(",\"next_box\":");
    boxes(&mut s, next);
    if let Some(x) = trial {
        s.push_str(",\"local_bounds\":");
        scalars(&mut s, &x.local_bounds);
        s.push_str(",\"public_widths\":[");
        scalars(&mut s, &x.public_widths[0]);
        s.push(',');
        scalars(&mut s, &x.public_widths[1]);
        s.push_str("],\"sites\":[");
        for (i, v) in x.sites.iter().enumerate() {
            if i > 0 {
                s.push(',');
            }
            site(&mut s, v);
        }
        s.push_str("],\"events\":");
        events_json(&mut s, &x.events);
    } else {
        write!(s, ",\"failure\":\"{}\"", failure.unwrap_or("UNKNOWN")).unwrap();
    }
    s.push_str(",\"ledgers\":");
    ledgers_json(&mut s, ledgers);
    s.push_str("}\n");
    s
}
fn initial_box(model: &Ft03Model, state: &HHeState) -> io::Result<[Interval; 7]> {
    let c = rei_microphysics::ft03_scaled(model, state);
    let mut out = [Interval { lo: 0.0, hi: 0.0 }; 7];
    for i in 0..7 {
        let a = Interval::point(c[i]).map_err(|_| error("initial center"))?;
        let d = Interval::point(RADII[i]).map_err(|_| error("initial radius"))?;
        let lo = a.sub(&d).map_err(|_| error("initial box"))?.lo;
        let hi = a.add(&d).map_err(|_| error("initial box"))?.hi;
        out[i] = Interval::new(lo, hi).map_err(|_| error("initial box"))?;
    }
    Ok(out)
}
fn run_level(dir: &Path, level: usize, factor: f64, mode: &str, resume: bool) -> io::Result<()> {
    let model = Ft03Model::controlled().map_err(|e| error(&e.to_string()))?;
    let initial = model.initial_state();
    let initial_parent = initial_box(&model, &initial)?;
    let log = dir.join(format!("level_{level}_transactions.jsonl"));
    let cp = dir.join(format!("level_{level}_checkpoint.dat"));
    let summary_path = dir.join(format!("level_{level}_summary.json"));
    let mut p = if resume && cp.exists() {
        read_checkpoint(&cp, level, mode)?
    } else {
        if resume && log.exists() {
            return Err(error("transaction log without checkpoint"));
        }
        if !resume && (log.exists() || cp.exists() || summary_path.exists()) {
            return Err(error("existing output; use --resume"));
        }
        Progress {
            time: 0.0,
            dt: 1e9 * factor,
            accepted: 0,
            rejected: 0,
            state: initial,
            parent: initial_parent,
            sum: [0.0; 7],
            comp: [0.0; 7],
            offset: 0,
        }
    };
    // A durable zero-offset checkpoint makes interruption before the first
    // transaction recoverable. Existing checkpoints retain their exact offset.
    if !cp.exists() {
        sync_replace(&cp, &checkpoint_text(level, mode, &p))?;
    }
    let mut file = OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .open(&log)?;
    if file.metadata()?.len() < p.offset {
        return Err(error("checkpoint exceeds transaction log"));
    }
    file.set_len(p.offset)?;
    use std::io::Seek;
    file.seek(std::io::SeekFrom::End(0))?;
    let target = if mode == "PILOT" { 3 } else { u64::MAX };
    let end = 1e12;
    let control = StepControl {
        max_iterations: 200,
        // Solve more tightly than the unchanged 1e-12 whole-budget gate.
        residual_tolerance: 1e-15,
    };
    while p.accepted < target && p.time < end {
        let dt = p.dt.min(end - p.time);
        let old = p.state;
        let parent = p.parent;
        let center = rei_microphysics::ft03_scaled(&model, &old);
        let result = certified_ft03_trial(&model, &old, &parent, dt, control).and_then(|trial| {
            let ledgers =
                step_residual(&model, &old, &trial.state, &trial.events).map_err(|_| {
                    rei_microphysics::ForwardError::InvalidInput("FT03_LEDGER_RESIDUAL")
                })?;
            Ok((trial, ledgers))
        });
        match result {
            Ok((trial, r)) => {
                let line = record(
                    true,
                    p.time,
                    dt,
                    &old,
                    &parent,
                    &center,
                    &trial.state,
                    &trial.next_box,
                    Some(&trial),
                    None,
                    &r,
                );
                file.write_all(line.as_bytes())?;
                file.sync_all()?;
                p.offset += line.len() as u64;
                p.time += dt;
                p.state = trial.state;
                p.parent = trial.next_box;
                p.accepted += 1;
                compensated(&mut p, &trial.events);
                p.dt = 1e9 * factor;
                sync_replace(&cp, &checkpoint_text(level, mode, &p))?;
                sync_replace(
                    &summary_path,
                    &summary(
                        level,
                        factor,
                        mode,
                        &initial,
                        &initial_parent,
                        &p,
                        p.time == end,
                    ),
                )?;
            }
            Err(e) => {
                let line = record(
                    false,
                    p.time,
                    dt,
                    &old,
                    &parent,
                    &center,
                    &old,
                    &parent,
                    None,
                    Some(e.code()),
                    &[0.0; 7],
                );
                file.write_all(line.as_bytes())?;
                file.sync_all()?;
                p.offset += line.len() as u64;
                p.rejected += 1;
                let minimum_reached = dt / 2.0 < 1000.0;
                if !minimum_reached {
                    p.dt = dt / 2.0;
                }
                sync_replace(&cp, &checkpoint_text(level, mode, &p))?;
                sync_replace(
                    &summary_path,
                    &summary(level, factor, mode, &initial, &initial_parent, &p, false),
                )?;
                if minimum_reached {
                    return Err(error(&format!(
                        "minimum step after {} at t={} dt={}",
                        e.code(),
                        p.time,
                        dt
                    )));
                }
            }
        }
    }
    sync_replace(
        &summary_path,
        &summary(
            level,
            factor,
            mode,
            &initial,
            &initial_parent,
            &p,
            p.time == end,
        ),
    )?;
    Ok(())
}
fn main() -> io::Result<()> {
    let args: Vec<_> = env::args().collect();
    let mut input = None;
    let mut output = None;
    let mut pilot = false;
    let mut resume = false;
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--input" => {
                i += 1;
                input = args.get(i).cloned();
            }
            "--output" => {
                i += 1;
                output = args.get(i).cloned();
            }
            "--pilot" => pilot = true,
            "--resume" => resume = true,
            _ => return Err(error("unknown argument")),
        }
        i += 1;
    }
    let input = PathBuf::from(input.ok_or_else(|| error("missing --input"))?);
    let out = PathBuf::from(output.ok_or_else(|| error("missing --output"))?);
    if fs::read(&input)? != INPUT.as_bytes() {
        return Err(error("frozen input identity mismatch"));
    }
    fs::create_dir_all(&out)?;
    let identity_path = out.join("source_identity.dat");
    let identity = source_identity();
    if identity_path.exists() {
        if fs::read(&identity_path)? != identity.as_bytes() {
            return Err(error("compiled source identity mismatch"));
        }
    } else {
        if fs::read_dir(&out)?.next().is_some() {
            return Err(error("existing output without source identity"));
        }
        sync_replace(&identity_path, &identity)?;
    }
    // The frozen validator names pilot output by the exact source hash and
    // calls this program again without --resume. A completed pilot is safe to
    // read from its exact checkpoint; an interrupted pilot resumes there.
    // Full campaigns retain explicit --resume so a new run cannot silently
    // inherit an unrelated history.
    resume |= pilot;
    let mode = if pilot { "PILOT" } else { "FULL" };
    for (level, factor) in [1.0, 0.5, 0.25].into_iter().enumerate() {
        run_level(&out, level, factor, mode, resume)?;
    }
    Ok(())
}
