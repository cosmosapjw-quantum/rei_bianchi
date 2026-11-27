//! Same original m=0 callbacks, with owned reusable storage and ordered j-lane SIMD.
//! The angular node reduction and D2 sum are never parallel or reassociated.

use std::num::NonZeroUsize;
use gauss_quad::GaussLegendre;
use num_complex::Complex64 as C;
use rodas5p_core::{CoreError, CoreResult};
use serde::{Deserialize, Serialize};
use wide::f64x4;
use wu088_hh_phys69_vigilode::{K, Q_SCALE, SHIFT, T, TARGET_A, TARGET_B, get, put};
use crate::block::FrozenJacobian;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Backend { Scalar, Simd }

#[derive(Clone, Debug, Default, Serialize)]
pub struct KernelCounters {
    pub rhs_calls: usize,
    pub time_partial_calls: usize,
    pub angular_evaluations: usize,
    pub angular_cache_hits: usize,
    pub linearizations: usize,
}

pub struct HhKernel {
    pub channels: usize,
    backend: Backend,
    nodes: Vec<(f64, f64)>,
    // q-major blocks, with zero-padded last j block. Two selected basis products.
    products_a: Vec<f64x4>,
    products_b: Vec<f64x4>,
    blocks: usize,
    rows: [Vec<f64>; 4],
    lanes: [Vec<f64x4>; 4],
    r_bits: Option<u64>,
    pub counts: KernelCounters,
}

impl HhKernel {
    pub fn new(lmax: usize, angular_nodes: usize, backend: Backend) -> CoreResult<Self> {
        if !(21..=64).contains(&lmax) || angular_nodes < lmax + TARGET_A + 8
            || angular_nodes > 1024 {
            return Err(CoreError::InvalidInput("invalid original HH angular dimensions".into()));
        }
        let channels = lmax + 1;
        let blocks = channels.div_ceil(4);
        let nodes: Vec<(f64,f64)> = GaussLegendre::new(NonZeroUsize::new(angular_nodes).unwrap()).into_iter().collect();
        let mut products_a = Vec::with_capacity(angular_nodes * blocks);
        let mut products_b = Vec::with_capacity(angular_nodes * blocks);
        for &(mu, weight) in &nodes {
            if !mu.is_finite() || mu.abs() >= 1.0 || !weight.is_finite() || weight <= 0.0 {
                return Err(CoreError::NonFinite("invalid Gaussian node or weight".into()));
            }
            let mut p = vec![1.0; channels];
            p[1] = mu;
            for j in 2..channels {
                p[j] = ((2*j-1) as f64 * mu * p[j-1] - (j-1) as f64 * p[j-2]) / j as f64;
            }
            for (j, value) in p.iter_mut().enumerate() { *value *= ((2*j+1) as f64 / 2.0).sqrt(); }
            for block in 0..blocks {
                let mut a = [0.0;4]; let mut b = [0.0;4];
                for lane in 0..4 {
                    let j = 4*block+lane;
                    if j < channels { a[lane] = p[TARGET_A]*p[j]; b[lane] = p[TARGET_B]*p[j]; }
                }
                products_a.push(f64x4::new(a)); products_b.push(f64x4::new(b));
            }
        }
        Ok(Self { channels, backend, nodes, products_a, products_b, blocks,
            rows: std::array::from_fn(|_| vec![0.0; blocks*4]),
            lanes: std::array::from_fn(|_| vec![f64x4::ZERO; blocks]),
            r_bits: None, counts: KernelCounters::default() })
    }
    pub fn dimension(&self) -> usize { 2*(4*self.channels+1) }
    pub fn config_key(&self) -> (usize,usize,Backend) { (self.channels,self.nodes.len(),self.backend) }
    pub fn workspace_bytes(&self) -> usize {
        self.nodes.capacity()*16 + (self.products_a.capacity()+self.products_b.capacity())*32
            + self.rows.iter().map(|v|v.capacity()*8).sum::<usize>()
            + self.lanes.iter().map(|v|v.capacity()*32).sum::<usize>()
    }
    fn check(&self, tau:f64, y:&[f64], out:&[f64]) -> CoreResult<f64> {
        let r = T-tau;
        if !tau.is_finite() || !r.is_finite() || r <= SHIFT { return Err(CoreError::InvalidInput("outside analytic collar".into())); }
        if y.len()!=self.dimension() || out.len()!=self.dimension() { return Err(CoreError::Dimension("HH state dimension".into())); }
        if y.iter().any(|x|!x.is_finite()) { return Err(CoreError::NonFinite("HH state".into())); }
        for j in 0..self.channels { if get(y,j).norm()==0.0 { return Err(CoreError::InvalidInput("zero Coulomb denominator".into())); } }
        Ok(r)
    }
    fn angular(&mut self, r:f64) -> CoreResult<()> {
        if self.r_bits==Some(r.to_bits()) { self.counts.angular_cache_hits+=1; return Ok(()); }
        self.r_bits=None;
        self.counts.angular_evaluations+=1;
        match self.backend {
            Backend::Scalar => {
                for row in &mut self.rows { row.fill(0.0); }
                for (q,&(mu,weight)) in self.nodes.iter().enumerate() {
                    let d=(r*r+SHIFT*SHIFT-2.0*r*SHIFT*mu).sqrt();
                    let exp=(-2.0*d).exp();
                    let v=2.0*(1.0+d.recip())*exp*weight;
                    let vr=-2.0*exp*(2.0+2.0/d+1.0/(d*d))*(r-SHIFT*mu)/d*weight;
                    for block in 0..self.blocks {
                        let pa=self.products_a[q*self.blocks+block].to_array();
                        let pb=self.products_b[q*self.blocks+block].to_array();
                        for lane in 0..4 {
                            let j=4*block+lane;
                            self.rows[0][j]+=pa[lane]*v; self.rows[1][j]+=pb[lane]*v;
                            self.rows[2][j]+=pa[lane]*vr; self.rows[3][j]+=pb[lane]*vr;
                        }
                    }
                }
            },
            Backend::Simd => {
                for row in &mut self.lanes { row.fill(f64x4::ZERO); }
                for (q,&(mu,weight)) in self.nodes.iter().enumerate() {
                    // Same scalar sqrt/exp/division as PHYS69. No approximate vector exp.
                    let d=(r*r+SHIFT*SHIFT-2.0*r*SHIFT*mu).sqrt();
                    let exp=(-2.0*d).exp();
                    let v=f64x4::splat(2.0*(1.0+d.recip())*exp*weight);
                    let vr=f64x4::splat(-2.0*exp*(2.0+2.0/d+1.0/(d*d))*(r-SHIFT*mu)/d*weight);
                    for block in 0..self.blocks {
                        let pa=self.products_a[q*self.blocks+block]; let pb=self.products_b[q*self.blocks+block];
                        // Multiplication then addition; intentionally no mul_add/reduce_add.
                        self.lanes[0][block]=self.lanes[0][block]+pa*v;
                        self.lanes[1][block]=self.lanes[1][block]+pb*v;
                        self.lanes[2][block]=self.lanes[2][block]+pa*vr;
                        self.lanes[3][block]=self.lanes[3][block]+pb*vr;
                    }
                }
                for k in 0..4 { for block in 0..self.blocks {
                    self.rows[k][4*block..4*block+4].copy_from_slice(&self.lanes[k][block].to_array());
                } }
            }
        }
        if self.rows.iter().flatten().any(|v|!v.is_finite()) { return Err(CoreError::NonFinite("angular rows".into())); }
        self.r_bits=Some(r.to_bits()); Ok(())
    }
    /// Diagnostic copy into caller storage; does not expose or mutate the cache.
    pub fn angular_into(&mut self,r:f64,out:&mut[f64])->CoreResult<()> {
        if !r.is_finite() || r<=SHIFT || out.len()!=4*self.channels { return Err(CoreError::InvalidInput("angular diagnostic shape/r".into())); }
        self.angular(r)?;
        for k in 0..4 { out[k*self.channels..(k+1)*self.channels].copy_from_slice(&self.rows[k][..self.channels]); }
        Ok(())
    }
    pub fn rhs(&mut self,tau:f64,y:&[f64],out:&mut[f64])->CoreResult<()> {
        let r=self.check(tau,y,out)?; self.angular(r)?; self.counts.rhs_calls+=1;
        let n=self.channels; let fa=get(y,TARGET_A); let fb=get(y,TARGET_B); let mut dz=C::default();
        for j in 0..n {
            let f=get(y,j); let q=K*K+2.0/r-(j*(j+1)) as f64/(r*r);
            put(out,j,-get(y,n+j)); put(out,n+j,f*q);
            put(out,2*n+j,fa*f*(Q_SCALE*self.rows[0][j]));
            put(out,3*n+j,fb*f*(Q_SCALE*self.rows[1][j]));
            dz+=(get(y,2*n+j)/f)*(get(y,3*n+j)/f);
        }
        put(out,4*n,dz); finite(out)
    }
    pub fn partial_tau(&mut self,tau:f64,y:&[f64],out:&mut[f64])->CoreResult<()> {
        let r=self.check(tau,y,out)?; self.angular(r)?; self.counts.time_partial_calls+=1; out.fill(0.0);
        let n=self.channels; let fa=get(y,TARGET_A); let fb=get(y,TARGET_B);
        for j in 0..n {
            let f=get(y,j); let qt=2.0/(r*r)-2.0*(j*(j+1)) as f64/(r*r*r);
            put(out,n+j,f*qt); put(out,2*n+j,fa*f*(-Q_SCALE*self.rows[2][j]));
            put(out,3*n+j,fb*f*(-Q_SCALE*self.rows[3][j]));
        }
        finite(out)
    }
    pub fn freeze(&mut self,tau:f64,y:&[f64],jac:&mut FrozenJacobian)->CoreResult<()> {
        // A failed public refresh must never leave the previous base usable.
        jac.invalidate();
        // This check uses y as the shape-only output argument; no mutation of y.
        let r=self.check(tau,y,y)?; self.angular(r)?;
        jac.prepare(r,y,&self.rows[0][..self.channels],&self.rows[1][..self.channels])?;
        self.counts.linearizations+=1; Ok(())
    }
}
pub(crate) fn finite(out:&[f64])->CoreResult<()> {
    if out.iter().any(|v|!v.is_finite()) { Err(CoreError::NonFinite("HH callback output".into())) } else { Ok(()) }
}
