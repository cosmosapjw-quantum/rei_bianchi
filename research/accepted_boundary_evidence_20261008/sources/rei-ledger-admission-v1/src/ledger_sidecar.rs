//! Conditional bookkeeping only. This module cannot admit a physical transaction.
use canonical::{Charge, Ledger, Wide};
use sidecar::Bounded;
use std::{
    collections::BTreeMap,
    fs::{self, File, OpenOptions},
    io::Write,
    path::{Path, PathBuf},
};
pub type R<T> = Result<T, String>;
pub const HOLD: &str = "HOLD_PROVIDER_RHS_STATE_TIME_QUADRATURE_HISTORY_FULL_WIDE";
pub const SOURCE_PIN: &str = "e92347b95513c01fdd70c4b31adbefaf053186e404a2c59323f4bc2384a36e0b";
fn err(e: impl std::fmt::Display) -> String {
    e.to_string()
}
fn w(x: f64) -> R<Wide> {
    Wide::from_f64(x).map_err(err)
}
fn wide_key(v: Wide) -> (u64, i32) {
    (v.mantissa().to_bits(), v.exponent())
}
fn atom(s: &str) -> String {
    format!("{}:{}", s.len(), s)
}
fn packed(parts: &[String]) -> String {
    parts.iter().map(|x| atom(x)).collect()
}
fn ulp(v: Wide) -> R<Wide> {
    if v.is_empty() {
        Ok(Wide::ZERO)
    } else {
        Wide::from_parts(v.mantissa().next_up() - v.mantissa(), v.exponent()).map_err(err)
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Species {
    HI,
    HeI,
    HeII,
}
impl Species {
    fn index(self) -> usize {
        match self {
            Self::HI => 0,
            Self::HeI => 1,
            Self::HeII => 2,
        }
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Owner {
    A(Species),
    B(Species),
}
impl Owner {
    pub fn term(self) -> usize {
        match self {
            Self::A(s) => 7 + s.index(),
            Self::B(s) => 10 + s.index(),
        }
    }
    fn unit(self) -> Unit {
        match self {
            Self::A(_) => Unit::PhotonsPerH,
            Self::B(_) => Unit::ErgPerH,
        }
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Stage {
    FullCostOnly,
    Half1,
    Half2,
    AcceptedHalfAdd,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Unit {
    PhotonsPerHSecond,
    EvPhotonsPerHSecond,
    ErgPerHSecond,
    PhotonsPerH,
    ErgPerH,
}
impl Unit {
    fn label(self) -> &'static str {
        match self {
            Self::PhotonsPerH => "photons/H",
            Self::ErgPerH => "erg/H",
            Self::PhotonsPerHSecond => "photons/H/s",
            Self::EvPhotonsPerHSecond => "eV photons/H/s",
            Self::ErgPerHSecond => "erg/H/s",
        }
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Conversion {
    EnergyEv,
    Epsilon,
    ProperDt,
    Identity,
}
pub fn conversion(input: Unit, c: Conversion) -> R<Unit> {
    match (input, c) {
        (Unit::PhotonsPerHSecond, Conversion::EnergyEv) => Ok(Unit::EvPhotonsPerHSecond),
        (Unit::EvPhotonsPerHSecond, Conversion::Epsilon) => Ok(Unit::ErgPerHSecond),
        (Unit::PhotonsPerHSecond, Conversion::ProperDt) => Ok(Unit::PhotonsPerH),
        (Unit::ErgPerHSecond, Conversion::ProperDt) => Ok(Unit::ErgPerH),
        (x, Conversion::Identity) => Ok(x),
        _ => Err("invalid dimensional conversion".into()),
    }
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Context {
    pub parent_checkpoint: String,
    pub transition: usize,
    pub source_pin: String,
    pub bits: Vec<u64>,
    pub total_dt_bits: u64,
}
impl Context {
    fn validate(&self) -> R<()> {
        let dt = f64::from_bits(self.total_dt_bits);
        if self.parent_checkpoint.is_empty()
            || self.bits.is_empty()
            || self.source_pin != SOURCE_PIN
            || !dt.is_normal()
            || dt <= 0.
        {
            Err("unsealed context/source/time".into())
        } else {
            Ok(())
        }
    }
    fn identity(&self) -> String {
        packed(&[
            self.parent_checkpoint.clone(),
            self.transition.to_string(),
            self.source_pin.clone(),
            format!("{:?}", self.bits),
            self.total_dt_bits.to_string(),
        ])
    }
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Attempt {
    namespace: String,
    serial: u64,
    path: PathBuf,
}
impl Attempt {
    pub fn identity(&self) -> String {
        packed(&[self.namespace.clone(), self.serial.to_string()])
    }
}
/// Namespace is issued by the parent authority, not invented from process-local time.
/// The exclusive namespace file and append-only attempt leases prevent local reuse.
pub struct Allocator {
    root: PathBuf,
    namespace: String,
}
struct Lock(PathBuf);
impl Drop for Lock {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}
fn lock(root: &Path) -> R<Lock> {
    let p = root.join("LOCK");
    OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&p)
        .map_err(err)?;
    Ok(Lock(p))
}
impl Allocator {
    pub fn open(root: impl AsRef<Path>, parent_issued_namespace: &str) -> R<Self> {
        if parent_issued_namespace.is_empty() {
            return Err("missing parent namespace lease".into());
        }
        let root = root.as_ref().to_path_buf();
        fs::create_dir_all(&root).map_err(err)?;
        let root = fs::canonicalize(&root).map_err(err)?;
        let namespace = packed(&[
            parent_issued_namespace.into(),
            root.to_str().ok_or("non-UTF8 namespace lease root")?.into(),
        ]);
        let _g = lock(&root)?;
        let file = root.join("NAMESPACE");
        match OpenOptions::new().write(true).create_new(true).open(&file) {
            Ok(mut f) => {
                f.write_all(namespace.as_bytes()).map_err(err)?;
                f.sync_all().map_err(err)?;
                File::open(&root).map_err(err)?.sync_all().map_err(err)?;
            }
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => {
                if fs::read_to_string(&file).map_err(err)? != namespace {
                    return Err("namespace lease conflict".into());
                }
            }
            Err(e) => return Err(err(e)),
        }
        Ok(Self { root, namespace })
    }
    pub fn reserve(&self) -> R<Attempt> {
        let _g = lock(&self.root)?;
        let mut next = 0u64;
        for entry in fs::read_dir(&self.root).map_err(err)? {
            let name = entry
                .map_err(err)?
                .file_name()
                .to_string_lossy()
                .into_owned();
            if let Some(v) = name.strip_prefix("attempt-") {
                let n = v.parse::<u64>().map_err(|_| "corrupt attempt lease")?;
                next = next.max(n.checked_add(1).ok_or("attempt exhaustion")?)
            }
        }
        let path = self.root.join(format!("attempt-{next}"));
        let mut f = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&path)
            .map_err(err)?;
        f.write_all(self.namespace.as_bytes()).map_err(err)?;
        f.sync_all().map_err(err)?;
        File::open(&self.root)
            .map_err(err)?
            .sync_all()
            .map_err(err)?;
        Ok(Attempt {
            namespace: self.namespace.clone(),
            serial: next,
            path,
        })
    }
}
#[derive(Clone, Debug, PartialEq)]
pub struct Event {
    pub node: usize,
    pub species: Species,
    pub rate: f64,
    pub energy_ev: f64,
    pub epsilon: f64,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Category {
    FreshSwallowed,
    OperationRounding,
    ReadoutQuantization,
}
#[derive(Clone, Debug, PartialEq)]
struct Op {
    stage: Stage,
    point: usize,
    owner: Owner,
    node: usize,
    ordinal: usize,
    kind: String,
    category: Category,
    raw: Wide,
    coefficient: Wide,
    input: Unit,
    output: Unit,
    path: Vec<Conversion>,
}
impl Op {
    fn edge(&self, c: &Context, a: &Attempt, generation: u64) -> String {
        packed(&[
            a.identity(),
            generation.to_string(),
            c.identity(),
            format!("{:?}", self.stage),
            self.point.to_string(),
            format!("{:?}", self.owner),
            self.node.to_string(),
            self.ordinal.to_string(),
            self.kind.clone(),
            format!("{:?}", self.category),
            format!("{:?}", self.path),
        ])
    }
}
#[derive(Clone, Debug)]
struct Replay {
    b: Bounded,
    ops: Vec<Op>,
    unit: Unit,
}
#[derive(Clone, Debug)]
struct Location {
    stage: Stage,
    point: usize,
    owner: Owner,
    node: usize,
    ordinal: usize,
}
impl Replay {
    fn zero(unit: Unit) -> Self {
        Self {
            b: Bounded::default(),
            ops: Vec::new(),
            unit,
        }
    }
    fn exact(x: f64, unit: Unit) -> R<Self> {
        Ok(Self {
            b: Bounded::exact(x).map_err(err)?,
            ops: Vec::new(),
            unit,
        })
    }
    fn born(&mut self, l: &Location, kind: &str, cat: Category, raw: Wide) -> R<()> {
        self.ops.push(Op {
            stage: l.stage,
            point: l.point,
            owner: l.owner,
            node: l.node,
            ordinal: l.ordinal,
            kind: kind.into(),
            category: cat,
            raw,
            coefficient: w(1.)?,
            input: self.unit,
            output: self.unit,
            path: vec![],
        });
        Ok(())
    }
    fn scale(mut self, x: f64, c: Conversion, l: &Location) -> R<Self> {
        let output = conversion(self.unit, c)?;
        let factor = w(x)?;
        for op in &mut self.ops {
            op.coefficient = op.coefficient.upper_mul(factor).map_err(err)?;
            op.output = conversion(op.output, c)?;
            op.path.push(c)
        }
        let nonzero = !self.b.value.is_empty();
        self.b = self.b.scale(x).map_err(err)?;
        self.unit = output;
        self.born(
            l,
            "multiply",
            Category::OperationRounding,
            if nonzero {
                ulp(self.b.value)?
            } else {
                Wide::ZERO
            },
        )?;
        Ok(self)
    }
    fn add(mut self, b: Self, l: &Location) -> R<Self> {
        if self.unit != b.unit {
            return Err("sum units mismatch".into());
        }
        let (_, lost) = self.b.value.add(b.b.value).map_err(err)?;
        let both = !self.b.value.is_empty() && !b.b.value.is_empty();
        self.b = self.b.add(b.b).map_err(err)?;
        self.ops.extend(b.ops);
        self.born(l, "ordered-add", Category::FreshSwallowed, lost)?;
        self.born(
            l,
            "ordered-add",
            Category::OperationRounding,
            if lost.is_empty() && both {
                ulp(self.b.value)?
            } else {
                Wide::ZERO
            },
        )?;
        Ok(self)
    }
}
#[derive(Clone, Debug, PartialEq)]
pub struct SealedStage {
    context: Context,
    role: Stage,
    point: usize,
    dt: f64,
    events: Vec<Event>,
    observed_bits: Vec<u64>,
    a: [Bounded; 3],
    b: [Bounded; 3],
    ops: Vec<Op>,
}
fn stages_replay(
    context: &Context,
    role: Stage,
    point: usize,
    dt: f64,
    events: &[Event],
) -> R<([Bounded; 3], [Bounded; 3], Vec<Op>)> {
    context.validate()?;
    if !matches!(role, Stage::Half1 | Stage::Half2 | Stage::FullCostOnly)
        || point == 0
        || events.len() > 4096
        || !dt.is_normal()
        || dt <= 0.
    {
        return Err("stage capture domain".into());
    }
    if dt.to_bits()
        != (f64::from_bits(context.total_dt_bits)
            * if role == Stage::FullCostOnly { 1. } else { 0.5 })
        .to_bits()
    {
        return Err("stage proper dt mismatch".into());
    }
    let mut aa: Vec<_> = (0..3)
        .map(|_| Replay::zero(Unit::PhotonsPerHSecond))
        .collect();
    let mut bb: Vec<_> = (0..3).map(|_| Replay::zero(Unit::ErgPerHSecond)).collect();
    let mut prev = None;
    for (j, e) in events.iter().enumerate() {
        let k = (e.node, e.species);
        if prev.is_some_and(|p| p >= k) {
            return Err("node/species order or duplicate capture".into());
        }
        prev = Some(k);
        if !e.energy_ev.is_normal()
            || e.energy_ev <= 0.
            || !e.epsilon.is_normal()
            || e.epsilon <= 0.
            || !e.rate.is_finite()
            || e.rate < 0.
        {
            return Err("observed operand domain".into());
        }
        let i = e.species.index();
        let loc = |owner, ordinal| Location {
            stage: role,
            point,
            owner,
            node: e.node,
            ordinal,
        };
        let term = Replay::exact(e.rate, Unit::PhotonsPerHSecond)?;
        aa[i] = aa[i]
            .clone()
            .add(term.clone(), &loc(Owner::A(e.species), j * 4))?;
        let term = term
            .scale(
                e.energy_ev,
                Conversion::EnergyEv,
                &loc(Owner::B(e.species), j * 4 + 1),
            )?
            .scale(
                e.epsilon,
                Conversion::Epsilon,
                &loc(Owner::B(e.species), j * 4 + 2),
            )?;
        bb[i] = bb[i]
            .clone()
            .add(term, &loc(Owner::B(e.species), j * 4 + 3))?;
    }
    let mut a = [Bounded::default(); 3];
    let mut b = a;
    let mut ops = Vec::new();
    for (i, s) in [Species::HI, Species::HeI, Species::HeII]
        .into_iter()
        .enumerate()
    {
        let loc = |owner| Location {
            stage: role,
            point,
            owner,
            node: usize::MAX,
            ordinal: events.len() * 4 + i,
        };
        let ar = aa[i]
            .clone()
            .scale(dt, Conversion::ProperDt, &loc(Owner::A(s)))?;
        let br = bb[i]
            .clone()
            .scale(dt, Conversion::ProperDt, &loc(Owner::B(s)))?;
        a[i] = ar.b;
        b[i] = br.b;
        ops.extend(ar.ops);
        ops.extend(br.ops);
    }
    Ok((a, b, ops))
}
impl SealedStage {
    pub fn capture(
        context: Context,
        role: Stage,
        point: usize,
        dt: f64,
        events: Vec<Event>,
    ) -> R<Self> {
        let (a, b, ops) = stages_replay(&context, role, point, dt, &events)?;
        let observed_bits = context.bits.clone();
        Ok(Self {
            context,
            role,
            point,
            dt,
            events,
            observed_bits,
            a,
            b,
            ops,
        })
    }
    pub fn owners(&self) -> ([Bounded; 3], [Bounded; 3]) {
        (self.a, self.b)
    }
    fn verify(&self) -> R<()> {
        let (a, b, ops) =
            stages_replay(&self.context, self.role, self.point, self.dt, &self.events)?;
        if self.observed_bits.is_empty() || a != self.a || b != self.b || ops != self.ops {
            return Err("sealed operation witness mismatch".into());
        }
        Ok(())
    }
}
#[derive(Clone, Debug, PartialEq)]
pub struct LeafClaim {
    pub edge: String,
    pub category: Category,
    pub owner: Owner,
    pub raw: Wide,
    pub coefficient: Wide,
    pub input: Unit,
    pub output: Unit,
    pub path: Vec<Conversion>,
}
impl LeafClaim {
    fn from_op(op: &Op, c: &Context, a: &Attempt, generation: u64) -> Self {
        Self {
            edge: op.edge(c, a, generation),
            category: op.category,
            owner: op.owner,
            raw: op.raw,
            coefficient: op.coefficient,
            input: op.input,
            output: op.output,
            path: op.path.clone(),
        }
    }
    fn validate(&self) -> R<()> {
        let mut u = self.input;
        for c in &self.path {
            u = conversion(u, *c)?
        }
        if u != self.output || u != self.owner.unit() {
            return Err("leaf units/owner mismatch".into());
        }
        if !self.raw.is_empty() && self.coefficient.is_empty() {
            return Err("positive bound with zero coefficient".into());
        }
        Ok(())
    }
}
#[derive(Clone, Debug, PartialEq)]
pub struct NativeReceipt {
    pub error_norm_bits: u64,
    pub total_rhs_evaluations: usize,
    pub accepted_stage_rhs: [usize; 2],
    pub accepted_stage_iterations: [usize; 2],
    pub legacy_ledger: String,
    pub scope: String,
}
#[derive(Clone, Debug)]
pub struct Proposal {
    attempt: Attempt,
    context: Context,
    pub expected_generation: u64,
    halves: [SealedStage; 2],
    pub leaves: Vec<LeafClaim>,
    pub a: [Bounded; 3],
    pub b: [Bounded; 3],
    pub state_out: Vec<u64>,
    pub original_increment: [Wide; 11],
    pub original_private_gate: bool,
    export: bool,
    native_receipt: Option<NativeReceipt>,
}
fn accepted_replay(
    c: &Context,
    a: &Attempt,
    h: &[SealedStage; 2],
    export: bool,
    generation: u64,
) -> R<([Bounded; 3], [Bounded; 3], Vec<LeafClaim>)> {
    c.validate()?;
    if h[0].role != Stage::Half1
        || h[1].role != Stage::Half2
        || h[0].context != *c
        || h[1].context != *c
        || h[0].point >= h[1].point
    {
        return Err("accepted half order/context mismatch".into());
    }
    for s in h {
        s.verify()?
    }
    let mut aa = [Bounded::default(); 3];
    let mut bb = aa;
    let mut claims = Vec::new();
    for op in h.iter().flat_map(|s| &s.ops) {
        claims.push(LeafClaim::from_op(op, c, a, generation))
    }
    for (i, s) in [Species::HI, Species::HeI, Species::HeII]
        .into_iter()
        .enumerate()
    {
        for (owner, left, right, out) in [
            (Owner::A(s), h[0].a[i], h[1].a[i], &mut aa[i]),
            (Owner::B(s), h[0].b[i], h[1].b[i], &mut bb[i]),
        ] {
            let (_, lost) = left.value.add(right.value).map_err(err)?;
            *out = left.add(right).map_err(err)?;
            let base = Op {
                stage: Stage::AcceptedHalfAdd,
                point: h[1].point,
                owner,
                node: usize::MAX,
                ordinal: i,
                kind: "half1-then-half2".into(),
                category: Category::FreshSwallowed,
                raw: lost,
                coefficient: w(1.)?,
                input: owner.unit(),
                output: owner.unit(),
                path: vec![],
            };
            claims.push(LeafClaim::from_op(&base, c, a, generation));
            let mut ro = base.clone();
            ro.category = Category::OperationRounding;
            ro.raw = if lost.is_empty() && !left.value.is_empty() && !right.value.is_empty() {
                ulp(out.value)?
            } else {
                Wide::ZERO
            };
            claims.push(LeafClaim::from_op(&ro, c, a, generation));
            if export {
                let read = out.readout().map_err(err)?;
                let mut q = base;
                q.kind = "performed-readout".into();
                q.category = Category::ReadoutQuantization;
                q.raw = read.quantization;
                claims.push(LeafClaim::from_op(&q, c, a, generation));
            }
        }
    }
    Ok((aa, bb, claims))
}
impl Proposal {
    /// Input increment/gate are the caller's existing canonical request; never inferred.
    pub fn new(
        attempt: Attempt,
        context: Context,
        generation: u64,
        halves: [SealedStage; 2],
        state_out: Vec<u64>,
        original_increment: [Wide; 11],
        original_private_gate: bool,
        performed_export: bool,
    ) -> R<Self> {
        let (a, b, leaves) =
            accepted_replay(&context, &attempt, &halves, performed_export, generation)?;
        Ok(Self {
            attempt,
            context,
            expected_generation: generation,
            halves,
            leaves,
            a,
            b,
            state_out,
            original_increment,
            original_private_gate,
            export: performed_export,
            native_receipt: None,
        })
    }
    pub fn from_native_trial(
        attempt: Attempt,
        context: Context,
        generation: u64,
        trial: sidecar::DetailedTrial,
        original_increment: [Wide; 11],
        original_private_gate: bool,
        performed_export: bool,
    ) -> R<Self> {
        let accepted = trial.accept().map_err(err)?;
        if accepted.scope != sidecar::SCOPE {
            return Err("native capture scope mismatch".into());
        }
        let capture = |role, stage: &sidecar::SpeciesStage| -> R<SealedStage> {
            let events = stage
                .rate
                .events
                .iter()
                .map(|e| {
                    Ok(Event {
                        node: e.node,
                        species: match e.species {
                            0 => Species::HI,
                            1 => Species::HeI,
                            2 => Species::HeII,
                            _ => return Err("native species identity".into()),
                        },
                        rate: e.event_per_h_s,
                        energy_ev: e.energy_ev,
                        epsilon: e.epsilon,
                    })
                })
                .collect::<R<Vec<_>>>()?;
            let mut seal = SealedStage::capture(
                context.clone(),
                role,
                stage.rate.point_ordinal,
                stage.dt_s,
                events,
            )?;
            if seal.a != stage.count
                || seal.b != stage.absorbed_energy
                || stage.rate.context_bits.is_empty()
            {
                return Err("native operation replay mismatch".into());
            }
            if context.bits.len() < 4
                || stage.rate.context_bits.len() < 4
                || stage.rate.context_bits[..4] != context.bits[..4]
            {
                return Err("native SAME-context density/H/TCMB mismatch".into());
            }
            seal.observed_bits = stage.rate.context_bits.clone();
            Ok(seal)
        };
        let halves = [
            capture(Stage::Half1, &accepted.stages[0])?,
            capture(Stage::Half2, &accepted.stages[1])?,
        ];
        let gas = &accepted.legacy.state.gas;
        let mut state = gas.fractions.map(f64::to_bits).to_vec();
        state.push(gas.w_erg_per_h.to_bits());
        for n in &accepted.legacy.state.photons {
            state.extend([n.energy_ev.to_bits(), n.photons_per_h.to_bits()]);
        }
        let mut p = Self::new(
            attempt,
            context,
            generation,
            halves,
            state,
            original_increment,
            original_private_gate,
            performed_export,
        )?;
        if p.a != accepted.count || p.b != accepted.absorbed_energy {
            return Err("native accepted-half mismatch".into());
        }
        p.native_receipt = Some(NativeReceipt {
            error_norm_bits: accepted.legacy.error_norm.to_bits(),
            total_rhs_evaluations: accepted.legacy.total_rhs_evaluations,
            accepted_stage_rhs: accepted.legacy.stages.each_ref().map(|s| s.rhs_evaluations),
            accepted_stage_iterations: accepted.legacy.stages.each_ref().map(|s| s.iterations),
            legacy_ledger: format!("{:?}", accepted.legacy.ledger),
            scope: accepted.scope.into(),
        });
        Ok(p)
    }
    pub fn native_receipt(&self) -> Option<&NativeReceipt> {
        self.native_receipt.as_ref()
    }
    fn verify(&self) -> R<()> {
        let (a, b, leaves) = accepted_replay(
            &self.context,
            &self.attempt,
            &self.halves,
            self.export,
            self.expected_generation,
        )?;
        if leaves != self.leaves || a != self.a || b != self.b || self.state_out.is_empty() {
            return Err("missing/extra/reordered operation witness or output".into());
        }
        Ok(())
    }
}
#[derive(Clone, Debug, PartialEq)]
struct Binding {
    category: Category,
    owner: Owner,
    raw: Wide,
    coefficient: (u64, i32),
    input: Unit,
    output: Unit,
    path: Vec<Conversion>,
}
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Registry {
    bindings: BTreeMap<String, Binding>,
}
impl Registry {
    pub fn len(&self) -> usize {
        self.bindings.len()
    }
    pub fn bind(&mut self, c: &LeafClaim) -> R<()> {
        c.validate()?;
        if let Some(b) = self.bindings.get(&c.edge) {
            return Err(if b.coefficient != wide_key(c.coefficient) {
                "conflicting coefficient for occurrence"
            } else {
                "duplicate global occurrence"
            }
            .into());
        }
        self.bindings.insert(
            c.edge.clone(),
            Binding {
                category: c.category,
                owner: c.owner,
                raw: c.raw,
                coefficient: wide_key(c.coefficient),
                input: c.input,
                output: c.output,
                path: c.path.clone(),
            },
        );
        Ok(())
    }
}
#[derive(Clone, Debug, PartialEq)]
pub struct WitnessBundle {
    generation: u64,
    attempt: String,
    context: Context,
    halves: [SealedStage; 2],
    leaves: Vec<LeafClaim>,
    performed_export: bool,
    native_receipt: Option<NativeReceipt>,
}
#[derive(Clone, Debug, PartialEq)]
pub struct Snapshot {
    pub generation: u64,
    pub ledger: Ledger,
    pub registry: Registry,
    pub state: Vec<u64>,
    pub a: [Bounded; 3],
    pub b: [Bounded; 3],
    pub context_identity: String,
    pub hold: &'static str,
    pub witnesses: Vec<WitnessBundle>,
}
impl Snapshot {
    pub fn initial(ledger: Ledger, state: Vec<u64>, context: &Context) -> R<Self> {
        context.validate()?;
        if state.is_empty() {
            return Err("empty snapshot state".into());
        }
        Ok(Self {
            generation: 0,
            ledger,
            registry: Registry::default(),
            state,
            a: [Bounded::default(); 3],
            b: [Bounded::default(); 3],
            context_identity: context.identity(),
            hold: HOLD,
            witnesses: Vec::new(),
        })
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FailAt {
    None,
    BeforeWitness,
    AfterRegistry,
    AfterCanonicalCommit,
    BeforePublish,
}
pub struct DiagnosticStore {
    root: PathBuf,
    snapshot: Snapshot,
}
#[derive(Debug)]
pub struct Publication {
    pub generation: u64,
    pub physical_admission: &'static str,
    pub directory_synced: bool,
}
fn image(s: &Snapshot) -> String {
    format!("{s:?}\n")
}
impl DiagnosticStore {
    /// Restart supplies the independently restored typed snapshot; full bytes must agree.
    pub fn open(root: impl AsRef<Path>, restored: Snapshot) -> R<Self> {
        let root = root.as_ref().to_path_buf();
        fs::create_dir_all(&root).map_err(err)?;
        let _g = lock(&root)?;
        let path = root.join("HEAD");
        match OpenOptions::new().write(true).create_new(true).open(&path) {
            Ok(mut f) => {
                f.write_all(image(&restored).as_bytes()).map_err(err)?;
                f.sync_all().map_err(err)?;
                File::open(&root).map_err(err)?.sync_all().map_err(err)?
            }
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => {
                if fs::read_to_string(&path).map_err(err)? != image(&restored) {
                    return Err("stale or conflicting restored snapshot".into());
                }
            }
            Err(e) => return Err(err(e)),
        }
        Ok(Self {
            root,
            snapshot: restored,
        })
    }
    pub fn snapshot(&self) -> &Snapshot {
        &self.snapshot
    }
    pub fn publish_physical(&self) -> R<()> {
        Err(HOLD.into())
    }
    pub fn apply(&mut self, p: &Proposal, fail: FailAt) -> R<Publication> {
        let _g = lock(&self.root)?;
        if fs::read_to_string(self.root.join("HEAD")).map_err(err)? != image(&self.snapshot)
            || p.expected_generation != self.snapshot.generation
            || p.context.identity() != self.snapshot.context_identity
        {
            return Err("stale ledger generation/context".into());
        }
        if fs::read_to_string(&p.attempt.path).map_err(err)? != p.attempt.namespace {
            return Err("invalid durable attempt lease".into());
        }
        if fail == FailAt::BeforeWitness {
            return Err("injected pre-witness refusal".into());
        }
        p.verify()?;
        let mut candidate = self.snapshot.clone();
        let mut charges = Vec::new();
        for c in &p.leaves {
            candidate.registry.bind(c)?;
            if matches!(
                c.category,
                Category::FreshSwallowed | Category::ReadoutQuantization
            ) {
                charges.push(Charge {
                    lane: p.attempt.namespace.clone(),
                    transition: p.context.transition,
                    boundary: format!("{:?}", c.category),
                    id: c.edge.clone(),
                    term: c.owner.term(),
                    bound: c.raw,
                    coefficient: c.coefficient,
                    units: c.output.label(),
                })
            }
        }
        if fail == FailAt::AfterRegistry {
            return Err("injected registry refusal".into());
        }
        candidate
            .ledger
            .commit(p.original_increment, charges, p.original_private_gate)?;
        if fail == FailAt::AfterCanonicalCommit {
            return Err("injected commit refusal".into());
        }
        candidate.generation = candidate
            .generation
            .checked_add(1)
            .ok_or("generation exhaustion")?;
        candidate.a = p.a;
        candidate.b = p.b;
        candidate.state = p.state_out.clone();
        candidate.hold = HOLD;
        candidate.witnesses.push(WitnessBundle {
            generation: p.expected_generation,
            attempt: p.attempt.identity(),
            context: p.context.clone(),
            halves: p.halves.clone(),
            leaves: p.leaves.clone(),
            performed_export: p.export,
            native_receipt: p.native_receipt.clone(),
        });
        let tmp = self.root.join(format!(
            "pending-{}-{}",
            p.attempt.serial, candidate.generation
        ));
        let mut f = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&tmp)
            .map_err(err)?;
        let stage = (|| -> R<()> {
            f.write_all(image(&candidate).as_bytes()).map_err(err)?;
            f.sync_all().map_err(err)?;
            File::open(&self.root)
                .map_err(err)?
                .sync_all()
                .map_err(err)?;
            if fail == FailAt::BeforePublish {
                return Err("injected publication refusal".into());
            }
            fs::rename(&tmp, self.root.join("HEAD")).map_err(err)?;
            Ok(())
        })();
        if stage.is_err() {
            let _ = fs::remove_file(&tmp);
            return stage.map(|_| unreachable!());
        }
        // Rename is the publication point. Nothing after it returns a rollback-shaped Err.
        self.snapshot = candidate;
        let directory_synced = File::open(&self.root).and_then(|f| f.sync_all()).is_ok();
        Ok(Publication {
            generation: self.snapshot.generation,
            physical_admission: HOLD,
            directory_synced,
        })
    }
}
