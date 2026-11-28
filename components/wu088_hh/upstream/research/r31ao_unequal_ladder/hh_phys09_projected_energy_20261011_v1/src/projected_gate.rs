//! Saved-data interval consumer for PHYS09. No native source or root bindings.
//!
//! Every incoming signed Jet component is parsed and validated. The exact HH
//! reaction-vector identity is applied before the energy Jet is assembled.
//! Binary64 results enclose the exact rational saved-data calculation, subject
//! to ordinary IEEE-754 arithmetic and the checked input/source premises.
#![forbid(unsafe_code)]

use std::collections::BTreeMap;
use std::path::Path;

pub const DIM: usize = 4;
pub const JET_DIM: usize = 7;
pub const LAMBDA: usize = 4;
pub const BIRTH: usize = 5;
pub const GROUPS: usize = 33;
pub const CHANNELS: usize = 3;
pub const JET_WORD_PAIRS: usize = 1 + JET_DIM + JET_DIM * JET_DIM;
pub const JET_COUNT: usize = DIM + DIM + GROUPS * CHANNELS + 1;
pub const ROWS_PER_STAGE: usize = 10 + 4 * DIM + DIM * DIM
    + JET_COUNT * JET_WORD_PAIRS + GROUPS * CHANNELS;
pub const TERM_NAMES: [&str; 5] = [
    "feedback", "hessian", "lambda_gradient_tail", "birth_gradient", "lambda_birth_tail",
];

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Interval { pub lo: f64, pub hi: f64 }
pub const ZERO: Interval = Interval { lo: 0.0, hi: 0.0 };
pub const ONE: Interval = Interval { lo: 1.0, hi: 1.0 };
pub type Vector = [Interval; DIM];
pub type Matrix = [Vector; DIM];
pub type Result<T> = std::result::Result<T, String>;

fn down(x: f64) -> f64 {
    if x == 0.0 { -f64::from_bits(1) }
    else if x > 0.0 { f64::from_bits(x.to_bits() - 1) }
    else { f64::from_bits(x.to_bits() + 1) }
}
fn up(x: f64) -> f64 {
    if x == 0.0 { f64::from_bits(1) }
    else if x > 0.0 { f64::from_bits(x.to_bits() + 1) }
    else { f64::from_bits(x.to_bits() - 1) }
}

impl Interval {
    pub fn new(lo: f64, hi: f64) -> Result<Self> {
        if lo.is_finite() && hi.is_finite() && lo <= hi { Ok(Self { lo, hi }) }
        else { Err("INVALID_INTERVAL".into()) }
    }
    pub fn point(x: f64) -> Result<Self> { Self::new(x, x) }
    pub fn validate(self) -> Result<()> { Self::new(self.lo, self.hi).map(|_| ()) }
    pub fn is_point(self) -> bool { self.lo.to_bits() == self.hi.to_bits() }
    fn rounded(lo: f64, hi: f64) -> Result<Self> {
        if !lo.is_finite() || !hi.is_finite() { return Err("NONFINITE_ARITHMETIC".into()); }
        let result = (down(lo), up(hi));
        if !result.0.is_finite() || !result.1.is_finite() {
            return Err("OUTWARD_RANGE_OVERFLOW".into());
        }
        Self::new(result.0, result.1)
    }
    pub fn add(self, rhs: Self) -> Result<Self> {
        self.validate()?; rhs.validate()?;
        Self::rounded(self.lo + rhs.lo, self.hi + rhs.hi)
    }
    pub fn sub(self, rhs: Self) -> Result<Self> {
        self.validate()?; rhs.validate()?;
        Self::rounded(self.lo - rhs.hi, self.hi - rhs.lo)
    }
    pub fn neg(self) -> Result<Self> {
        self.validate()?;
        // Negation is exact for finite binary64, including signed zero.
        Self::new(-self.hi, -self.lo)
    }
    pub fn mul(self, rhs: Self) -> Result<Self> {
        self.validate()?; rhs.validate()?;
        let values = [self.lo * rhs.lo, self.lo * rhs.hi,
                      self.hi * rhs.lo, self.hi * rhs.hi];
        if values.iter().any(|x| !x.is_finite()) { return Err("NONFINITE_ARITHMETIC".into()); }
        let lo = values.iter().copied().fold(values[0], f64::min);
        let hi = values.iter().copied().fold(values[0], f64::max);
        Self::rounded(lo, hi)
    }
    pub fn div(self, rhs: Self) -> Result<Self> {
        self.validate()?; rhs.validate()?;
        if rhs.lo <= 0.0 && rhs.hi >= 0.0 { return Err("DIVISOR_CONTAINS_ZERO".into()); }
        let values = [self.lo / rhs.lo, self.lo / rhs.hi,
                      self.hi / rhs.lo, self.hi / rhs.hi];
        if values.iter().any(|x| !x.is_finite()) { return Err("NONFINITE_ARITHMETIC".into()); }
        let lo = values.iter().copied().fold(values[0], f64::min);
        let hi = values.iter().copied().fold(values[0], f64::max);
        Self::rounded(lo, hi)
    }
    pub fn abs_upper(self) -> Result<f64> {
        self.validate()?;
        // Absolute value and endpoint selection introduce no rounding.
        Ok(self.lo.abs().max(self.hi.abs()))
    }
    pub fn contains(self, x: f64) -> bool { self.lo <= x && x <= self.hi }
    pub fn sign(self) -> &'static str {
        if self.hi < 0.0 { "STRICT_NEGATIVE" }
        else if self.lo > 0.0 { "STRICT_POSITIVE" }
        else { "ZERO_CONTAINING" }
    }
    pub fn json(self) -> String {
        format!("{{\"lo_bits\":\"{:016x}\",\"hi_bits\":\"{:016x}\",\"sign\":\"{}\"}}",
                self.lo.to_bits(), self.hi.to_bits(), self.sign())
    }
}

/// These finite probes reject observed flush-to-zero/denormals-as-zero and
/// non-nearest modes. They are a guard, not exhaustive platform attestation.
pub fn check_arithmetic_environment() -> Result<()> {
    use std::hint::black_box;
    let half_normal = black_box(f64::MIN_POSITIVE) * black_box(0.5);
    let twice_sub = black_box(f64::from_bits(1)) * black_box(2.0);
    let half_ulp = f64::from_bits(0x3ca0_0000_0000_0000);
    let three_quarter_ulp = f64::from_bits(0x3ca8_0000_0000_0000);
    let tie = black_box(1.0) + black_box(half_ulp);
    let negative_tie = black_box(-1.0) - black_box(half_ulp);
    let above_tie = black_box(1.0) + black_box(three_quarter_ulp);
    if half_normal.to_bits() != 0x0008_0000_0000_0000 || twice_sub.to_bits() != 2
        || tie.to_bits() != 1.0_f64.to_bits()
        || negative_tie.to_bits() != (-1.0_f64).to_bits()
        || above_tie.to_bits() != 1.0_f64.to_bits() + 1 {
        Err("UNSUPPORTED_ARITHMETIC_ENVIRONMENT".into())
    } else { Ok(()) }
}

#[derive(Clone, Copy, Debug)]
pub struct Jet {
    pub v: Interval,
    pub g: [Interval; JET_DIM],
    pub h: [[Interval; JET_DIM]; JET_DIM],
}
impl Jet {
    pub fn zero() -> Self {
        Self { v: ZERO, g: [ZERO; JET_DIM], h: [[ZERO; JET_DIM]; JET_DIM] }
    }
    pub fn validate(&self) -> Result<()> {
        self.v.validate()?;
        for x in self.g.iter().chain(self.h.iter().flatten()) { x.validate()?; }
        Ok(())
    }
    pub fn add_scaled(&mut self, coefficient: Interval, rhs: &Self) -> Result<()> {
        self.v = self.v.add(coefficient.mul(rhs.v)?)?;
        for i in 0..JET_DIM {
            self.g[i] = self.g[i].add(coefficient.mul(rhs.g[i])?)?;
            for j in 0..JET_DIM {
                self.h[i][j] = self.h[i][j].add(coefficient.mul(rhs.h[i][j])?)?;
            }
        }
        Ok(())
    }
}

#[derive(Clone, Debug)]
pub struct StageInput {
    pub dt: Interval, pub f_he: Interval, pub n_h: Interval, pub n_he: Interval,
    pub kb: Interval, pub ev: Interval, pub hmean: Interval, pub chi: [Interval; 3],
    pub x: Vector, pub center: Vector, pub radius: Vector, pub gc: Vector,
    pub c: Matrix, pub residual: [Jet; DIM], pub nonphoto: [Jet; DIM],
    pub rates: [[Jet; CHANNELS]; GROUPS], pub hhq: Jet,
    pub heat: [[Interval; CHANNELS]; GROUPS],
}

pub fn dot(a: Vector, b: Vector) -> Result<Interval> {
    let mut out = ZERO;
    for i in 0..DIM { out = out.add(a[i].mul(b[i])?)?; }
    Ok(out)
}
pub fn matvec(a: &Matrix, x: Vector) -> Result<Vector> {
    let mut out = [ZERO; DIM];
    for i in 0..DIM { out[i] = dot(a[i], x)?; }
    Ok(out)
}
pub fn bilinear(a: &Matrix, u: Vector, v: Vector) -> Result<Interval> {
    // Match the stated double sum, retaining each signed Hessian entry.
    let mut out = ZERO;
    for i in 0..DIM {
        for j in 0..DIM { out = out.add(a[i][j].mul(u[i])?.mul(v[j])?)?; }
    }
    Ok(out)
}
pub fn determinant(c: &Matrix) -> Result<Interval> {
    let mut out = ZERO;
    for a in 0..DIM { for b in 0..DIM { for d in 0..DIM { for e in 0..DIM {
        let p = [a, b, d, e];
        if (0..DIM).any(|i| (i + 1..DIM).any(|j| p[i] == p[j])) { continue; }
        let inversions: usize = (0..DIM).map(|i|
            (i + 1..DIM).filter(|&j| p[i] > p[j]).count()).sum();
        let mut term = ONE;
        for i in 0..DIM { term = term.mul(c[i][p[i]])?; }
        out = if inversions % 2 == 0 { out.add(term)? } else { out.sub(term)? };
    }}}}
    Ok(out)
}

#[derive(Clone, Copy, Debug)]
pub struct InverseData { pub k: Matrix, pub c: Matrix, pub radius: Vector, pub gamma_upper: f64 }

fn nonnegative_upper(value: Interval) -> Result<f64> {
    value.validate()?;
    if value.hi < 0.0 { Err("NEGATIVE_NORM_BOUND".into()) } else { Ok(value.hi) }
}

pub fn inverse_setup(a: &Matrix, c: &Matrix, radius: Vector) -> Result<InverseData> {
    for r in radius { r.validate()?;
        if !r.is_point() || r.lo <= 0.0 { return Err("INVALID_RADIUS".into()); }
    }
    let mut k = [[ZERO; DIM]; DIM];
    for i in 0..DIM { for j in 0..DIM {
        let mut ca = ZERO;
        for m in 0..DIM { ca = ca.add(c[i][m].mul(a[m][j])?)?; }
        k[i][j] = (if i == j { ONE } else { ZERO }).sub(ca)?;
    }}
    let mut gamma_upper = 0.0_f64;
    for i in 0..DIM {
        let mut sum = ZERO;
        for j in 0..DIM {
            sum = sum.add(Interval::point(k[i][j].abs_upper()?)?.mul(radius[j])?)?;
        }
        gamma_upper = gamma_upper.max(nonnegative_upper(sum.div(radius[i])?)?);
    }
    if gamma_upper >= 1.0 { return Err("CONTRACTION_NOT_STRICT".into()); }
    Ok(InverseData { k, c: *c, radius, gamma_upper })
}

pub fn inverse_action(data: &InverseData, rhs: Vector) -> Result<Vector> {
    let cs = matvec(&data.c, rhs)?;
    let mut total = cs;
    let mut term = cs;
    for _ in 1..4 {
        term = matvec(&data.k, term)?;
        for i in 0..DIM { total[i] = total[i].add(term[i])?; }
    }
    let mut norm_upper = 0.0_f64;
    for i in 0..DIM {
        let bound = Interval::point(cs[i].abs_upper()?)?.div(data.radius[i])?;
        norm_upper = norm_upper.max(nonnegative_upper(bound)?);
    }
    let gamma = Interval::point(data.gamma_upper)?;
    let mut fourth = ONE;
    for _ in 0..4 { fourth = fourth.mul(gamma)?; }
    let tail_factor = fourth.mul(Interval::point(norm_upper)?)?.div(ONE.sub(gamma)?)?;
    for i in 0..DIM {
        let tail_upper = nonnegative_upper(data.radius[i].mul(tail_factor)?)?;
        total[i] = total[i].add(Interval::new(-tail_upper, tail_upper)?)?;
    }
    Ok(total)
}

pub fn energy_row(input: &StageInput) -> Result<Vector> {
    Ok([input.chi[0], input.f_he.mul(input.chi[1])?,
        input.f_he.mul(input.chi[1].add(input.chi[2])?)?, ONE])
}

/// HHQ is validated by evaluate/read_stage. It is absent from this expression
/// because ell H = ell H_g = ell H_gg = 0 for the identical captured chi_H.
/// This omission is the stated algebraic identity, not numerical thresholding.
pub fn assemble_energy(input: &StageInput) -> Result<Jet> {
    let ell = energy_row(input)?;
    let mut energy = Jet::zero();
    for i in 0..DIM { energy.add_scaled(ell[i], &input.nonphoto[i])?; }
    for j in 0..GROUPS { for a in 0..CHANNELS {
        let coefficient = input.heat[j][a].add(input.chi[a])?;
        energy.add_scaled(coefficient, &input.rates[j][a])?;
    }}
    let mut thermal = Jet::zero();
    thermal.v = input.x[3]; thermal.g[3] = ONE;
    let expansion = Interval::point(-2.0)?.mul(input.hmean)?;
    energy.add_scaled(expansion, &thermal)?;
    Ok(energy)
}

pub fn projected_terms(dt: Interval, energy: &Jet, u: Vector, v: Vector, w: Vector)
    -> Result<[Interval; 5]> {
    let eg = std::array::from_fn(|i| energy.g[i]);
    let egg = std::array::from_fn(|i| std::array::from_fn(|j| energy.h[i][j]));
    let eg_lambda = std::array::from_fn(|i| energy.h[i][LAMBDA]);
    let eg_birth = std::array::from_fn(|i| energy.h[i][BIRTH]);
    Ok([dt.mul(dot(eg, w)?)?, dt.mul(bilinear(&egg, u, v)?)?,
        dt.mul(dot(eg_lambda, v)?)?, dt.mul(dot(eg_birth, u)?)?,
        dt.mul(energy.h[LAMBDA][BIRTH])?])
}

#[derive(Clone, Debug)]
pub struct GateOutput {
    pub gamma: Interval, pub margins: Vector, pub u: Vector, pub v: Vector, pub w: Vector,
    pub direct_energy: Interval, pub projected_energy: Interval,
    pub energy_terms: [Interval; 5], pub det_c: Interval,
}

fn validate_input(input: &StageInput) -> Result<()> {
    for (name, leaf) in [("dt", input.dt), ("fHe", input.f_he), ("nH", input.n_h),
        ("nHe", input.n_he), ("kb", input.kb), ("ev", input.ev), ("hmean", input.hmean)] {
        leaf.validate()?;
        if !leaf.is_point() { return Err(format!("NONPOINT_CONSTANT:{name}")); }
        let nonnegative = name == "hmean";
        if (nonnegative && leaf.lo < 0.0) || (!nonnegative && leaf.lo <= 0.0) {
            return Err(format!("INVALID_CONSTANT_DOMAIN:{name}"));
        }
    }
    for chi in input.chi { chi.validate()?;
        if !chi.is_point() || chi.lo <= 0.0 { return Err("INVALID_CHI".into()); }
    }
    for i in 0..DIM {
        input.x[i].validate()?; input.center[i].validate()?; input.radius[i].validate()?;
        input.gc[i].validate()?;
        if !input.center[i].is_point() || !input.radius[i].is_point() || input.radius[i].lo <= 0.0 {
            return Err("INVALID_CENTER_OR_RADIUS".into());
        }
        let ball = input.center[i].add(Interval::new(-input.radius[i].hi, input.radius[i].hi)?)?;
        if ball.lo < input.x[i].lo || ball.hi > input.x[i].hi { return Err("BALL_NOT_INSIDE_X".into()); }
        for x in input.c[i] { x.validate()?;
            if !x.is_point() { return Err("NONPOINT_PRECONDITIONER".into()); }
        }
        input.residual[i].validate()?; input.nonphoto[i].validate()?;
    }
    if input.x.iter().any(|x| x.lo <= 0.0) || input.x[0].hi >= 1.0
        || input.x[1].add(input.x[2])?.hi >= 1.0 {
        return Err("INVALID_GAS_CHART".into());
    }
    input.hhq.validate()?;
    for j in 0..GROUPS { for a in 0..CHANNELS {
        input.rates[j][a].validate()?; input.heat[j][a].validate()?;
        if !input.heat[j][a].is_point() { return Err("NONPOINT_HEAT_LEAF".into()); }
    }}
    Ok(())
}

pub fn evaluate(input: &StageInput) -> Result<GateOutput> {
    check_arithmetic_environment()?;
    validate_input(input)?;
    let det_c = determinant(&input.c)?;
    if det_c.contains(0.0) { return Err("PRECONDITIONER_NONSINGULARITY_UNRESOLVED".into()); }
    let a = std::array::from_fn(|i| std::array::from_fn(|j| input.residual[i].g[j]));
    let inverse = inverse_setup(&a, &input.c, input.radius)?;
    let cgc = matvec(&input.c, input.gc)?;
    let mut margins = [ZERO; DIM];
    for i in 0..DIM {
        let mut row = ZERO;
        for j in 0..DIM {
            row = row.add(Interval::point(inverse.k[i][j].abs_upper()?)?.mul(input.radius[j])?)?;
        }
        let beta_upper = cgc[i].abs_upper()?;
        let row_upper = nonnegative_upper(row)?;
        // A safe interval for the exact-rational scalar margin. The beta and
        // row estimates are upper bounds, not exact scalar approximations.
        margins[i] = input.radius[i].sub(Interval::new(0.0, beta_upper)?)?
            .sub(Interval::new(0.0, row_upper)?)?;
        if margins[i].lo <= 0.0 { return Err(format!("STRICT_IMAGE_MARGIN_FAILED:{i}")); }
    }
    let mut s_lambda = [ZERO; DIM];
    let mut s_birth = [ZERO; DIM];
    for i in 0..DIM {
        s_lambda[i] = input.residual[i].g[LAMBDA].neg()?;
        s_birth[i] = input.residual[i].g[BIRTH].neg()?;
    }
    let u = inverse_action(&inverse, s_lambda)?;
    let v = inverse_action(&inverse, s_birth)?;
    let mut sw = [ZERO; DIM];
    for i in 0..DIM {
        let residual = &input.residual[i];
        let gl = std::array::from_fn(|j| residual.h[j][LAMBDA]);
        let gb = std::array::from_fn(|j| residual.h[j][BIRTH]);
        let gg = std::array::from_fn(|j| std::array::from_fn(|k| residual.h[j][k]));
        sw[i] = residual.h[LAMBDA][BIRTH].add(dot(gl, v)?)?
            .add(dot(gb, u)?)?.add(bilinear(&gg, u, v)?)?.neg()?;
    }
    let w = inverse_action(&inverse, sw)?;
    let direct_energy = dot(energy_row(input)?, w)?;
    let energy = assemble_energy(input)?;
    let energy_terms = projected_terms(input.dt, &energy, u, v, w)?;
    let mut projected_energy = ZERO;
    for term in energy_terms { projected_energy = projected_energy.add(term)?; }
    Ok(GateOutput { gamma: Interval::new(0.0, inverse.gamma_upper)?, margins, u, v, w,
                    direct_energy, projected_energy, energy_terms, det_c })
}

fn bits(word: &str) -> Result<f64> {
    if word.len() != 16 || !word.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)) {
        return Err("EXPECTED_LOWERCASE_16_HEX_BITS".into());
    }
    let raw = u64::from_str_radix(word, 16).map_err(|e| e.to_string())?;
    Ok(f64::from_bits(raw))
}
fn take(map: &mut BTreeMap<String, Interval>, key: &str) -> Result<Interval> {
    map.remove(key).ok_or_else(|| format!("MISSING_KEY:{key}"))
}
fn take_jet(map: &mut BTreeMap<String, Interval>, key: &str) -> Result<Jet> {
    let mut jet = Jet::zero();
    jet.v = take(map, &format!("{key}.v"))?;
    for i in 0..JET_DIM {
        jet.g[i] = take(map, &format!("{key}.g.{i}"))?;
        for j in 0..JET_DIM { jet.h[i][j] = take(map, &format!("{key}.h.{i}.{j}"))?; }
    }
    Ok(jet)
}
fn stage_from_map(mut map: BTreeMap<String, Interval>) -> Result<StageInput> {
    if map.len() != ROWS_PER_STAGE { return Err(format!("STAGE_ROW_COUNT:{}", map.len())); }
    let dt = take(&mut map, "dt")?; let f_he = take(&mut map, "fHe")?;
    let n_h = take(&mut map, "nH")?; let n_he = take(&mut map, "nHe")?;
    let kb = take(&mut map, "kb")?; let ev = take(&mut map, "ev")?;
    let hmean = take(&mut map, "hmean")?;
    let mut chi = [ZERO; 3];
    for i in 0..3 { chi[i] = take(&mut map, &format!("chi.{i}"))?; }
    let mut x = [ZERO; DIM]; let mut center = x; let mut radius = x; let mut gc = x;
    let mut c = [[ZERO; DIM]; DIM];
    let mut residual = [Jet::zero(); DIM]; let mut nonphoto = residual;
    for i in 0..DIM {
        x[i] = take(&mut map, &format!("X.{i}"))?;
        center[i] = take(&mut map, &format!("center.{i}"))?;
        radius[i] = take(&mut map, &format!("radius.{i}"))?;
        gc[i] = take(&mut map, &format!("gc.{i}"))?;
        for j in 0..DIM { c[i][j] = take(&mut map, &format!("C.{i}.{j}"))?; }
        residual[i] = take_jet(&mut map, &format!("G.{i}"))?;
        nonphoto[i] = take_jet(&mut map, &format!("NP.{i}"))?;
    }
    let mut rates = [[Jet::zero(); CHANNELS]; GROUPS];
    let mut heat = [[ZERO; CHANNELS]; GROUPS];
    for j in 0..GROUPS { for a in 0..CHANNELS {
        rates[j][a] = take_jet(&mut map, &format!("RATE.{j}.{a}"))?;
        heat[j][a] = take(&mut map, &format!("HEAT.{j}.{a}"))?;
    }}
    let hhq = take_jet(&mut map, "HHQ")?;
    if !map.is_empty() { return Err(format!("EXTRANEOUS_KEYS:{:?}", map.keys())); }
    let out = StageInput { dt, f_he, n_h, n_he, kb, ev, hmean, chi,
        x, center, radius, gc, c, residual, nonphoto, rates, hhq, heat };
    validate_input(&out)?;
    Ok(out)
}

pub fn parse_input(text: &str) -> Result<[StageInput; 2]> {
    let mut lines = text.lines();
    if lines.next() != Some("stage\tkey\tlo_bits\thi_bits") { return Err("INPUT_HEADER".into()); }
    let mut maps: [BTreeMap<String, Interval>; 2] = std::array::from_fn(|_| BTreeMap::new());
    for (i, line) in lines.enumerate() {
        let columns: Vec<_> = line.split('\t').collect();
        if columns.len() != 4 { return Err(format!("INPUT_COLUMNS:{}", i + 2)); }
        let stage = match columns[0] { "full" => 0, "first_half" => 1,
            _ => return Err(format!("INPUT_STAGE:{}", i + 2)) };
        let value = Interval::new(bits(columns[2])?, bits(columns[3])?)?;
        if maps[stage].insert(columns[1].to_owned(), value).is_some() {
            return Err(format!("DUPLICATE_KEY:{}:{}", columns[0], columns[1]));
        }
    }
    let [full, first_half] = maps;
    Ok([stage_from_map(full)?, stage_from_map(first_half)?])
}

pub fn read_input(path: &Path) -> Result<[StageInput; 2]> {
    use std::io::Read;
    let mut file = std::fs::File::open(path).map_err(|e| format!("INPUT_OPEN:{e}"))?;
    let mut data = Vec::new();
    (&mut file).take(16 * 1024 * 1024 + 1).read_to_end(&mut data)
        .map_err(|e| format!("INPUT_READ:{e}"))?;
    if data.len() > 16 * 1024 * 1024 { return Err("INPUT_SIZE_LIMIT".into()); }
    let text = std::str::from_utf8(&data).map_err(|e| format!("INPUT_UTF8:{e}"))?;
    parse_input(text)
}

fn vector_json(vector: Vector) -> String {
    format!("[{}]", vector.iter().map(|x| x.json()).collect::<Vec<_>>().join(","))
}
impl GateOutput {
    pub fn json(&self, stage: &str) -> Result<String> {
        if stage != "full" && stage != "first_half" { return Err("OUTPUT_STAGE".into()); }
        let terms = TERM_NAMES.iter().zip(self.energy_terms.iter())
            .map(|(name, interval)| format!("\"{}\":{}", name, interval.json()))
            .collect::<Vec<_>>().join(",");
        Ok(format!(concat!("{{\"type\":\"stage\",\"stage\":\"{}\",",
            "\"gamma\":{},\"margins\":{},\"U\":{},\"V\":{},\"W\":{},",
            "\"direct_energy\":{},\"projected_energy\":{},\"energy_terms\":{{{}}},\"det_C\":{}}}"),
            stage, self.gamma.json(), vector_json(self.margins), vector_json(self.u),
            vector_json(self.v), vector_json(self.w), self.direct_energy.json(),
            self.projected_energy.json(), terms, self.det_c.json()))
    }
}
