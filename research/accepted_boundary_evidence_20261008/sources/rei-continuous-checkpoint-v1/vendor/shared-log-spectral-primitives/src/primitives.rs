//! Bounded standalone primitives. No material solver or persistent photon atoms.
#[path = "../../continuous-boundary-prototype-v2/src/primitives.rs"]
#[allow(dead_code)]
mod v2;
use std::sync::atomic::{AtomicUsize, Ordering};
static LIVE_SITES: AtomicUsize = AtomicUsize::new(0);
static PEAK_SITES: AtomicUsize = AtomicUsize::new(0);
pub struct SiteLease(usize);
pub fn reserve_site_capacity(n:usize)->R<SiteLease>{SiteLease::new(n)}
impl SiteLease {
    fn new(n: usize) -> R<Self> {
        let live = LIVE_SITES.fetch_add(n, Ordering::SeqCst) + n;
        if live > 4096 {
            LIVE_SITES.fetch_sub(n, Ordering::SeqCst);
            return Err("quadrature site cap");
        };
        PEAK_SITES.fetch_max(live, Ordering::SeqCst);
        Ok(Self(n))
    }
}
impl Drop for SiteLease {
    fn drop(&mut self) {
        LIVE_SITES.fetch_sub(self.0, Ordering::SeqCst);
    }
}
pub fn site_counts() -> (usize, usize) {
    (
        LIVE_SITES.load(Ordering::SeqCst),
        PEAK_SITES.load(Ordering::SeqCst),
    )
}
pub const EPS: f64 = 1.602176634e-12;
const MAX_EXP: i32 = 1 << 20;
const LN2_LO: f64 = 2.3190468138462996e-17;
type R<T> = Result<T, &'static str>;
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Wide {
    mant: f64,
    exp: i32,
}
impl Wide {
    pub fn mantissa(self) -> f64 {
        self.mant
    }
    pub fn exponent(self) -> i32 {
        self.exp
    }
    pub const ZERO: Self = Self { mant: 0.0, exp: 0 };
    pub fn is_empty(self) -> bool {
        self.mant == 0.0
    }
    pub fn from_parts(mant: f64, exp: i32) -> R<Self> {
        if !mant.is_finite() || mant < 0.0 || !(-MAX_EXP..=MAX_EXP).contains(&exp) {
            return Err("invalid wide amplitude");
        }
        if mant == 0.0 {
            return Ok(Self::ZERO);
        }
        let (m, e) = if mant.is_normal() {
            let e = ((mant.to_bits() >> 52) & 2047) as i32 - 1023;
            (
                f64::from_bits((mant.to_bits() & ((1u64 << 52) - 1)) | (1023u64 << 52)),
                e,
            )
        } else {
            let a = Self::from_parts(mant * 2.0f64.powi(52), 0)?;
            (a.mant, a.exp - 52)
        };
        let k = exp.checked_add(e).ok_or("exponent overflow")?;
        if !(-MAX_EXP..=MAX_EXP).contains(&k) {
            return Err("wide exponent outside contract");
        }
        Ok(Self { mant: m, exp: k })
    }
    pub fn from_f64(x: f64) -> R<Self> {
        Self::from_parts(x, 0)
    }
    pub fn from_log(x: f64) -> R<Self> {
        if !x.is_finite() {
            return Err("nonfinite positive log");
        }
        let k = (x / std::f64::consts::LN_2).floor();
        if k.abs() > MAX_EXP as f64 - 2.0 {
            return Err("log outside exponent contract");
        }
        let r = (-k).mul_add(std::f64::consts::LN_2, x) - k * LN2_LO;
        Self::from_parts(r.exp(), k as i32)
    }
    pub fn log(self) -> f64 {
        if self.is_empty() {
            f64::NEG_INFINITY
        } else {
            (self.exp as f64).mul_add(
                std::f64::consts::LN_2,
                self.mant.ln() + (self.exp as f64) * LN2_LO,
            )
        }
    }
    pub fn validate_log(self, log: f64) -> R<()> {
        if self.is_empty() {
            if log == f64::NEG_INFINITY {
                Ok(())
            } else {
                Err("empty/log inconsistency")
            }
        } else if !log.is_finite() || (log - self.log()).abs() > 2e-13 + 8.0 * ulp(self.log()) {
            Err("positive/log inconsistency")
        } else {
            Ok(())
        }
    }
    pub fn mul(self, b: Self) -> R<Self> {
        if self.is_empty() || b.is_empty() {
            Ok(Self::ZERO)
        } else {
            Self::from_parts(
                self.mant * b.mant,
                self.exp.checked_add(b.exp).ok_or("exponent overflow")?,
            )
        }
    }
    // The second result is the whole contribution lost by common-scale arithmetic,
    // not a dimensionless MIN_POSITIVE placeholder. Partial normal rounding is separate.
    pub fn add(self, b: Self) -> R<(Self, Self)> {
        if self.is_empty() {
            return Ok((b, Self::ZERO));
        }
        if b.is_empty() {
            return Ok((self, Self::ZERO));
        }
        let (a, b) = if self.exp >= b.exp {
            (self, b)
        } else {
            (b, self)
        };
        let d = a.exp - b.exp;
        if d > 1022 {
            return Ok((a, b));
        }
        let x = b.mant * 2.0f64.powi(-d);
        let s = a.mant + x;
        let lost = if s == a.mant { b } else { Self::ZERO };
        Ok((Self::from_parts(s, a.exp)?, lost))
    }
    pub fn upper_add(self, b: Self) -> R<Self> {
        if self.is_empty() {
            return Ok(b);
        }
        if b.is_empty() {
            return Ok(self);
        }
        let (s, _) = self.add(b)?;
        Self::from_parts(s.mant.next_up(), s.exp)
    }
    pub fn upper_mul(self, b: Self) -> R<Self> {
        let s = self.mul(b)?;
        if s.is_empty() {
            Ok(s)
        } else {
            Self::from_parts(s.mant.next_up(), s.exp)
        }
    }
    pub fn le(self, b: Self) -> bool {
        self.is_empty()
            || (!b.is_empty() && (self.exp < b.exp || (self.exp == b.exp && self.mant <= b.mant)))
    }
    /// Readout is optional. The second result encloses only quantization at this boundary.
    pub fn readout(self) -> R<(f64, Self)> {
        if self.is_empty() {
            return Ok((0.0, Self::ZERO));
        }
        if self.exp > 1023 {
            return Err("readout overflow");
        }
        let v = if self.exp >= -1022 {
            self.mant * 2.0f64.powi(self.exp)
        } else if self.exp >= -1075 {
            (self.mant * 2.0f64.powi(self.exp + 1074)) * f64::from_bits(1)
        } else {
            0.0
        };
        if !v.is_finite() {
            return Err("readout overflow");
        }
        let bound = if v == 0.0 {
            self
        } else if self.exp < -1022 && Self::from_f64(v)? != self {
            Self::from_parts(1.0, -1075)?
        } else {
            Self::ZERO
        };
        Ok((v, bound))
    }
    pub fn bound_readout(self) -> R<f64> {
        let (v, b) = self.readout()?;
        Ok(if b.is_empty() { v } else { v.next_up() })
    }
}
fn ulp(x: f64) -> f64 {
    if x == 0.0 {
        f64::from_bits(1)
    } else {
        (x.abs().next_up() - x.abs()).abs()
    }
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Tracked {
    pub value: Wide,
    pub loss: Wide,
}
impl Tracked {
    pub fn exact(v: Wide) -> Self {
        Self {
            value: v,
            loss: Wide::ZERO,
        }
    }
    pub fn empty() -> Self {
        Self::exact(Wide::ZERO)
    }
    pub fn from_f64(v: f64) -> R<Self> {
        Ok(Self::exact(Wide::from_f64(v)?))
    }
    pub fn add(self, b: Self) -> R<Self> {
        let (value, lost) = self.value.add(b.value)?;
        Ok(Self {
            value,
            loss: self.loss.upper_add(b.loss)?.upper_add(lost)?,
        })
    }
    pub fn mul(self, b: Self) -> R<Self> {
        Ok(Self {
            value: self.value.mul(b.value)?,
            loss: self
                .loss
                .upper_mul(b.value)?
                .upper_add(b.loss.upper_mul(self.value)?)?
                .upper_add(self.loss.upper_mul(b.loss)?)?,
        })
    }
    pub fn scale(self, w: f64) -> R<Self> {
        self.mul(Self::from_f64(w)?)
    }
    pub fn readout(self) -> R<(f64, Wide)> {
        let (v, b) = self.value.readout()?;
        Ok((v, self.loss.upper_add(b)?))
    }
}
#[derive(Clone, Copy, Debug)]
pub struct PairReadout {
    pub n: f64,
    pub m: f64,
    pub n_bound: Wide,
    pub m_bound: Wide,
}
#[derive(Clone, Copy, Debug)]
pub struct MomentPair {
    l: f64,
    r: f64,
    k: i32,
    n: f64,
    m: f64,
    ln_n: f64,
    ln_m: f64,
    front: bool,
}
impl MomentPair {
    pub fn components(&self) -> (i32, f64, f64) {
        (self.k, self.n, self.m)
    }
    pub fn logs(&self) -> (f64, f64) {
        (self.ln_n, self.ln_m)
    }
    pub fn new(l: f64, r: f64, k: i32, n: f64, m: f64, front: bool) -> R<Self> {
        let mu = v2::normalized_target(l, r, n, m)?;
        if !(0.0..1.0).contains(&mu) {
            return Err("unrealizable pair");
        }
        // This checks actual inherited beta brackets too; no new bracket is inferred.
        {
            let _sites = SiteLease::new(64)?;
            v2::reconstruct(l, r, n, m, front)?;
        }
        let a = Wide::from_parts(n, k)?;
        let b = Wide::from_parts(m, k)?;
        Ok(Self {
            l,
            r,
            k,
            n,
            m,
            ln_n: a.log(),
            ln_m: b.log(),
            front,
        })
    }
    pub fn with_logs(
        l: f64,
        r: f64,
        k: i32,
        n: f64,
        m: f64,
        front: bool,
        ln_n: f64,
        ln_m: f64,
    ) -> R<Self> {
        let p = Self::new(l, r, k, n, m, front)?;
        Wide::from_parts(n, k)?.validate_log(ln_n)?;
        Wide::from_parts(m, k)?.validate_log(ln_m)?;
        Ok(p)
    }
    pub fn normalized_mean(&self) -> R<f64> {
        v2::normalized_target(self.l, self.r, self.n, self.m)
    }
    pub fn readout(&self) -> R<PairReadout> {
        let (n, n_bound) = Wide::from_parts(self.n, self.k)?.readout()?;
        let (m, m_bound) = Wide::from_parts(self.m, self.k)?.readout()?;
        Ok(PairReadout {
            n,
            m,
            n_bound,
            m_bound,
        })
    }
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Owners {
    pub n: Tracked,
    pub u: Tracked,
    pub a: [Tracked; 3],
    pub b: [Tracked; 3],
    pub red: Tracked,
    pub qn: Tracked,
    pub qe: Tracked,
    pub outn: Tracked,
    pub oute: Tracked,
}
impl Owners {
    /// Atomic cumulative aggregation. Each residual term contributes one readout bound.
    pub fn budget_bounds(self) -> R<(Wide, Wide)> {
        let (mut bn, mut be) = (Wide::ZERO, Wide::ZERO);
        for t in [self.n, self.qn, self.outn, self.a[0], self.a[1], self.a[2]] {
            bn = bn.upper_add(t.readout()?.1)?;
        }
        for t in [
            self.u, self.qe, self.oute, self.red, self.b[0], self.b[1], self.b[2],
        ] {
            be = be.upper_add(t.readout()?.1)?;
        }
        Ok((bn, be))
    }
    pub fn checked_add(
        &mut self,
        b: Self,
        w: Tracked,
        rn: f64,
        re: f64,
        an: f64,
        ae: f64,
    ) -> R<()> {
        let candidate = self.add(b.weighted(w)?)?;
        let (bn, be) = candidate.budget_bounds()?;
        if !admit(rn, bn, an, 1e-20)? || !admit(re, be, ae, 1e-30)? {
            return Err("original budget plus bound or cumulative cap exceeded");
        }
        *self = candidate;
        Ok(())
    }
    pub fn empty() -> Self {
        let z = Tracked::empty();
        Self {
            n: z,
            u: z,
            a: [z; 3],
            b: [z; 3],
            red: z,
            qn: z,
            qe: z,
            outn: z,
            oute: z,
        }
    }
    pub fn weighted(self, w: Tracked) -> R<Self> {
        let mut o = self;
        o.n = o.n.mul(w)?;
        o.u = o.u.mul(w)?;
        o.red = o.red.mul(w)?;
        o.qn = o.qn.mul(w)?;
        o.qe = o.qe.mul(w)?;
        o.outn = o.outn.mul(w)?;
        o.oute = o.oute.mul(w)?;
        for i in 0..3 {
            o.a[i] = o.a[i].mul(w)?;
            o.b[i] = o.b[i].mul(w)?;
        }
        Ok(o)
    }
    pub fn add(self, b: Self) -> R<Self> {
        let mut o = self;
        o.n = o.n.add(b.n)?;
        o.u = o.u.add(b.u)?;
        o.red = o.red.add(b.red)?;
        o.qn = o.qn.add(b.qn)?;
        o.qe = o.qe.add(b.qe)?;
        o.outn = o.outn.add(b.outn)?;
        o.oute = o.oute.add(b.oute)?;
        for i in 0..3 {
            o.a[i] = o.a[i].add(b.a[i])?;
            o.b[i] = o.b[i].add(b.b[i])?;
        }
        Ok(o)
    }
    pub fn export(&mut self) -> R<()> {
        let n = self.outn.add(self.n)?;
        let e = self.oute.add(self.u)?;
        self.outn = n;
        self.oute = e;
        self.n = Tracked::empty();
        self.u = Tracked::empty();
        Ok(())
    }
    pub fn photo_readouts(self) -> R<([f64; 3], [f64; 3], Wide, Wide)> {
        let (mut a, mut b) = ([0.0; 3], [0.0; 3]);
        let (mut bn, mut be) = (Wide::ZERO, Wide::ZERO);
        for i in 0..3 {
            let (x, xb) = self.a[i].readout()?;
            let (y, yb) = self.b[i].readout()?;
            a[i] = x;
            b[i] = y;
            bn = bn.upper_add(xb)?;
            be = be.upper_add(yb)?;
        }
        Ok((a, b, bn, be))
    }
}
fn two_sum(a: f64, b: f64) -> (f64, f64) {
    let s = a + b;
    let v = s - a;
    (s, (a - (s - v)) + (b - v))
}
fn phi(z: f64) -> f64 {
    if z == 0.0 {
        1.0
    } else {
        -(-z).exp_m1() / z
    }
}
fn j(k: f64, h: f64) -> f64 {
    h * phi(k * h)
}
fn psi(z: f64) -> f64 {
    if z.abs() < 0.1 {
        let (mut sum, mut term) = (0.5, 0.5);
        for k in 1..48 {
            term *= -z / (k + 2) as f64;
            sum += term;
        }
        sum
    } else {
        (1.0 - phi(z)) / z
    }
}
fn energy_source(lambda: f64, h: f64) -> f64 {
    let z = lambda * h;
    if z < 0.1 {
        let (mut p, mut hp, mut fact, mut sum) = (1.0, 1.0, 2.0, 0.5);
        for m in 1..96 {
            hp *= h;
            p = (h + z) * p + hp;
            fact *= (m + 2) as f64;
            let term = p / fact;
            sum += if m % 2 == 0 { term } else { -term };
            if term < 1e-18 * sum.abs() {
                break;
            }
        }
        h * h * sum
    } else {
        (j(1.0, h) - j(lambda + 1.0, h)) / lambda
    }
}
/// Segment in s=ln(a), f photons/H, q photons/H/ds; rates per ds, e in eV.
/// Caller must supply one exact, already topology-split segment.
pub fn segment(f: Tracked, q: Tracked, rates: [f64; 3], h: f64, e: f64) -> R<Owners> {
    if !h.is_finite()
        || h < 0.0
        || h > 2.0
        || (h > 0.0 && h < 1e-12)
        || !e.is_finite()
        || !(13.6..=1e4).contains(&e)
        || !rates.into_iter().all(|r| r.is_finite() && r >= 0.0)
    {
        return Err("unsupported segment input");
    }
    // Preserve the exact binary64 input sum and product through attenuation.
    let (a, ea) = two_sum(rates[0], rates[1]);
    let (b, eb) = two_sum(a, rates[2]);
    let (lambda, lambda_lo) = two_sum(b, ea + eb);
    let z = lambda * h;
    let (z_hi, z_lo) = two_sum(z, lambda.mul_add(h, -z) + lambda_lo * h);
    if lambda > 2e6
        || (lambda == 2e6 && lambda_lo > 0.0)
        || z_hi > 5e5
        || (z_hi == 5e5 && z_lo > 0.0)
    {
        return Err("unsupported segment opacity");
    }
    let end_e = e * (-h).exp();
    for i in 0..3 {
        if rates[i] > 0.0 && end_e < [13.6, 24.59, 54.42][i] {
            return Err("unsplit species cutoff");
        }
    }
    let decay = Tracked::exact(Wide::from_log(-z_hi)?.mul(Wide::from_log(-z_lo)?)?);
    let initial_n = f.mul(decay)?;
    let source_n = q.scale(j(lambda, h))?;
    let initial_i = f.scale(j(lambda, h))?;
    let source_i = q.scale(h)?.scale(h)?.scale(psi(z))?;
    let initial_e = f.scale(j(lambda + 1.0, h))?.scale(e)?.scale(EPS)?;
    let source_e = q.scale(energy_source(lambda, h))?.scale(e)?.scale(EPS)?;
    let count_i = initial_i.add(source_i)?;
    let energy_i = initial_e.add(source_e)?;
    let n = initial_n.add(source_n)?;
    let mut o = Owners::empty();
    o.n = n;
    o.u = n.scale(end_e)?.scale(EPS)?;
    o.red = energy_i;
    o.qn = q.scale(h)?;
    o.qe = q.scale(j(1.0, h))?.scale(e)?.scale(EPS)?;
    for i in 0..3 {
        o.a[i] = count_i.scale(rates[i])?;
        o.b[i] = energy_i.scale(rates[i])?;
    }
    Ok(o)
}
/// `bound` already has the residual's physical units; caps are cumulative.
pub fn admit(residual: f64, bound: Wide, allowance: f64, cap: f64) -> R<bool> {
    if !residual.is_finite()
        || !allowance.is_finite()
        || allowance < 0.0
        || !cap.is_finite()
        || cap < 0.0
    {
        return Err("invalid budget");
    }
    Ok(bound.le(Wide::from_f64(cap)?)
        && Wide::from_f64(residual.abs())?
            .upper_add(bound)?
            .le(Wide::from_f64(allowance)?))
}
#[derive(Clone, Copy)]
pub struct ClosureInput {
    pub l: f64,
    pub r: f64,
    pub beta: f64,
    pub front: bool,
    pub n: Tracked,
}
// Positive local integral: use physical differences before normalization.
// Separately normalized endpoints may coalesce or lose a large fraction of a sliver.
fn zint(t: f64, origin_y: f64, width: Wide, right_distance: Wide, front: bool) -> R<Tracked> {
    let d = width.readout()?.0;
    let z = -t * d;
    let base = Tracked::exact(Wide::from_log(t * origin_y)?);
    let width = Tracked::exact(width);
    let value = if front {
        width
            .mul(Tracked::exact(right_distance))?
            .scale(phi(z))?
            .add(width.mul(width)?.scale(psi(z))?)?
    } else {
        width.scale(phi(z))?
    };
    base.mul(value)
}
pub fn restrict(c: ClosureInput, a: f64, b: f64) -> R<(Tracked, Tracked)> {
    if ![c.l, c.r, c.beta, a, b].into_iter().all(f64::is_finite)
        || c.l >= c.r
        || a > b
        || c.beta.abs() > 128.0
    {
        return Err("invalid closure restriction");
    }
    // V2 performs exact-width admission; a benign geometric pair is sufficient here.
    let _ = v2::normalized_target(c.l, c.r, 1.0, c.l.exp())?;
    let a = a.max(c.l);
    let b = b.min(c.r);
    if c.n.value.is_empty() && !c.n.loss.is_empty() {
        return Err("uncertain empty restriction");
    }
    if a >= b || c.n.value.is_empty() {
        return Ok((Tracked::empty(), Tracked::empty()));
    }
    let w = c.r - c.l;
    let ya = (a - c.l) / w;
    let divide_width = |x: f64| -> R<Wide> {
        let v = Wide::from_f64(x)?;
        let wd = Wide::from_f64(w)?;
        Wide::from_parts(v.mant / wd.mant, v.exp - wd.exp)
    };
    let local_width = divide_width(b - a)?;
    let right = divide_width(c.r - b)?;
    let den = zint(c.beta, 0.0, Wide::from_f64(1.0)?, Wide::ZERO, c.front)?;
    let zn = zint(c.beta, ya, local_width, right, c.front)?;
    let zm = zint(c.beta + w, ya, local_width, right, c.front)?;
    if !den.loss.is_empty() {
        return Err("uncertain normalization integral");
    }
    let ratio = |v: Tracked| -> R<Tracked> {
        let dv = den.value;
        let value = Wide::from_parts(v.value.mant / dv.mant, v.value.exp - dv.exp)?;
        let reciprocal = Wide::from_parts((1.0 / dv.mant).next_up(), -dv.exp)?;
        Ok(Tracked {
            value,
            loss: v.loss.upper_mul(reciprocal)?,
        })
    };
    Ok((
        c.n.mul(ratio(zn)?)?,
        c.n.mul(ratio(zm)?)?
            .mul(Tracked::exact(Wide::from_log(c.l)?))?,
    ))
}
#[derive(Clone, Copy, Debug)]
pub struct EndpointPair {
    pub pair: Option<MomentPair>,
    pub n_loss: Wide,
    pub m_loss: Wide,
    pub carried_u: Tracked,
}
/// M = exp(s1) U / epsilon, formed from actual carried U, with common-scale N/M.
/// M loss is in comoving-moment units, not erg/H; carried_u retains the physical energy.
pub fn endpoint_pair(l: f64, r: f64, s1: f64, o: Owners, front: bool) -> R<EndpointPair> {
    let _ = v2::normalized_target(l, r, 1.0, l.exp())?;
    if !s1.is_finite() || s1.abs() > 32.0 {
        return Err("unsupported endpoint epoch");
    }
    if o.n.value.is_empty() != o.u.value.is_empty() {
        return Err("inconsistent endpoint number/energy");
    }
    if o.n.value.is_empty() {
        if !o.n.loss.is_empty() || !o.u.loss.is_empty() {
            return Err("uncertain empty endpoint");
        };
        return Ok(EndpointPair {
            pair: None,
            n_loss: Wide::ZERO,
            m_loss: Wide::ZERO,
            carried_u: o.u,
        });
    }
    let m =
        o.u.mul(Tracked::exact(Wide::from_log(s1)?))?
            .scale(1.0 / EPS)?;
    let k = o.n.value.exp.max(m.value.exp);
    let dn = k - o.n.value.exp;
    let dm = k - m.value.exp;
    if dn > 1022 || dm > 1022 {
        return Err("incompatible endpoint moment scales");
    }
    let ns = o.n.value.mant * 2.0f64.powi(-dn);
    let ms = m.value.mant * 2.0f64.powi(-dm);
    let p = MomentPair::new(l, r, k, ns, ms, front)?;
    let recovered = Wide::from_parts(p.m, p.k)?
        .mul(Wide::from_log(-s1)?)?
        .mul(Wide::from_f64(EPS)?)?;
    let rel = recovered.mant / o.u.value.mant * 2.0f64.powi(recovered.exp - o.u.value.exp) - 1.0;
    if rel.abs() > 2e-12 {
        return Err("endpoint energy roundtrip failed");
    }
    Ok(EndpointPair {
        pair: Some(p),
        n_loss: o.n.loss,
        m_loss: m.loss,
        carried_u: o.u,
    })
}
