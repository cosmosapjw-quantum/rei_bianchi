//! Positive restrictions of a fixed spectral shape with an independent log amplitude.
//!
//! f(eta) is proportional to w(y) exp(beta*y), y=(eta-L)/(R-L).
//! These are integration pieces of the parent measure, not independently retapered
//! child closures. Geometry-empty intersections have no positive amplitude.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Family { Ordinary, RightFront }
#[derive(Clone, Copy, Debug)]
pub struct Panel {
    pub l: f64, pub r: f64, pub beta: f64, pub family: Family,
    /// Natural log of the positive parent photon count. Exact empty is external.
    pub ln_n: f64,
}
#[derive(Clone, Copy, Debug)]
pub struct Restriction {
    pub lo: f64, pub hi: f64, pub ln_fraction: f64, pub ln_n: f64,
    /// E[(exp(eta-lo)-1)/(exp(hi-lo)-1)] evaluated without near-equal subtraction.
    pub normalized_mean: f64,
    /// Moment-exact positive stock-rule site in exact arithmetic.
    pub mean_eta: f64, pub mean_exp_eta: f64,
    pub panels: usize,
    /// Successive positive quadrature differences: empirical, not interval proof.
    pub convergence_error: f64,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum PanelError { Domain, Quadrature, Arithmetic }

// Positive eight-point Gauss-Legendre rule. Pair symmetry is retained explicitly.
const X: [f64;4]=[0.1834346424956498,0.5255324099163290,0.7966664774136267,0.9602898564975363];
const W: [f64;4]=[0.3626837833783620,0.3137066458778873,0.2223810344533745,0.1012285362903763];
const TOL: f64=2e-14;
fn diff_exact(a:f64,b:f64)->(f64,f64) {
    let x=a-b;let bb=x-a;let low=(a-(x-bb))+(-b-bb);(x,low)
}
fn below(pair:(f64,f64),x:f64)->bool {pair.0<x || (pair.0==x && pair.1<0.0)}
fn above(pair:(f64,f64),x:f64)->bool {pair.0>x || (pair.0==x && pair.1>0.0)}
fn compensated_add(sum:&mut f64,correction:&mut f64,x:f64) {
    let y=x-*correction;let t=*sum+y;*correction=(t-*sum)-y;*sum=t;
}
#[derive(Clone, Copy)]
struct Integral { log_value:f64,mu:f64,panels:usize,error:f64 }
impl Panel {
    pub fn validate(&self)->Result<(),PanelError> {
        if ![self.l,self.r,self.beta,self.ln_n].iter().all(|x|x.is_finite())
            || self.l < -32.0 || self.r >32.0 || self.r<=self.l || self.beta.abs()>128.0 {
            return Err(PanelError::Domain);
        }
        let width=diff_exact(self.r,self.l);
        if below(width,1e-7) || above(width,32.0) {return Err(PanelError::Domain);}
        Ok(())
    }
    fn integral(&self,a:f64,b:f64)->Result<Integral,PanelError> {
        let width=self.r-self.l;let d=b-a;
        let stretch=d/width;
        let slope=self.beta*stretch;
        let anchor=if self.beta>=0.0 {1.0} else {0.0};
        let anchor_y=if self.beta>=0.0 {(b-self.l)/width} else {(a-self.l)/width};
        // Scale the taper before integration. Right-front narrow restrictions do
        // not evaluate 1-y near y=1, where cancellation would erase the shape.
        let taper_scale=match self.family {Family::Ordinary=>1.0,Family::RightFront=>(self.r-a)/width};
        if !(stretch>0.0 && taper_scale>0.0 && d.is_finite()) {return Err(PanelError::Arithmetic);}
        let taper_offset=match self.family {Family::Ordinary=>1.0,Family::RightFront=>(self.r-b)/(self.r-a)};
        let taper_slope=match self.family {Family::Ordinary=>0.0,Family::RightFront=>d/(self.r-a)};
        let denom=d.exp_m1();
        let rule=|panels:usize|->Result<(f64,f64),PanelError> {
            let mut n=0.0;let mut m=0.0;let mut nc=0.0;let mut mc=0.0;
            for j in 0..panels {
                let center=(j as f64+0.5)/panels as f64;let half=0.5/panels as f64;
                for k in 0..4 {for sign in [-1.0,1.0] {
                    let t=center+sign*half*X[k];
                    let taper=taper_offset+taper_slope*(1.0-t);
                    let weight=half*W[k]*taper*(slope*(t-anchor)).exp();
                    let target=(d*t).exp_m1()/denom;
                    if !(weight>0.0 && weight.is_normal() && target.is_finite()) {return Err(PanelError::Arithmetic);}
                    compensated_add(&mut n,&mut nc,weight);
                    compensated_add(&mut m,&mut mc,weight*target);
                }}
            }
            if n>0.0 && n.is_finite() && m.is_finite() {Ok((n,m/n))} else {Err(PanelError::Arithmetic)}
        };
        let mut old=rule(1)?;
        for panels in [2,4,8,16,32,64] {
            let current=rule(panels)?;
            let error=((current.0-old.0)/current.0).abs().max((current.1-old.1).abs());
            if error<=TOL {
                let log_value=stretch.ln()+taper_scale.ln()+self.beta*anchor_y+current.0.ln();
                if !log_value.is_finite() || !(0.0..=1.0).contains(&current.1) {return Err(PanelError::Arithmetic);}
                return Ok(Integral{log_value,mu:current.1,panels,error});
            }
            old=current;
        }
        Err(PanelError::Quadrature)
    }
    /// Restrict the actual parent measure to [a,b]∩[L,R]. Outside support is empty.
    /// Finite ln_n amplitude survives arbitrary readout underflow independently of shape.
    pub fn restrict(&self,a:f64,b:f64)->Result<Option<Restriction>,PanelError> {
        self.validate()?;
        if !(a.is_finite() && b.is_finite()) || b<a {return Err(PanelError::Domain);}
        let lo=a.max(self.l);let hi=b.min(self.r);
        if hi<=lo {return Ok(None);}
        let total=self.integral(self.l,self.r)?;
        let part=if lo==self.l && hi==self.r {total} else {self.integral(lo,hi)?};
        let ln_fraction=part.log_value-total.log_value;
        if !ln_fraction.is_finite() || ln_fraction>0.0 {return Err(PanelError::Arithmetic);}
        let ln_n=self.ln_n+ln_fraction;
        let mean_eta=lo+(part.mu*(hi-lo).exp_m1()).ln_1p();
        let mean_exp_eta=mean_eta.exp();
        if !(ln_n.is_finite() && mean_eta>=lo && mean_eta<=hi && mean_exp_eta.is_normal()) {
            return Err(PanelError::Arithmetic);
        }
        Ok(Some(Restriction{lo,hi,ln_fraction,ln_n,normalized_mean:part.mu,mean_eta,mean_exp_eta,
            panels:total.panels.max(part.panels),convergence_error:total.error.max(part.error)}))
    }
}
