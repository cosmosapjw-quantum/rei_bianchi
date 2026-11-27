//! B1 FFI boundary. The scientific operator is the unmodified bass module.
//! The C caller owns all buffers and supplies non-overlapping valid pointers.

#[path = "pol_collide.rs"]
mod pol_collide;

use std::panic::{catch_unwind, AssertUnwindSafe};
use std::slice;

#[no_mangle]
pub extern "C" fn b1_kernel_abi() -> u64 { 1 }

/// Return 0 on success, 1 for invalid dimensions/pointers, 2 for invalid x,
/// 3 for nonfinite input/output, or 4 for a caught Rust panic.
#[no_mangle]
pub unsafe extern "C" fn b1_collide_modeb(
    ehat_ptr: *const f64,
    w_ptr: *const f64,
    j_ptr: *const f64,
    n_ang: usize,
    n_energy: usize,
    x: f64,
    out_ptr: *mut f64,
) -> i32 {
    if n_ang == 0 || n_energy == 0 || ehat_ptr.is_null() || w_ptr.is_null()
        || j_ptr.is_null() || out_ptr.is_null() { return 1; }
    if !x.is_finite() || x < 0.0 { return 2; }
    let e_len = match n_ang.checked_mul(3) { Some(v) => v, None => return 1 };
    let j_len = match n_ang.checked_mul(n_energy).and_then(|v| v.checked_mul(9)) {
        Some(v) => v, None => return 1,
    };
    if j_len > (isize::MAX as usize) / std::mem::size_of::<f64>() { return 1; }
    let result = catch_unwind(AssertUnwindSafe(|| {
        let ehat = slice::from_raw_parts(ehat_ptr, e_len);
        let w = slice::from_raw_parts(w_ptr, n_ang);
        let j = slice::from_raw_parts(j_ptr, j_len);
        if !ehat.iter().chain(w.iter()).chain(j.iter()).all(|v| v.is_finite()) {
            return 3;
        }
        // Actual native scientific call; no alternative formula or fallback.
        let got = pol_collide::collide_modeb(ehat, w, j, n_energy, x);
        if !got.iter().all(|v| v.is_finite()) { return 3; }
        out_ptr.copy_from_nonoverlapping(got.as_ptr(), j_len);
        0
    }));
    result.unwrap_or(4)
}

/// Recompute the existing kernel's rank-9 moment eigenvalues on caller grid.
#[no_mangle]
pub unsafe extern "C" fn b1_kcal_eigenvalues(
    ehat_ptr: *const f64, w_ptr: *const f64, n_ang: usize, out_ptr: *mut f64,
) -> i32 {
    if n_ang == 0 || ehat_ptr.is_null() || w_ptr.is_null() || out_ptr.is_null() {
        return 1;
    }
    let e_len = match n_ang.checked_mul(3) { Some(v) => v, None => return 1 };
    if e_len > (isize::MAX as usize) / std::mem::size_of::<f64>() { return 1; }
    catch_unwind(AssertUnwindSafe(|| {
        let ehat = slice::from_raw_parts(ehat_ptr, e_len);
        let w = slice::from_raw_parts(w_ptr, n_ang);
        if !ehat.iter().chain(w.iter()).all(|v| v.is_finite()) { return 3; }
        let got = pol_collide::kcal_eigenvalues(ehat, w);
        out_ptr.copy_from_nonoverlapping(got.as_ptr(), 3);
        0
    })).unwrap_or(4)
}
