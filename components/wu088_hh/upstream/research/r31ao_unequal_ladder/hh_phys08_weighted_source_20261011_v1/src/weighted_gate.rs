//! Scalar interval gate for B = p*v_w - w*(v_x + fhat*v_y1 + 2*fhat*v_y2).
//!
//! Inputs are finite binary64 enclosures, including all signed vector tails.
//! A strict sign of B implies the same sign of C*B/p^2 when C,p > 0.
//! Optional DT encloses (T/(w*p))*B, conditional on the caller supplying an
//! enclosure of the same temperature T = C*w/p. The role is a caller label.
//! This module establishes no source identity, C2 domain, parameter coverage,
//! root, mixed-response, private permit, or native authority.

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Interval {
    pub lo: f64,
    pub hi: f64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum GateError {
    InvalidInterval,
    NonPositiveP,
    NonPositiveW,
    NonPositiveTemperature,
    DenominatorContainsZero,
    NonFiniteArithmetic,
    OutwardRangeOverflow,
    UnsupportedArithmeticEnvironment,
}

impl GateError {
    pub fn code(self) -> &'static str {
        match self {
            Self::InvalidInterval => "INVALID_INTERVAL",
            Self::NonPositiveP => "NON_POSITIVE_P",
            Self::NonPositiveW => "NON_POSITIVE_W",
            Self::NonPositiveTemperature => "NON_POSITIVE_TEMPERATURE",
            Self::DenominatorContainsZero => "DENOMINATOR_CONTAINS_ZERO",
            Self::NonFiniteArithmetic => "NON_FINITE_ARITHMETIC",
            Self::OutwardRangeOverflow => "OUTWARD_RANGE_OVERFLOW",
            Self::UnsupportedArithmeticEnvironment => "UNSUPPORTED_ARITHMETIC_ENVIRONMENT",
        }
    }
}

pub type Result<T> = std::result::Result<T, GateError>;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum StrictSign {
    Negative,
    Positive,
    Unresolved,
}

impl StrictSign {
    pub fn code(self) -> &'static str {
        match self {
            Self::Negative => "NEGATIVE",
            Self::Positive => "POSITIVE",
            Self::Unresolved => "UNRESOLVED",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum VectorRole {
    PhysicalPhotoPN,
    BirthDerivativePM,
    SignedVector,
}

impl VectorRole {
    pub fn code(self) -> &'static str {
        match self {
            Self::PhysicalPhotoPN => "P_N",
            Self::BirthDerivativePM => "P_M",
            Self::SignedVector => "SIGNED_VECTOR",
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct GateInput {
    pub role: VectorRole,
    pub p: Interval,
    pub w: Interval,
    pub fhat: Interval,
    /// Coordinate order: x_HII, y_HeII, y_HeIII, thermal w.
    pub v: [Interval; 4],
    pub temperature: Option<Interval>,
}

#[derive(Clone, Copy, Debug)]
pub struct GateOutput {
    pub role: VectorRole,
    pub balance: Interval,
    pub balance_sign: StrictSign,
    pub dt: Option<Interval>,
    /// Independently classified from the computed DT enclosure. Underflow
    /// can make this Unresolved even when balance_sign is strict.
    pub dt_sign: Option<StrictSign>,
}

// Called only on finite rounded scalar results. Neither signed zero nor a
// subnormal is flushed. If expansion reaches infinity, rounded() rejects it.
fn down(x: f64) -> f64 {
    if x == 0.0 {
        -f64::from_bits(1)
    } else if x > 0.0 {
        f64::from_bits(x.to_bits() - 1)
    } else {
        f64::from_bits(x.to_bits() + 1)
    }
}

fn up(x: f64) -> f64 {
    if x == 0.0 {
        f64::from_bits(1)
    } else if x > 0.0 {
        f64::from_bits(x.to_bits() + 1)
    } else {
        f64::from_bits(x.to_bits() - 1)
    }
}

impl Interval {
    pub fn new(lo: f64, hi: f64) -> Result<Self> {
        if lo.is_finite() && hi.is_finite() && lo <= hi {
            Ok(Self { lo, hi })
        } else {
            Err(GateError::InvalidInterval)
        }
    }

    pub fn point(x: f64) -> Result<Self> {
        Self::new(x, x)
    }

    pub fn validate(self) -> Result<()> {
        Self::new(self.lo, self.hi).map(|_| ())
    }

    fn rounded(lo: f64, hi: f64) -> Result<Self> {
        if !lo.is_finite() || !hi.is_finite() {
            return Err(GateError::NonFiniteArithmetic);
        }
        let outer_lo = down(lo);
        let outer_hi = up(hi);
        if !outer_lo.is_finite() || !outer_hi.is_finite() {
            return Err(GateError::OutwardRangeOverflow);
        }
        Self::new(outer_lo, outer_hi)
    }

    pub fn add(self, rhs: Self) -> Result<Self> {
        self.validate()?;
        rhs.validate()?;
        Self::rounded(self.lo + rhs.lo, self.hi + rhs.hi)
    }

    pub fn sub(self, rhs: Self) -> Result<Self> {
        self.validate()?;
        rhs.validate()?;
        Self::rounded(self.lo - rhs.hi, self.hi - rhs.lo)
    }

    pub fn mul(self, rhs: Self) -> Result<Self> {
        self.validate()?;
        rhs.validate()?;
        let a = [
            self.lo * rhs.lo,
            self.lo * rhs.hi,
            self.hi * rhs.lo,
            self.hi * rhs.hi,
        ];
        if a.iter().any(|v| !v.is_finite()) {
            return Err(GateError::NonFiniteArithmetic);
        }
        let lo = a.iter().copied().fold(a[0], f64::min);
        let hi = a.iter().copied().fold(a[0], f64::max);
        Self::rounded(lo, hi)
    }

    pub fn div(self, rhs: Self) -> Result<Self> {
        self.validate()?;
        rhs.validate()?;
        if rhs.lo <= 0.0 && rhs.hi >= 0.0 {
            return Err(GateError::DenominatorContainsZero);
        }
        let a = [
            self.lo / rhs.lo,
            self.lo / rhs.hi,
            self.hi / rhs.lo,
            self.hi / rhs.hi,
        ];
        if a.iter().any(|v| !v.is_finite()) {
            return Err(GateError::NonFiniteArithmetic);
        }
        let lo = a.iter().copied().fold(a[0], f64::min);
        let hi = a.iter().copied().fold(a[0], f64::max);
        Self::rounded(lo, hi)
    }

    pub fn strict_sign(self) -> Result<StrictSign> {
        self.validate()?;
        Ok(if self.hi < 0.0 {
            StrictSign::Negative
        } else if self.lo > 0.0 {
            StrictSign::Positive
        } else {
            StrictSign::Unresolved
        })
    }
}

/// Reject observed flush-to-zero, denormals-as-zero, or non-nearest rounding.
/// These probes are a runtime guard, not exhaustive platform attestation.
/// Correctness requires ordinary IEEE-754 binary64 operations without unsafe
/// fast-math transformations or an externally changed floating-point mode.
pub fn check_arithmetic_environment() -> Result<()> {
    use std::hint::black_box;
    let half_min_normal = black_box(f64::MIN_POSITIVE) * black_box(0.5);
    let twice_min_subnormal = black_box(f64::from_bits(1)) * black_box(2.0);
    let half_ulp_at_one = f64::from_bits(0x3ca0_0000_0000_0000);
    let three_quarter_ulp_at_one = f64::from_bits(0x3ca8_0000_0000_0000);
    let tie = black_box(1.0) + black_box(half_ulp_at_one);
    let negative_tie = black_box(-1.0) - black_box(half_ulp_at_one);
    let above_tie = black_box(1.0) + black_box(three_quarter_ulp_at_one);
    if half_min_normal.to_bits() != 0x0008_0000_0000_0000
        || twice_min_subnormal.to_bits() != 2
        || tie.to_bits() != 1.0_f64.to_bits()
        || negative_tie.to_bits() != (-1.0_f64).to_bits()
        || above_tie.to_bits() != 1.0_f64.to_bits() + 1
    {
        return Err(GateError::UnsupportedArithmeticEnvironment);
    }
    Ok(())
}

/// Enclose the scalar weighted balance and, optionally, its temperature
/// direction. fhat and v are allowed to be signed; no small terms are clipped.
pub fn evaluate(input: &GateInput) -> Result<GateOutput> {
    input.p.validate()?;
    input.w.validate()?;
    input.fhat.validate()?;
    for component in input.v {
        component.validate()?;
    }
    if let Some(t) = input.temperature {
        t.validate()?;
        if t.lo <= 0.0 {
            return Err(GateError::NonPositiveTemperature);
        }
    }
    if input.p.lo <= 0.0 {
        return Err(GateError::NonPositiveP);
    }
    if input.w.lo <= 0.0 {
        return Err(GateError::NonPositiveW);
    }
    check_arithmetic_environment()?;

    let two = Interval::point(2.0)?;
    let particle_direction = input.v[0]
        .add(input.fhat.mul(input.v[1])?)?
        .add(two.mul(input.fhat)?.mul(input.v[2])?)?;
    let balance = input.p.mul(input.v[3])?.sub(input.w.mul(particle_direction)?)?;
    let balance_sign = balance.strict_sign()?;
    let dt = match input.temperature {
        Some(t) => Some(t.div(input.w.mul(input.p)?)?.mul(balance)?),
        None => None,
    };
    let dt_sign = match dt {
        Some(value) => Some(value.strict_sign()?),
        None => None,
    };
    Ok(GateOutput { role: input.role, balance, balance_sign, dt, dt_sign })
}
