//! Outward-rounded bounds for the sparse local bilinear Taylor representation.
//!
//! This crate deliberately uses only the Rust standard library.  It is an
//! optional BASS-style hot-loop backend: the Python implementation remains the
//! scientific oracle and every exported operation is differential-tested.

use std::slice;

#[no_mangle]
pub unsafe extern "C" fn sparse_local_bounds(
    n_coordinate: usize,
    n_node: usize,
    n_global: usize,
    center_ptr: *const f64,
    local_v_ptr: *const f64,
    local_f_ptr: *const f64,
    mixed_ptr: *const f64,
    global_ptr: *const f64,
    remainder_lo_ptr: *const f64,
    remainder_hi_ptr: *const f64,
    out_lo_ptr: *mut f64,
    out_hi_ptr: *mut f64,
) -> i32 {
    if n_coordinate == 0 || n_node == 0 {
        return 1;
    }
    let size = match n_coordinate.checked_mul(n_node) {
        Some(value) => value,
        None => return 2,
    };
    if center_ptr.is_null()
        || local_v_ptr.is_null()
        || local_f_ptr.is_null()
        || mixed_ptr.is_null()
        || remainder_lo_ptr.is_null()
        || remainder_hi_ptr.is_null()
        || out_lo_ptr.is_null()
        || out_hi_ptr.is_null()
        || (n_global > 0 && global_ptr.is_null())
    {
        return 3;
    }

    // SAFETY: pointer validity and lengths are established by the Python FFI
    // wrapper, which passes contiguous float64 arrays with the locked shapes.
    let center = unsafe { slice::from_raw_parts(center_ptr, size) };
    let local_v = unsafe { slice::from_raw_parts(local_v_ptr, size) };
    let local_f = unsafe { slice::from_raw_parts(local_f_ptr, size) };
    let mixed = unsafe { slice::from_raw_parts(mixed_ptr, size) };
    let global = if n_global == 0 {
        &[][..]
    } else {
        unsafe { slice::from_raw_parts(global_ptr, n_global * size) }
    };
    let remainder_lo = unsafe { slice::from_raw_parts(remainder_lo_ptr, size) };
    let remainder_hi = unsafe { slice::from_raw_parts(remainder_hi_ptr, size) };
    let out_lo = unsafe { slice::from_raw_parts_mut(out_lo_ptr, size) };
    let out_hi = unsafe { slice::from_raw_parts_mut(out_hi_ptr, size) };

    for index in 0..size {
        let c = center[index];
        let av = local_v[index];
        let af = local_f[index];
        let q = mixed[index];
        let corners = [
            ((c - av) - af) + q,
            ((c - av) + af) - q,
            ((c + av) - af) - q,
            ((c + av) + af) + q,
        ];
        let mut lower = corners[0];
        let mut upper = corners[0];
        for value in corners.iter().skip(1) {
            lower = lower.min(*value);
            upper = upper.max(*value);
        }
        let mut radius = 0.0_f64;
        for mode in 0..n_global {
            radius += global[mode * size + index].abs();
        }
        lower = ((lower - radius) + remainder_lo[index]).next_down();
        upper = ((upper + radius) + remainder_hi[index]).next_up();
        if !lower.is_finite() || !upper.is_finite() || lower > upper {
            return 4;
        }
        out_lo[index] = lower;
        out_hi[index] = upper;
    }
    0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exact_bilinear_corner_range() {
        let center = [0.0];
        let av = [1.0];
        let af = [1.0];
        let mixed = [1.0];
        let rem = [0.0];
        let mut lo = [0.0];
        let mut hi = [0.0];
        let code = unsafe {
            sparse_local_bounds(
                1,
                1,
                0,
                center.as_ptr(),
                av.as_ptr(),
                af.as_ptr(),
                mixed.as_ptr(),
                std::ptr::null(),
                rem.as_ptr(),
                rem.as_ptr(),
                lo.as_mut_ptr(),
                hi.as_mut_ptr(),
            )
        };
        assert_eq!(code, 0);
        assert!(lo[0] < -1.0 && lo[0].next_up() == -1.0);
        assert!(hi[0] > 3.0 && hi[0].next_down() == 3.0);
    }
}
