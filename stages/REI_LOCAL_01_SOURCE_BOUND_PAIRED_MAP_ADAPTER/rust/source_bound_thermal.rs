//! Rust-first MPFR-256 interval certificate kernel.
//!
//! The C ABI accepts binary64 interval endpoints, but every load-bearing
//! operation is performed with MPFR at 256-bit precision.  Lower endpoints
//! use `MPFR_RNDD`, upper endpoints use `MPFR_RNDU`, and midpoint-only work
//! (the point preconditioner) uses `MPFR_RNDN`.  A successful certificate is
//! therefore a full interval Krawczyk self-inclusion, not a midpoint-inverse
//! image presented as an enclosure.
//!
//! This crate certifies supplied 2x2/3x3 linear, tangent, and mixed blocks.
//! It does not by itself bind the four evaluation sites, the resolved OTS
//! photoheating law, or the outer owner-normalization context; those remain
//! obligations of the production four-site operator.
//!
//! ABI compatibility note: the two output pointers historically named
//! `residual_lower`/`residual_upper` carry the certified right-hand side of
//! the implicit equation (`b`, `db-dA*Z`, or the complete mixed RHS).  The
//! internal defect `b-A*center` is used to form the Krawczyk image but is not
//! exported under ABI v4.

use std::cmp::Ordering;
use std::ffi::{c_int, c_long, c_ulong};
use std::fmt;
use std::mem::{align_of, size_of, MaybeUninit};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::slice;

pub const STATUS_OK: i32 = 0;
pub const STATUS_INVALID_DIMENSION: i32 = 1;
pub const STATUS_NULL_POINTER: i32 = 2;
pub const STATUS_INVALID_INTERVAL: i32 = 3;
pub const STATUS_ZERO_DIVISOR_INTERVAL: i32 = 4;
pub const STATUS_SINGULAR_MIDPOINT: i32 = 5;
pub const STATUS_NO_STRICT_SELF_INCLUSION: i32 = 6;
pub const STATUS_NONFINITE_OUTPUT: i32 = 7;
pub const STATUS_MISSING_DELTA_A: i32 = 8;
pub const STATUS_MISSING_MIXED_TERM: i32 = 9;
pub const STATUS_LENGTH_MISMATCH: i32 = 10;
pub const STATUS_NATIVE_PANIC: i32 = 11;
pub const STATUS_ALIASED_OUTPUT: i32 = 12;

const PRECISION: c_long = 256;
const RNDN: c_int = 0;
const RNDU: c_int = 2;
const RNDD: c_int = 3;

/// Public layout mirror for MPFR 4.x on the locked x86_64 GNU ABI.
///
/// This is deliberately used only as storage passed to the native MPFR API;
/// Rust never reads or writes the fields after `mpfr_init2`.
#[repr(C)]
struct MpfrRaw {
    precision: c_long,
    sign: c_int,
    exponent: c_long,
    limbs: *mut c_ulong,
}

#[link(name = "libmpfr.so.6", kind = "dylib", modifiers = "+verbatim")]
unsafe extern "C" {
    fn mpfr_init2(value: *mut MpfrRaw, precision: c_long);
    fn mpfr_clear(value: *mut MpfrRaw);
    fn mpfr_set_d(result: *mut MpfrRaw, value: f64, rounding: c_int) -> c_int;
    fn mpfr_set_si(result: *mut MpfrRaw, value: c_long, rounding: c_int) -> c_int;
    fn mpfr_set(result: *mut MpfrRaw, value: *const MpfrRaw, rounding: c_int) -> c_int;
    fn mpfr_add(
        result: *mut MpfrRaw,
        left: *const MpfrRaw,
        right: *const MpfrRaw,
        rounding: c_int,
    ) -> c_int;
    fn mpfr_sub(
        result: *mut MpfrRaw,
        left: *const MpfrRaw,
        right: *const MpfrRaw,
        rounding: c_int,
    ) -> c_int;
    fn mpfr_mul(
        result: *mut MpfrRaw,
        left: *const MpfrRaw,
        right: *const MpfrRaw,
        rounding: c_int,
    ) -> c_int;
    fn mpfr_div(
        result: *mut MpfrRaw,
        left: *const MpfrRaw,
        right: *const MpfrRaw,
        rounding: c_int,
    ) -> c_int;
    fn mpfr_div_2ui(
        result: *mut MpfrRaw,
        value: *const MpfrRaw,
        power: c_ulong,
        rounding: c_int,
    ) -> c_int;
    fn mpfr_abs(result: *mut MpfrRaw, value: *const MpfrRaw, rounding: c_int) -> c_int;
    fn mpfr_cmp(left: *const MpfrRaw, right: *const MpfrRaw) -> c_int;
    fn mpfr_zero_p(value: *const MpfrRaw) -> c_int;
    fn mpfr_get_d(value: *const MpfrRaw, rounding: c_int) -> f64;
}

struct Mpfr {
    raw: MpfrRaw,
}

impl Mpfr {
    fn uninitialized() -> Self {
        let mut raw = MaybeUninit::<MpfrRaw>::uninit();
        unsafe { mpfr_init2(raw.as_mut_ptr(), PRECISION) };
        Self {
            raw: unsafe { raw.assume_init() },
        }
    }

    fn from_f64(value: f64, rounding: c_int) -> Self {
        let mut result = Self::uninitialized();
        unsafe { mpfr_set_d(&mut result.raw, value, rounding) };
        result
    }

    fn from_i64(value: i64) -> Self {
        let mut result = Self::uninitialized();
        unsafe { mpfr_set_si(&mut result.raw, value as c_long, RNDN) };
        result
    }

    fn binary(
        left: &Self,
        right: &Self,
        rounding: c_int,
        operation: unsafe extern "C" fn(
            *mut MpfrRaw,
            *const MpfrRaw,
            *const MpfrRaw,
            c_int,
        ) -> c_int,
    ) -> Self {
        let mut result = Self::uninitialized();
        unsafe { operation(&mut result.raw, &left.raw, &right.raw, rounding) };
        result
    }

    fn add(left: &Self, right: &Self, rounding: c_int) -> Self {
        Self::binary(left, right, rounding, mpfr_add)
    }

    fn sub(left: &Self, right: &Self, rounding: c_int) -> Self {
        Self::binary(left, right, rounding, mpfr_sub)
    }

    fn mul(left: &Self, right: &Self, rounding: c_int) -> Self {
        Self::binary(left, right, rounding, mpfr_mul)
    }

    fn div(left: &Self, right: &Self, rounding: c_int) -> Self {
        Self::binary(left, right, rounding, mpfr_div)
    }

    fn half(value: &Self, rounding: c_int) -> Self {
        let mut result = Self::uninitialized();
        unsafe { mpfr_div_2ui(&mut result.raw, &value.raw, 1, rounding) };
        result
    }

    fn abs(value: &Self, rounding: c_int) -> Self {
        let mut result = Self::uninitialized();
        unsafe { mpfr_abs(&mut result.raw, &value.raw, rounding) };
        result
    }

    fn compare(&self, other: &Self) -> Ordering {
        match unsafe { mpfr_cmp(&self.raw, &other.raw) } {
            value if value < 0 => Ordering::Less,
            value if value > 0 => Ordering::Greater,
            _ => Ordering::Equal,
        }
    }

    fn is_zero(&self) -> bool {
        unsafe { mpfr_zero_p(&self.raw) != 0 }
    }

    fn to_f64(&self, rounding: c_int) -> f64 {
        unsafe { mpfr_get_d(&self.raw, rounding) }
    }
}

impl Clone for Mpfr {
    fn clone(&self) -> Self {
        let mut result = Self::uninitialized();
        unsafe { mpfr_set(&mut result.raw, &self.raw, RNDN) };
        result
    }
}

impl Drop for Mpfr {
    fn drop(&mut self) {
        unsafe { mpfr_clear(&mut self.raw) };
    }
}

#[derive(Clone)]
struct Interval {
    lower: Mpfr,
    upper: Mpfr,
}

impl Interval {
    fn new(lower: f64, upper: f64) -> Result<Self, i32> {
        if !lower.is_finite() || !upper.is_finite() || lower > upper {
            return Err(STATUS_INVALID_INTERVAL);
        }
        Ok(Self {
            lower: Mpfr::from_f64(lower, RNDD),
            upper: Mpfr::from_f64(upper, RNDU),
        })
    }

    fn from_mpfr(lower: Mpfr, upper: Mpfr) -> Self {
        Self { lower, upper }
    }

    fn point(value: f64) -> Self {
        Self::new(value, value).expect("finite point fixture")
    }

    fn point_mpfr(value: &Mpfr) -> Self {
        Self {
            lower: value.clone(),
            upper: value.clone(),
        }
    }

    fn zero() -> Self {
        Self::point(0.0)
    }

    fn midpoint(&self) -> Mpfr {
        Mpfr::half(&Mpfr::add(&self.lower, &self.upper, RNDN), RNDN)
    }

    fn add(&self, other: &Self) -> Self {
        Self::from_mpfr(
            Mpfr::add(&self.lower, &other.lower, RNDD),
            Mpfr::add(&self.upper, &other.upper, RNDU),
        )
    }

    fn sub(&self, other: &Self) -> Self {
        Self::from_mpfr(
            Mpfr::sub(&self.lower, &other.upper, RNDD),
            Mpfr::sub(&self.upper, &other.lower, RNDU),
        )
    }

    fn mul(&self, other: &Self) -> Self {
        let lower_products = [
            Mpfr::mul(&self.lower, &other.lower, RNDD),
            Mpfr::mul(&self.lower, &other.upper, RNDD),
            Mpfr::mul(&self.upper, &other.lower, RNDD),
            Mpfr::mul(&self.upper, &other.upper, RNDD),
        ];
        let upper_products = [
            Mpfr::mul(&self.lower, &other.lower, RNDU),
            Mpfr::mul(&self.lower, &other.upper, RNDU),
            Mpfr::mul(&self.upper, &other.lower, RNDU),
            Mpfr::mul(&self.upper, &other.upper, RNDU),
        ];
        let mut lower = lower_products[0].clone();
        let mut upper = upper_products[0].clone();
        for value in lower_products.iter().skip(1) {
            if value.compare(&lower) == Ordering::Less {
                lower = value.clone();
            }
        }
        for value in upper_products.iter().skip(1) {
            if value.compare(&upper) == Ordering::Greater {
                upper = value.clone();
            }
        }
        Self::from_mpfr(lower, upper)
    }

    fn contains_zero(&self) -> bool {
        let zero = Mpfr::from_i64(0);
        self.lower.compare(&zero) != Ordering::Greater
            && self.upper.compare(&zero) != Ordering::Less
    }

    fn div(&self, other: &Self) -> Result<Self, i32> {
        if other.contains_zero() {
            return Err(STATUS_ZERO_DIVISOR_INTERVAL);
        }
        let reciprocal = Self::from_mpfr(
            Mpfr::div(&Mpfr::from_i64(1), &other.upper, RNDD),
            Mpfr::div(&Mpfr::from_i64(1), &other.lower, RNDU),
        );
        let reciprocal = if reciprocal.lower.compare(&reciprocal.upper) == Ordering::Greater {
            Self::from_mpfr(reciprocal.upper, reciprocal.lower)
        } else {
            reciprocal
        };
        Ok(self.mul(&reciprocal))
    }

    #[cfg(test)]
    fn contains(&self, value: f64) -> bool {
        let point = Mpfr::from_f64(value, RNDN);
        self.lower.compare(&point) != Ordering::Greater
            && self.upper.compare(&point) != Ordering::Less
    }

    fn strictly_inside(&self, outer: &Self) -> bool {
        self.lower.compare(&outer.lower) == Ordering::Greater
            && self.upper.compare(&outer.upper) == Ordering::Less
    }

    fn maximum_absolute(&self) -> Mpfr {
        let left = Mpfr::abs(&self.lower, RNDU);
        let right = Mpfr::abs(&self.upper, RNDU);
        if left.compare(&right) == Ordering::Greater {
            left
        } else {
            right
        }
    }

    fn endpoints(&self) -> (f64, f64) {
        (self.lower.to_f64(RNDD), self.upper.to_f64(RNDU))
    }
}

impl PartialEq for Interval {
    fn eq(&self, other: &Self) -> bool {
        self.lower.compare(&other.lower) == Ordering::Equal
            && self.upper.compare(&other.upper) == Ordering::Equal
    }
}

impl fmt::Debug for Interval {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_tuple("Interval")
            .field(&self.endpoints())
            .finish()
    }
}

#[derive(Debug)]
struct Certificate {
    candidate: Vec<Interval>,
    krawczyk: Vec<Interval>,
    center: Vec<Mpfr>,
    rhs: Vec<Interval>,
    preconditioner: Vec<Mpfr>,
    contraction_upper: Mpfr,
    lower_margins: Vec<Mpfr>,
    upper_margins: Vec<Mpfr>,
    strict: bool,
    iterations: u32,
}

impl fmt::Debug for Mpfr {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_tuple("Mpfr")
            .field(&self.to_f64(RNDN))
            .finish()
    }
}

fn validate_shape(n: usize, matrix_len: usize, vector_len: usize) -> Result<(), i32> {
    if !(2..=3).contains(&n) {
        return Err(STATUS_INVALID_DIMENSION);
    }
    let expected_matrix = n.checked_mul(n).ok_or(STATUS_LENGTH_MISMATCH)?;
    if matrix_len != expected_matrix || vector_len != n {
        return Err(STATUS_LENGTH_MISMATCH);
    }
    Ok(())
}

fn invert_point_matrix(n: usize, matrix: &[Mpfr]) -> Result<Vec<Mpfr>, i32> {
    let width = 2 * n;
    let mut augmented = Vec::with_capacity(n * width);
    for row in 0..n {
        for column in 0..n {
            augmented.push(matrix[row * n + column].clone());
        }
        for column in 0..n {
            augmented.push(Mpfr::from_i64((row == column) as i64));
        }
    }

    for column in 0..n {
        let mut pivot = column;
        let mut pivot_absolute = Mpfr::abs(&augmented[column * width + column], RNDN);
        for row in (column + 1)..n {
            let candidate = Mpfr::abs(&augmented[row * width + column], RNDN);
            if candidate.compare(&pivot_absolute) == Ordering::Greater {
                pivot = row;
                pivot_absolute = candidate;
            }
        }
        if pivot_absolute.is_zero() {
            return Err(STATUS_SINGULAR_MIDPOINT);
        }
        if pivot != column {
            for entry in 0..width {
                augmented.swap(column * width + entry, pivot * width + entry);
            }
        }

        let pivot_value = augmented[column * width + column].clone();
        for entry in 0..width {
            let updated = Mpfr::div(&augmented[column * width + entry], &pivot_value, RNDN);
            augmented[column * width + entry] = updated;
        }
        for row in 0..n {
            if row == column {
                continue;
            }
            let factor = augmented[row * width + column].clone();
            for entry in 0..width {
                let product = Mpfr::mul(&factor, &augmented[column * width + entry], RNDN);
                let updated = Mpfr::sub(&augmented[row * width + entry], &product, RNDN);
                augmented[row * width + entry] = updated;
            }
        }
    }

    let mut inverse = Vec::with_capacity(n * n);
    for row in 0..n {
        for column in 0..n {
            inverse.push(augmented[row * width + n + column].clone());
        }
    }
    Ok(inverse)
}

fn point_matrix_vector(n: usize, matrix: &[Mpfr], vector: &[Mpfr]) -> Vec<Mpfr> {
    let mut result = Vec::with_capacity(n);
    for row in 0..n {
        let mut sum = Mpfr::from_i64(0);
        for column in 0..n {
            let product = Mpfr::mul(&matrix[row * n + column], &vector[column], RNDN);
            sum = Mpfr::add(&sum, &product, RNDN);
        }
        result.push(sum);
    }
    result
}

fn interval_matrix_point(n: usize, matrix: &[Interval], vector: &[Mpfr]) -> Vec<Interval> {
    let mut result = Vec::with_capacity(n);
    for row in 0..n {
        let mut sum = Interval::zero();
        for column in 0..n {
            sum = sum.add(&matrix[row * n + column].mul(&Interval::point_mpfr(&vector[column])));
        }
        result.push(sum);
    }
    result
}

fn interval_matrix_vector(n: usize, matrix: &[Interval], vector: &[Interval]) -> Vec<Interval> {
    let mut result = Vec::with_capacity(n);
    for row in 0..n {
        let mut sum = Interval::zero();
        for column in 0..n {
            sum = sum.add(&matrix[row * n + column].mul(&vector[column]));
        }
        result.push(sum);
    }
    result
}

fn point_matrix_interval_vector(n: usize, matrix: &[Mpfr], vector: &[Interval]) -> Vec<Interval> {
    let point_matrix: Vec<Interval> = matrix.iter().map(Interval::point_mpfr).collect();
    interval_matrix_vector(n, &point_matrix, vector)
}

fn point_matrix_interval_matrix(n: usize, point: &[Mpfr], interval: &[Interval]) -> Vec<Interval> {
    let mut result = Vec::with_capacity(n * n);
    for row in 0..n {
        for column in 0..n {
            let mut sum = Interval::zero();
            for inner in 0..n {
                let left = Interval::point_mpfr(&point[row * n + inner]);
                sum = sum.add(&left.mul(&interval[inner * n + column]));
            }
            result.push(sum);
        }
    }
    result
}

fn krawczyk_evaluate(
    n: usize,
    a: &[Interval],
    rhs: &[Interval],
    candidate: &[Interval],
    preconditioner: &[Mpfr],
    center: &[Mpfr],
    iterations: u32,
) -> Certificate {
    let a_center = interval_matrix_point(n, a, center);
    let nonlinear_residual: Vec<Interval> = rhs
        .iter()
        .zip(a_center.iter())
        .map(|(right, image)| right.sub(image))
        .collect();
    let correction = point_matrix_interval_vector(n, preconditioner, &nonlinear_residual);
    let ca = point_matrix_interval_matrix(n, preconditioner, a);
    let mut identity_minus_ca = Vec::with_capacity(n * n);
    for row in 0..n {
        for column in 0..n {
            let identity = Interval::point((row == column) as u8 as f64);
            identity_minus_ca.push(identity.sub(&ca[row * n + column]));
        }
    }
    let displacement: Vec<Interval> = candidate
        .iter()
        .zip(center.iter())
        .map(|(outer, point)| outer.sub(&Interval::point_mpfr(point)))
        .collect();
    let propagated = interval_matrix_vector(n, &identity_minus_ca, &displacement);
    let krawczyk: Vec<Interval> = (0..n)
        .map(|index| {
            Interval::point_mpfr(&center[index])
                .add(&correction[index])
                .add(&propagated[index])
        })
        .collect();

    let mut contraction_upper = Mpfr::from_i64(0);
    for row in 0..n {
        let mut row_sum = Mpfr::from_i64(0);
        for column in 0..n {
            row_sum = Mpfr::add(
                &row_sum,
                &identity_minus_ca[row * n + column].maximum_absolute(),
                RNDU,
            );
        }
        if row_sum.compare(&contraction_upper) == Ordering::Greater {
            contraction_upper = row_sum;
        }
    }

    let lower_margins: Vec<Mpfr> = (0..n)
        .map(|index| Mpfr::sub(&krawczyk[index].lower, &candidate[index].lower, RNDD))
        .collect();
    let upper_margins: Vec<Mpfr> = (0..n)
        .map(|index| Mpfr::sub(&candidate[index].upper, &krawczyk[index].upper, RNDD))
        .collect();
    let strict_inclusion = krawczyk
        .iter()
        .zip(candidate.iter())
        .all(|(inner, outer)| inner.strictly_inside(outer));
    let strict_contraction = contraction_upper.compare(&Mpfr::from_i64(1)) == Ordering::Less;
    let strict = strict_inclusion && strict_contraction;

    Certificate {
        candidate: candidate.to_vec(),
        krawczyk: krawczyk.clone(),
        center: center.to_vec(),
        rhs: rhs.to_vec(),
        preconditioner: preconditioner.to_vec(),
        contraction_upper,
        lower_margins,
        upper_margins,
        strict,
        iterations,
    }
}

fn certify_linear_with_candidate(
    n: usize,
    a: &[Interval],
    rhs: &[Interval],
    candidate: Option<&[Interval]>,
) -> Result<Certificate, i32> {
    if a.len() != n * n || rhs.len() != n {
        return Err(STATUS_LENGTH_MISMATCH);
    }
    let midpoint_a: Vec<Mpfr> = a.iter().map(Interval::midpoint).collect();
    let midpoint_rhs: Vec<Mpfr> = rhs.iter().map(Interval::midpoint).collect();
    let preconditioner = invert_point_matrix(n, &midpoint_a)?;
    let center = point_matrix_vector(n, &preconditioner, &midpoint_rhs);

    if let Some(candidate) = candidate {
        if candidate.len() != n {
            return Err(STATUS_LENGTH_MISMATCH);
        }
        let certificate = krawczyk_evaluate(n, a, rhs, candidate, &preconditioner, &center, 1);
        return if certificate.strict {
            Ok(certificate)
        } else {
            Err(STATUS_NO_STRICT_SELF_INCLUSION)
        };
    }

    let point_candidate: Vec<Interval> = center.iter().map(Interval::point_mpfr).collect();
    let point_image = krawczyk_evaluate(n, a, rhs, &point_candidate, &preconditioner, &center, 1);
    let rho = point_image.contraction_upper.to_f64(RNDU);
    if !rho.is_finite() || rho >= 1.0 {
        return Err(STATUS_NO_STRICT_SELF_INCLUSION);
    }
    let denominator = 1.0 - rho;
    let mut maximum_gap = 0.0_f64;
    let mut maximum_scale = 1.0_f64;
    for index in 0..n {
        let lower_gap = Mpfr::sub(&center[index], &point_image.krawczyk[index].lower, RNDU)
            .to_f64(RNDU)
            .abs();
        let upper_gap = Mpfr::sub(&point_image.krawczyk[index].upper, &center[index], RNDU)
            .to_f64(RNDU)
            .abs();
        let scale = center[index].to_f64(RNDN).abs().max(1.0);
        if !lower_gap.is_finite() || !upper_gap.is_finite() || !scale.is_finite() {
            return Err(STATUS_NONFINITE_OUTPUT);
        }
        maximum_gap = maximum_gap.max(lower_gap).max(upper_gap);
        maximum_scale = maximum_scale.max(scale);
    }
    // A common radius turns the infinity-norm contraction bound into the
    // scalar inequality q + rho*r < r.  Per-component seeds can fail forever
    // under cross-component coupling even when rho < 1.
    let width = (2.0 * maximum_gap / denominator).max(maximum_scale * f64::EPSILON);
    if !width.is_finite() {
        return Err(STATUS_NONFINITE_OUTPUT);
    }
    let mut widths = vec![width; n];
    for iteration in 2..=32_u32 {
        let mut trial = Vec::with_capacity(n);
        for index in 0..n {
            let radius = Mpfr::from_f64(widths[index], RNDU);
            trial.push(Interval::from_mpfr(
                Mpfr::sub(&center[index], &radius, RNDD),
                Mpfr::add(&center[index], &radius, RNDU),
            ));
        }
        let certificate = krawczyk_evaluate(n, a, rhs, &trial, &preconditioner, &center, iteration);
        if certificate.strict {
            return Ok(certificate);
        }
        for width in &mut widths {
            *width *= 2.0;
            if !width.is_finite() {
                return Err(STATUS_NONFINITE_OUTPUT);
            }
        }
    }
    Err(STATUS_NO_STRICT_SELF_INCLUSION)
}

#[cfg(test)]
fn certify_linear(
    n: usize,
    a: &[Interval],
    rhs: &[Interval],
    candidate: &[Interval],
) -> Result<Certificate, i32> {
    certify_linear_with_candidate(n, a, rhs, Some(candidate))
}

fn tangent_rhs(
    n: usize,
    z: &[Interval],
    delta_a: &[Interval],
    delta_b: &[Interval],
) -> Result<Vec<Interval>, i32> {
    if z.len() != n || delta_a.len() != n * n || delta_b.len() != n {
        return Err(STATUS_LENGTH_MISMATCH);
    }
    let delta_a_z = interval_matrix_vector(n, delta_a, z);
    Ok(delta_b
        .iter()
        .zip(delta_a_z.iter())
        .map(|(right, product)| right.sub(product))
        .collect())
}

#[cfg(test)]
fn certify_tangent(
    n: usize,
    a: &[Interval],
    z: &[Interval],
    delta_a: &[Interval],
    delta_b: &[Interval],
    candidate: &[Interval],
) -> Result<Certificate, i32> {
    let rhs = tangent_rhs(n, z, delta_a, delta_b)?;
    certify_linear(n, a, &rhs, candidate)
}

fn mixed_rhs(
    n: usize,
    b_vf: &[Interval],
    a_vf: &[Interval],
    z: &[Interval],
    a_v: &[Interval],
    z_f: &[Interval],
    a_f: &[Interval],
    z_v: &[Interval],
) -> Result<Vec<Interval>, i32> {
    if b_vf.len() != n
        || z.len() != n
        || z_f.len() != n
        || z_v.len() != n
        || a_vf.len() != n * n
        || a_v.len() != n * n
        || a_f.len() != n * n
    {
        return Err(STATUS_LENGTH_MISMATCH);
    }
    let first = interval_matrix_vector(n, a_vf, z);
    let second = interval_matrix_vector(n, a_v, z_f);
    let third = interval_matrix_vector(n, a_f, z_v);
    Ok((0..n)
        .map(|index| {
            b_vf[index]
                .sub(&first[index])
                .sub(&second[index])
                .sub(&third[index])
        })
        .collect())
}

fn read_intervals(
    lower: *const f64,
    upper: *const f64,
    length: usize,
) -> Result<Vec<Interval>, i32> {
    if lower.is_null()
        || upper.is_null()
        || (lower as usize) % align_of::<f64>() != 0
        || (upper as usize) % align_of::<f64>() != 0
    {
        return Err(STATUS_NULL_POINTER);
    }
    let lower = unsafe { slice::from_raw_parts(lower, length) };
    let upper = unsafe { slice::from_raw_parts(upper, length) };
    lower
        .iter()
        .zip(upper.iter())
        .map(|(&lo, &hi)| Interval::new(lo, hi))
        .collect()
}

fn byte_range(address: usize, length: usize, element_size: usize) -> Option<(usize, usize)> {
    let bytes = length.checked_mul(element_size)?;
    Some((address, address.checked_add(bytes)?))
}

fn overlaps(left: (usize, usize), right: (usize, usize)) -> bool {
    left.0 < right.1 && right.0 < left.1
}

fn validate_output_aliases(
    outputs: &[(usize, usize)],
    inputs: &[(usize, usize)],
) -> Result<(), i32> {
    for (index, output) in outputs.iter().enumerate() {
        if output.0 == 0 {
            return Err(STATUS_NULL_POINTER);
        }
        if inputs.iter().any(|input| overlaps(*output, *input))
            || outputs[..index]
                .iter()
                .any(|other| overlaps(*output, *other))
        {
            return Err(STATUS_ALIASED_OUTPUT);
        }
    }
    Ok(())
}

fn data_range(pointer: *const f64, length: usize) -> Result<(usize, usize), i32> {
    if pointer.is_null() || (pointer as usize) % align_of::<f64>() != 0 {
        return Err(STATUS_NULL_POINTER);
    }
    byte_range(pointer as usize, length, size_of::<f64>()).ok_or(STATUS_LENGTH_MISMATCH)
}

fn output_range(pointer: *mut f64, length: usize) -> Result<(usize, usize), i32> {
    data_range(pointer.cast_const(), length)
}

#[allow(clippy::too_many_arguments)]
fn write_certificate(
    certificate: &Certificate,
    solution_lower: *mut f64,
    solution_upper: *mut f64,
    krawczyk_lower: *mut f64,
    krawczyk_upper: *mut f64,
    center: *mut f64,
    residual_lower: *mut f64,
    residual_upper: *mut f64,
    preconditioner: *mut f64,
    contraction_upper: *mut f64,
    lower_margins: *mut f64,
    upper_margins: *mut f64,
    iterations: *mut u32,
) -> Result<(), i32> {
    let n = certificate.candidate.len();
    let mut solution_lowers = Vec::with_capacity(n);
    let mut solution_uppers = Vec::with_capacity(n);
    let mut krawczyk_lowers = Vec::with_capacity(n);
    let mut krawczyk_uppers = Vec::with_capacity(n);
    let mut centers = Vec::with_capacity(n);
    let mut residual_lowers = Vec::with_capacity(n);
    let mut residual_uppers = Vec::with_capacity(n);
    let mut lower_margin_values = Vec::with_capacity(n);
    let mut upper_margin_values = Vec::with_capacity(n);
    for index in 0..n {
        let (solution_lo, solution_hi) = certificate.candidate[index].endpoints();
        let (k_lo, k_hi) = certificate.krawczyk[index].endpoints();
        let (rhs_lo, rhs_hi) = certificate.rhs[index].endpoints();
        let center_value = certificate.center[index].to_f64(RNDN);
        let lower_margin = certificate.lower_margins[index].to_f64(RNDD);
        let upper_margin = certificate.upper_margins[index].to_f64(RNDD);
        solution_lowers.push(solution_lo);
        solution_uppers.push(solution_hi);
        krawczyk_lowers.push(k_lo);
        krawczyk_uppers.push(k_hi);
        centers.push(center_value);
        residual_lowers.push(rhs_lo);
        residual_uppers.push(rhs_hi);
        lower_margin_values.push(lower_margin);
        upper_margin_values.push(upper_margin);
    }
    let preconditioner_values: Vec<f64> = certificate
        .preconditioner
        .iter()
        .map(|value| value.to_f64(RNDN))
        .collect();
    let rho = certificate.contraction_upper.to_f64(RNDU);
    let all_values = [
        solution_lowers.as_slice(),
        solution_uppers.as_slice(),
        krawczyk_lowers.as_slice(),
        krawczyk_uppers.as_slice(),
        centers.as_slice(),
        residual_lowers.as_slice(),
        residual_uppers.as_slice(),
        preconditioner_values.as_slice(),
        lower_margin_values.as_slice(),
        upper_margin_values.as_slice(),
    ];
    if !rho.is_finite()
        || all_values
            .iter()
            .flat_map(|values| values.iter())
            .any(|value| !value.is_finite())
    {
        return Err(STATUS_NONFINITE_OUTPUT);
    }
    if rho >= 1.0 {
        return Err(STATUS_NO_STRICT_SELF_INCLUSION);
    }
    // The public certificate is binary64.  A strict MPFR inclusion that
    // collapses onto a candidate endpoint during outward conversion is not a
    // valid ABI-v4 certificate and must not be emitted as STATUS_OK.
    for index in 0..n {
        if !(solution_lowers[index] < krawczyk_lowers[index]
            && krawczyk_lowers[index] <= krawczyk_uppers[index]
            && krawczyk_uppers[index] < solution_uppers[index]
            && lower_margin_values[index] > 0.0
            && upper_margin_values[index] > 0.0)
        {
            return Err(STATUS_NO_STRICT_SELF_INCLUSION);
        }
    }
    unsafe {
        std::ptr::copy_nonoverlapping(solution_lowers.as_ptr(), solution_lower, n);
        std::ptr::copy_nonoverlapping(solution_uppers.as_ptr(), solution_upper, n);
        std::ptr::copy_nonoverlapping(krawczyk_lowers.as_ptr(), krawczyk_lower, n);
        std::ptr::copy_nonoverlapping(krawczyk_uppers.as_ptr(), krawczyk_upper, n);
        std::ptr::copy_nonoverlapping(centers.as_ptr(), center, n);
        std::ptr::copy_nonoverlapping(residual_lowers.as_ptr(), residual_lower, n);
        std::ptr::copy_nonoverlapping(residual_uppers.as_ptr(), residual_upper, n);
        std::ptr::copy_nonoverlapping(preconditioner_values.as_ptr(), preconditioner, n * n);
        std::ptr::copy_nonoverlapping(lower_margin_values.as_ptr(), lower_margins, n);
        std::ptr::copy_nonoverlapping(upper_margin_values.as_ptr(), upper_margins, n);
        *contraction_upper = rho;
        *iterations = certificate.iterations;
    }
    Ok(())
}

fn ffi_guard(work: impl FnOnce() -> Result<(), i32>) -> i32 {
    match catch_unwind(AssertUnwindSafe(work)) {
        Ok(Ok(())) => STATUS_OK,
        Ok(Err(status)) => status,
        Err(_) => STATUS_NATIVE_PANIC,
    }
}

#[no_mangle]
pub extern "C" fn rei_source_bound_abi_version() -> u32 {
    4
}

#[no_mangle]
pub extern "C" fn rei_mpfr_precision_bits() -> u32 {
    PRECISION as u32
}

#[no_mangle]
pub extern "C" fn rei_pointer_width_bits() -> u32 {
    usize::BITS
}

#[no_mangle]
pub extern "C" fn rei_limb_bits() -> u32 {
    c_ulong::BITS
}

#[no_mangle]
pub extern "C" fn rei_mpfr_raw_size() -> usize {
    size_of::<MpfrRaw>()
}

#[no_mangle]
pub extern "C" fn rei_mpfr_raw_align() -> usize {
    align_of::<MpfrRaw>()
}

#[no_mangle]
pub extern "C" fn rei_validate_lengths_mpfr256(
    n: usize,
    matrix_length: usize,
    vector_length: usize,
) -> i32 {
    match validate_shape(n, matrix_length, vector_length) {
        Ok(()) => STATUS_OK,
        Err(status) => status,
    }
}

#[no_mangle]
pub unsafe extern "C" fn rei_interval_divide_mpfr256(
    numerator_lower: f64,
    numerator_upper: f64,
    denominator_lower: f64,
    denominator_upper: f64,
    output_lower: *mut f64,
    output_upper: *mut f64,
) -> i32 {
    ffi_guard(|| {
        if output_lower.is_null() || output_upper.is_null() {
            return Err(STATUS_NULL_POINTER);
        }
        let lower_range = output_range(output_lower, 1)?;
        let upper_range = output_range(output_upper, 1)?;
        validate_output_aliases(&[lower_range, upper_range], &[])?;
        let numerator = Interval::new(numerator_lower, numerator_upper)?;
        let denominator = Interval::new(denominator_lower, denominator_upper)?;
        let quotient = numerator.div(&denominator)?;
        let (lower, upper) = quotient.endpoints();
        if !lower.is_finite() || !upper.is_finite() {
            return Err(STATUS_NONFINITE_OUTPUT);
        }
        unsafe {
            *output_lower = lower;
            *output_upper = upper;
        }
        Ok(())
    })
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn rei_certify_linear_mpfr256(
    n: usize,
    matrix_length: usize,
    vector_length: usize,
    a_lower: *const f64,
    a_upper: *const f64,
    b_lower: *const f64,
    b_upper: *const f64,
    candidate_lower: *const f64,
    candidate_upper: *const f64,
    solution_lower: *mut f64,
    solution_upper: *mut f64,
    krawczyk_lower: *mut f64,
    krawczyk_upper: *mut f64,
    center: *mut f64,
    residual_lower: *mut f64,
    residual_upper: *mut f64,
    preconditioner: *mut f64,
    contraction_upper: *mut f64,
    lower_margins: *mut f64,
    upper_margins: *mut f64,
    iterations: *mut u32,
) -> i32 {
    ffi_guard(|| {
        validate_shape(n, matrix_length, vector_length)?;
        let candidate_is_null = candidate_lower.is_null() && candidate_upper.is_null();
        if candidate_lower.is_null() != candidate_upper.is_null() {
            return Err(STATUS_NULL_POINTER);
        }
        let mut inputs = vec![
            data_range(a_lower, matrix_length)?,
            data_range(a_upper, matrix_length)?,
            data_range(b_lower, vector_length)?,
            data_range(b_upper, vector_length)?,
        ];
        if !candidate_is_null {
            inputs.push(data_range(candidate_lower, vector_length)?);
            inputs.push(data_range(candidate_upper, vector_length)?);
        }
        let mut outputs = vec![
            output_range(solution_lower, n)?,
            output_range(solution_upper, n)?,
            output_range(krawczyk_lower, n)?,
            output_range(krawczyk_upper, n)?,
            output_range(center, n)?,
            output_range(residual_lower, n)?,
            output_range(residual_upper, n)?,
            output_range(preconditioner, matrix_length)?,
            output_range(contraction_upper, 1)?,
            output_range(lower_margins, n)?,
            output_range(upper_margins, n)?,
        ];
        if iterations.is_null() || (iterations as usize) % align_of::<u32>() != 0 {
            return Err(STATUS_NULL_POINTER);
        }
        outputs.push(
            byte_range(iterations as usize, 1, size_of::<u32>()).ok_or(STATUS_LENGTH_MISMATCH)?,
        );
        validate_output_aliases(&outputs, &inputs)?;

        let a = read_intervals(a_lower, a_upper, matrix_length)?;
        let b = read_intervals(b_lower, b_upper, vector_length)?;
        let candidate = if candidate_is_null {
            None
        } else {
            Some(read_intervals(
                candidate_lower,
                candidate_upper,
                vector_length,
            )?)
        };
        let certificate = certify_linear_with_candidate(n, &a, &b, candidate.as_deref())?;
        write_certificate(
            &certificate,
            solution_lower,
            solution_upper,
            krawczyk_lower,
            krawczyk_upper,
            center,
            residual_lower,
            residual_upper,
            preconditioner,
            contraction_upper,
            lower_margins,
            upper_margins,
            iterations,
        )
    })
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn rei_certify_tangent_mpfr256(
    n: usize,
    matrix_length: usize,
    vector_length: usize,
    a_lower: *const f64,
    a_upper: *const f64,
    z_lower: *const f64,
    z_upper: *const f64,
    delta_a_lower: *const f64,
    delta_a_upper: *const f64,
    delta_b_lower: *const f64,
    delta_b_upper: *const f64,
    candidate_lower: *const f64,
    candidate_upper: *const f64,
    solution_lower: *mut f64,
    solution_upper: *mut f64,
    krawczyk_lower: *mut f64,
    krawczyk_upper: *mut f64,
    center: *mut f64,
    residual_lower: *mut f64,
    residual_upper: *mut f64,
    preconditioner: *mut f64,
    contraction_upper: *mut f64,
    lower_margins: *mut f64,
    upper_margins: *mut f64,
    iterations: *mut u32,
) -> i32 {
    ffi_guard(|| {
        validate_shape(n, matrix_length, vector_length)?;
        if delta_a_lower.is_null() || delta_a_upper.is_null() {
            return Err(STATUS_MISSING_DELTA_A);
        }
        let candidate_is_null = candidate_lower.is_null() && candidate_upper.is_null();
        if candidate_lower.is_null() != candidate_upper.is_null() {
            return Err(STATUS_NULL_POINTER);
        }
        let mut inputs = vec![
            data_range(a_lower, matrix_length)?,
            data_range(a_upper, matrix_length)?,
            data_range(z_lower, vector_length)?,
            data_range(z_upper, vector_length)?,
            data_range(delta_a_lower, matrix_length)?,
            data_range(delta_a_upper, matrix_length)?,
            data_range(delta_b_lower, vector_length)?,
            data_range(delta_b_upper, vector_length)?,
        ];
        if !candidate_is_null {
            inputs.push(data_range(candidate_lower, vector_length)?);
            inputs.push(data_range(candidate_upper, vector_length)?);
        }
        let mut outputs = vec![
            output_range(solution_lower, n)?,
            output_range(solution_upper, n)?,
            output_range(krawczyk_lower, n)?,
            output_range(krawczyk_upper, n)?,
            output_range(center, n)?,
            output_range(residual_lower, n)?,
            output_range(residual_upper, n)?,
            output_range(preconditioner, matrix_length)?,
            output_range(contraction_upper, 1)?,
            output_range(lower_margins, n)?,
            output_range(upper_margins, n)?,
        ];
        if iterations.is_null() || (iterations as usize) % align_of::<u32>() != 0 {
            return Err(STATUS_NULL_POINTER);
        }
        outputs.push(
            byte_range(iterations as usize, 1, size_of::<u32>()).ok_or(STATUS_LENGTH_MISMATCH)?,
        );
        validate_output_aliases(&outputs, &inputs)?;

        let a = read_intervals(a_lower, a_upper, matrix_length)?;
        let z = read_intervals(z_lower, z_upper, vector_length)?;
        let delta_a = read_intervals(delta_a_lower, delta_a_upper, matrix_length)?;
        let delta_b = read_intervals(delta_b_lower, delta_b_upper, vector_length)?;
        let rhs = tangent_rhs(n, &z, &delta_a, &delta_b)?;
        let candidate = if candidate_is_null {
            None
        } else {
            Some(read_intervals(
                candidate_lower,
                candidate_upper,
                vector_length,
            )?)
        };
        let certificate = certify_linear_with_candidate(n, &a, &rhs, candidate.as_deref())?;
        write_certificate(
            &certificate,
            solution_lower,
            solution_upper,
            krawczyk_lower,
            krawczyk_upper,
            center,
            residual_lower,
            residual_upper,
            preconditioner,
            contraction_upper,
            lower_margins,
            upper_margins,
            iterations,
        )
    })
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn rei_diagnostic_mixed_rhs_mpfr256(
    n: usize,
    matrix_length: usize,
    vector_length: usize,
    b_vf_lower: *const f64,
    b_vf_upper: *const f64,
    a_vf_lower: *const f64,
    a_vf_upper: *const f64,
    z_lower: *const f64,
    z_upper: *const f64,
    a_v_lower: *const f64,
    a_v_upper: *const f64,
    z_f_lower: *const f64,
    z_f_upper: *const f64,
    a_f_lower: *const f64,
    a_f_upper: *const f64,
    z_v_lower: *const f64,
    z_v_upper: *const f64,
    output_lower: *mut f64,
    output_upper: *mut f64,
) -> i32 {
    ffi_guard(|| {
        validate_shape(n, matrix_length, vector_length)?;
        if [
            a_vf_lower, a_vf_upper, z_lower, z_upper, a_v_lower, a_v_upper, z_f_lower, z_f_upper,
            a_f_lower, a_f_upper, z_v_lower, z_v_upper,
        ]
        .iter()
        .any(|pointer| pointer.is_null())
        {
            return Err(STATUS_MISSING_MIXED_TERM);
        }
        let inputs = vec![
            data_range(b_vf_lower, vector_length)?,
            data_range(b_vf_upper, vector_length)?,
            data_range(a_vf_lower, matrix_length)?,
            data_range(a_vf_upper, matrix_length)?,
            data_range(z_lower, vector_length)?,
            data_range(z_upper, vector_length)?,
            data_range(a_v_lower, matrix_length)?,
            data_range(a_v_upper, matrix_length)?,
            data_range(z_f_lower, vector_length)?,
            data_range(z_f_upper, vector_length)?,
            data_range(a_f_lower, matrix_length)?,
            data_range(a_f_upper, matrix_length)?,
            data_range(z_v_lower, vector_length)?,
            data_range(z_v_upper, vector_length)?,
        ];
        let outputs = vec![
            output_range(output_lower, vector_length)?,
            output_range(output_upper, vector_length)?,
        ];
        validate_output_aliases(&outputs, &inputs)?;
        let rhs = mixed_rhs(
            n,
            &read_intervals(b_vf_lower, b_vf_upper, vector_length)?,
            &read_intervals(a_vf_lower, a_vf_upper, matrix_length)?,
            &read_intervals(z_lower, z_upper, vector_length)?,
            &read_intervals(a_v_lower, a_v_upper, matrix_length)?,
            &read_intervals(z_f_lower, z_f_upper, vector_length)?,
            &read_intervals(a_f_lower, a_f_upper, matrix_length)?,
            &read_intervals(z_v_lower, z_v_upper, vector_length)?,
        )?;
        let endpoints: Vec<(f64, f64)> = rhs.iter().map(Interval::endpoints).collect();
        if endpoints
            .iter()
            .any(|(lower, upper)| !lower.is_finite() || !upper.is_finite())
        {
            return Err(STATUS_NONFINITE_OUTPUT);
        }
        for (index, (lower, upper)) in endpoints.into_iter().enumerate() {
            unsafe {
                *output_lower.add(index) = lower;
                *output_upper.add(index) = upper;
            }
        }
        Ok(())
    })
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn rei_certify_mixed_vf_mpfr256(
    n: usize,
    matrix_length: usize,
    vector_length: usize,
    a_lower: *const f64,
    a_upper: *const f64,
    b_vf_lower: *const f64,
    b_vf_upper: *const f64,
    a_vf_lower: *const f64,
    a_vf_upper: *const f64,
    z_lower: *const f64,
    z_upper: *const f64,
    a_v_lower: *const f64,
    a_v_upper: *const f64,
    z_f_lower: *const f64,
    z_f_upper: *const f64,
    a_f_lower: *const f64,
    a_f_upper: *const f64,
    z_v_lower: *const f64,
    z_v_upper: *const f64,
    candidate_lower: *const f64,
    candidate_upper: *const f64,
    solution_lower: *mut f64,
    solution_upper: *mut f64,
    krawczyk_lower: *mut f64,
    krawczyk_upper: *mut f64,
    center: *mut f64,
    residual_lower: *mut f64,
    residual_upper: *mut f64,
    preconditioner: *mut f64,
    contraction_upper: *mut f64,
    lower_margins: *mut f64,
    upper_margins: *mut f64,
    iterations: *mut u32,
) -> i32 {
    ffi_guard(|| {
        validate_shape(n, matrix_length, vector_length)?;
        if [
            a_vf_lower, a_vf_upper, z_lower, z_upper, a_v_lower, a_v_upper, z_f_lower, z_f_upper,
            a_f_lower, a_f_upper, z_v_lower, z_v_upper,
        ]
        .iter()
        .any(|pointer| pointer.is_null())
        {
            return Err(STATUS_MISSING_MIXED_TERM);
        }
        let candidate_is_null = candidate_lower.is_null() && candidate_upper.is_null();
        if candidate_lower.is_null() != candidate_upper.is_null() {
            return Err(STATUS_NULL_POINTER);
        }
        let mut inputs = vec![
            data_range(a_lower, matrix_length)?,
            data_range(a_upper, matrix_length)?,
            data_range(b_vf_lower, vector_length)?,
            data_range(b_vf_upper, vector_length)?,
            data_range(a_vf_lower, matrix_length)?,
            data_range(a_vf_upper, matrix_length)?,
            data_range(z_lower, vector_length)?,
            data_range(z_upper, vector_length)?,
            data_range(a_v_lower, matrix_length)?,
            data_range(a_v_upper, matrix_length)?,
            data_range(z_f_lower, vector_length)?,
            data_range(z_f_upper, vector_length)?,
            data_range(a_f_lower, matrix_length)?,
            data_range(a_f_upper, matrix_length)?,
            data_range(z_v_lower, vector_length)?,
            data_range(z_v_upper, vector_length)?,
        ];
        if !candidate_is_null {
            inputs.push(data_range(candidate_lower, vector_length)?);
            inputs.push(data_range(candidate_upper, vector_length)?);
        }
        let mut outputs = vec![
            output_range(solution_lower, n)?,
            output_range(solution_upper, n)?,
            output_range(krawczyk_lower, n)?,
            output_range(krawczyk_upper, n)?,
            output_range(center, n)?,
            output_range(residual_lower, n)?,
            output_range(residual_upper, n)?,
            output_range(preconditioner, matrix_length)?,
            output_range(contraction_upper, 1)?,
            output_range(lower_margins, n)?,
            output_range(upper_margins, n)?,
        ];
        if iterations.is_null() || (iterations as usize) % align_of::<u32>() != 0 {
            return Err(STATUS_NULL_POINTER);
        }
        outputs.push(
            byte_range(iterations as usize, 1, size_of::<u32>()).ok_or(STATUS_LENGTH_MISMATCH)?,
        );
        validate_output_aliases(&outputs, &inputs)?;
        let a = read_intervals(a_lower, a_upper, matrix_length)?;
        let rhs = mixed_rhs(
            n,
            &read_intervals(b_vf_lower, b_vf_upper, vector_length)?,
            &read_intervals(a_vf_lower, a_vf_upper, matrix_length)?,
            &read_intervals(z_lower, z_upper, vector_length)?,
            &read_intervals(a_v_lower, a_v_upper, matrix_length)?,
            &read_intervals(z_f_lower, z_f_upper, vector_length)?,
            &read_intervals(a_f_lower, a_f_upper, matrix_length)?,
            &read_intervals(z_v_lower, z_v_upper, vector_length)?,
        )?;
        let candidate = if candidate_is_null {
            None
        } else {
            Some(read_intervals(
                candidate_lower,
                candidate_upper,
                vector_length,
            )?)
        };
        let certificate = certify_linear_with_candidate(n, &a, &rhs, candidate.as_deref())?;
        write_certificate(
            &certificate,
            solution_lower,
            solution_upper,
            krawczyk_lower,
            krawczyk_upper,
            center,
            residual_lower,
            residual_upper,
            preconditioner,
            contraction_upper,
            lower_margins,
            upper_margins,
            iterations,
        )
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn p(value: f64) -> Interval {
        Interval::point(value)
    }

    fn i(lower: f64, upper: f64) -> Interval {
        Interval::new(lower, upper).unwrap()
    }

    fn export_status(certificate: &Certificate) -> (i32, Vec<f64>) {
        let n = certificate.candidate.len();
        let mut solution_lower = vec![99.0; n];
        let mut solution_upper = vec![99.0; n];
        let mut krawczyk_lower = vec![99.0; n];
        let mut krawczyk_upper = vec![99.0; n];
        let mut center = vec![99.0; n];
        let mut residual_lower = vec![99.0; n];
        let mut residual_upper = vec![99.0; n];
        let mut preconditioner = vec![99.0; n * n];
        let mut contraction_upper = 99.0;
        let mut lower_margins = vec![99.0; n];
        let mut upper_margins = vec![99.0; n];
        let mut iterations = 99;
        let status = match write_certificate(
            certificate,
            solution_lower.as_mut_ptr(),
            solution_upper.as_mut_ptr(),
            krawczyk_lower.as_mut_ptr(),
            krawczyk_upper.as_mut_ptr(),
            center.as_mut_ptr(),
            residual_lower.as_mut_ptr(),
            residual_upper.as_mut_ptr(),
            preconditioner.as_mut_ptr(),
            &mut contraction_upper,
            lower_margins.as_mut_ptr(),
            upper_margins.as_mut_ptr(),
            &mut iterations,
        ) {
            Ok(()) => STATUS_OK,
            Err(status) => status,
        };
        (status, solution_lower)
    }

    #[test]
    fn c_abi_length_and_panic_guards_are_closed() {
        assert_eq!(rei_source_bound_abi_version(), 4);
        assert_eq!(rei_mpfr_precision_bits(), 256);
        assert_eq!(rei_pointer_width_bits(), 64);
        assert_eq!(rei_limb_bits(), 64);
        assert_eq!(rei_mpfr_raw_size(), 32);
        assert_eq!(rei_mpfr_raw_align(), 8);
        assert_eq!(rei_validate_lengths_mpfr256(2, 4, 2), STATUS_OK);
        assert_eq!(
            rei_validate_lengths_mpfr256(2, 3, 2),
            STATUS_LENGTH_MISMATCH
        );
        assert_eq!(
            rei_validate_lengths_mpfr256(0, 0, 0),
            STATUS_INVALID_DIMENSION
        );
        let mut lower = 123.0;
        let mut upper = 456.0;
        assert_eq!(
            unsafe { rei_interval_divide_mpfr256(1.0, 2.0, -1.0, 1.0, &mut lower, &mut upper) },
            STATUS_ZERO_DIVISOR_INTERVAL
        );
        assert_eq!((lower, upper), (123.0, 456.0));
        assert_eq!(
            unsafe { rei_interval_divide_mpfr256(1.0, 2.0, 3.0, 4.0, &mut lower, &mut lower) },
            STATUS_ALIASED_OUTPUT
        );
        assert_eq!(
            ffi_guard(|| -> Result<(), i32> { panic!("native guard fixture") }),
            STATUS_NATIVE_PANIC
        );
    }

    #[test]
    fn point_linear_primitive_recovers_locked_solution() {
        let a = vec![p(2.0), p(1.0), p(1.0), p(3.0)];
        let b = vec![p(1.0), p(2.0)];
        let x = vec![i(0.19, 0.21), i(0.59, 0.61)];
        let certificate = certify_linear(2, &a, &b, &x).unwrap();
        assert!((certificate.center[0].to_f64(RNDN) - 0.2).abs() <= f64::EPSILON);
        assert!((certificate.center[1].to_f64(RNDN) - 0.6).abs() <= f64::EPSILON);
        assert!(certificate.strict);

        let coupled_a = vec![p(1.0), i(-0.25, 0.25), p(0.0), p(1.0)];
        let coupled_b = vec![p(0.0), i(-1.0, 1.0)];
        let automatic = certify_linear_with_candidate(2, &coupled_a, &coupled_b, None).unwrap();
        assert!(automatic.strict);
        assert!(automatic.candidate[0].endpoints().0 < -0.5);
        assert!(automatic.candidate[0].endpoints().1 > 0.5);
    }

    #[test]
    fn research_tangent_replays_supplied_candidate_and_exact_image() {
        let a = vec![p(2.0), p(1.0), p(1.0), p(3.0)];
        let z = vec![p(0.2), p(0.6)];
        let da = vec![p(1.0), p(0.0), p(0.0), p(-1.0)];
        let db = vec![p(1.0), p(-1.0)];
        let x = vec![i(0.55, 0.57), i(-0.33, -0.31)];
        let certificate = certify_tangent(2, &a, &z, &da, &db, &x).unwrap();
        assert!((certificate.center[0].to_f64(RNDN) - 14.0 / 25.0).abs() <= 2.0 * f64::EPSILON);
        assert!((certificate.center[1].to_f64(RNDN) + 8.0 / 25.0).abs() <= 2.0 * f64::EPSILON);
    }

    #[test]
    fn locked_corner_tangent_is_contained() {
        let a = vec![i(1.5, 2.5), p(-1.0), p(-1.0), p(2.0)];
        let z = vec![i(0.75, 1.5), p(0.0)];
        let da = vec![p(1.0), p(0.0), p(0.0), p(0.0)];
        let db = vec![p(0.0), p(0.0)];
        let x = vec![i(-2.25, 0.75), i(-1.125, 0.375)];
        let certificate = certify_tangent(2, &a, &z, &da, &db, &x).unwrap();
        assert_eq!(
            certificate.krawczyk[0].endpoints(),
            (-1.7500000000000002, 0.25000000000000006)
        );
        assert_eq!(
            certificate.krawczyk[1].endpoints(),
            (-0.8750000000000001, 0.12500000000000003)
        );
    }

    #[test]
    fn missing_delta_a_is_not_interpreted_as_zero() {
        let z = vec![p(0.2), p(0.6)];
        let da = vec![p(1.0), p(0.0), p(0.0), p(-1.0)];
        let db = vec![p(1.0), p(-1.0)];
        let rhs = tangent_rhs(2, &z, &da, &db).unwrap();
        let (first_lower, first_upper) = rhs[0].endpoints();
        let (second_lower, second_upper) = rhs[1].endpoints();
        assert!(
            (first_lower - 0.8).abs() <= f64::EPSILON && (first_upper - 0.8).abs() <= f64::EPSILON
        );
        assert!(
            (second_lower + 0.4).abs() <= f64::EPSILON
                && (second_upper + 0.4).abs() <= f64::EPSILON
        );
        assert!(!rhs[0].contains(1.0));
    }

    #[test]
    fn locked_three_by_three_research_fixture_is_exactly_enclosed() {
        let a = three_by_three_matrix();
        let b = vec![i(-1.25, -0.75), p(0.0), p(0.0)];
        let x = vec![i(-1.125, -0.125), i(-0.5, 0.0), i(-0.25, 0.0)];
        let certificate = certify_linear(3, &a, &b, &x).unwrap();
        assert!(certificate.strict);
        assert_eq!(
            certificate.krawczyk[0].endpoints(),
            (-245.0 / 256.0, -75.0 / 256.0)
        );
        assert_eq!(
            certificate.krawczyk[1].endpoints(),
            (-49.0 / 128.0, -15.0 / 128.0)
        );
        assert_eq!(
            certificate.krawczyk[2].endpoints(),
            (-49.0 / 256.0, -15.0 / 256.0)
        );
    }

    #[test]
    fn three_by_three_interval_tangent_is_contained() {
        let a = three_by_three_matrix();
        let z = vec![p(1.0), p(0.0), p(0.0)];
        let da = vec![p(0.0); 9];
        let db = vec![i(-1.25, -0.75), p(0.0), p(0.0)];
        let x = vec![i(-1.125, -0.125), i(-0.5, 0.0), i(-0.25, 0.0)];
        assert!(certify_tangent(3, &a, &z, &da, &db, &x).unwrap().strict);
    }

    #[test]
    fn mixed_rhs_uses_all_three_products() {
        let rhs = mixed_fixture_rhs(0).unwrap();
        assert!(rhs[0].contains(-7.0));
        assert!(rhs[1].contains(3.0));
    }

    #[test]
    fn mixed_vf_zero_term_mutations_are_distinct() {
        let complete = mixed_fixture_rhs(0).unwrap();
        let no_avf = mixed_fixture_rhs(1).unwrap();
        let no_av = mixed_fixture_rhs(2).unwrap();
        let no_af = mixed_fixture_rhs(3).unwrap();
        assert_ne!(complete, no_avf);
        assert_ne!(complete, no_av);
        assert_ne!(complete, no_af);
    }

    #[test]
    fn non_strict_candidate_is_rejected() {
        let a = vec![p(2.0), p(1.0), p(1.0), p(3.0)];
        let b = vec![p(1.0), p(2.0)];
        let x = vec![p(0.2), p(0.6)];
        assert_eq!(
            certify_linear(2, &a, &b, &x).unwrap_err(),
            STATUS_NO_STRICT_SELF_INCLUSION
        );

        let one_third = 1.0 / 3.0;
        let representationally_narrow = vec![
            i(one_third, one_third.next_up()),
            i(-f64::from_bits(1), f64::from_bits(1)),
        ];
        let diagonal = vec![p(3.0), p(0.0), p(0.0), p(1.0)];
        let right_hand_side = vec![p(1.0), p(0.0)];
        let internal = certify_linear(2, &diagonal, &right_hand_side, &representationally_narrow)
            .expect("MPFR strict fixture");
        let (status, untouched_output) = export_status(&internal);
        assert_eq!(status, STATUS_NO_STRICT_SELF_INCLUSION);
        assert_eq!(untouched_output, vec![99.0, 99.0]);

        let almost_unit_contraction = vec![i(2.0_f64.powi(-200), 1.0), p(0.0), p(0.0), p(1.0)];
        let zero_rhs = vec![p(0.0), p(0.0)];
        let broad_candidate = vec![i(-1.0, 1.0), i(-1.0, 1.0)];
        let internal = certify_linear(2, &almost_unit_contraction, &zero_rhs, &broad_candidate)
            .expect("MPFR rho is strictly below one");
        let (status, untouched_output) = export_status(&internal);
        assert_eq!(status, STATUS_NO_STRICT_SELF_INCLUSION);
        assert_eq!(untouched_output, vec![99.0, 99.0]);
    }

    #[test]
    fn zero_divisor_is_rejected_before_division() {
        assert_eq!(
            i(1.0, 2.0).div(&i(-1.0, 1.0)).unwrap_err(),
            STATUS_ZERO_DIVISOR_INTERVAL
        );
    }

    fn three_by_three_matrix() -> Vec<Interval> {
        vec![
            i(1.75, 2.25),
            p(-1.0),
            p(0.0),
            p(-1.0),
            p(3.0),
            p(-1.0),
            p(0.0),
            p(-1.0),
            p(2.0),
        ]
    }

    fn mixed_fixture_rhs(mutation: usize) -> Result<Vec<Interval>, i32> {
        let bvf = vec![p(3.0), p(8.0)];
        let avf = if mutation == 1 {
            vec![p(0.0); 4]
        } else {
            vec![p(1.0), p(0.0), p(0.0), p(1.0)]
        };
        let z = vec![p(1.0), p(2.0)];
        let av = if mutation == 2 {
            vec![p(0.0); 4]
        } else {
            vec![p(2.0), p(0.0), p(0.0), p(1.0)]
        };
        let zf = vec![p(3.0), p(1.0)];
        let af = if mutation == 3 {
            vec![p(0.0); 4]
        } else {
            vec![p(1.0), p(0.0), p(0.0), p(2.0)]
        };
        let zv = vec![p(3.0), p(1.0)];
        mixed_rhs(2, &bvf, &avf, &z, &av, &zf, &af, &zv)
    }
}
