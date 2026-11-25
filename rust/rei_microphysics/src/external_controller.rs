//! Step-size suggestion for externally owned full/half trials.
//! It never changes the REI acceptance criterion or energy budget.
use crate::ForwardError;
const MIN_STEP: f64 = 1e-10;
fn bad() -> ForwardError {
    ForwardError::InvalidInput("EXTERNAL_CONTROLLER_DOMAIN")
}
pub fn accepted_step(du: f64, err: f64, target: f64, max_du: f64) -> Result<f64, ForwardError> {
    if ![du, err, target, max_du].iter().all(|x| x.is_finite())
        || du <= 0.
        || err < 0.
        || target <= 0.
        || err >= target
        || max_du < MIN_STEP
        || du > max_du
    {
        return Err(bad());
    }
    let factor = if err == 0. {
        1.25
    } else {
        (0.9 * (0.5 * target / err).cbrt()).clamp(0.5, 1.25)
    };
    Ok((du * factor).clamp(MIN_STEP, max_du))
}
pub fn rejected_step(du: f64) -> Result<f64, ForwardError> {
    if !du.is_finite() || du / 2. < MIN_STEP {
        return Err(bad());
    }
    Ok(du / 2.)
}
