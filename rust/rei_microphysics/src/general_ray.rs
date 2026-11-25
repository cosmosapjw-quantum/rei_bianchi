//! General Bianchi-I canonical momentum handoff, independent of the LRS driver.
//! C is a physical coframe, g=C^T C, with common coordinate labels.
use crate::ForwardError;
#[derive(Clone, Copy, Debug)]
pub struct CanonicalRay {
    pub energy_scale: f64,
    pub direction: [f64; 3],
    pub jacobian: f64,
}
fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a.iter().zip(b).map(|(x, y)| x * y).sum()
}
fn cross(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
fn col(a: [[f64; 3]; 3], i: usize) -> [f64; 3] {
    [a[0][i], a[1][i], a[2][i]]
}
fn det(a: [[f64; 3]; 3]) -> f64 {
    dot(a[0], cross(a[1], a[2]))
}
pub fn canonical_ray(
    c0: [[f64; 3]; 3],
    c1: [[f64; 3]; 3],
    n: [f64; 3],
) -> Result<CanonicalRay, ForwardError> {
    let bad = || ForwardError::InvalidInput("GENERAL_RAY_DOMAIN");
    if !c0
        .iter()
        .flatten()
        .chain(c1.iter().flatten())
        .chain(n.iter())
        .all(|x| x.is_finite())
        || (dot(n, n) - 1.).abs() > 1e-10
    {
        return Err(bad());
    }
    let d0 = det(c0);
    let d1 = det(c1);
    if d0 <= 0. || d1 <= 0. || !d0.is_finite() || !d1.is_finite() {
        return Err(bad());
    }
    let q: [f64; 3] = std::array::from_fn(|i| dot(col(c0, i), n));
    let c = [col(c1, 0), col(c1, 1), col(c1, 2)];
    let x = cross(c[1], c[2]);
    let y = cross(c[2], c[0]);
    let z = cross(c[0], c[1]);
    let p = std::array::from_fn(|i| (x[i] * q[0] + y[i] * q[1] + z[i] * q[2]) / d1);
    let e = dot(p, p).sqrt();
    let j = (d0 / d1) / e.powi(3);
    if e <= 0. || j <= 0. || !e.is_finite() || !j.is_finite() {
        return Err(bad());
    }
    Ok(CanonicalRay {
        energy_scale: e,
        direction: p.map(|v| v / e),
        jacobian: j,
    })
}
