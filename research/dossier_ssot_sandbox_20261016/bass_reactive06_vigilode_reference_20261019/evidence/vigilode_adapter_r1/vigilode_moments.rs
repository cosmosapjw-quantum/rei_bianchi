//! Recovery revision R1 of the BR06 scalar VigilODE moment adapter.
//!
//! The pre-interruption adapter bytes were not recovered. This source is an
//! explicit reconstruction, not a byte-identical restoration and not an
//! inherited verification result. Upstream kernel files remain unmodified.
//!
//! With chronological birth fraction u and age fraction x = 1-u,
//! J[j,k](tau) = integral_0^1 exp(-tau*x) x^j (1-x)^k dx.
//! These scalar intervals do not enclose a variable-geometry transfer operator.

use rodas5p_core::CoreError;
use rodas5p_core::damped_moments::compute_normalized_damped_moment;
use rodas5p_core::directed::{Interval, add_down, exp_interval, mul_down, sub_up};
use std::fmt;

/// Coarse attempted work. Counts remain available after typed refusal.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct MomentWork {
    pub validation_attempts: u64,
    pub kernel_calls: u64,
    pub exponential_calls: u64,
    pub dyadic_steps: u64,
    pub interval_operations: u64,
    pub width_checks: u64,
}

#[derive(Debug)]
pub enum MomentRefusal {
    InvalidInput(&'static str),
    Kernel(CoreError),
    Arithmetic(CoreError),
    UnsupportedMoment {
        j: usize,
        k: usize,
    },
    WidthExceeded {
        j: usize,
        k: usize,
        width_upper: f64,
        width_limit: f64,
    },
}

impl fmt::Display for MomentRefusal {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidInput(message) => write!(f, "invalid moment input: {message}"),
            Self::Kernel(error) => write!(f, "VigilODE moment kernel refused: {error}"),
            Self::Arithmetic(error) => write!(f, "moment interval arithmetic refused: {error}"),
            Self::UnsupportedMoment { j, k } => write!(f, "unsupported moment J[{j},{k}]"),
            Self::WidthExceeded {
                j,
                k,
                width_upper,
                width_limit,
            } => write!(
                f,
                "moment J[{j},{k}] width {width_upper:e} exceeds limit {width_limit:e}"
            ),
        }
    }
}

impl std::error::Error for MomentRefusal {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Self::Kernel(error) | Self::Arithmetic(error) => Some(error),
            _ => None,
        }
    }
}

#[derive(Clone, Debug)]
pub struct PositiveMomentTable {
    pub tau: f64,
    pub dyadic_levels: usize,
    moments: [[Interval; 3]; 3],
}

impl PositiveMomentTable {
    /// Returns a supported moment. Panics if j or k exceeds 2.
    pub fn get(&self, j: usize, k: usize) -> Interval {
        assert!(j <= 2 && k <= 2, "moment order must be at most two");
        self.moments[j][k]
    }

    pub fn try_get(&self, j: usize, k: usize) -> Result<Interval, MomentRefusal> {
        if j > 2 || k > 2 {
            return Err(MomentRefusal::UnsupportedMoment { j, k });
        }
        Ok(self.moments[j][k])
    }

    /// Integral in normalized time for j(u)=j_left*(1-u)+j_right*u.
    /// Multiply by the physical duration outside this scalar helper.
    pub fn linear_source_mass(&self, j_left: f64, j_right: f64) -> Result<Interval, MomentRefusal> {
        if !j_left.is_finite() || j_left < 0.0 || !j_right.is_finite() || j_right < 0.0 {
            return Err(MomentRefusal::InvalidInput(
                "source endpoints must be finite and nonnegative",
            ));
        }
        let left = self
            .get(1, 0)
            .scale(j_left)
            .map_err(MomentRefusal::Arithmetic)?;
        let right = self
            .get(0, 1)
            .scale(j_right)
            .map_err(MomentRefusal::Arithmetic)?;
        nonnegative(left.add(right).map_err(MomentRefusal::Arithmetic)?)
    }
}

pub fn linear_source_mass(
    table: &PositiveMomentTable,
    j_left: f64,
    j_right: f64,
) -> Result<Interval, MomentRefusal> {
    table.linear_source_mass(j_left, j_right)
}

fn nonnegative(value: Interval) -> Result<Interval, MomentRefusal> {
    // Positivity is known from the integral, so intersecting with [0,infinity)
    // preserves an enclosure. A wholly negative interval is a refusal.
    if value.hi < 0.0 {
        return Err(MomentRefusal::InvalidInput(
            "kernel returned an interval disjoint from nonnegative moments",
        ));
    }
    Interval::new(value.lo.max(0.0), value.hi).map_err(MomentRefusal::Arithmetic)
}

fn add_positive(
    left: Interval,
    right: Interval,
    work: &mut MomentWork,
) -> Result<Interval, MomentRefusal> {
    work.interval_operations = work.interval_operations.saturating_add(1);
    nonnegative(left.add(right).map_err(MomentRefusal::Arithmetic)?)
}

fn multiply_positive(
    left: Interval,
    right: Interval,
    work: &mut MomentWork,
) -> Result<Interval, MomentRefusal> {
    work.interval_operations = work.interval_operations.saturating_add(1);
    nonnegative(left.mul(right).map_err(MomentRefusal::Arithmetic)?)
}

fn small_binomial(n: usize, r: usize) -> f64 {
    if n == 2 && r == 1 { 2.0 } else { 1.0 }
}

/// Builds all J[j,k], 0<=j,k<=2, using the unchanged small-tau VigilODE
/// kernel and positive dyadic composition. No birth cohort is created,
/// discarded or merged by this scalar validation helper.
///
/// The exact identity used at each doubling is
/// J[j,k](2z) = 2^(-j-k-1) (sum_l C(k,l) J[j,l](z)
///                         + exp(-z) sum_r C(j,r) J[r,k](z)).
///
/// Every final moment must satisfy
/// `width <= absolute_width + relative_width * lower_endpoint`.
/// The permitted width is rounded down,
/// making this gate conservative with respect to the exact unknown moment.
pub fn positive_moment_table(
    tau: f64,
    relative_width: f64,
    absolute_width: f64,
    work: &mut MomentWork,
) -> Result<PositiveMomentTable, MomentRefusal> {
    work.validation_attempts = work.validation_attempts.saturating_add(1);
    if !tau.is_finite() || tau < 0.0 {
        return Err(MomentRefusal::InvalidInput(
            "optical depth must be finite and nonnegative",
        ));
    }
    if !relative_width.is_finite()
        || relative_width < 0.0
        || !absolute_width.is_finite()
        || absolute_width < 0.0
    {
        return Err(MomentRefusal::InvalidInput(
            "width tolerances must be finite and nonnegative",
        ));
    }

    let mut reduced = tau;
    let mut levels = 0;
    while reduced > 1.0 {
        reduced *= 0.5;
        levels += 1;
    }
    let zero = Interval { lo: 0.0, hi: 0.0 };
    let mut moments = [[zero; 3]; 3];
    for (j, row) in moments.iter_mut().enumerate() {
        for (k, value) in row.iter_mut().enumerate() {
            work.kernel_calls = work.kernel_calls.saturating_add(1);
            *value = nonnegative(
                compute_normalized_damped_moment(reduced, 1.0, j, k)
                    .map_err(MomentRefusal::Kernel)?,
            )?;
        }
    }

    let mut z = reduced;
    for _ in 0..levels {
        work.dyadic_steps = work.dyadic_steps.saturating_add(1);
        work.exponential_calls = work.exponential_calls.saturating_add(1);
        let damping = nonnegative(exp_interval(-z).map_err(MomentRefusal::Arithmetic)?)?;
        let previous = moments;
        for (j, row) in moments.iter_mut().enumerate() {
            for (k, value) in row.iter_mut().enumerate() {
                let mut first = zero;
                for (l, item) in previous[j].iter().take(k + 1).enumerate() {
                    let coefficient = small_binomial(k, l);
                    let term = multiply_positive(
                        *item,
                        Interval {
                            lo: coefficient,
                            hi: coefficient,
                        },
                        work,
                    )?;
                    first = add_positive(first, term, work)?;
                }
                let mut second = zero;
                for (r, old_row) in previous.iter().take(j + 1).enumerate() {
                    let coefficient = small_binomial(j, r);
                    let term = multiply_positive(
                        old_row[k],
                        Interval {
                            lo: coefficient,
                            hi: coefficient,
                        },
                        work,
                    )?;
                    second = add_positive(second, term, work)?;
                }
                second = multiply_positive(damping, second, work)?;
                let sum = add_positive(first, second, work)?;
                let factor = 0.5_f64.powi((j + k + 1) as i32);
                *value = multiply_positive(
                    sum,
                    Interval {
                        lo: factor,
                        hi: factor,
                    },
                    work,
                )?;
            }
        }
        z *= 2.0;
    }

    for (j, row) in moments.iter().enumerate() {
        for (k, value) in row.iter().enumerate() {
            work.width_checks = work.width_checks.saturating_add(1);
            let width_upper = sub_up(value.hi, value.lo).map_err(MomentRefusal::Arithmetic)?;
            let relative_limit = mul_down(relative_width, value.lo)
                .map_err(MomentRefusal::Arithmetic)?
                .max(0.0);
            let width_limit = add_down(absolute_width, relative_limit)
                .map_err(MomentRefusal::Arithmetic)?
                .max(0.0);
            if width_upper > width_limit {
                return Err(MomentRefusal::WidthExceeded {
                    j,
                    k,
                    width_upper,
                    width_limit,
                });
            }
        }
    }
    Ok(PositiveMomentTable {
        tau,
        dyadic_levels: levels,
        moments,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn scalar_phi_thin_thick_and_zero_are_contained() {
        for tau in [
            0.0, 1e-12, 1e-8, 0.03, 0.5, 1.0, 1.000001, 2.0, 10.0, 32.0, 93.0, 156.0, 1e3, 1e12,
        ] {
            let mut work = MomentWork::default();
            let table = positive_moment_table(tau, 1e-10, 0.0, &mut work).unwrap();
            let phi = if tau == 0.0 {
                1.0
            } else {
                -(-tau).exp_m1() / tau
            };
            assert!(table.get(0, 0).contains(phi), "tau={tau}");
            assert_eq!(work.kernel_calls, 9);
            assert_eq!(work.width_checks, 9);
            for j in 0..=2 {
                for k in 0..=2 {
                    assert!(table.get(j, k).lo > 0.0);
                }
            }
        }
    }

    #[test]
    fn invalid_inputs_width_refusal_and_work_are_explicit() {
        for tau in [-1.0, f64::NAN, f64::INFINITY] {
            let mut work = MomentWork::default();
            assert!(matches!(
                positive_moment_table(tau, 1e-10, 0.0, &mut work),
                Err(MomentRefusal::InvalidInput(_))
            ));
            assert_eq!(work.validation_attempts, 1);
            assert_eq!(work.kernel_calls, 0);
        }
        let mut work = MomentWork::default();
        assert!(matches!(
            positive_moment_table(32.0, 0.0, 0.0, &mut work),
            Err(MomentRefusal::WidthExceeded { .. })
        ));
        assert!(work.width_checks > 0);
        assert!(work.dyadic_steps > 0);
    }

    #[test]
    fn chronological_source_mapping_and_zero_source_are_preserved() {
        let table = positive_moment_table(10.0, 1e-10, 0.0, &mut MomentWork::default()).unwrap();
        assert_eq!(table.linear_source_mass(1.0, 0.0).unwrap(), table.get(1, 0));
        assert_eq!(table.linear_source_mass(0.0, 1.0).unwrap(), table.get(0, 1));
        assert_eq!(
            table.linear_source_mass(0.0, 0.0).unwrap(),
            Interval { lo: 0.0, hi: 0.0 }
        );
        assert!(matches!(
            table.linear_source_mass(-1.0, 0.0),
            Err(MomentRefusal::InvalidInput(_))
        ));
        assert!(matches!(
            table.try_get(3, 0),
            Err(MomentRefusal::UnsupportedMoment { .. })
        ));
    }
}
