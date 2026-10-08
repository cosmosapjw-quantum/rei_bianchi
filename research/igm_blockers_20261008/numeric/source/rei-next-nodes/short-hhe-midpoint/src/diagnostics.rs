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
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct PhotonNode {
    pub number: canonical::Tracked,
    pub energy: canonical::Tracked,
}
impl PhotonNode {
    pub fn empty() -> Self {
        Self {
            number: canonical::Tracked::empty(),
            energy: canonical::Tracked::empty(),
        }
    }
}
#[derive(Debug, PartialEq)]
pub struct Density {
    scalar_number: Vec<f64>,
    canonical: Vec<PhotonNode>,
}
impl Density {
    pub fn new(v: Vec<f64>) -> Self {
        assert!(v.iter().all(|&x| x == 0.0), "nonzero density requires paired moments");
        let canonical = v
            .iter()
            .map(|&number| PhotonNode {
                number: canonical::Tracked::from_f64(number)
                    .expect("finite nonnegative density"),
                energy: canonical::Tracked::empty(),
            })
            .collect();
        Self::from_parts(v, canonical).expect("matching density parts")
    }
    pub fn from_parts(v: Vec<f64>, canonical: Vec<PhotonNode>) -> Result<Self, &'static str> {
        if v.len() != canonical.len() {
            return Err("density canonical length mismatch");
        }
        for (&number, moment) in v.iter().zip(&canonical) {
            if !number.is_finite() || number < 0.0 {
                return Err("invalid scalar density");
            }
            if moment.number.readout()?.0.to_bits() != number.to_bits() {
                return Err("density canonical/readout mismatch");
            }
            if moment.number.value.is_empty() != moment.energy.value.is_empty() {
                return Err("density canonical pair mismatch");
            }
        }
        let n = LIVE.fetch_add(1, Ordering::SeqCst) + 1;
        let slots = SLOTS.fetch_add(v.capacity(), Ordering::SeqCst) + v.capacity();
        PEAK.fetch_max(n, Ordering::SeqCst);
        PEAK_SLOTS.fetch_max(slots, Ordering::SeqCst);
        Ok(Self {
            scalar_number: v,
            canonical,
        })
    }
    pub fn legacy_unpaired(v: Vec<f64>) -> Self {
        let canonical = v
            .iter()
            .map(|&number| PhotonNode {
                number: canonical::Tracked::from_f64(number)
                    .expect("finite nonnegative legacy density"),
                energy: canonical::Tracked::empty(),
            })
            .collect();
        let n = LIVE.fetch_add(1, Ordering::SeqCst) + 1;
        let slots = SLOTS.fetch_add(v.capacity(), Ordering::SeqCst) + v.capacity();
        PEAK.fetch_max(n, Ordering::SeqCst);
        PEAK_SLOTS.fetch_max(slots, Ordering::SeqCst);
        Self { scalar_number: v, canonical }
    }
    pub fn replace_canonical(&mut self, canonical: Vec<PhotonNode>) -> Result<(), &'static str> {
        let checked = Self::from_parts(self.scalar_number.clone(), canonical)?;
        self.canonical = checked.canonical.clone();
        Ok(())
    }
    pub fn resize_zeros(&mut self, len: usize) {
        self.scalar_number.resize(len, 0.0);
        self.canonical.resize(len, PhotonNode::empty());
    }
    pub fn truncate(&mut self, len: usize) {
        self.scalar_number.truncate(len);
        self.canonical.truncate(len);
    }
    pub fn canonical(&self) -> &[PhotonNode] {
        &self.canonical
    }
}
impl Clone for Density {
    fn clone(&self) -> Self {
        Self::from_parts(self.scalar_number.clone(), self.canonical.clone())
            .expect("valid cloned density")
    }
}
impl Drop for Density {
    fn drop(&mut self) {
        LIVE.fetch_sub(1, Ordering::SeqCst);
        SLOTS.fetch_sub(self.scalar_number.capacity(), Ordering::SeqCst);
    }
}
impl Deref for Density {
    type Target = Vec<f64>;
    fn deref(&self) -> &Self::Target {
        &self.scalar_number
    }
}
impl DerefMut for Density {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.scalar_number
    }
}
pub fn array_peak() -> (usize, usize) {
    (
        PEAK.load(Ordering::SeqCst),
        PEAK_SLOTS.load(Ordering::SeqCst),
    )
}

#[cfg(test)]
mod paired_density_tests {
    use super::*;
    #[test]
    fn canonical_energy_may_project_to_zero_without_becoming_empty() {
        let number = canonical::Tracked::from_f64(1.0).unwrap();
        let energy = canonical::Tracked::exact(canonical::Wide::from_parts(1.0, -1100).unwrap());
        let density = Density::from_parts(vec![1.0], vec![PhotonNode { number, energy }]).unwrap();
        assert_eq!(density[0], 1.0);
        assert_eq!(density.canonical()[0].energy.readout().unwrap().0, 0.0);
        assert!(!density.canonical()[0].energy.value.is_empty());
    }

    #[test]
    fn structural_pair_mismatch_is_rejected() {
        let number = canonical::Tracked::from_f64(1.0).unwrap();
        let bad = PhotonNode { number, energy: canonical::Tracked::empty() };
        assert_eq!(Density::from_parts(vec![1.0], vec![bad]).unwrap_err(), "density canonical pair mismatch");
    }
}
