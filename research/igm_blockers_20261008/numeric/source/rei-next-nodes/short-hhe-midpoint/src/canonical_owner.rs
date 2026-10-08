//! Bounded research primitives only. No gas solver or production integration.
pub const EPS: f64 = 1.602176634e-12;
pub const EC: f64 = 13.6;
pub const CHI: [f64; 3] = [13.598434599702, 24.587389011, 54.41776];
const CUTOFF: [f64; 3] = [13.6, 24.59, 54.42];
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Owners {
    pub canonical: Option<OwnerLedger>,
    pub n: f64,
    pub u: f64,
    pub an: [f64; 3],
    pub be: [f64; 3],
    pub red: f64,
    pub qn: f64,
    pub qe: f64,
    pub outn: f64,
    pub oute: f64,
    pub ln_n: Option<f64>,
    pub ln_u: Option<f64>,
}
#[derive(Clone, Copy, Debug)]
pub struct Density {
    pub l: f64,
    pub r: f64,
    pub a: f64,
    pub k: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct Closure {
    pub l: f64,
    pub r: f64,
    pub n: f64,
    pub beta: f64,
    pub front: bool,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Inventory {
    Empty,
    Linear { n: f64, m: f64 },
    LogTail { ln_n: f64, ln_m: f64 },
    Atom { eta: f64, n: f64 },
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
        for k in 1..32 {
            term *= -z / (k + 2) as f64;
            sum += term;
        }
        sum
    } else {
        (1.0 - phi(z)) / z
    }
}
fn energy_source_integral(lambda: f64, h: f64) -> f64 {
    let z = lambda * h;
    if z < 0.1 {
        // divided difference series in scaled h and z, including lambda=0.
        let (mut p, mut bp, mut factorial, mut sum) = (1.0, 1.0, 2.0, 0.5);
        for m in 1..80 {
            bp *= h;
            p = (h + z) * p + bp;
            factorial *= (m + 2) as f64;
            let term = p / factorial;
            if m % 2 == 0 {
                sum += term
            } else {
                sum -= term
            };
            if term < 1e-18 * sum.abs() {
                break;
            }
        }
        h * h * sum
    } else {
        (j(1.0, h) - j(lambda + 1.0, h)) / lambda
    }
}
pub fn kernel(f: f64, q: f64, rates: [f64; 3], h: f64, e: f64) -> Result<Owners, &'static str> {
    if ![f, q, h, e]
        .into_iter()
        .chain(rates)
        .all(|x| x.is_finite() && x >= 0.0)
        || e == 0.0
    {
        return Err("invalid kernel input");
    }
    let end_e = e * (-h).exp();
    for i in 0..3 {
        if rates[i] > 0.0 && end_e < CUTOFF[i] {
            return Err("unsplit absorption cutoff");
        }
    }
    let lambda = rates.iter().sum::<f64>();
    if !lambda.is_finite() {
        return Err("nonfinite total rate");
    }
    let z = lambda * h;
    let decay = (-z).exp();
    let n = f * decay + q * j(lambda, h);
    if n == 0.0 && q > 0.0 && h > 0.0 {
        return Err("positive source underflow requires unsupported log evolution");
    }
    let count_integral = f * j(lambda, h) + q * h * h * psi(z);
    let energy_integral =
        EPS * e * (f * j(lambda + 1.0, h) + q * energy_source_integral(lambda, h));
    let mut o = Owners {
        n,
        u: EPS * end_e * n,
        red: energy_integral,
        qn: q * h,
        qe: EPS * e * q * j(1.0, h),
        ln_n: if n > 0.0 {
            Some(n.ln())
        } else if f > 0.0 && q == 0.0 {
            Some(f.ln() - z)
        } else {
            None
        },
        ..Owners::default()
    };
    if let Some(ln_n) = o.ln_n {
        o.ln_u = Some(EPS.ln() + e.ln() - h + ln_n);
    }
    for i in 0..3 {
        o.an[i] = rates[i] * count_integral;
        o.be[i] = rates[i] * energy_integral;
    }
    if ![o.n, o.u, o.red, o.qn, o.qe]
        .into_iter()
        .chain(o.an)
        .chain(o.be)
        .all(|x| x.is_finite() && x >= 0.0)
    {
        return Err("nonfinite or negative owner");
    }
    Ok(o)
}
pub fn moments(d: Density, a: f64, b: f64) -> (f64, f64) {
    try_moments(d, a, b).expect("initial moments require supported normal inventory")
}
pub fn topology(l: f64, r: f64, events: &[f64]) -> Vec<f64> {
    assert!(l.is_finite() && r.is_finite() && l <= r);
    let mut x = vec![l, r];
    x.extend(
        events
            .iter()
            .copied()
            .filter(|v| v.is_finite() && *v > l && *v < r),
    );
    x.sort_by(f64::total_cmp);
    x.dedup();
    x
}
fn add_scaled(a: &mut Owners, b: Owners, w: f64) {
    try_add_scaled(a, b, w).expect("weighted owners require supported normal inventory")
}
pub fn initial_transaction(d: Density, s0: f64, s1: f64, parts: usize, opacity: bool) -> Owners {
    assert!(s1 >= s0 && parts > 0 && parts <= 1024);
    let l = d.l.max(EC.ln() + s0);
    if l >= d.r {
        return Owners::default();
    }
    let mut events: Vec<f64> = (1..parts)
        .map(|i| l + (d.r - l) * i as f64 / parts as f64)
        .collect();
    events.push(EC.ln() + s1);
    let cuts = topology(l, d.r, &events);
    let mut out = Owners::default();
    for pair in cuts.windows(2) {
        let (a, b) = (pair[0], pair[1]);
        let (n, m) = moments(d, a, b);
        if n == 0.0 {
            continue;
        }
        let eta = admit_sample(a, b, n, m).expect("unresolved initial quadrature sample");
        let exits = b <= EC.ln() + s1;
        let end = if exits { eta - EC.ln() } else { s1 };
        let rates = if opacity {
            [2.0 * (-3.0 * (eta - EC.ln())).exp(), 0.0, 0.0]
        } else {
            [0.0; 3]
        };
        let mut o = kernel(1.0, 0.0, rates, end - s0, (eta - s0).exp()).unwrap();
        if exits {
            o.outn = o.n;
            o.oute = EPS * EC * o.n;
            o.n = 0.0;
            o.u = 0.0;
            o.ln_n = None;
            o.ln_u = None;
        }
        add_scaled(&mut out, o, n);
    }
    out
}
/// Legendre rule, positive weights constructed before any moment/owner evaluation.
pub fn gauss(a: f64, b: f64, n: usize) -> Vec<(f64, f64)> {
    assert!(n >= 2 && n <= 64 && b >= a);
    let mut out = Vec::with_capacity(n);
    let half = (b - a) * 0.5;
    for i in 0..n {
        let mut z = (std::f64::consts::PI * (i as f64 + 0.75) / (n as f64 + 0.5)).cos();
        for _ in 0..32 {
            let (mut p0, mut p1) = (1.0, z);
            for k in 2..=n {
                let p = ((2 * k - 1) as f64 * z * p1 - (k - 1) as f64 * p0) / k as f64;
                p0 = p1;
                p1 = p;
            }
            let dp = n as f64 * (z * p1 - p0) / (z * z - 1.0);
            let next = z - p1 / dp;
            if (next - z).abs() < 2e-16 {
                z = next;
                break;
            }
            z = next;
        }
        let (mut p0, mut p1) = (1.0, z);
        for k in 2..=n {
            let p = ((2 * k - 1) as f64 * z * p1 - (k - 1) as f64 * p0) / k as f64;
            p0 = p1;
            p1 = p;
        }
        let dp = n as f64 * (z * p1 - p0) / (z * z - 1.0);
        let w = half * 2.0 / ((1.0 - z * z) * dp * dp);
        out.push((a + half * (1.0 + z), w));
    }
    out.sort_by(|x, y| x.0.total_cmp(&y.0));
    out
}
fn source_characteristic(eta: f64, s0: f64, s1: f64, t: f64, emin: f64, emax: f64) -> Owners {
    let tau = eta - EC.ln();
    let end = t.min(tau);
    let a = s0.max(eta - emax.ln());
    let b = s1.min(eta - emin.ln()).min(end);
    if b <= a {
        return Owners::default();
    }
    let h = b - a;
    let q0 = (a - eta).exp();
    let n = q0 * h * phi(-h);
    let energy_b = EPS * (eta - b).exp() * n;
    let red_source = EPS * h * h * psi(h);
    let dark = end - b;
    let red = red_source + energy_b * (-(-dark).exp_m1());
    let mut o = Owners {
        n,
        u: EPS * (eta - end).exp() * n,
        red,
        qn: n,
        qe: EPS * h,
        ..Owners::default()
    };
    if tau <= t {
        o.outn = n;
        o.oute = EPS * EC * n;
        o.n = 0.0;
        o.u = 0.0;
        o.ln_n = None;
        o.ln_u = None;
    }
    o
}
pub fn source_transaction(s0: f64, s1: f64, t: f64, emin: f64, emax: f64, order: usize) -> Owners {
    assert!(s0 >= 0.0 && s1 >= s0 && t >= s1 && emin > 0.0 && emax > emin);
    let min = emin.max(EC);
    let mut out = Owners::default();
    if emin < EC {
        let top = EC.min(emax);
        let n = (s1 - s0) * (1.0 / emin - 1.0 / top);
        let e = EPS * (s1 - s0) * (top / emin).ln();
        out.qn = n;
        out.qe = e;
        out.outn = n;
        out.oute = e;
    }
    if min >= emax {
        return out;
    }
    let l = s0 + min.ln();
    let r = s1 + emax.ln();
    let events = [s0 + emax.ln(), s1 + min.ln(), t + EC.ln()];
    let cuts = topology(l, r, &events);
    for ab in cuts.windows(2) {
        for (eta, w) in gauss(ab[0], ab[1], order) {
            let o = source_characteristic(eta, s0, s1, t, min, emax);
            add_scaled(&mut out, o, w);
        }
    }
    out
}
pub fn source_density(eta: f64, t: f64, emin: f64, emax: f64) -> f64 {
    if eta < t + EC.ln() {
        return 0.0;
    }
    let a = 0.0f64.max(eta - emax.ln());
    let b = t.min(eta - emin.ln());
    if b <= a {
        0.0
    } else {
        (a - eta).exp() * (b - a).exp_m1()
    }
}
fn closure_stats(c: Closure) -> (f64, f64) {
    let w = c.r - c.l;
    let mut z = 0.0;
    let mut moment = 0.0;
    let shift = c.beta.max(0.0);
    for (y, v) in gauss(0.0, 1.0, 64) {
        let base = if c.front { 1.0 - y } else { 1.0 };
        let mass = v * base * (c.beta * y - shift).exp();
        z += mass;
        moment += mass * (w * y).exp_m1() / w.exp_m1();
    }
    (z, moment / z)
}
pub fn closure_moments(c: Closure) -> (f64, f64) {
    let (_, mu) = closure_stats(c);
    (c.n, c.n * c.l.exp() * (1.0 + (c.r - c.l).exp_m1() * mu))
}
pub fn reconstruct(l: f64, r: f64, n: f64, m: f64, front: bool) -> Result<Closure, &'static str> {
    if ![l, r, n, m].into_iter().all(f64::is_finite) || r - l < 1e-7 || n <= 0.0 || m <= 0.0 {
        return Err("invalid/unresolved support or inventory");
    }
    let target = normalized_target(l, r, n, m)?;
    if target <= 0.0 || target >= 1.0 {
        return Err("noninterior moment; atom representation or reject required");
    }
    let mut c = Closure {
        l,
        r,
        n,
        beta: -128.0,
        front,
    };
    let low_mu = closure_stats(c).1;
    c.beta = 128.0;
    let high_mu = closure_stats(c).1;
    if target < low_mu || target > high_mu {
        return Err("extreme mean outside bounded inversion bracket");
    }
    let (mut lo, mut hi) = (-128.0, 128.0);
    for _ in 0..64 {
        c.beta = (lo + hi) * 0.5;
        let mu = closure_stats(c).1;
        if mu < target {
            lo = c.beta
        } else {
            hi = c.beta
        }
    }
    c.beta = (lo + hi) * 0.5;
    Ok(c)
}
pub fn density_value(c: Closure, eta: f64) -> f64 {
    if eta < c.l || eta >= c.r {
        return 0.0;
    }
    let y = (eta - c.l) / (c.r - c.l);
    let z = closure_stats(c).0;
    let base = if c.front { 1.0 - y } else { 1.0 };
    c.n / (c.r - c.l) * base * (c.beta * y - c.beta.max(0.0)).exp() / z
}
pub fn inventory(lnn: Option<f64>, lnm: Option<f64>) -> Result<Inventory, &'static str> {
    match (lnn, lnm) {
        (None, None) => Ok(Inventory::Empty),
        (Some(ln_n), Some(ln_m)) if ln_n.is_finite() && ln_m.is_finite() => {
            let (n, m) = (ln_n.exp(), ln_m.exp());
            if n == 0.0 || m == 0.0 {
                Ok(Inventory::LogTail { ln_n, ln_m })
            } else if n.is_finite() && m.is_finite() {
                Ok(Inventory::Linear { n, m })
            } else {
                Err("overflow")
            }
        }
        _ => Err("inconsistent authoritative inventory"),
    }
}
pub fn merge_moments(pairs: &[(f64, f64)]) -> (f64, f64) {
    pairs
        .iter()
        .fold((0.0, 0.0), |(n, m), (a, b)| (n + a, m + b))
}

pub fn admit_sample(a: f64, b: f64, n: f64, m: f64) -> Result<f64, &'static str> {
    if ![a, b, n, m].into_iter().all(f64::is_finite) || n <= 0.0 || m <= 0.0 || a >= b {
        return Err("invalid moment interval");
    }
    let eta = (m / n).ln();
    if eta <= a || eta >= b {
        return Err("no resolved interior moment abscissa");
    };
    Ok(eta)
}
pub fn source_support_admitted(c: Closure, front: f64) -> bool {
    c.l < c.r && c.r <= front && c.front
}

pub fn atomic_transaction(atom: Inventory, s0: f64, s1: f64) -> Result<Owners, &'static str> {
    let Inventory::Atom { eta, n } = atom else {
        return Err("explicit atom required");
    };
    let tau = eta - EC.ln();
    if tau < s0 || s1 < s0 {
        return Err("invalid atomic active interval");
    };
    let mut o = kernel(n, 0.0, [0.0; 3], s1.min(tau) - s0, (eta - s0).exp())?;
    if tau <= s1 {
        o.outn = o.n;
        o.oute = EPS * EC * o.n;
        o.n = 0.0;
        o.u = 0.0;
        o.ln_n = None;
        o.ln_u = None;
    }
    Ok(o)
}
pub fn characteristic(
    eta: f64,
    s0: f64,
    s1: f64,
    f: f64,
    q: f64,
    start: f64,
    stop: f64,
    rates: [f64; 3],
) -> Result<Owners, &'static str> {
    let tau = eta - EC.ln();
    if s1 < s0 || tau < s0 || stop < start {
        return Err("invalid characteristic interval");
    };
    let end = s1.min(tau);
    let mut events = vec![start, stop];
    for cutoff in CUTOFF {
        events.push(eta - cutoff.ln());
    }
    let cuts = topology(s0, end, &events);
    let mut stock = f;
    let mut total = Owners::default();
    for ab in cuts.windows(2) {
        let (a, b) = (ab[0], ab[1]);
        let mid = (a + b) * 0.5;
        let mut active = [0.0; 3];
        for i in 0..3 {
            if (eta - mid).exp() >= CUTOFF[i] {
                active[i] = rates[i]
            }
        }
        let inject = if mid >= start && mid < stop { q } else { 0.0 };
        let mut o = kernel(stock, inject, active, b - a, (eta - a).exp())?;
        if (o.n == 0.0 && o.ln_n.is_some()) || (o.u == 0.0 && o.ln_u.is_some()) {
            return Err("authoritative underflow tail requires unsupported log evolution");
        };
        stock = o.n;
        o.n = 0.0;
        o.u = 0.0;
        o.ln_n = None;
        o.ln_u = None;
        o.ln_n = None;
        o.ln_u = None;
        add_scaled(&mut total, o, 1.0);
    }
    if tau <= s1 {
        total.outn = stock;
        total.oute = EPS * EC * stock;
    } else {
        total.n = stock;
        total.u = EPS * (eta - s1).exp() * stock;
    }
    Ok(total)
}

/// Conservative normal-only admission. Zero is permitted only for an exact empty
/// input or empty geometric intersection; no floor, projection or tail deletion.
fn normal_product(a: f64, b: f64) -> Result<f64, &'static str> {
    if !a.is_normal() || !b.is_normal() {
        return Err("unsupported multiplicative input");
    };
    let value = a * b;
    if !value.is_normal() {
        return Err("intermediate product underflow/overflow");
    };
    Ok(value)
}
fn finite_product_allow_exact_zero(a: f64, b: f64) -> Result<f64, &'static str> {
    if a == 0.0 || b == 0.0 {
        return Ok(0.0);
    };
    normal_product(a, b)
}
pub fn try_moments(d: Density, a: f64, b: f64) -> Result<(f64, f64), &'static str> {
    if ![d.l, d.r, d.a, d.k, a, b].into_iter().all(f64::is_finite) || d.r < d.l || d.a < 0.0 {
        return Err("invalid density/support");
    }
    let a = a.max(d.l);
    let b = b.min(d.r);
    if b <= a || d.a == 0.0 {
        return Ok((0.0, 0.0));
    }
    if !d.a.is_normal() {
        return Err("initial subnormal amplitude requires log evolution");
    }
    let w = b - a;
    if !w.is_normal() {
        return Err("unsupported interval width");
    }
    let arg = finite_product_allow_exact_zero(d.k, a - d.l)?;
    let decay = arg.exp();
    let amp = normal_product(d.a, decay)?;
    let nphi = phi(-finite_product_allow_exact_zero(d.k, w)?);
    let mphi = phi(-finite_product_allow_exact_zero(d.k + 1.0, w)?);
    // Check each positive intermediate BEFORE a later large factor could hide
    // precision already lost through subnormal multiplication or exp underflow.
    let n = normal_product(normal_product(amp, w)?, nphi)?;
    let m = normal_product(normal_product(normal_product(amp, a.exp())?, w)?, mphi)?;
    if n <= 0.0 || m <= 0.0 {
        return Err("nonpositive analytic moments");
    };
    Ok((n, m))
}
/// Validate every contribution and candidate sum before the single commit.
// Research-only authoritative paired owner accumulation. Original kernel is unchanged.
use canonical::{Tracked,Wide};
#[derive(Clone,Copy,Debug,PartialEq)]
pub struct OwnerLedger { pub terms:[Tracked;13], pub occurrence:[u64;13], pub coefficient:[Wide;13] }
fn scalar(o:Owners)->[f64;13]{[o.n,o.u,o.red,o.qn,o.qe,o.outn,o.oute,o.an[0],o.an[1],o.an[2],o.be[0],o.be[1],o.be[2]]}
fn rounding(v:Wide)->Result<Wide,&'static str>{if v.is_empty(){Ok(Wide::ZERO)}else{Wide::from_parts(1.,v.exponent()-51)}}
pub fn owner_ledger(o:Owners)->Result<OwnerLedger,&'static str>{
 let vals=scalar(o);let mut t=[Tracked::empty();13];let mut occurrence=[0;13];let mut coefficient=[Wide::ZERO;13];
 for i in 0..13 {t[i]=Tracked::from_f64(vals[i])?;if let Some(l)=o.canonical{if l.terms[i].readout()?.0.to_bits()==vals[i].to_bits(){t[i]=l.terms[i];occurrence[i]=l.occurrence[i];coefficient[i]=l.coefficient[i];}else{return Err("canonical owner/readout mismatch");}}}
 Ok(OwnerLedger{terms:t,occurrence,coefficient})
}
pub fn replace_owner_components(o:&mut Owners,indices:&[usize])->Result<(),&'static str>{let vals=scalar(*o);if let Some(mut l)=o.canonical{for &i in indices{l.terms[i]=Tracked::from_f64(vals[i])?;l.occurrence[i]=0;l.coefficient[i]=Wide::ZERO;}o.canonical=Some(l);}Ok(())}
pub fn owner_bounds(o:Owners)->Result<[Wide;13],&'static str>{let l=owner_ledger(o)?;let mut b=[Wide::ZERO;13];for i in 0..13{b[i]=l.terms[i].readout()?.1;}Ok(b)}
pub fn try_add_scaled(a:&mut Owners,b:Owners,w:f64)->Result<(),&'static str>{
 let valid=|x:f64|x.is_finite()&&x>=0.;if !valid(w){return Err("invalid owner weight");}
 for o in [*a,b]{if !scalar(o).into_iter().all(valid)||o.ln_n.into_iter().chain(o.ln_u).any(|x|!x.is_finite()){return Err("invalid owner/log");}
 for (n,e) in [(o.n,o.u),(o.qn,o.qe),(o.outn,o.oute),(o.an[0],o.be[0]),(o.an[1],o.be[1]),(o.an[2],o.be[2])]{if (n==0.)!=(e==0.){return Err("unrepresented paired number/energy owner");}}
 if (o.n==0.&&o.ln_n.is_some())||(o.u==0.&&o.ln_u.is_some()){return Err("authoritative tail is not empty");}}
 if w==0.{return Ok(())}let lhs=owner_ledger(*a)?;let rhs=owner_ledger(b)?;let weight=Tracked::from_f64(w)?;
 let mut l=lhs;let mut sums=[0.;13];
 for i in 0..13{let mut product=rhs.terms[i].mul(weight)?;
 // Canonical primitives record whole losses. Charge partial mantissa rounding separately.
 if !rhs.terms[i].value.is_empty(){product.loss=product.loss.upper_add(rounding(product.value)?)?;}
 let mut sum=lhs.terms[i].add(product)?;
 if !lhs.terms[i].value.is_empty()&&!product.value.is_empty(){sum.loss=sum.loss.upper_add(rounding(sum.value)?)?;}
 l.terms[i]=sum;l.occurrence[i]=lhs.occurrence[i].checked_add(rhs.occurrence[i]).and_then(|x|x.checked_add((!product.value.is_empty())as u64)).ok_or("occurrence overflow")?;
 l.coefficient[i]=lhs.coefficient[i].upper_add(rhs.coefficient[i].upper_mul(weight.value)?)?.upper_add(if product.value.is_empty(){Wide::ZERO}else{weight.value})?;
 sums[i]=sum.readout()?.0;
 }
 let candidate=Owners{canonical:Some(l),n:sums[0],u:sums[1],red:sums[2],qn:sums[3],qe:sums[4],outn:sums[5],oute:sums[6],an:[sums[7],sums[8],sums[9]],be:[sums[10],sums[11],sums[12]],ln_n:if sums[0]>0.{Some(sums[0].ln())}else{None},ln_u:if sums[1]>0.{Some(sums[1].ln())}else{None}};
 // Paired readouts may not silently replace a positive canonical component by zero.
 for (n,e) in [(0,1),(3,4),(5,6),(7,10),(8,11),(9,12)]{if (sums[n]==0.)!=(sums[e]==0.){return Err("paired readout requires extended material path");}}
 *a=candidate;Ok(())
}
/// Minimal double-double lane for normalization, not a new physical state.
#[derive(Clone, Copy, Debug)]
struct Dd {
    hi: f64,
    lo: f64,
}
impl Dd {
    fn from(x: f64) -> Self {
        Self { hi: x, lo: 0.0 }
    }
    fn sum(a: f64, b: f64) -> Self {
        let hi = a + b;
        let v = hi - a;
        Self {
            hi,
            lo: (a - (hi - v)) + (b - v),
        }
    }
    fn add(self, b: Self) -> Self {
        let s = Self::sum(self.hi, b.hi);
        let e = s.lo + self.lo + b.lo;
        Self::sum(s.hi, e)
    }
    fn neg(self) -> Self {
        Self {
            hi: -self.hi,
            lo: -self.lo,
        }
    }
    fn sub(self, b: Self) -> Self {
        self.add(b.neg())
    }
    fn mul(self, b: Self) -> Self {
        let p = self.hi * b.hi;
        let e = self.hi.mul_add(b.hi, -p) + self.hi * b.lo + self.lo * b.hi;
        Self::sum(p, e).add(Self::from(self.lo * b.lo))
    }
    fn div(self, b: Self) -> Self {
        let q1 = self.hi / b.hi;
        let r = self.sub(b.mul(Self::from(q1)));
        let q2 = r.hi / b.hi;
        let r2 = r.sub(b.mul(Self::from(q2)));
        let q3 = r2.hi / b.hi;
        Self::from(q1).add(Self::from(q2)).add(Self::from(q3))
    }
    fn value(self) -> f64 {
        self.hi + self.lo
    }
    fn finite(self) -> bool {
        self.hi.is_finite() && self.lo.is_finite()
    }
    fn exp(self) -> Result<Self, &'static str> {
        if !self.finite() || self.hi.abs() > 32.0 {
            return Err("DD exponential outside bounded domain");
        }
        let mut x = self;
        let mut squares = 0;
        while x.hi.abs() > 0.125 {
            x = x.mul(Self::from(0.5));
            squares += 1;
            if squares > 9 {
                return Err("DD range reduction bound");
            }
        }
        let mut term = Self::from(1.0);
        let mut sum = term;
        for k in 1..=48 {
            term = term.mul(x).div(Self::from(k as f64));
            sum = sum.add(term);
            if term.hi.abs() < 1e-35 * sum.hi.abs() {
                break;
            }
        }
        for _ in 0..squares {
            sum = sum.mul(sum)
        }
        if !sum.finite() || !sum.hi.is_normal() {
            return Err("DD exponential nonnormal result");
        };
        Ok(sum)
    }
}
pub fn normalized_target(l: f64, r: f64, n: f64, m: f64) -> Result<f64, &'static str> {
    if !l.is_finite()
        || !r.is_finite()
        || l.abs() > 32.0
        || r.abs() > 32.0
        || n <= 0.0
        || m <= 0.0
        || !n.is_normal()
        || !m.is_normal()
    {
        return Err("unsupported DD normalization input");
    }
    let width = Dd::from(r).sub(Dd::from(l));
    if width.hi < 1e-7
        || (width.hi == 1e-7 && width.lo < 0.0)
        || width.hi > 32.0
        || (width.hi == 32.0 && width.lo > 0.0)
    {
        return Err("unsupported DD support width");
    }
    // Common power-of-two scaling prevents quotient residuals from underflowing
    // for otherwise normal but extremely small physical moment inputs.
    let exponent = ((n.to_bits() >> 52) & 0x7ff) as i32 - 1023;
    let scale = 2.0f64.powi(-exponent);
    let ns = n * scale;
    let ms = m * scale;
    if !ns.is_normal() || !ms.is_normal() {
        return Err("unsupported scaled moment ratio");
    }
    let mean = Dd::from(ms).div(Dd::from(ns));
    let eml = Dd::from(-l).exp()?;
    let numerator = mean.mul(eml).sub(Dd::from(1.0));
    let denominator = width.exp()?.sub(Dd::from(1.0));
    let answer = numerator.div(denominator);
    if !answer.finite() {
        return Err("nonfinite normalized moment");
    };
    Ok(answer.value())
}
#[cfg(test)] mod owner_tests {
 use super::*;
 #[test] fn positive_subnormal_not_zero(){let mut a=Owners::default();let b=Owners{red:2.7403074891849688e-303,..Default::default()};try_add_scaled(&mut a,b,1.4493951880436e-6).unwrap();assert_eq!(a.red.to_bits(),(b.red*1.4493951880436e-6).to_bits());assert!(a.red>0.&&!a.red.is_normal());assert!(!a.canonical.unwrap().terms[2].value.is_empty());}
 #[test] fn normal_regression(){let mut a=Owners::default();let mut expected=0.;for (v,w) in [(1.,0.5),(3.,0.125),(7.,0.25)]{try_add_scaled(&mut a,Owners{red:v,..Default::default()},w).unwrap();expected+=v*w;}assert_eq!(a.red.to_bits(),expected.to_bits());}
 #[test] fn mismatch_rejected(){let mut a=Owners::default();try_add_scaled(&mut a,Owners{red:1.,..Default::default()},1.).unwrap();a.red=2.;assert!(try_add_scaled(&mut a,Owners::default(),1.).is_err());}
 #[test] fn paired_and_invalid_atomic(){let mut a=Owners::default();let original=a;assert!(try_add_scaled(&mut a,Owners{n:1.,..Default::default()},1.).is_err());assert_eq!(a,original);assert!(try_add_scaled(&mut a,Owners::default(),f64::NAN).is_err());assert_eq!(a,original);}
}

#[cfg(test)] mod exact_fixture_tests{use super::*;#[test]fn fraction_fixtures(){for(a,b,w)in [(0.,2.7403074891849688e-303,1.4493951880436e-6),(0.1,0.3,0.7),(1.,f64::from_bits(1),0.5)]{let mut out=Owners{red:a,..Default::default()};try_add_scaled(&mut out,Owners{red:b,..Default::default()},w).unwrap();let t=out.canonical.unwrap().terms[2];let bound=t.readout().unwrap().1;println!("ORACLE {} {} {} {} {} {}",a.to_bits(),b.to_bits(),w.to_bits(),out.red.to_bits(),bound.mantissa().to_bits(),bound.exponent());}}}
