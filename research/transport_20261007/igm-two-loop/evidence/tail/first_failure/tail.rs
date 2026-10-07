//! Authoritative positive amplitudes for one frozen-opacity characteristic.
//!
//! s=ln(a), E(s)=E0 exp(-s); dN/ds=q-lambda N. Every owner is
//! assembled from its nonnegative initial and source contributions. Rates are
//! frozen per segment; callers split source fronts and all atomic cutoffs.
//! No panel shape, chemistry integration, or production certificate is added.
pub const EV_ERG: f64 = 1.602176634e-12;
pub const CUTOFF_EV: [f64; 3] = [13.6, 24.59, 54.42];
pub type TailResult<T> = Result<T, &'static str>;

/// -infinity denotes exact empty; every finite log denotes positive inventory.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct LogPositive {
    ln: f64,
}
impl Default for LogPositive {
    fn default() -> Self {
        Self::empty()
    }
}
#[derive(Clone, Copy, Debug)]
pub struct PositiveSum {
    pub value: LogPositive,
    pub omitted_addend_bound: LogPositive,
}
#[derive(Clone, Copy, Debug)]
pub struct Readout {
    pub value: f64,
    /// Exact-real value of the represented log amplitude when exp readout is zero.
    pub zero_readout_bound: LogPositive,
    /// Conservative absolute bound for subnormal conversion only, not all FP error.
    pub subnormal_readout_bound: LogPositive,
}
impl LogPositive {
    pub const fn empty() -> Self {
        Self {
            ln: f64::NEG_INFINITY,
        }
    }
    pub fn from_log(ln: f64) -> TailResult<Self> {
        if ln.is_finite() || ln == f64::NEG_INFINITY {
            Ok(Self { ln })
        } else {
            Err("nonfinite positive amplitude")
        }
    }
    pub fn from_linear(x: f64) -> TailResult<Self> {
        if x == 0.0 {
            Ok(Self::empty())
        } else if x.is_finite() && x > 0.0 {
            Self::from_log(x.ln())
        } else {
            Err("invalid linear positive amplitude")
        }
    }
    pub fn log_value(self) -> f64 {
        self.ln
    }
    pub fn is_empty(self) -> bool {
        self.ln == f64::NEG_INFINITY
    }
    pub fn mul(self, other: Self) -> TailResult<Self> {
        if self.is_empty() || other.is_empty() {
            Ok(Self::empty())
        } else {
            Self::from_log(self.ln + other.ln).and_then(|x| {
                if x.is_empty() {
                    Err("log product overflow")
                } else {
                    Ok(x)
                }
            })
        }
    }
    pub fn scale(self, x: f64) -> TailResult<Self> {
        self.mul(Self::from_linear(x)?)
    }
    /// Stable log-add-exp. The bound records a *whole omitted positive addend*
    /// when the result rounds to the larger log. It does not bound all rounding.
    pub fn add(self, other: Self) -> TailResult<PositiveSum> {
        if self.is_empty() {
            return Ok(PositiveSum {
                value: other,
                omitted_addend_bound: Self::empty(),
            });
        }
        if other.is_empty() {
            return Ok(PositiveSum {
                value: self,
                omitted_addend_bound: Self::empty(),
            });
        }
        let (a, b) = if self.ln >= other.ln {
            (self, other)
        } else {
            (other, self)
        };
        let correction = (b.ln - a.ln).exp().ln_1p();
        let value = Self::from_log(a.ln + correction)?;
        Ok(PositiveSum {
            value,
            omitted_addend_bound: if value.ln == a.ln { b } else { Self::empty() },
        })
    }
    pub fn readout(self) -> TailResult<Readout> {
        if self.is_empty() {
            return Ok(Readout {
                value: 0.0,
                zero_readout_bound: Self::empty(),
                subnormal_readout_bound: Self::empty(),
            });
        }
        let value = self.ln.exp();
        if !value.is_finite() {
            return Err("linear readout overflow; log remains authoritative");
        }
        // For the admitted subnormal branch both represented exact-real x and
        // reported y are <=MIN_POSITIVE, hence |x-y|<=2*MIN_POSITIVE, regardless
        // of whether libm is correctly rounded. This intentionally loose bound
        // is not an exp/ln error certificate for the preceding kernel.
        let sub = if self.ln < f64::MIN_POSITIVE.ln() && value <= f64::MIN_POSITIVE && value > 0.0 {
            Self::from_linear(2.0 * f64::MIN_POSITIVE)?
        } else {
            Self::empty()
        };
        Ok(Readout {
            value,
            zero_readout_bound: if value == 0.0 { self } else { Self::empty() },
            subnormal_readout_bound: sub,
        })
    }
}
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct TailOwners {
    pub n: LogPositive,
    pub u: LogPositive,
    pub an: [LogPositive; 3],
    pub be: [LogPositive; 3],
    pub red: LogPositive,
    pub qn: LogPositive,
    pub qe: LogPositive,
    pub outn: LogPositive,
    pub oute: LogPositive,
}
impl TailOwners {
    pub fn as_array(self) -> [LogPositive; 13] {
        [
            self.n, self.u, self.an[0], self.an[1], self.an[2], self.be[0], self.be[1], self.be[2],
            self.red, self.qn, self.qe, self.outn, self.oute,
        ]
    }
    pub fn from_array(a: [LogPositive; 13]) -> Self {
        Self {
            n: a[0],
            u: a[1],
            an: [a[2], a[3], a[4]],
            be: [a[5], a[6], a[7]],
            red: a[8],
            qn: a[9],
            qe: a[10],
            outn: a[11],
            oute: a[12],
        }
    }
    pub fn scale(self, weight: LogPositive) -> TailResult<Self> {
        let mut a = self.as_array();
        for v in &mut a {
            *v = v.mul(weight)?;
        }
        Ok(Self::from_array(a))
    }
    /// Returns summed owners and per-owner omitted-addend bounds.
    pub fn add(self, other: Self) -> TailResult<(Self, Self)> {
        let a = self.as_array();
        let b = other.as_array();
        let mut v = [LogPositive::empty(); 13];
        let mut loss = v;
        for i in 0..13 {
            let s = a[i].add(b[i])?;
            v[i] = s.value;
            loss[i] = s.omitted_addend_bound;
        }
        Ok((Self::from_array(v), Self::from_array(loss)))
    }
}
#[derive(Clone, Copy, Debug)]
pub struct CharacteristicResult {
    pub owners: TailOwners,
    /// Independent initial/source addition audit; not a total roundoff bound.
    pub omitted_addend_bounds: TailOwners,
}
fn lp(ln: f64) -> TailResult<LogPositive> {
    LogPositive::from_log(ln)
}
fn phi(z: f64) -> f64 {
    if z == 0.0 {
        1.0
    } else {
        -(-z).exp_m1() / z
    }
}
fn log_j(k: f64, h: f64) -> f64 {
    if h == 0.0 {
        return f64::NEG_INFINITY;
    }
    let z = k * h;
    if z < 0.25 {
        h.ln() + phi(z).ln()
    } else {
        -k.ln() + (-(-z).exp_m1()).ln()
    }
}
fn log_count_source(h: f64, z: f64) -> f64 {
    let psi = if z < 0.25 {
        let (mut sum, mut term) = (0.5, 0.5);
        for n in 1..32 {
            term *= -z / (n + 2) as f64;
            sum += term;
            if term.abs() < 1e-18 * sum {
                break;
            }
        }
        psi_log(sum)
    } else {
        (z + (-z).exp_m1()).ln() - 2.0 * z.ln()
    };
    2.0 * h.ln() + psi
}
fn psi_log(x: f64) -> f64 {
    x.ln()
}
/// I_m(h)=integral_0^1 v^m exp(-h*v)dv, evaluated by a positive series.
/// Here 0<=h<=ln(50000/13.6)<9, fixed by physical energy admission.
fn unit_moment(m: usize, h: f64) -> f64 {
    let mut term = 1.0 / (m + 1) as f64;
    let mut sum = term;
    for k in 1..160 {
        term *= h / (m + k + 1) as f64;
        sum += term;
        if term <= 2e-18 * sum {
            break;
        }
    }
    (-h).exp() * sum
}
fn log_energy_source(h: f64, z: f64) -> TailResult<f64> {
    let normalized = if z < 0.25 {
        // (1-exp(-z*v))/z = v-z*v^2/2+...; terms decrease in the admitted range.
        let mut factor = 1.0;
        let mut sum = unit_moment(1, h);
        for n in 1..32 {
            factor *= -z / (n + 1) as f64;
            let term = factor * unit_moment(n + 1, h);
            sum += term;
            if term.abs() <= 2e-18 * sum {
                break;
            }
        }
        sum
    } else {
        // Divide only after taking the log below; z may be near f64::MAX.
        let d = phi(h) - phi(h + z);
        if !(d > 0.0 && d.is_finite()) {
            return Err("energy source divided difference");
        }
        return Ok(2.0 * h.ln() + d.ln() - z.ln());
    };
    if !(normalized > 0.0 && normalized.is_finite()) {
        return Err("energy source series");
    }
    Ok(2.0 * h.ln() + normalized.ln())
}
/// Single characteristic. Initial/source counts are per H (and per fixed
/// characteristic measure); q is per unit ln(a). u/be/red/qe are erg/H.
/// Inputs must stay in the tracked Verner energy domain [13.6,50000] eV.
/// Nonzero species rate is illegal if its cutoff is crossed within the segment.
pub fn characteristic(
    initial: LogPositive,
    source_per_s: LogPositive,
    rates: [f64; 3],
    h: f64,
    energy_start_ev: f64,
) -> TailResult<CharacteristicResult> {
    if !h.is_finite()
        || h < 0.0
        || !energy_start_ev.is_finite()
        || !(CUTOFF_EV[0]..=50000.0).contains(&energy_start_ev)
        || rates.iter().any(|x| !x.is_finite() || *x < 0.0)
    {
        return Err("invalid characteristic input");
    }
    let end_e = energy_start_ev * (-h).exp();
    if end_e < CUTOFF_EV[0] {
        return Err("unsplit tracked lower boundary");
    }
    for i in 0..3 {
        if rates[i] > 0.0 && end_e < CUTOFF_EV[i] {
            return Err("unsplit atomic cutoff");
        }
    }
    let lambda = rates.iter().sum::<f64>();
    let z = lambda * h;
    if !lambda.is_finite() || !z.is_finite() {
        return Err("unrepresentable optical depth");
    }
    let energy = lp(EV_ERG.ln() + energy_start_ev.ln())?;
    if h == 0.0 {
        return Ok(CharacteristicResult {
            owners: TailOwners {
                n: initial,
                u: initial.mul(energy)?,
                ..TailOwners::default()
            },
            omitted_addend_bounds: TailOwners::default(),
        });
    }
    let survivor = initial.mul(lp(-z)?)?;
    let injected_stock = source_per_s.mul(lp(log_j(lambda, h))?)?;
    let ns = survivor.add(injected_stock)?;
    let n_initial_count = initial.mul(lp(log_j(lambda, h))?)?;
    let n_source_count = source_per_s.mul(lp(log_count_source(h, z))?)?;
    let count = n_initial_count.add(n_source_count)?;
    let e_initial = initial.mul(energy)?.mul(lp(log_j(lambda + 1.0, h))?)?;
    let e_source = source_per_s
        .mul(energy)?
        .mul(lp(log_energy_source(h, z)?)?)?;
    let eint = e_initial.add(e_source)?;
    let endpoint_energy = lp(EV_ERG.ln() + energy_start_ev.ln() - h)?;
    let mut o = TailOwners {
        n: ns.value,
        u: ns.value.mul(endpoint_energy)?,
        red: eint.value,
        qn: source_per_s.scale(h)?,
        qe: source_per_s.mul(energy)?.mul(lp(log_j(1.0, h))?)?,
        ..TailOwners::default()
    };
    let mut loss = TailOwners {
        n: ns.omitted_addend_bound,
        u: ns.omitted_addend_bound.mul(endpoint_energy)?,
        red: eint.omitted_addend_bound,
        ..TailOwners::default()
    };
    for i in 0..3 {
        o.an[i] = count.value.scale(rates[i])?;
        o.be[i] = eint.value.scale(rates[i])?;
        loss.an[i] = count.omitted_addend_bound.scale(rates[i])?;
        loss.be[i] = eint.omitted_addend_bound.scale(rates[i])?;
    }
    Ok(CharacteristicResult {
        owners: o,
        omitted_addend_bounds: loss,
    })
}
/// Boundary transfer moves the existing energy owner unchanged before emptying.
/// The caller must first terminate the characteristic at its physical cutoff.
pub fn export(mut owners: TailOwners) -> TailResult<CharacteristicResult> {
    let n = owners.outn.add(owners.n)?;
    let u = owners.oute.add(owners.u)?;
    owners.outn = n.value;
    owners.oute = u.value;
    owners.n = LogPositive::empty();
    owners.u = LogPositive::empty();
    Ok(CharacteristicResult {
        owners,
        omitted_addend_bounds: TailOwners {
            outn: n.omitted_addend_bound,
            oute: u.omitted_addend_bound,
            ..TailOwners::default()
        },
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    fn pos(v: f64) -> LogPositive {
        LogPositive::from_linear(v).unwrap()
    }
    fn val(v: LogPositive) -> f64 {
        v.readout().unwrap().value
    }
    fn close(a: f64, b: f64) {
        assert!((a - b).abs() < 2e-13 * b.abs().max(1e-300), "{a} != {b}");
    }
    #[test]
    fn empty_is_not_underflow() {
        let x = lp(-1100.0).unwrap();
        assert!(!x.is_empty());
        assert_eq!(val(x), 0.0);
        assert_eq!(x.readout().unwrap().zero_readout_bound, x);
        assert!(LogPositive::empty()
            .readout()
            .unwrap()
            .zero_readout_bound
            .is_empty());
    }
    #[test]
    fn zero_time_preserves_inventory() {
        let a = characteristic(lp(-900.0).unwrap(), pos(2.0), [1e6, 0.0, 0.0], 0.0, 14.0).unwrap();
        assert_eq!(a.owners.n.log_value(), -900.0);
        assert!(a.owners.qn.is_empty());
        assert!(a.owners.red.is_empty());
    }
    #[test]
    fn lambda_zero_limits() {
        let h = 0.1;
        let a = characteristic(pos(2.0), pos(3.0), [0.0; 3], h, 100.0)
            .unwrap()
            .owners;
        close(val(a.n), 2.3);
        close(val(a.qn), 0.3);
        close(
            val(a.red),
            EV_ERG * 100.0 * (2.0 * (-(-h).exp_m1()) + 3.0 * (1.0 - (1.0 + h) * (-h).exp())),
        );
        assert!(a.an.iter().all(|x| x.is_empty()));
    }
    #[test]
    fn source_restarts_positive_tail() {
        let a =
            characteristic(lp(-1000.0).unwrap(), pos(1.0), [1e6, 0.0, 0.0], 1e-4, 14.0).unwrap();
        close(val(a.owners.n), 1e-6);
        assert!(!a.omitted_addend_bounds.n.is_empty());
    }
    #[test]
    fn exported_tail_stays_authoritative() {
        let a = characteristic(
            lp(-1000.0).unwrap(),
            LogPositive::empty(),
            [0.0; 3],
            0.0,
            13.6,
        )
        .unwrap()
        .owners;
        let b = export(a).unwrap().owners;
        assert!(b.n.is_empty());
        assert_eq!(b.outn, a.n);
        assert_eq!(b.oute, a.u);
        assert!(!b.oute.is_empty());
    }
    #[test]
    fn cuts_are_explicit() {
        assert!(characteristic(pos(1.0), pos(1.0), [1.0, 0.0, 0.0], 0.1, 14.0).is_err());
        assert!(characteristic(pos(1.0), pos(1.0), [0.0, 1.0, 0.0], 0.001, 20.0).is_err());
    }
    #[test]
    fn invalid_amplitudes_rejected() {
        assert!(lp(f64::INFINITY).is_err());
        assert!(lp(f64::NAN).is_err());
        assert!(LogPositive::from_linear(-1.0).is_err());
    }
    #[test]
    fn species_owners_and_number_energy_budgets() {
        let init = 2.0;
        let q = 3.0;
        let h = 0.2;
        let e = 100.0;
        let o = characteristic(pos(init), pos(q), [2.0, 3.0, 4.0], h, e)
            .unwrap()
            .owners;
        close(
            val(o.n) + o.an.iter().map(|x| val(*x)).sum::<f64>(),
            init + val(o.qn),
        );
        close(
            val(o.u) + o.be.iter().map(|x| val(*x)).sum::<f64>() + val(o.red),
            EV_ERG * e * init + val(o.qe),
        );
    }
    #[test]
    fn aggregation_retains_tail_and_bounds_whole_lost_addend() {
        let a = TailOwners {
            n: lp(-1000.0).unwrap(),
            ..TailOwners::default()
        };
        let b = TailOwners {
            n: pos(1.0),
            ..TailOwners::default()
        };
        let (sum, loss) = a.add(b).unwrap();
        assert_eq!(sum.n, b.n);
        assert_eq!(loss.n, a.n);
        assert_eq!(
            a.scale(pos(2.0)).unwrap().n.log_value(),
            -1000.0 + 2.0f64.ln()
        );
    }
    #[test]
    fn source_tiny_rate_and_tiny_width() {
        let a = characteristic(pos(1.0), pos(1.0), [1e-200, 0.0, 0.0], 1e-100, 14.0)
            .unwrap()
            .owners;
        assert!(a.n.log_value().is_finite());
        assert!(a.red.log_value().is_finite());
        assert!(a.an[0].log_value().is_finite());
    }
}
