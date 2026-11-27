//! Exact-state packed HE29 Jacobian action. Foreign callbacks run only on the
//! sequential caller thread; optional Rayon workers write independent photon
//! rows after the physical Jacobian payload is complete and checked.

use rayon::prelude::*;
use rayon::{ThreadPool, ThreadPoolBuilder};

const GAS: usize = 4;
const LEDGERS: usize = 19;
const PHOTON_PACK_ROWS: usize = 12;
const LEDGER_PACK: [usize; 7] = [2, 3, 4, 5, 6, 7, 10];

#[derive(Clone, Copy, Debug, Default)]
pub(super) struct PackedCounts {
    pub prepare_calls: u64,
    pub prepare_successes: u64,
    pub cache_hits: u64,
    pub jvp_attempts: u64,
    pub jvp_completed: u64,
}

pub(super) struct PackedWork {
    n: usize,
    k: usize,
    scale: Vec<f64>,
    dt: f64,
    gas: Vec<f64>,
    photon: Vec<f64>,
    direction: Vec<f64>,
    key_state: Vec<u64>,
    key_u: Option<u64>,
    first_error: Option<String>,
    threads: usize,
    pool: Option<ThreadPool>,
    counts: PackedCounts,
}

fn buffer<T: Clone>(len: usize, value: T) -> Result<Vec<T>, String> {
    let mut out = Vec::new();
    out.try_reserve_exact(len).map_err(|_| "HE29_PACKED_ALLOCATION".to_string())?;
    out.resize(len, value);
    Ok(out)
}

impl PackedWork {
    pub fn new(n: usize, scale: &[f64], dt: f64, threads: usize) -> Result<Self, String> {
        if n <= GAS + LEDGERS || scale.len() != n {
            return Err("HE29_PACKED_DIMENSION_REQUIRES_N_EQ_K_PLUS_23_K_POSITIVE".into());
        }
        if !dt.is_finite() || dt <= 0.0 || !scale.iter().all(|s| s.is_finite() && *s > 0.0) {
            return Err("HE29_PACKED_SCALE_OR_DT".into());
        }
        if !matches!(threads, 1 | 2 | 4) {
            return Err("HE29_PACKED_THREADS_MUST_BE_1_2_OR_4".into());
        }
        let k = n - GAS - LEDGERS;
        let max_len = isize::MAX as usize / std::mem::size_of::<f64>();
        let ng = n.checked_mul(GAS).filter(|x| *x <= max_len)
            .ok_or("HE29_PACKED_SIZE_OVERFLOW")?;
        let np = k.checked_mul(PHOTON_PACK_ROWS).filter(|x| *x <= max_len)
            .ok_or("HE29_PACKED_SIZE_OVERFLOW")?;
        ng.checked_add(np).and_then(|v| v.checked_add(n.checked_mul(3)?))
            .and_then(|v| v.checked_mul(8))
            .ok_or("HE29_PACKED_SIZE_OVERFLOW")?;
        let mut scale_copy = buffer(n, 0.0)?;
        scale_copy.copy_from_slice(scale);
        let pool = if threads == 1 { None } else {
            Some(ThreadPoolBuilder::new().num_threads(threads).build()
                .map_err(|e| format!("HE29_PACKED_THREAD_POOL: {e}"))?)
        };
        Ok(Self {
            n, k, scale: scale_copy, dt,
            gas: buffer(ng, f64::NAN)?, photon: buffer(np, f64::NAN)?,
            direction: buffer(n, 0.0)?, key_state: buffer(n, 0)?, key_u: None,
            first_error: None, threads, pool, counts: PackedCounts::default(),
        })
    }

    pub fn counts(&self) -> PackedCounts { self.counts }
    pub fn packed_bytes(&self) -> usize { (self.gas.len() + self.photon.len()) * 8 }
    pub fn workspace_bytes(&self) -> usize {
        // Payload plus scale, direction and exact state key. Thread-pool memory
        // and allocator metadata are not included; this is not an RSS bound.
        self.packed_bytes() + 3 * self.n * 8
    }
    pub fn threads(&self) -> usize { self.threads }

    fn fail(&mut self, message: String) -> String {
        self.key_u = None;
        if self.first_error.is_none() { self.first_error = Some(message); }
        self.first_error.as_ref().unwrap().clone()
    }

    pub fn apply<F>(&mut self, u: f64, z: &[f64], v: &[f64], out: &mut [f64],
                    mut prepare: F) -> Result<(), String>
    where F: FnMut(&mut [f64], &mut [f64]) -> Result<(), String> {
        if let Some(e) = self.first_error.as_ref() { return Err(e.clone()); }
        self.counts.jvp_attempts += 1;
        if !u.is_finite() || z.len() != self.n || v.len() != self.n || out.len() != self.n
            || !z.iter().all(|q| q.is_finite()) || !v.iter().all(|q| q.is_finite()) {
            return Err(self.fail("HE29_PACKED_JVP_INPUT".into()));
        }
        // The original callback computes physical direction before asking for
        // the Jacobian. Overflow must fail before any preparation callback.
        for j in 0..self.n {
            self.direction[j] = v[j] * self.scale[j];
            if !self.direction[j].is_finite() {
                return Err(self.fail("HE29_PACKED_DIRECTION_OVERFLOW".into()));
            }
        }
        let hit = self.key_u == Some(u.to_bits())
            && z.iter().zip(&self.key_state).all(|(q, bits)| q.to_bits() == *bits);
        if hit {
            self.counts.cache_hits += 1;
        } else {
            self.key_u = None;
            self.gas.fill(f64::NAN);
            self.photon.fill(f64::NAN);
            self.counts.prepare_calls += 1;
            if let Err(e) = prepare(&mut self.gas, &mut self.photon) {
                return Err(self.fail(e));
            }
            if !self.gas.iter().chain(&self.photon).all(|q| q.is_finite()) {
                return Err(self.fail("HE29_PACKED_NONFINITE_OR_UNWRITTEN_PAYLOAD".into()));
            }
            for (to, from) in self.key_state.iter_mut().zip(z) { *to = from.to_bits(); }
            self.key_u = Some(u.to_bits());
            self.counts.prepare_successes += 1;
        }
        let k = self.k;
        let gas = &self.gas;
        let photon = &self.photon;
        let direction = &self.direction;
        let scale = &self.scale;
        let dt = self.dt;
        let action = |row: usize| {
            // Ascending original CSR column order; no reassociated reduction
            // or explicit FMA. Scaling order matches (dt * J.dot(v*scale))/scale.
            (dt * physical_row_sum(row, k, gas, photon, direction)) / scale[row]
        };
        for (row, q) in out[..GAS].iter_mut().enumerate() { *q = action(row); }
        if let Some(pool) = &self.pool {
            pool.install(|| {
                out[GAS..GAS+k].par_iter_mut().enumerate()
                    .for_each(|(j, q)| *q = action(GAS+j));
            });
        } else {
            for (j, q) in out[GAS..GAS+k].iter_mut().enumerate() { *q = action(GAS+j); }
        }
        for (j, q) in out[GAS+k..].iter_mut().enumerate() { *q = action(GAS+k+j); }
        if !out.iter().all(|q| q.is_finite()) {
            return Err(self.fail("HE29_PACKED_JVP_OUTPUT_OVERFLOW".into()));
        }
        self.counts.jvp_completed += 1;
        Ok(())
    }
}

fn physical_row_sum(row: usize, k: usize, gas: &[f64], photon: &[f64], direction: &[f64]) -> f64 {
    let mut sum = 0.0;
    for col in 0..GAS {
        let a = gas[row * GAS + col];
        if a != 0.0 { sum += a * direction[col]; }
    }
    if row < GAS {
        for j in 0..k {
            let a = photon[row * k + j];
            if a != 0.0 { sum += a * direction[GAS+j]; }
        }
    } else if row < GAS + k {
        let j = row - GAS;
        let a = photon[4 * k + j];
        if a != 0.0 { sum += a * direction[GAS+j]; }
    } else if let Some(p) = LEDGER_PACK.iter().position(|l| *l == row - GAS - k) {
        for j in 0..k {
            let a = photon[(5+p) * k + j];
            if a != 0.0 { sum += a * direction[GAS+j]; }
        }
    }
    sum
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::Cell;

    fn arrays(k: usize) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
        let n = k + 23;
        let gas: Vec<_> = (0..n*4).map(|j| if j % 7 == 0 { 0.0 } else { (j as f64 - 17.0) / 32.0 }).collect();
        let photon: Vec<_> = (0..12*k).map(|j| if j % 5 == 0 { 0.0 } else { (13.0 - j as f64) / 64.0 }).collect();
        // Independent full matrix used only in this tiny test. Explicit global
        // row/column coordinates make missing or misplaced ledger rows visible.
        let mut dense = vec![0.0; n*n];
        for row in 0..n { dense[row*n..row*n+4].copy_from_slice(&gas[row*4..row*4+4]); }
        for j in 0..k {
            for row in 0..4 { dense[row*n+4+j] = photon[row*k+j]; }
            dense[(4+j)*n+4+j] = photon[4*k+j];
            for (p, ledger) in [2,3,4,5,6,7,10].iter().enumerate() {
                dense[(4+k+ledger)*n+4+j] = photon[(5+p)*k+j];
            }
        }
        (gas, photon, dense)
    }

    #[test]
    fn packed_matches_full_matrix_order_for_all_rows_and_threads() {
        let k = 17; let n = k+23;
        let (g,p,m) = arrays(k);
        let scale: Vec<_> = (0..n).map(|j| 2.0_f64.powi((j%7) as i32-3)).collect();
        let v: Vec<_> = (0..n).map(|j| (j as f64-11.0)/16.0).collect();
        let d: Vec<_> = v.iter().zip(&scale).map(|(v,s)| v*s).collect();
        let expected: Vec<_> = (0..n).map(|row| {
            let mut total=0.0;
            for col in 0..n { let a=m[row*n+col]; if a != 0.0 { total += a*d[col]; } }
            (0.125*total)/scale[row]
        }).collect();
        for threads in [1,2,4] {
            let mut w=PackedWork::new(n,&scale,0.125,threads).unwrap();
            let mut out=vec![f64::NAN;n];
            w.apply(0.0,&vec![0.0;n],&v,&mut out,|a,b| { a.copy_from_slice(&g);b.copy_from_slice(&p);Ok(()) }).unwrap();
            assert_eq!(out.iter().map(|q|q.to_bits()).collect::<Vec<_>>(),expected.iter().map(|q|q.to_bits()).collect::<Vec<_>>());
            assert_eq!(w.counts().prepare_calls,1); assert_eq!(w.counts().jvp_completed,1);
        }
    }

    #[test]
    fn exact_key_uses_u_and_every_state_bit_but_not_direction() {
        let n=26; let mut w=PackedWork::new(n,&vec![1.0;n],1.0,1).unwrap();
        let (g,p,_)=arrays(3); let calls=Cell::new(0);
        let mut prepare=|a:&mut[f64],b:&mut[f64]|{calls.set(calls.get()+1);a.copy_from_slice(&g);b.copy_from_slice(&p);Ok(())};
        let mut z=vec![0.0;n];let mut out=vec![0.0;n];
        w.apply(0.0,&z,&vec![1.0;n],&mut out,&mut prepare).unwrap();
        w.apply(0.0,&z,&vec![2.0;n],&mut out,&mut prepare).unwrap();
        assert_eq!(calls.get(),1); assert_eq!(w.counts().cache_hits,1);
        z[n-1]=f64::from_bits(1);
        w.apply(0.0,&z,&vec![1.0;n],&mut out,&mut prepare).unwrap();
        w.apply(-0.0,&z,&vec![1.0;n],&mut out,&mut prepare).unwrap();
        z[4]=f64::from_bits(1);
        w.apply(-0.0,&z,&vec![1.0;n],&mut out,&mut prepare).unwrap();
        assert_eq!(calls.get(),4);
    }

    #[test]
    fn preparation_failure_is_preserved_and_cache_cannot_revive() {
        let n=24;let mut w=PackedWork::new(n,&vec![1.0;n],1.0,1).unwrap();
        let mut out=vec![0.0;n];
        let e=w.apply(0.0,&vec![0.0;n],&vec![1.0;n],&mut out,|g,_|{g.fill(1.0);Err("first prepare failure".into())}).unwrap_err();
        assert_eq!(e,"first prepare failure"); assert!(w.key_u.is_none());
        let e2=w.apply(0.1,&vec![1.0;n],&vec![2.0;n],&mut out,|_,_|panic!("must not retry")).unwrap_err();
        assert_eq!(e,e2);assert_eq!(w.counts().prepare_calls,1);assert_eq!(w.counts().jvp_completed,0);
    }

    #[test]
    fn unwritten_payload_is_rejected() {
        let n=24;let mut w=PackedWork::new(n,&vec![1.0;n],1.0,1).unwrap();
        let e=w.apply(0.0,&vec![0.0;n],&vec![1.0;n],&mut vec![0.0;n],|g,_|{g.fill(0.0);Ok(())}).unwrap_err();
        assert_eq!(e,"HE29_PACKED_NONFINITE_OR_UNWRITTEN_PAYLOAD");assert!(w.key_u.is_none());
    }

    #[test]
    fn direction_overflow_fails_before_preparation() {
        let n=24;let mut w=PackedWork::new(n,&vec![2.0;n],1.0,1).unwrap();
        let e=w.apply(0.0,&vec![0.0;n],&vec![f64::MAX;n],&mut vec![0.0;n],|_,_|panic!("prepare must not run")).unwrap_err();
        assert_eq!(e,"HE29_PACKED_DIRECTION_OVERFLOW");assert_eq!(w.counts().prepare_calls,0);
    }

    #[test]
    fn final_scaling_overflow_is_reported() {
        let n=24;let mut w=PackedWork::new(n,&vec![1.0;n],f64::MAX,1).unwrap();
        let e=w.apply(0.0,&vec![0.0;n],&vec![1.0;n],&mut vec![0.0;n],|g,p|{g.fill(1.0);p.fill(0.0);Ok(())}).unwrap_err();
        assert_eq!(e,"HE29_PACKED_JVP_OUTPUT_OVERFLOW");assert_eq!(w.counts().jvp_completed,0);
    }

    #[test]
    fn invalid_dimension_scale_dt_and_threads_are_rejected() {
        assert!(PackedWork::new(23,&vec![1.0;23],1.0,1).is_err());
        for invalid in [0.0,-1.0,f64::NAN,f64::INFINITY] {
            assert!(PackedWork::new(24,&vec![invalid;24],1.0,1).is_err());
            assert!(PackedWork::new(24,&vec![1.0;24],invalid,1).is_err());
        }
        assert!(PackedWork::new(24,&vec![1.0;24],1.0,3).is_err());
    }
}
