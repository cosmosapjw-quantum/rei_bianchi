//! Bounded observational summaries; never alter scientific state or admission thresholds.
use crate::{err, material, Fallible};
use rei_microphysics::{igm_background::FlrwPoint, igm_rates::igm_rates};
use std::{
    cell::RefCell,
    ops::{Deref, DerefMut},
    sync::atomic::{AtomicUsize, Ordering},
};
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Summary {
    pub count: usize,
    pub min: f64,
    pub max: f64,
    pub any: u16,
    pub all: u16,
}
impl Default for Summary {
    fn default() -> Self {
        Self {
            count: 0,
            min: f64::INFINITY,
            max: 0.,
            any: 0,
            all: u16::MAX,
        }
    }
}
impl Summary {
    pub fn merge(&mut self, b: Self) {
        if b.count > 0 {
            self.count += b.count;
            self.min = self.min.min(b.min);
            self.max = self.max.max(b.max);
            self.any |= b.any;
            self.all &= b.all;
        }
    }
}
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Trace {
    pub stages: [Summary; 3],
    pub continuity_max_relative: f64,
    pub continuity_checks: usize,
}
impl Trace {
    pub fn merge(&mut self, b: Self) {
        for i in 0..3 {
            self.stages[i].merge(b.stages[i]);
        }
        self.continuity_max_relative = self.continuity_max_relative.max(b.continuity_max_relative);
        self.continuity_checks += b.continuity_checks;
    }
}
thread_local! {static TRACE:RefCell<Trace>=RefCell::new(Trace::default());}
pub fn reset() {
    TRACE.with(|t| *t.borrow_mut() = Trace::default());
}
pub fn snapshot() -> Trace {
    TRACE.with(|t| *t.borrow())
}
pub fn stage(kind: usize, y: [f64; 4], p: FlrwPoint) -> Fallible<()> {
    let t = material::gas(y)?
        .eos(p.n_h_cm3, p.n_he_cm3)
        .map_err(err)?
        .temperature_k;
    let r = igm_rates(t).map_err(err)?;
    let mut mask = 0;
    if t > 5500. {
        mask |= 1;
    }
    if t / 11605. > 0.8 {
        mask |= 2;
    }
    for i in 0..3 {
        if r.diagnostics.ci_floor_cm3_s[i] != 0. {
            mask |= 1 << (2 + i);
        }
        if r.diagnostics.ce_cap_erg[i] != 0. {
            mask |= 1 << (5 + i);
        }
    }
    TRACE.with(|v| {
        v.borrow_mut().stages[kind].merge(Summary {
            count: 1,
            min: t,
            max: t,
            any: mask,
            all: mask,
        })
    });
    Ok(())
}
pub fn continuity(previous: f64, next: f64) -> Fallible<()> {
    let scale = previous.abs().max(next.abs());
    let rel = if scale == 0. {
        0.
    } else {
        (previous - next).abs() / scale
    };
    TRACE.with(|t| {
        let mut t = t.borrow_mut();
        t.continuity_checks += 1;
        t.continuity_max_relative = t.continuity_max_relative.max(rel);
    });
    if rel > 2e-12 {
        return Err("cross-transaction energy discontinuity".into());
    }
    Ok(())
}
static LIVE: AtomicUsize = AtomicUsize::new(0);
static SLOTS: AtomicUsize = AtomicUsize::new(0);
static PEAK: AtomicUsize = AtomicUsize::new(0);
static PEAK_SLOTS: AtomicUsize = AtomicUsize::new(0);
#[derive(Debug, PartialEq)]
pub struct Density(Vec<f64>);
impl Density {
    pub fn new(v: Vec<f64>) -> Self {
        let n = LIVE.fetch_add(1, Ordering::SeqCst) + 1;
        let slots = SLOTS.fetch_add(v.capacity(), Ordering::SeqCst) + v.capacity();
        PEAK.fetch_max(n, Ordering::SeqCst);
        PEAK_SLOTS.fetch_max(slots, Ordering::SeqCst);
        Self(v)
    }
}
impl Clone for Density {
    fn clone(&self) -> Self {
        Self::new(self.0.clone())
    }
}
impl Drop for Density {
    fn drop(&mut self) {
        LIVE.fetch_sub(1, Ordering::SeqCst);
        SLOTS.fetch_sub(self.0.capacity(), Ordering::SeqCst);
    }
}
impl Deref for Density {
    type Target = Vec<f64>;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}
impl DerefMut for Density {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}
pub fn array_peak() -> (usize, usize) {
    (
        PEAK.load(Ordering::SeqCst),
        PEAK_SLOTS.load(Ordering::SeqCst),
    )
}
