//! Strict bounded v2 binary checkpoint. Replay canonical ordered operations, never RHS.
use super::*;
use std::process::{Command, Stdio};
const MAGIC: &[u8] = b"REI_NATIVE_RECEIVER_CHECKPOINT_V2\n";
pub(super) const MAX: usize = 4 * 1024 * 1024;
fn hash(bytes: &[u8]) -> R<String> {
    // Matches the accepted receiver's sha256sum-based checkpoint convention.
    let mut child = Command::new("sha256sum")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(err)?;
    let written = child.stdin.take().ok_or("hash stdin")?.write_all(bytes);
    let result = child.wait_with_output().map_err(err)?;
    written.map_err(err)?;
    if !result.status.success() {
        return Err("SHA256 failed".into());
    }
    let h = std::str::from_utf8(&result.stdout)
        .map_err(err)?
        .split_whitespace()
        .next()
        .ok_or("hash output")?;
    if h.len() != 64
        || !h
            .bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
    {
        return Err("invalid hash".into());
    }
    Ok(h.into())
}
struct W(Vec<u8>);
impl W {
    fn n(&mut self, x: u64) {
        self.0.extend(x.to_le_bytes())
    }
    fn text(&mut self, x: &str) {
        self.n(x.len() as u64);
        self.0.extend(x.as_bytes())
    }
    fn bits(&mut self, x: &[u64]) {
        self.n(x.len() as u64);
        for v in x {
            self.n(*v)
        }
    }
    fn wide(&mut self, x: Wide) {
        self.n(x.mantissa().to_bits());
        self.n(x.exponent() as i64 as u64)
    }
    fn context(&mut self, c: &Context) {
        self.text(&c.parent_checkpoint);
        self.n(c.transition as u64);
        self.text(&c.source_pin);
        self.bits(&c.bits);
        self.n(c.total_dt_bits)
    }
    fn proposal(&mut self, p: &Proposal) {
        self.text(&p.attempt.namespace);
        self.n(p.attempt.serial);
        self.text(p.attempt.path.to_str().unwrap());
        self.context(&p.context);
        self.n(p.expected_generation);
        for s in &p.halves {
            self.n(s.point as u64);
            self.n(s.dt.to_bits());
            self.bits(&s.observed_bits);
            self.n(s.events.len() as u64);
            for e in &s.events {
                self.n(e.node as u64);
                self.n(e.species.index() as u64);
                self.n(e.rate.to_bits());
                self.n(e.energy_ev.to_bits());
                self.n(e.epsilon.to_bits())
            }
        }
        self.bits(&p.state_out);
        for v in p.original_increment {
            self.wide(v)
        }
        self.n(p.original_private_gate as u64);
        self.n(p.export as u64);
        match &p.native_receipt {
            None => self.n(0),
            Some(n) => {
                self.n(1);
                self.n(n.error_norm_bits);
                self.n(n.total_rhs_evaluations as u64);
                self.n(n.observed_point_calls as u64);
                self.n(n.observed_provider_calls as u64);
                for v in n.accepted_stage_rhs {
                    self.n(v as u64)
                }
                for v in n.accepted_stage_iterations {
                    self.n(v as u64)
                }
                self.text(&n.legacy_ledger);
                self.text(&n.scope)
            }
        }
    }
}
struct D<'a> {
    b: &'a [u8],
    i: usize,
}
impl<'a> D<'a> {
    fn take(&mut self, n: usize) -> R<&'a [u8]> {
        let end = self.i.checked_add(n).ok_or("length overflow")?;
        let b = self.b.get(self.i..end).ok_or("incomplete checkpoint")?;
        self.i = end;
        Ok(b)
    }
    fn n(&mut self) -> R<u64> {
        Ok(u64::from_le_bytes(self.take(8)?.try_into().unwrap()))
    }
    fn size(&mut self, cap: usize) -> R<usize> {
        let n = usize::try_from(self.n()?).map_err(err)?;
        if n > cap {
            return Err("checkpoint length cap".into());
        }
        Ok(n)
    }
    fn text(&mut self) -> R<String> {
        let n = self.size(65536)?;
        String::from_utf8(self.take(n)?.to_vec()).map_err(err)
    }
    fn bits(&mut self) -> R<Vec<u64>> {
        let n = self.size(4096)?;
        (0..n).map(|_| self.n()).collect()
    }
    fn boolean(&mut self) -> R<bool> {
        match self.n()? {
            0 => Ok(false),
            1 => Ok(true),
            _ => Err("invalid boolean".into()),
        }
    }
    fn wide(&mut self) -> R<Wide> {
        let bits = self.n()?;
        let exp = i32::try_from(self.n()? as i64).map_err(err)?;
        let v = Wide::from_parts(f64::from_bits(bits), exp).map_err(err)?;
        if wide_key(v) != (bits, exp) {
            return Err("noncanonical Wide".into());
        }
        Ok(v)
    }
    fn context(&mut self) -> R<Context> {
        let c = Context {
            parent_checkpoint: self.text()?,
            transition: self.size(4)?,
            source_pin: self.text()?,
            bits: self.bits()?,
            total_dt_bits: self.n()?,
        };
        c.validate()?;
        Ok(c)
    }
    fn proposal(&mut self) -> R<Proposal> {
        let attempt = Attempt {
            namespace: self.text()?,
            serial: self.n()?,
            path: PathBuf::from(self.text()?),
        };
        let context = self.context()?;
        let generation = self.n()?;
        let mut stages = Vec::new();
        for role in [Stage::Half1, Stage::Half2] {
            let point = self.size(1000000)?;
            let dt = f64::from_bits(self.n()?);
            let observed = self.bits()?;
            let n = self.size(4096)?;
            let mut events = Vec::new();
            for _ in 0..n {
                let node = self.size(4096)?;
                let species = match self.n()? {
                    0 => Species::HI,
                    1 => Species::HeI,
                    2 => Species::HeII,
                    _ => return Err("invalid species".into()),
                };
                events.push(Event {
                    node,
                    species,
                    rate: f64::from_bits(self.n()?),
                    energy_ev: f64::from_bits(self.n()?),
                    epsilon: f64::from_bits(self.n()?),
                })
            }
            let mut s = SealedStage::capture(context.clone(), role, point, dt, events)?;
            if observed.len() < 4 || context.bits.len() < 4 || observed[..4] != context.bits[..4] {
                return Err("checkpoint observed context conflict".into());
            }
            s.observed_bits = observed;
            stages.push(s);
        }
        let state = self.bits()?;
        let mut inc = [Wide::ZERO; 11];
        for v in &mut inc {
            *v = self.wide()?
        }
        let gate = self.boolean()?;
        let export = self.boolean()?;
        let mut p = Proposal::new(
            attempt,
            context,
            generation,
            stages.try_into().unwrap(),
            state,
            inc,
            gate,
            export,
        )?;
        if self.boolean()? {
            let n = NativeReceipt {
                error_norm_bits: self.n()?,
                total_rhs_evaluations: self.size(1000000)?,
                observed_point_calls: self.size(1000000)?,
                observed_provider_calls: self.size(1000000)?,
                accepted_stage_rhs: [self.size(1000000)?, self.size(1000000)?],
                accepted_stage_iterations: [self.size(1000000)?, self.size(1000000)?],
                legacy_ledger: self.text()?,
                scope: self.text()?,
            };
            let error = f64::from_bits(n.error_norm_bits);
            if n.scope != sidecar::SCOPE
                || !error.is_finite()
                || !(0. ..=1.).contains(&error)
                || n.total_rhs_evaluations < n.accepted_stage_rhs.iter().sum()
                || n.observed_point_calls != n.total_rhs_evaluations
            {
                return Err("native receipt refusal".into());
            }
            p.native_receipt = Some(n);
        }
        Ok(p)
    }
}
pub(super) fn encode(s: &Snapshot) -> R<Vec<u8>> {
    let mut w = W(Vec::new());
    w.context(&s.base_context);
    w.bits(&s.base_state);
    w.n(s.journal.len() as u64);
    for p in &s.journal {
        w.proposal(p)
    }
    w.text(&hash(format!("{s:?}").as_bytes())?);
    if w.0.len() > MAX {
        return Err("checkpoint cap".into());
    }
    let mut out = MAGIC.to_vec();
    out.extend(hash(&w.0)?.as_bytes());
    out.push(b'\n');
    out.extend(w.0);
    if out.len() > MAX {
        return Err("full checkpoint envelope cap".into());
    }
    // Preflight the exact restart decoder before publication. Never publish an
    // image whose schema limits or typed canonical replay cannot round-trip.
    if decode(&out)? != *s {
        return Err("checkpoint encoder roundtrip".into());
    }
    Ok(out)
}
pub(super) fn decode(bytes: &[u8]) -> R<Snapshot> {
    if bytes.len() > MAX || !bytes.starts_with(MAGIC) {
        return Err("checkpoint schema/cap".into());
    }
    let (h, payload) = bytes[MAGIC.len()..]
        .split_at_checked(65)
        .ok_or("incomplete checkpoint header")?;
    if h[64] != b'\n' || hash(payload)?.as_bytes() != &h[..64] {
        return Err("checkpoint checksum".into());
    }
    let mut d = D { b: payload, i: 0 };
    let c = d.context()?;
    let state = d.bits()?;
    let mut s = Snapshot::initial(Ledger::default(), state, &c)?;
    let n = d.size(4)?;
    for _ in 0..n {
        let p = d.proposal()?;
        s = replay_candidate(&s, &p, FailAt::None)?
    }
    let expected = d.text()?;
    if d.i != payload.len() || hash(format!("{s:?}").as_bytes())? != expected {
        return Err("checkpoint typed state mismatch/trailing bytes".into());
    }
    Ok(s)
}
