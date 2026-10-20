#[inline]
pub fn centered_weights(t: f64) -> [f64; 4] {
    [-t*(t-1.0)*(t-2.0)/6.0, (t+1.0)*(t-1.0)*(t-2.0)/2.0,
     -(t+1.0)*t*(t-2.0)/2.0, (t+1.0)*t*(t-1.0)/6.0]
}

#[inline]
pub fn weighted_channels<const N: usize>(a: &[f64; N], b: &[f64; N], c: &[f64; N], d: &[f64; N], w: [f64;4]) -> [f64; N] {
    // Preserve operation order: no fast-math, reassociation, or manual FMA.
    std::array::from_fn(|j| ((w[0]*a[j] + w[1]*b[j]) + w[2]*c[j]) + w[3]*d[j])
}
