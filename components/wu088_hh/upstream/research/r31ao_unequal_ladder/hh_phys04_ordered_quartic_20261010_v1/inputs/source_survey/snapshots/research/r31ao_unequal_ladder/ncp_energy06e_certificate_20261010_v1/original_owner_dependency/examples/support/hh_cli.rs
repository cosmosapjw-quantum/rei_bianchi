//! Explicit, bounded HH route in the existing paired_history executable.
//! Trusted single-writer local persistence only, not an untrusted proof reader.
use rei_microphysics::coupled_primary::HhMode;
use rei_microphysics::paired_runtime::{
    hh_checkpoint_decode, hh_checkpoint_encode, hh_paired_initial, try_hh_paired_ensemble,
    HhPairedState, HhRunConfig, PairedConfig,
};
use std::{
    collections::HashSet,
    fs::{self, File, OpenOptions},
    io,
    path::PathBuf,
};

const MAGIC: &str = "HH06C_RUN_V1";
const MAX_STEPS: usize = 8;
const MAX_TIME: f64 = 1e10;
const MAX_PENDING_BYTES: usize = 64 * 1024 * 1024;
fn err(s: &str) -> io::Error {
    super::error(s)
}
fn forward(e: rei_microphysics::ForwardError) -> io::Error {
    err(e.code())
}

#[derive(Clone, Debug)]
struct Args {
    mode: String,
    spec: String,
    steps: usize,
    resume: bool,
    output: PathBuf,
    scenario: Option<PathBuf>,
}
fn parse(args: &[String]) -> io::Result<Args> {
    let mut seen = HashSet::new();
    let mut mode = None;
    let mut spec = String::from("T0");
    let mut steps = 1;
    let mut resume = false;
    let mut output = None;
    let mut scenario = None;
    let mut i = 0;
    while i < args.len() {
        let key = args[i].as_str();
        if !seen.insert(key) {
            return Err(err("HH_CLI_DUPLICATE"));
        }
        if key == "--full" {
            return Err(err("HH_FULL_NOT_QUALIFIED"));
        }
        if key == "--resume" {
            resume = true;
            i += 1;
            continue;
        }
        if key == "--pilot" {
            i += 1;
            continue;
        }
        if !matches!(
            key,
            "--hh" | "--hh-grid" | "--hh-steps" | "--scenario" | "--output"
        ) {
            return Err(err("HH_CLI_UNKNOWN"));
        }
        let value = args
            .get(i + 1)
            .filter(|v| !v.starts_with("--"))
            .ok_or_else(|| err("HH_CLI_VALUE"))?;
        match key {
            "--hh" => {
                if !matches!(value.as_str(), "OFF" | "LCS" | "COMPARE") {
                    return Err(err("HH_CLI_MODE"));
                }
                mode = Some(value.clone());
            }
            "--hh-grid" => {
                if !super::SPECS.iter().any(|s| s.label == value) {
                    return Err(err("HH_CLI_GRID"));
                }
                spec = value.clone();
            }
            "--hh-steps" => {
                steps = value.parse::<usize>().map_err(|_| err("HH_CLI_STEPS"))?;
                if !(1..=MAX_STEPS).contains(&steps) {
                    return Err(err("HH_CLI_STEPS"));
                }
            }
            "--scenario" => scenario = Some(PathBuf::from(value)),
            "--output" => output = Some(PathBuf::from(value)),
            _ => unreachable!(),
        }
        i += 2;
    }
    Ok(Args {
        mode: mode.ok_or_else(|| err("HH_CLI_MODE"))?,
        spec,
        steps,
        resume,
        output: output.ok_or_else(|| err("HH_CLI_OUTPUT"))?,
        scenario,
    })
}
fn configs(a: &Args) -> io::Result<Vec<HhRunConfig>> {
    let spec = super::SPECS
        .iter()
        .find(|s| s.label == a.spec)
        .ok_or_else(|| err("HH_CLI_GRID"))?;
    let modes: &[HhMode] = match a.mode.as_str() {
        "COMPARE" => &[HhMode::Off, HhMode::Lcs91],
        "OFF" => &[HhMode::Off],
        "LCS" => &[HhMode::Lcs91],
        _ => unreachable!(),
    };
    let mut out = Vec::new();
    for geometry in ["FLRW", "BI"] {
        for &mode in modes {
            out.push(
                HhRunConfig::new(
                    PairedConfig {
                        spectral_subdivisions: spec.m,
                        n_mu: spec.mu,
                        n_phi: spec.phi,
                    },
                    super::h(geometry),
                    mode,
                )
                .map_err(forward)?,
            );
        }
    }
    Ok(out)
}
fn fnv(bytes: &[u8]) -> u64 {
    bytes.iter().fold(0xcbf29ce484222325, |h, &b| {
        (h ^ b as u64).wrapping_mul(0x100000001b3)
    })
}
fn identity(a: &Args) -> io::Result<Vec<u8>> {
    let binary = fs::read(std::env::current_exe()?)?;
    let mut out = format!("{MAGIC}\nmode={}\ngrid={}\nsteps-max={MAX_STEPS}\ntime-max={MAX_TIME}\nbinary-fnv={:016x}\n", a.mode, a.spec, fnv(&binary)).into_bytes();
    // Exact source bytes plus a non-cryptographic same-binary check. Neither is
    // an authentication scheme for maliciously supplied checkpoints.
    out.extend(super::source_bytes());
    out.extend_from_slice(include_bytes!("hh_cli.rs"));
    for bytes in [
        include_bytes!("../../src/hh_primary_extension.rs").as_slice(),
        include_bytes!("../../src/hh_return_enclosure.rs").as_slice(),
        include_bytes!("../../src/hh_paired_extension.rs").as_slice(),
    ] {
        out.extend_from_slice(&(bytes.len() as u64).to_le_bytes());
        out.extend_from_slice(bytes);
    }
    Ok(out)
}
fn hex(bytes: &[u8]) -> String {
    const DIGITS: &[u8] = b"0123456789abcdef";
    let mut s = String::with_capacity(bytes.len() * 2);
    for &b in bytes {
        s.push(DIGITS[(b >> 4) as usize] as char);
        s.push(DIGITS[(b & 15) as usize] as char);
    }
    s
}
fn unhex(s: &str) -> io::Result<Vec<u8>> {
    if !s.len().is_multiple_of(2) || s.len() > MAX_PENDING_BYTES {
        return Err(err("HH_RUN_ENCODING"));
    }
    let digit = |c: u8| -> io::Result<u8> {
        match c {
            b'0'..=b'9' => Ok(c - b'0'),
            b'a'..=b'f' => Ok(c - b'a' + 10),
            _ => Err(err("HH_RUN_ENCODING")),
        }
    };
    s.as_bytes()
        .chunks_exact(2)
        .map(|x| Ok((digit(x[0])? << 4) | digit(x[1])?))
        .collect()
}
struct RunState {
    states: Vec<HhPairedState>,
    accepted: usize,
    rejected: usize,
    dt: f64,
    offset: u64,
    metrics: [f64; 3],
}
fn encode(c: &[HhRunConfig], r: &RunState) -> io::Result<String> {
    // Offset is field 7, shared with the existing durable transaction protocol.
    let mut s = format!(
        "{MAGIC} {} {} {:016x} {} 0 0 {} {:016x} {:016x} {:016x}\n",
        r.accepted,
        r.rejected,
        r.dt.to_bits(),
        c.len(),
        r.offset,
        r.metrics[0].to_bits(),
        r.metrics[1].to_bits(),
        r.metrics[2].to_bits()
    );
    for (c, state) in c.iter().zip(&r.states) {
        s.push_str(&hex(&hh_checkpoint_encode(c, state).map_err(forward)?));
        s.push('\n');
    }
    s.push_str(&format!("checksum {:016x}\n", fnv(s.as_bytes())));
    Ok(s)
}
fn decode(c: &[HhRunConfig], text: &str, max_dt: f64) -> io::Result<RunState> {
    let (body, checksum_line) = text
        .rsplit_once("checksum ")
        .ok_or_else(|| err("HH_RUN_CHECKSUM"))?;
    let stored = checksum_line
        .strip_suffix('\n')
        .filter(|v| v.len() == 16)
        .ok_or_else(|| err("HH_RUN_CHECKSUM"))?;
    let expected = u64::from_str_radix(stored, 16).map_err(|_| err("HH_RUN_CHECKSUM"))?;
    if fnv(body.as_bytes()) != expected {
        return Err(err("HH_RUN_CHECKSUM"));
    }
    let mut lines = body.lines();
    let v: Vec<_> = lines
        .next()
        .ok_or_else(|| err("HH_RUN_HEADER"))?
        .split_whitespace()
        .collect();
    if v.len() != 11
        || v[0] != MAGIC
        || v[4].parse::<usize>().ok() != Some(c.len())
        || v[5..7] != ["0", "0"]
    {
        return Err(err("HH_RUN_HEADER"));
    }
    let accepted = v[1].parse::<usize>().map_err(|_| err("HH_RUN_HEADER"))?;
    let rejected = v[2].parse::<usize>().map_err(|_| err("HH_RUN_HEADER"))?;
    let dt = super::f(v[3])?;
    let offset = v[7].parse::<u64>().map_err(|_| err("HH_RUN_HEADER"))?;
    let metrics = [super::f(v[8])?, super::f(v[9])?, super::f(v[10])?];
    if accepted > MAX_STEPS
        || rejected > 1000000
        || !dt.is_finite()
        || dt < 1000.0
        || dt > max_dt
        || metrics.iter().any(|x| !x.is_finite() || *x < 0.0)
        || metrics[0] >= 2e-4
        || metrics[1] >= 2e-3
        || metrics[2] > 1e-12
    {
        return Err(err("HH_RUN_DOMAIN"));
    }
    let states = c
        .iter()
        .map(|cfg| {
            hh_checkpoint_decode(
                cfg,
                &unhex(lines.next().ok_or_else(|| err("HH_RUN_TRUNCATED"))?)?,
            )
            .map_err(forward)
        })
        .collect::<io::Result<Vec<_>>>()?;
    if lines.next().is_some()
        || states.iter().any(|s| {
            s.base().time_s.to_bits() != states[0].base().time_s.to_bits()
                || s.base().time_s > MAX_TIME
        })
    {
        return Err(err("HH_RUN_STATE_ALIGNMENT"));
    }
    Ok(RunState {
        states,
        accepted,
        rejected,
        dt,
        offset,
        metrics,
    })
}
fn summary(c: &[HhRunConfig], r: &RunState) -> String {
    let members = c.iter().zip(&r.states).map(|(c,s)| {
        let b=s.base(); let g=&b.gas;
        format!("{{\"mode\":\"{}\",\"geometry\":\"{}\",\"time_s\":{:.17e},\"gas\":[{:.17e},{:.17e},{:.17e},{:.17e}],\"hh_events_per_h\":{:.17e},\"hh_heat_ev_per_h\":{:.17e},\"energy_comp\":{:.17e}}}",
            if c.mode()==HhMode::Off {"OFF"} else {"LCS"}, if c.hubble()==[1e-14;3] {"FLRW"} else {"BIANCHI_I"},
            b.time_s,g.fractions[0],g.fractions[1],g.fractions[2],g.w_ev_per_h,s.hh_events_per_h(),s.hh_heat_ev_per_h(),b.energy_comp)
    }).collect::<Vec<_>>().join(",");
    format!("{{\"schema\":\"HH-ON06C-bounded-run\",\"accepted_macros\":{},\"rejected_candidates\":{},\"next_dt_s\":{:.17e},\"max_local\":{:.17e},\"max_width\":{:.17e},\"max_ledger\":{:.17e},\"members\":[{}],\"canonical_S0_modified\":false,\"physical_admission\":false,\"whole_history_qualified\":false}}\n",
        r.accepted,r.rejected,r.dt,r.metrics[0],r.metrics[1],r.metrics[2],members)
}

pub(super) fn run(args: &[String]) -> io::Result<()> {
    let a = parse(args)?;
    if let Some(path) = &a.scenario {
        if fs::read(path)? != super::SCENARIO.as_bytes() {
            return Err(err("HH_SCENARIO_IDENTITY"));
        }
    }
    let wanted = identity(&a)?;
    let c = configs(&a)?;
    let spec = super::SPECS.iter().find(|s| s.label == a.spec).unwrap();
    let cp = a.output.join("checkpoint.dat");
    let log = a.output.join("trials.jsonl");
    let identity_path = a.output.join("source_identity.bin");
    let mut r;
    if a.resume {
        if fs::read(&identity_path)? != wanted {
            return Err(err("HH_RUN_IDENTITY"));
        }
        // Validate both current and pending state before repairing any bytes.
        let old = decode(&c, &fs::read_to_string(&cp)?, spec.dt)?;
        let pending = a.output.join("pending.transaction");
        if pending.exists() {
            let data = fs::read(&pending)?;
            if data.len() < 8 || data.len() > MAX_PENDING_BYTES {
                return Err(err("HH_RUN_PENDING_SIZE"));
            }
            let n = usize::try_from(u64::from_le_bytes(data[..8].try_into().unwrap()))
                .map_err(|_| err("HH_RUN_PENDING_SIZE"))?;
            let raw_end = 8usize
                .checked_add(n)
                .filter(|&n| n <= data.len())
                .ok_or_else(|| err("HH_RUN_PENDING_SIZE"))?;
            let next = decode(
                &c,
                std::str::from_utf8(&data[raw_end..]).map_err(|_| err("HH_RUN_ENCODING"))?,
                spec.dt,
            )?;
            if next.accepted < old.accepted
                || next.accepted > old.accepted + 1
                || next.offset < old.offset
            {
                return Err(err("HH_RUN_PENDING_ORDER"));
            }
        }
        super::reconcile_transaction(&a.output, &cp, &log)?;
        r = decode(&c, &fs::read_to_string(&cp)?, spec.dt)?;
        if fs::metadata(&log)?.len() != r.offset {
            return Err(err("HH_RUN_LOG_OFFSET"));
        }
        if a.steps < r.accepted {
            return Err(err("HH_RUN_TARGET_BEFORE_CHECKPOINT"));
        }
    } else {
        let states = c
            .iter()
            .map(hh_paired_initial)
            .collect::<Result<Vec<_>, _>>()
            .map_err(forward)?;
        r = RunState {
            states,
            accepted: 0,
            rejected: 0,
            dt: spec.dt,
            offset: 0,
            metrics: [0.0; 3],
        };
        fs::create_dir(&a.output)?;
        super::sync_replace(&identity_path, &wanted)?;
        super::sync_replace(&log, b"")?;
        super::sync_replace(&cp, encode(&c, &r)?.as_bytes())?;
    }
    let mut file = OpenOptions::new().append(true).open(&log)?;
    let start = r.accepted;
    while r.accepted < a.steps {
        let time = r.states[0].base().time_s;
        if time + r.dt > MAX_TIME {
            return Err(err("HH_PREFIX_LIMIT"));
        }
        let before = c
            .iter()
            .zip(&r.states)
            .map(|(c, s)| hh_checkpoint_encode(c, s).map_err(forward))
            .collect::<io::Result<Vec<_>>>()?;
        match try_hh_paired_ensemble(&c, &mut r.states, r.dt) {
            Ok(trials) => {
                let number = r.accepted + 1;
                let mut raw = String::new();
                for (i, t) in trials.iter().enumerate() {
                    r.metrics[0] = r.metrics[0].max(t.local_bound);
                    r.metrics[1] = r.metrics[1].max(t.public_width);
                    r.metrics[2] = r.metrics[2].max(t.max_ledger);
                    let s = &r.states[i];
                    let b = s.base();
                    raw.push_str(&format!("{{\"kind\":\"accepted\",\"macro\":{},\"member\":{},\"mode\":\"{}\",\"geometry\":\"{}\",\"time_s\":{:.17e},\"dt_s\":{:.17e},\"local\":{:.17e},\"width\":{:.17e},\"ledger\":{:.17e},\"hh_events_per_h\":{:.17e},\"hh_heat_ev_per_h\":{:.17e},\"site_hh_events\":[{:.17e},{:.17e},{:.17e}],\"site_hh_heat\":[{:.17e},{:.17e},{:.17e}],\"audits\":[{}]}}\n",
                        number,i,if c[i].mode()==HhMode::Off {"OFF"} else {"LCS"},if c[i].hubble()==[1e-14;3] {"FLRW"} else {"BIANCHI_I"},
                        b.time_s,r.dt,t.local_bound,t.public_width,t.max_ledger,s.hh_events_per_h(),s.hh_heat_ev_per_h(),
                        t.source_hh_events[0],t.source_hh_events[1],t.source_hh_events[2],t.source_hh_heat[0],t.source_hh_heat[1],t.source_hh_heat[2],t.audits.join(",")));
                }
                r.accepted = number;
                r.offset += raw.len() as u64;
                super::commit_transaction(&a.output, &mut file, &cp, &raw, &encode(&c, &r)?)?;
            }
            Err(e) => {
                for ((cfg, s), bytes) in c.iter().zip(&r.states).zip(&before) {
                    if hh_checkpoint_encode(cfg, s).map_err(forward)? != *bytes {
                        return Err(err("HH_ROLLBACK_VIOLATION"));
                    }
                }
                // Only the established numerical gates are retryable. A domain,
                // model, identity or source error is not cured by silent halving.
                if !matches!(
                    e.code(),
                    "PAIRED_LOCAL_GATE"
                        | "PAIRED_WIDTH_GATE"
                        | "PAIRED_LEDGER_GATE"
                        | "PRIMARY_NONCONVERGENCE"
                        | "PRIMARY_ROOT_NONCONVERGENCE"
                ) {
                    return Err(forward(e));
                }
                let raw=format!("{{\"kind\":\"rejected\",\"time_s\":{:.17e},\"dt_s\":{:.17e},\"error\":\"{}\",\"all_states_unchanged\":true}}\n",time,r.dt,e.code());
                r.rejected += 1;
                let half = r.dt / 2.0;
                if half < 1000.0 {
                    return Err(err("HH_MINIMUM_STEP"));
                }
                r.dt = half;
                r.offset += raw.len() as u64;
                super::commit_transaction(&a.output, &mut file, &cp, &raw, &encode(&c, &r)?)?;
            }
        }
    }
    super::sync_replace(&a.output.join("summary.json"), summary(&c, &r).as_bytes())?;
    File::open(&a.output)?.sync_all()?;
    println!("{{\"hh_run\":\"{}\",\"accepted_total\":{},\"computed_macros_this_process\":{},\"bounded_only\":true}}",a.mode,r.accepted,r.accepted-start);
    Ok(())
}
