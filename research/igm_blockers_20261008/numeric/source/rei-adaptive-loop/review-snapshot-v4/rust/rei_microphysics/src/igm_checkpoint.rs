//! Strict, round-trip text checkpoints for the manufactured IGM history.
//!
//! This is a versioned key/value format, not JSON. Floats use Rust's shortest
//! round-trip decimal representation. SHA-256 is supplied by `sha256sum`; no
//! hash is substituted when that command is unavailable. Loading is immutable:
//! identity is checked before numeric state parsing or returning a candidate.
use crate::{
    igm_history::{ActivePacket, History, HistoryState, Ledger},
    igm_state::IgmGasState,
    verner_cutoff_ev, Absorber, HHeModel,
};
use std::{
    collections::{BTreeMap, BTreeSet},
    fmt::Write as _,
    io::Write as _,
    process::{Command, Stdio},
};

pub const CHECKPOINT_SCHEMA: &str = "igm_history_checkpoint_v1";
pub const SOLVER_ID: &str = "flrw_transport_endpoint_coupled_be_v1";
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct CheckpointIdentity {
    pub schema_id: String,
    pub solver_id: String,
    pub provider_id: String,
    pub closure_id: String,
    pub config_sha256: String,
    pub source_sha256: String,
}
#[derive(Clone, Debug)]
pub struct Checkpoint {
    pub state: HistoryState,
    pub complete: bool,
}
fn invalid() -> String {
    "IGM_CHECKPOINT_INVALID".into()
}
fn identity_mismatch() -> String {
    "IGM_CHECKPOINT_IDENTITY_MISMATCH".into()
}

pub fn sha256_bytes(bytes: &[u8]) -> Result<String, String> {
    let mut child = Command::new("sha256sum")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("IGM_SHA256_UNAVAILABLE: {e}"))?;
    let written = child.stdin.take().ok_or_else(invalid)?.write_all(bytes);
    let result = child
        .wait_with_output()
        .map_err(|e| format!("IGM_SHA256_IO: {e}"))?;
    written.map_err(|e| format!("IGM_SHA256_IO: {e}"))?;
    if !result.status.success() {
        return Err("IGM_SHA256_FAILED".into());
    }
    let output = std::str::from_utf8(&result.stdout).map_err(|_| invalid())?;
    let hash = output.split_whitespace().next().ok_or_else(invalid)?;
    if !valid_hash(hash) {
        return Err(invalid());
    }
    Ok(hash.into())
}
fn valid_hash(s: &str) -> bool {
    s.len() == 64
        && s.bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}
impl CheckpointIdentity {
    /// Source identity includes the exact binary source parameters, quadrature
    /// controls and every deterministic (epoch, energy, photons/H) birth node.
    /// Config identity additionally distinguishes comments and whitespace.
    pub fn new(config_bytes: &[u8], h: &History) -> Result<Self, String> {
        let c = &h.config;
        let mut source = format!(
            "igm_source_constant_powerlaw_minus2_gauss2_v1\n{:016x}\n{:016x}\n{:016x}\n{}\n{}\n",
            c.source.photons_per_h_per_s.to_bits(),
            c.source.energy_min_ev.to_bits(),
            c.source.energy_max_ev.to_bits(),
            c.birth_panels,
            c.energy_panels
        );
        for b in &h.births {
            writeln!(
                &mut source,
                "{:016x},{:016x},{:016x}",
                b.ln_a.to_bits(),
                b.energy_ev.to_bits(),
                b.per_h.to_bits()
            )
            .unwrap();
        }
        Ok(Self {
            schema_id: CHECKPOINT_SCHEMA.into(),
            solver_id: SOLVER_ID.into(),
            provider_id: c.provider_id.clone(),
            closure_id: c.closure_id.clone(),
            config_sha256: sha256_bytes(config_bytes)?,
            source_sha256: sha256_bytes(source.as_bytes())?,
        })
    }
}
fn validate_identity(id: &CheckpointIdentity, h: &History) -> Result<(), String> {
    if id.schema_id != CHECKPOINT_SCHEMA
        || id.solver_id != SOLVER_ID
        || id.provider_id != h.config.provider_id
        || id.closure_id != h.config.closure_id
        || !valid_hash(&id.config_sha256)
        || !valid_hash(&id.source_sha256)
    {
        return Err(identity_mismatch());
    }
    Ok(())
}
/// Shared output coordinates. Index zero is the initial state, and the last
/// index is exactly the configured endpoint rather than a rounded expression.
pub fn output_coordinate(h: &History, index: usize) -> Result<f64, String> {
    if index > h.config.output_panels {
        return Err(invalid());
    }
    Ok(if index == h.config.output_panels {
        h.config.end
    } else {
        h.config.start
            + (h.config.end - h.config.start) * index as f64 / h.config.output_panels as f64
    })
}
fn validate_state(h: &History, s: &HistoryState, complete: bool) -> Result<(), String> {
    let c = &h.config;
    if !s.ln_a.is_finite()
        || s.ln_a < c.start
        || s.ln_a > c.end
        || s.birth_cursor > h.births.len()
        || s.output_cursor > c.output_panels.checked_add(1).ok_or_else(invalid)?
        || s.accepted_steps > c.max_steps
        || !s.next_dln_a.is_normal()
        || s.next_dln_a <= 0.0
        || s.next_dln_a > c.max_dln_a
        || !s.max_residual.is_finite()
        || s.max_residual < 0.0
        || (complete && s.ln_a != c.end)
    {
        return Err(invalid());
    }
    if (s.output_cursor > 0 && output_coordinate(h, s.output_cursor - 1)? > s.ln_a)
        || (s.output_cursor <= c.output_panels && output_coordinate(h, s.output_cursor)? < s.ln_a)
    {
        return Err(invalid());
    }
    let point = c.background.at_ln_a(s.ln_a).map_err(|_| invalid())?;
    s.gas
        .eos(point.n_h_cm3, point.n_he_cm3)
        .map_err(|_| invalid())?;
    crate::igm_thermal::igm_point_rhs(
        &s.gas,
        point.n_h_cm3,
        point.n_he_cm3,
        point.hubble_per_s,
        point.tcmb_k,
        Default::default(),
    )
    .map_err(|_| invalid())?;
    let expected_cursor = h.births.partition_point(|b| b.ln_a <= s.ln_a);
    if s.birth_cursor != expected_cursor || s.packets.len() > c.max_packets {
        return Err(invalid());
    }
    let mut seen = BTreeSet::new();
    for packet in &s.packets {
        if packet.birth_index >= s.birth_cursor
            || !seen.insert(packet.birth_index)
            || !packet.per_h.is_finite()
            || packet.per_h < 0.0
            || !packet.log_per_h.is_finite()
        {
            return Err(invalid());
        }
        let birth = h.births[packet.birth_index];
        if packet.log_per_h > birth.per_h.ln()
            || (packet.per_h.is_normal()
                && packet.log_per_h.to_bits() != packet.per_h.ln().to_bits())
            || (!packet.per_h.is_normal() && packet.log_per_h > f64::MIN_POSITIVE.ln())
        {
            return Err(invalid());
        }
        let crossing = birth.ln_a + (birth.energy_ev / verner_cutoff_ev(Absorber::HI)).ln();
        if crossing <= s.ln_a || packet.per_h > birth.per_h || !h.energy(packet, s.ln_a).is_normal()
        {
            return Err(invalid());
        }
    }
    for (index, b) in h.births[..s.birth_cursor].iter().enumerate() {
        let crossing = b.ln_a + (b.energy_ev / verner_cutoff_ev(Absorber::HI)).ln();
        if (crossing > s.ln_a) != seen.contains(&index) {
            return Err(invalid());
        }
    }
    let l = &s.ledger;
    for value in [
        l.emitted_n,
        l.emitted_e,
        l.out_n,
        l.out_e,
        l.redshift_e,
        l.escape_e,
        l.work_e,
        l.dr,
        l.excluded_dr_e,
        l.underflow_n_bound,
        l.underflow_e_bound,
        l.cmb_abs_e,
    ]
    .iter()
    .chain(l.absorption.iter())
    .chain(l.ci.iter())
    .chain(l.rr.iter())
    .chain(l.floor.iter())
    .chain(l.cap_e.iter())
    {
        if !value.is_finite() || *value < 0.0 {
            return Err(invalid());
        }
    }
    if l.underflow_n_bound > 1e-20
        || l.underflow_e_bound > 1e-30
        || !l.cmb_e.is_finite()
        || l.cmb_abs_e + 1e-30 < l.cmb_e.abs()
    {
        return Err(invalid());
    }
    let mut n = 0.0;
    let mut e = 0.0;
    let ev = HHeModel::controlled_fixture().ev_erg;
    for b in &h.births[..s.birth_cursor] {
        n += b.per_h;
        e += b.per_h * b.energy_ev * ev;
    }
    if n.to_bits() != l.emitted_n.to_bits() || e.to_bits() != l.emitted_e.to_bits() {
        return Err(invalid());
    }
    let balance = h.balances(s).map_err(|_| invalid())?;
    if !balance.iter().all(|x| x.is_finite())
        || balance[0].abs() > 1e-10 * l.emitted_n.max(1e-10)
        || balance[1].abs() > 1e-10 * (l.emitted_e + l.work_e + l.cmb_abs_e + l.escape_e).max(1e-20)
    {
        return Err(invalid());
    }
    Ok(())
}

pub fn encode_checkpoint(
    id: &CheckpointIdentity,
    h: &History,
    s: &HistoryState,
    complete: bool,
) -> Result<String, String> {
    validate_identity(id, h)?;
    validate_state(h, s, complete)?;
    let mut out = String::new();
    macro_rules! put {
        ($key:expr, $v:expr) => {
            writeln!(&mut out, "{}={}", $key, $v).unwrap()
        };
    }
    put!("schema", id.schema_id);
    put!("solver", id.solver_id);
    put!("provider", id.provider_id);
    put!("closure", id.closure_id);
    put!("config_sha256", id.config_sha256);
    put!("source_sha256", id.source_sha256);
    put!("complete", complete);
    put!("ln_a", s.ln_a);
    put!("x_hii", s.gas.fractions[0]);
    put!("x_heii", s.gas.fractions[1]);
    put!("x_heiii", s.gas.fractions[2]);
    put!("w", s.gas.w_erg_per_h);
    put!("birth_cursor", s.birth_cursor);
    put!("output_cursor", s.output_cursor);
    put!("next_dln_a", s.next_dln_a);
    put!("accepted_steps", s.accepted_steps);
    put!("rejected_steps", s.rejected_steps);
    put!("max_residual", s.max_residual);
    let l = &s.ledger;
    for (key, value) in [
        ("emitted_n", l.emitted_n),
        ("emitted_e", l.emitted_e),
        ("out_n", l.out_n),
        ("out_e", l.out_e),
        ("redshift_e", l.redshift_e),
        ("escape_e", l.escape_e),
        ("work_e", l.work_e),
        ("cmb_e", l.cmb_e),
        ("cmb_abs_e", l.cmb_abs_e),
        ("dr", l.dr),
        ("excluded_dr_e", l.excluded_dr_e),
        ("underflow_n_bound", l.underflow_n_bound),
        ("underflow_e_bound", l.underflow_e_bound),
    ] {
        put!(key, value);
    }
    for (key, values) in [
        ("absorption", l.absorption),
        ("ci", l.ci),
        ("rr", l.rr),
        ("floor", l.floor),
        ("cap_e", l.cap_e),
    ] {
        writeln!(&mut out, "{key}={},{},{}", values[0], values[1], values[2]).unwrap();
    }
    put!("packet_count", s.packets.len());
    for p in &s.packets {
        writeln!(
            &mut out,
            "packet={},{},{}",
            p.birth_index, p.per_h, p.log_per_h
        )
        .unwrap();
    }
    Ok(out)
}
fn take<'a, 'b>(map: &mut BTreeMap<&'a str, &'b str>, key: &str) -> Result<&'b str, String> {
    map.remove(key).ok_or_else(invalid)
}
fn number(map: &mut BTreeMap<&str, &str>, key: &str) -> Result<f64, String> {
    let x = take(map, key)?.parse::<f64>().map_err(|_| invalid())?;
    if x.is_finite() {
        Ok(x)
    } else {
        Err(invalid())
    }
}
fn integer(map: &mut BTreeMap<&str, &str>, key: &str) -> Result<usize, String> {
    take(map, key)?.parse().map_err(|_| invalid())
}
fn triple(map: &mut BTreeMap<&str, &str>, key: &str) -> Result<[f64; 3], String> {
    let values: Vec<_> = take(map, key)?.split(',').collect();
    if values.len() != 3 {
        return Err(invalid());
    }
    let mut out = [0.0; 3];
    for (v, text) in out.iter_mut().zip(values) {
        *v = text.parse().map_err(|_| invalid())?;
    }
    Ok(out)
}
pub fn decode_checkpoint(
    text: &str,
    id: &CheckpointIdentity,
    h: &History,
) -> Result<Checkpoint, String> {
    validate_identity(id, h)?;
    let mut map = BTreeMap::new();
    let mut raw_packets = Vec::new();
    for line in text.lines() {
        let (key, value) = line.split_once('=').ok_or_else(invalid)?;
        if key.is_empty() || value.is_empty() {
            return Err(invalid());
        }
        if key == "packet" {
            if raw_packets.len() >= h.config.max_packets {
                return Err(invalid());
            }
            raw_packets.push(value);
        } else if map.insert(key, value).is_some() {
            return Err(invalid());
        }
    }
    for (key, expected) in [
        ("schema", &id.schema_id),
        ("solver", &id.solver_id),
        ("provider", &id.provider_id),
        ("closure", &id.closure_id),
        ("config_sha256", &id.config_sha256),
        ("source_sha256", &id.source_sha256),
    ] {
        if take(&mut map, key)? != expected {
            return Err(identity_mismatch());
        }
    }
    let complete = match take(&mut map, "complete")? {
        "true" => true,
        "false" => false,
        _ => return Err(invalid()),
    };
    let ln_a = number(&mut map, "ln_a")?;
    let gas = IgmGasState::new(
        [
            number(&mut map, "x_hii")?,
            number(&mut map, "x_heii")?,
            number(&mut map, "x_heiii")?,
        ],
        number(&mut map, "w")?,
    )
    .map_err(|_| invalid())?;
    let birth_cursor = integer(&mut map, "birth_cursor")?;
    let output_cursor = integer(&mut map, "output_cursor")?;
    let next_dln_a = number(&mut map, "next_dln_a")?;
    let accepted_steps = integer(&mut map, "accepted_steps")?;
    let rejected_steps = integer(&mut map, "rejected_steps")?;
    let max_residual = number(&mut map, "max_residual")?;
    let ledger = Ledger {
        emitted_n: number(&mut map, "emitted_n")?,
        emitted_e: number(&mut map, "emitted_e")?,
        absorption: triple(&mut map, "absorption")?,
        out_n: number(&mut map, "out_n")?,
        out_e: number(&mut map, "out_e")?,
        redshift_e: number(&mut map, "redshift_e")?,
        escape_e: number(&mut map, "escape_e")?,
        work_e: number(&mut map, "work_e")?,
        cmb_e: number(&mut map, "cmb_e")?,
        cmb_abs_e: number(&mut map, "cmb_abs_e")?,
        ci: triple(&mut map, "ci")?,
        rr: triple(&mut map, "rr")?,
        dr: number(&mut map, "dr")?,
        floor: triple(&mut map, "floor")?,
        cap_e: triple(&mut map, "cap_e")?,
        excluded_dr_e: number(&mut map, "excluded_dr_e")?,
        underflow_n_bound: number(&mut map, "underflow_n_bound")?,
        underflow_e_bound: number(&mut map, "underflow_e_bound")?,
    };
    if integer(&mut map, "packet_count")? != raw_packets.len() || !map.is_empty() {
        return Err(invalid());
    }
    let mut packets = Vec::with_capacity(raw_packets.len());
    for line in raw_packets {
        let values: Vec<_> = line.split(',').collect();
        if values.len() != 3 {
            return Err(invalid());
        }
        packets.push(ActivePacket {
            birth_index: values[0].parse().map_err(|_| invalid())?,
            per_h: values[1].parse().map_err(|_| invalid())?,
            log_per_h: values[2].parse().map_err(|_| invalid())?,
        });
    }
    let state = HistoryState {
        ln_a,
        gas,
        packets,
        birth_cursor,
        output_cursor,
        ledger,
        next_dln_a,
        accepted_steps,
        rejected_steps,
        max_residual,
    };
    validate_state(h, &state, complete)?;
    Ok(Checkpoint { state, complete })
}
