//! Immutable T-only coefficient tables. This module knows no density, radiation,
//! time, geometry, EOS, or evolved abundance. No derivative/Jacobian API.
//!
//! A four-node stencil must fit inside one caller-certified smooth source branch.
//! Negative exterior interpolation weights are allowed; nonpositive/non-normal
//! results fall back to the source. Positivity checks alone do not certify accuracy.
#![forbid(unsafe_code)]

use sha2::{Digest, Sha256};
use std::{fmt, fs::OpenOptions, io::{Read, Write}, path::Path};

pub const MAX_NODES: usize = 65_537;
pub const DEFAULT_NODES: usize = 32_769;
const BLOCKED: u32 = 1 << 31;
const MAGIC: &[u8; 16] = b"REI_TCUBIC_00001";

#[derive(Debug)]
pub enum Error { Invalid(&'static str), Io(std::io::Error) }
impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self { Self::Invalid(s) => f.write_str(s), Self::Io(e) => e.fmt(f) }
    }
}
impl std::error::Error for Error {}
impl From<std::io::Error> for Error { fn from(e: std::io::Error) -> Self { Self::Io(e) } }

#[derive(Clone, Copy, Debug)]
pub struct Sample<const N: usize> {
    pub values: [f64; N],
    /// Caller-defined branch/floor/diagnostic identity, immutable within a stencil.
    pub tag: u8,
}

/// Node-major coefficient storage supports contiguous channel arithmetic. The
/// compiler may vectorize the kernel; this API does not assume a SIMD width.
#[derive(Clone, Debug)]
pub struct CubicRateGrid<const N: usize> {
    lower: f64, upper: f64, log_lower: f64, inv_step: f64,
    source_id: [u8; 32],
    values: Vec<[f64; N]>,
    tags: Vec<u8>,
    /// High bit: whole-cell fallback. Low N bits: certified structural zero.
    flags: Vec<u32>,
}

impl<const N: usize> CubicRateGrid<N> {
    pub fn build(
        lower: f64, upper: f64, nodes: usize, source_id: [u8; 32],
        reference: impl Fn(f64) -> Result<Sample<N>, Error>,
        blocked: impl Fn(f64, f64) -> bool,
        structural_zero: impl Fn(usize, f64, f64) -> bool,
    ) -> Result<Self, Error> {
        Self::validate_shape(lower, upper, nodes)?;
        let log_lower = lower.ln();
        let step = (upper.ln() - log_lower) / (nodes - 1) as f64;
        if !step.is_normal() || step <= 0.0 { return Err(Error::Invalid("CUBIC_GRID_STEP")); }
        let ts: Vec<_> = (0..nodes).map(|i| {
            if i == 0 { lower } else if i + 1 == nodes { upper }
            else { (log_lower + step * i as f64).exp() }
        }).collect();
        let mut values = Vec::with_capacity(nodes);
        let mut tags = Vec::with_capacity(nodes);
        for &t in &ts {
            let s = reference(t)?;
            if s.values.iter().any(|v| !v.is_finite() || *v < 0.0) {
                return Err(Error::Invalid("CUBIC_SOURCE_VALUE"));
            }
            values.push(s.values); tags.push(s.tag);
        }
        let mut flags = vec![BLOCKED; nodes - 1];
        for i in 1..nodes - 2 {
            let a = ts[i - 1]; let b = ts[i + 2];
            let mut flag = 0;
            if blocked(a, b) || tags[i-1..=i+2].iter().any(|&tag| tag != tags[i]) {
                flag |= BLOCKED;
            }
            for j in 0..N {
                let v = &values[i-1..=i+2];
                if structural_zero(j, a, b) && v.iter().all(|row| row[j] == 0.0) {
                    flag |= 1 << j;
                } else if v.iter().any(|row| !row[j].is_normal() || row[j] <= 0.0) {
                    flag |= BLOCKED;
                }
            }
            flags[i] = flag;
        }
        Ok(Self { lower, upper, log_lower, inv_step: 1.0 / step,
            source_id, values, tags, flags })
    }

    fn validate_shape(lower: f64, upper: f64, nodes: usize) -> Result<(), Error> {
        if N == 0 || N > 31 || !lower.is_normal() || !upper.is_normal()
            || lower <= 0.0 || upper <= lower || !(4..=MAX_NODES).contains(&nodes) {
            return Err(Error::Invalid("CUBIC_GRID_SHAPE"));
        }
        Ok(())
    }
    pub fn nodes(&self) -> usize { self.values.len() }
    pub fn domain(&self) -> [f64; 2] { [self.lower, self.upper] }
    pub fn source_id(&self) -> [u8; 32] { self.source_id }
    pub fn blocked_cells(&self) -> usize { self.flags.iter().filter(|&&f| f & BLOCKED != 0).count() }
    /// Heap payload excluding Vec/struct headers and allocator bookkeeping.
    pub fn storage_bytes(&self) -> usize {
        self.values.len() * N * 8 + self.tags.len() + self.flags.len() * 4
    }
    pub fn temperature_at(&self, i: usize) -> Option<f64> {
        if i >= self.nodes() { None } else if i == 0 { Some(self.lower) }
        else if i + 1 == self.nodes() { Some(self.upper) }
        else { Some((self.log_lower + ((self.upper.ln()-self.log_lower)/(self.nodes()-1) as f64) * i as f64).exp()) }
    }

    /// None requests the unchanged direct provider (including domain validation).
    #[inline]
    pub fn sample(&self, t: f64) -> Option<Sample<N>> {
        if !t.is_finite() || t < self.lower || t > self.upper { return None; }
        let x = (t.ln() - self.log_lower) * self.inv_step;
        let i = (x.floor() as usize).min(self.nodes() - 2);
        let flags = self.flags[i];
        if flags & BLOCKED != 0 { return None; }
        let theta = (x - i as f64).clamp(0.0, 1.0);
        let weights = centered_weights(theta);
        let mut v = weighted_channels(&self.values[i-1], &self.values[i],
            &self.values[i+1], &self.values[i+2], weights);
        for (j, value) in v.iter_mut().enumerate() {
            if flags & (1 << j) != 0 { *value = 0.0; }
            else if !value.is_normal() || *value <= 0.0 { return None; }
        }
        Some(Sample { values: v, tag: self.tags[i] })
    }

    /// Reuses the caller's output buffer. The evaluator can restore tagged exact
    /// floors/diagnostics or assemble a physical bundle. No floating reduction.
    pub fn batch_into<R: Send>(ts: &[f64], out: &mut [R], workers: usize,
        evaluate: impl Fn(f64) -> Result<R, Error> + Sync) -> Result<(), Error> {
        if ts.len() != out.len() { return Err(Error::Invalid("CUBIC_BATCH_LENGTH")); }
        if !(1..=4).contains(&workers) { return Err(Error::Invalid("CUBIC_BATCH_WORKERS")); }
        if workers == 1 || ts.is_empty() {
            for (&t, row) in ts.iter().zip(out) { *row = evaluate(t)?; }
            return Ok(());
        }
        let chunk = ts.len().div_ceil(workers);
        std::thread::scope(|scope| {
            let mut handles = Vec::with_capacity(workers);
            for (ts, out) in ts.chunks(chunk).zip(out.chunks_mut(chunk)) {
                let eval = &evaluate;
                handles.push(scope.spawn(move || {
                    for (&t, row) in ts.iter().zip(out) { *row = eval(t)?; }
                    Ok(())
                }));
            }
            // Join every worker before returning; choose the first chunk error.
            let mut error = None;
            for h in handles {
                let result = h.join().map_err(|_| Error::Invalid("CUBIC_BATCH_PANIC")).and_then(|r| r);
                if error.is_none() { if let Err(e) = result { error = Some(e); } }
            }
            error.map_or(Ok(()), Err)
        })
    }

    /// A content digest is an integrity check, not authentication of a producer.
    /// Caller supplies the exact source+algorithm identity used to create the grid.
    pub fn save_new(&self, path: impl AsRef<Path>) -> Result<(), Error> {
        let mut bytes = Vec::with_capacity(120 + self.storage_bytes());
        bytes.extend_from_slice(MAGIC);
        bytes.extend_from_slice(&(N as u32).to_le_bytes());
        bytes.extend_from_slice(&(self.nodes() as u32).to_le_bytes());
        bytes.extend_from_slice(&self.source_id);
        for v in [self.lower, self.upper, self.log_lower, self.inv_step] {
            bytes.extend_from_slice(&v.to_le_bytes());
        }
        for row in &self.values { for v in row { bytes.extend_from_slice(&v.to_le_bytes()); } }
        bytes.extend_from_slice(&self.tags);
        for flags in &self.flags { bytes.extend_from_slice(&flags.to_le_bytes()); }
        let digest = Sha256::digest(&bytes);
        bytes.extend_from_slice(&digest);
        let mut file = OpenOptions::new().create_new(true).write(true).open(path)?;
        file.write_all(&bytes)?; file.sync_all()?;
        Ok(())
    }

    pub fn load(path: impl AsRef<Path>, expected_source: [u8; 32]) -> Result<Self, Error> {
        if N == 0 || N > 31 { return Err(Error::Invalid("CUBIC_GRID_SHAPE")); }
        let mut f = std::fs::File::open(path)?;
        // Bound allocation before trusting dimensions from the file.
        let max = 120 + MAX_NODES * (N * 8 + 1) + (MAX_NODES - 1) * 4;
        let size = f.metadata()?.len();
        if size < 120 || size > max as u64 { return Err(Error::Invalid("CUBIC_CACHE_LENGTH")); }
        let mut bytes = Vec::with_capacity(size as usize);
        (&mut f).take(max as u64 + 1).read_to_end(&mut bytes)?;
        if bytes.len() != size as usize { return Err(Error::Invalid("CUBIC_CACHE_LENGTH")); }
        let (payload, digest) = bytes.split_at(bytes.len() - 32);
        if Sha256::digest(payload).as_slice() != digest { return Err(Error::Invalid("CUBIC_CACHE_DIGEST")); }
        if &payload[..16] != MAGIC { return Err(Error::Invalid("CUBIC_CACHE_MAGIC")); }
        let channel_count = u32::from_le_bytes(payload[16..20].try_into().unwrap()) as usize;
        let nodes = u32::from_le_bytes(payload[20..24].try_into().unwrap()) as usize;
        if channel_count != N || payload[24..56] != expected_source {
            return Err(Error::Invalid("CUBIC_CACHE_IDENTITY"));
        }
        if !(4..=MAX_NODES).contains(&nodes) || bytes.len() != 120 + nodes * (N * 8 + 1) + (nodes - 1) * 4 {
            return Err(Error::Invalid("CUBIC_CACHE_LENGTH"));
        }
        let mut offset = 56;
        let take_f64 = |offset: &mut usize| {
            let v = f64::from_le_bytes(payload[*offset..*offset+8].try_into().unwrap()); *offset += 8; v
        };
        let lower = take_f64(&mut offset); let upper = take_f64(&mut offset);
        let log_lower = take_f64(&mut offset); let inv_step = take_f64(&mut offset);
        Self::validate_shape(lower, upper, nodes)?;
        let expected_inv = 1.0 / ((upper.ln() - lower.ln()) / (nodes - 1) as f64);
        if !inv_step.is_normal() || inv_step <= 0.0 || log_lower.to_bits() != lower.ln().to_bits() || inv_step.to_bits() != expected_inv.to_bits() {
            return Err(Error::Invalid("CUBIC_CACHE_COORDINATES"));
        }
        let mut values = Vec::with_capacity(nodes);
        for _ in 0..nodes {
            let v = std::array::from_fn(|_| take_f64(&mut offset));
            if v.iter().any(|v: &f64| !v.is_finite() || *v < 0.0) { return Err(Error::Invalid("CUBIC_CACHE_VALUE")); }
            values.push(v);
        }
        let tags = payload[offset..offset+nodes].to_vec(); offset += nodes;
        let allowed = BLOCKED | ((1u32 << N) - 1);
        let mut flags = Vec::with_capacity(nodes-1);
        for _ in 0..nodes-1 {
            let v = u32::from_le_bytes(payload[offset..offset+4].try_into().unwrap()); offset += 4;
            if v & !allowed != 0 { return Err(Error::Invalid("CUBIC_CACHE_FLAGS")); }
            flags.push(v);
        }
        if flags[0] & BLOCKED == 0 || flags[nodes-2] & BLOCKED == 0 { return Err(Error::Invalid("CUBIC_CACHE_BOUNDARY")); }
        for i in 1..nodes-2 {
            if flags[i] & BLOCKED != 0 { continue; }
            if tags[i-1..=i+2].iter().any(|&t| t != tags[i]) { return Err(Error::Invalid("CUBIC_CACHE_TAGS")); }
            for j in 0..N {
                if values[i-1..=i+2].iter().any(|v| if flags[i] & (1 << j) != 0 { v[j] != 0.0 }
                    else { !v[j].is_normal() || v[j] <= 0.0 }) { return Err(Error::Invalid("CUBIC_CACHE_SUPPORT")); }
            }
        }
        Ok(Self { lower, upper, log_lower, inv_step, source_id: expected_source, values, tags, flags })
    }
}

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

pub fn source_digest(bytes: &[u8]) -> [u8; 32] { Sha256::digest(bytes).into() }

